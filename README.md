[![Feature Flag, Remote Config and A/B Testing platform, Flagsmith](https://raw.githubusercontent.com/Flagsmith/flagsmith/main/static-files/hero.png)](https://www.flagsmith.com/)

[![Join the Discord chat](https://img.shields.io/discord/517647859495993347)](https://discord.gg/hFhxNtXzgm)

[Flagsmith](https://flagsmith.com/) is an open source, fully featured, Feature Flag and Remote Config service. Use our
hosted API, deploy to your own private cloud, or run on-premise.

# Edge Proxy

The Flagsmith Edge Proxy allows you to run an instance of the Flagsmith Engine close to your servers. If you are running
Flagsmith within a server-side environment and you want to have very low latency flags, you have two options:

1. Run the Edge Proxy and connect to it from your server-side SDKs
2. Run your server-side SDKs in [Local Evaluation Mode](https://docs.flagsmith.com/clients/overview#2---local-evaluation).

The main benefit to running the Edge Proxy is that you reduce your polling requests against the Flagsmith API itself.

The main benefit to running server side SDKs in [Local Evaluation Mode](https://docs.flagsmith.com/clients/overview#2---local-evaluation) is that you get the lowest possible latency.

## Local development

### Prerequisites

- [Rye](https://rye-up.com/guide/installation/)
- [Docker](https://docs.docker.com/engine/install/)

### Setup local environment

Install locked dependencies:

`rye sync --no-lock`

Install pre-commit hooks:

`pre-commit install`

Run tests:

`rye test`


### Build and run Docker image locally

```shell
# Build image
docker build . -t edge-proxy-local

# Run image 
docker run --rm \
  -p 8000:8000 \
  edge-proxy-local
```

## Configuration

See complete configuration [reference](https://docs.flagsmith.com/deployment/hosting/locally-edge-proxy).

Edge Proxy expects to load configuration from `./config.json`.

Create an example configuration by running the `edge-proxy-config` entrypoint:

```sh
rye run edge-proxy-config
```

This will output the example configuration to stdout and write it to `./config.json`.

Here's how to mount the file into Edge Proxy's Docker container:

```sh
docker run -v ./config.json:/app/config.json flagsmith/edge-proxy:latest
```

You can specify custom path to `config.json`, e.g.:

```sh
export CONFIG_PATH=/<path-to-config>/config.json

edge-proxy-config            # Will write an example configuration to custom path.
edge-proxy-serve             # Will read configuration from custom path.
```

You can also mount to custom path inside container:

```sh
docker run \
    -e CONFIG_PATH=/var/foo.json \
    -v /<path-to-config>/config.json:/var/foo.json \
    flagsmith/edge-proxy:latest
``` 

## Load Testing

You can send post request with `wrk` like this:

```bash
cd load-test
wrk -t10 -c40 -d5 -s post.lua -H 'X-Environment-Key: <your environment key>' 'http://localhost:8001/api/v1/identities/?identifier=development_user_123456'
```

## Documentation

See [Edge Proxy documentation](https://docs.flagsmith.com/advanced-use/edge-proxy).
