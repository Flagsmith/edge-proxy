# Flagsmith Edge Proxy

https://docs.flagsmith.com/advanced-use/edge-proxy

## Configuration

Edge proxy can be configured using the `config.json` file located at the root.

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

## Load Testing

You can send post request with `wrk` like this:

```bash
cd load-test
wrk -t10 -c40 -d5 -s post.lua -H 'X-Environment-Key: NC7zfaBWg7QJhbHpUMs7tv' 'http://localhost:8001/api/v1/identities/?identifier=development_user_123456'
```
