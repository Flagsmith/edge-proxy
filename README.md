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

## Useful Links

[Documentation](https://docs.flagsmith.com/advanced-use/edge-proxy)
