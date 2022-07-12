# Flagsmith Edge Proxy

https://docs.flagsmith.com/advanced-use/edge-proxy


## Configuration
Edge proxy can be configured using the `config.json` file located at the root.
* With docker run:

 docker run -v  /<path-to-local>/config.json:/app/config.json flagsmith/edge-proxy:latest

## Load Testing

You can send post request with `wrk` like this:

```bash
cd load-test
wrk -t10 -c40 -d5 -s post.lua -H 'X-Environment-Key: NC7zfaBWg7QJhbHpUMs7tv' 'http://localhost:8001/api/v1/identities/?identifier=development_user_123456'
```
