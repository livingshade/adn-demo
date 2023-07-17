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
    
    os.chdir("./phoenix")
    os.system("git switch adn")
    os.system("git pull")
    os.chdir("..")
    
    os.chdir("./adn/compiler")    
    os.system("git switch main")
    os.system("git pull")
    res = subprocess.run(["python", "main.py", "-e", chain, "--mrpc_dir", "../../phoenix/experimental/mrpc"], capture_output=True)
    os.chdir("../..")
    print(res.stdout)
    
    engine_name = [i.strip() for i in chain.split("->")]
    print("Engines: ", engine_name)

    engines = []
    for engine in engine_name:
        name = f"gen_{engine}_{len(engines)}"
        engines.append(name)
    
    engines = [to_cargo_toml(i) for i in engines]    

    api = [f"generated/api/{i}" for i in engines]
    
    plugins = [f"generated/plugin/{i}" for i in engines]
    
    dep = [(f"phoenix-api-policy-{i}", {"path": f"generated/api/{i}"}) for i in engines]
    print(api, plugins)

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
    
    os.system("cp ./phoenix/experimental/mrpc/load-mrpc-plugins.toml ./load-mrpc-plugins.toml")
    
    with open("load-mrpc-plugins.toml", "a") as f:
        for e in engines:
            app = modify_load(e)
            f.write(app)
    
    os.system("cp ./load-mrpc-plugins.toml ./phoenix/experimental/mrpc/load-mrpc-plugins.toml")
    
    os.chdir("./phoenix/experimental/mrpc")
    for e in engines:
        os.system(f"cargo make build-mrpc-plugin-single {e}")
        
    os.system("cargo make deploy-plugins")
    
    os.chdir("../..")
    os.system("cargo run --release --bin upgrade -- --config experimental/mrpc/load-mrpc-plugins.toml")
    
    print("Finish Loading Generated Plugins!")
    
    