# TV app

## Webassembly

### emscripten

#### install

```bash
# clone emsdk repo
git clone https://github.com/emscripten-core/emsdk.git

# enter the directory
cd emsdk

# update
git pull

# Download and install the latest SDK tools
./emsdk install latest

# Make the "latest" SDK "active" for the current user. (writes .emscripten file)
./emsdk activate latest

# Activate PATH and other environment variables in the current terminal
source ./emsdk_env.sh
```
