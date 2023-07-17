import os
import sys
import tomli
import tomli_w
import subprocess

def to_cargo_toml(name: str) -> str:   
    return name.replace("_", "-")

def modify_load(engine: str) -> str:
    name = engine.split("-")
    firstcap = [i.capitalize() for i in name]
    firstcap = "".join(firstcap)
    rlib = engine.replace("-", "_")
    rlib = rlib.lower()
    return f"""
[[addons]]
name = "{firstcap}"
lib_path = "plugins/libphoenix_{rlib}.rlib"
config_string = \'\'\'
\'\'\'
"""

if __name__ == "__main__":
    with open("input", "r") as f:
        chain = f.read().strip()
        
    print("Graph Sepc: ", chain)
    chain = chain.replace("()", "")
    
    print("Using default protobuf...")
    # res = subprocess.run(["python", "main.py", "-e", chain, "--mrpc_dir", "../../phoenix/experimental/mrpc"], capture_output=True, text=True)
    os.chdir("./adn/compiler")    
    os.system("PYTHONPATH=$PYTHONPATH:$(pwd):$(dirname $(pwd)) python main.py -e '" + chain + "' --mrpc_dir ../../phoenix/experimental/mrpc")
    os.chdir("../..")

    # print("Running ADN Compiler...")
    # print(res.stdout)
    # print(res.stderr)
    # print("Code generated!")
    
    engine_name = [i.strip() for i in chain.split("->")]

    
    print("Deploying to mRPC...")
    engines = []
    for engine in engine_name:
        name = f"gen_{engine}_{len(engines)}"
        engines.append(name)
    
    engines = [to_cargo_toml(i) for i in engines]    

    api = [f"generated/api/{i}" for i in engines]
    
    plugins = [f"generated/plugin/{i}" for i in engines]
    
    dep = [(f"phoenix-api-policy-{i}", {"path": f"generated/api/{i}"}) for i in engines]


    os.system("cp ./phoenix/experimental/mrpc/Cargo.toml ./Cargo.toml")
    with open("Cargo.toml", "r") as f:
        cargo_toml = tomli.loads(f.read())
        
    members = cargo_toml["workspace"]["members"]
    members = members + api + plugins
    cargo_toml["workspace"]["members"] = members 
    depends = cargo_toml["workspace"]["dependencies"]
    depends.update({i[0]: i[1] for i in dep})
    
    with open("Cargo2.toml", "w") as f:
        f.write(tomli_w.dumps(cargo_toml))
    os.system("cp ./Cargo2.toml ./phoenix/experimental/mrpc/Cargo.toml")
    
    with open("load-mrpc-plugins-gen.toml", "a") as f:
        for e in engines:
            app = modify_load(e)
            f.write(app)
    
    os.system("cp ./load-mrpc-plugins-gen.toml ./phoenix/experimental/mrpc/generated/load-mrpc-plugins-gen.toml")
    
    
    os.chdir("./phoenix/experimental/mrpc")
    for e in engines:
        print("Compiling mRPC Plugin: ", e)
        res = subprocess.run(["cargo", "make", "build-mrpc-plugin-single", e], capture_output=True)
        #os.system(f"cargo make build-mrpc-plugin-single {e}")
    
    print("Installing mRPC Plugin...")    
    res = subprocess.run(["cargo", "make", "deploy-plugins"], capture_output=True)
    
    os.chdir("../..")

    res = subprocess.run(["cargo", "run", "--release" ,"--bin", "upgrade", "--", "--config", "./experimental/mrpc/generated/load-mrpc-plugins-gen.toml"], capture_output=True)

    print("Deployed to mRPC!")
    
   # print("Cleaning up...")
    #os.chdir("..")
    #os.system("cp ./Cargo.toml ./phoenix/experimental/mrpc/Cargo.toml")
    
