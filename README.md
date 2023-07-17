# Get Started

## Boostrap

```bash
git clone https://github.com/livingshade/adn-demo.git --recursive
python -m pip install tomli tomli-w lark
cd phoenix
git switch adn
git pull
# install other dependencies to run phoenix
cd ../adn
git switch graph
git pull
```

## Startup (3 Seperate Terminal)

### Control Plane

```bash
cd phoenix
cargo make
# wait for the build to finish
cd ./experimental/mrpc
cargo make
# wait control plane to start, do not close the terminal
```

### Server
 
```bash
cd phoenix/experimental/mrpc
cargo run --release -p rpc_echo --bin rpc_echo_server
# do not close the terminal
```

### Client

```bash
cd phoenix/experimental/mrpc
cargo run --release -p rpc_echo --bin rpc_echo_client
# do not close the terminal
```

## Live Upgrade

Make sure input is `fault->logging`

```bash
python run.py
# wait for "Finish Loading Generated Plugins!"
```

Then you can attach engines, for example:

```bash
cd phoenix/experimental/mrpc
# assume the pid of client is 666725
# attach
cargo run --release --bin addonctl -- --config experimental/mrpc/generated/addonctl/gen_fault_0_attach.toml --pid 666725 --sid 1
cargo run --release --bin addonctl -- --config experimental/mrpc/generated/addonctl/gen_logging_1_detach.toml --pid 666725 --sid 1

# wait for few seconds to see the effect of the engine

# detach
# note the order matters
cargo run --release --bin addonctl -- --config experimental/mrpc/generated/addonctl/gen_logging_1_detach.toml --pid 666725 --sid 1
cargo run --release --bin addonctl -- --config experimental/mrpc/generated/addonctl/gen_fault_0_detach.toml --pid 666725 --sid 1
```