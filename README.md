# nginx-with-RCE

> **Parody demo - NOT the official nginx.** The code-execution feature below is planted intentionally as a joke.
>
> **This demo does not execute code.** The browser buttons show fixed, canned output. No request header is evaluated, and there is no command runner.

A small static joke page for `nginx.gtelem.com`. It has a fake terminal, canned responses, and a little celebratory animation. The page is self-contained; it does not proxy requests or run a backend.

## Local preview

Open `index.html` in a browser. Click a command button to see the canned simulation and animation. The page works without a build step or network access.

## Deploy to an existing nginx host

See `deploy/README.md` for the hostname-specific nginx server block and cautious deployment steps. The config serves only this static directory and does not alter the global nginx config.
