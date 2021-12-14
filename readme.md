# Flagsmith Edge Proxy

https://docs.flagsmith.com/advanced-use/edge-proxy

## Load Testing

You can send post request with `wrk` like this:

```bash
cd load-test
wrk -t10 -c40 -d5 -s post.lua -H 'X-Environment-Key: NC7zfaBWg7QJhbHpUMs7tv' 'http://localhost:8001/api/v1/identities/?identifier=development_user_123456'
```