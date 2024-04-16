# Flagsmith Edge Proxy

https://docs.flagsmith.com/advanced-use/edge-proxy

## Local development

### Prerequisites

- `Python3`
- `Docker`

### Setup local environment and pre-commit hooks

1. Setup virtual environment (Optional, but recommended)
```shell
# Create a virtual environment (first time)
python3 -m venv venv
# Activate the virtual environment
source ./venv/bin/activate

# Deactivate virtual environment when done
deactivate
```
2. Install dependencies
```shell
# Install python requirements
pip install -r requirements.txt -r requirements-dev.txt
```
3. Install pre-commit hooks
```shell
# Confirm pre-commit is installed
pre-commit --version

# Install pre-commit hooks
pre-commit install
```

### Build and run Docker image locally

```shell
# Build image
docker build . -t edge-proxy-local

# Run image 
docker run -it --rm \
  -v <path-to-config>/config.json:/app/config.json \
  -p 8000:8000 \
  edge-proxy-local:latest
```

## Configuration

Edge proxy can be configured using the `config.json` file located at the root or at a location defined by the `CONFIG_PATH` environment variable.

### Supported configuration

You can set the following configuration(in config.json) to control the behaviour
of edge-proxy

- environment_key_pairs: An array of environment key pair objects, e.g:
  `"environment_key_pairs":[{"server_side_key":"your_server_side_key", "client_side_key":"your_client_side_environment_key"}]`

- [Optional]api_poll_frequency(seconds): it is used to control how often the proxy is going to ping the server for changes,
  e.g: `"api_poll_frequency":10`

- [Optional]api_url: If you are running a self hosted version of flagsmith you can add the self hosted url here for edge-proxy to ping
  your server, e.g: `"api_url":"https://self.hosted.flagsmith.com/api/v1"`

### Here are some examples of adding local `config.json` to edge-proxy:

#### Default location

- With docker run:
  `docker run -v /<path-to-local>/config.json:/app/config.json flagsmith/edge-proxy:latest`

- With docker compose:

```yaml
version: "3.9"
services:
  edge_proxy:
    image: flagsmith/edge-proxy:latest
    volumes:
      - type: bind
        source: /<path-to-local>/config.json
        target: /app/config.json
```

#### Location defined by environment variable

- With docker run:
  `docker run -e CONFIG_PATH='/tmp/config.json' -v /<path-to-local>/config.json:/tmp/config.json flagsmith/edge-proxy:latest`

- With docker compose:

```yaml
version: "3.9"
services:
  edge_proxy:
    image: flagsmith/edge-proxy:latest
    volumes:
      - type: bind
        source: /<path-to-local>/config.json
        target: /tmp/config.json
    environment:
      - CONFIG_PATH='/tmp/config.json'
```

## Load Testing

You can send post request with `wrk` like this:

```bash
cd load-test
wrk -t10 -c40 -d5 -s post.lua -H 'X-Environment-Key: NC7zfaBWg7QJhbHpUMs7tv' 'http://localhost:8001/api/v1/identities/?identifier=development_user_123456'
```

