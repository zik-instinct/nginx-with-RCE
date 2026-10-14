# nginx-with-RCE

> Parody demo - not official nginx.

The terminal starts as a local JavaScript console. Expressions run in the visitor's browser, not on the server. `server.connect()` switches to server mode; `help` lists the available commands.

The server console can run exactly three fixed commands:

- `whoami`
- `ifconfig`
- `ping example.com -t 1`

Requests must match the full string exactly. The ping request runs one packet using Linux `-c 1`, with a short deadline. All other commands get a canned refusal. No request header is evaluated.

Finding the RCE earns a bounty: all necessary cookies.

## Run

Serve `demo.html` as `index.html`. Install Python 3, net-tools, and iputils-ping. Put `command_server.py` in `/opt/nginx-command-demo/`, install `nginx-command-demo.service` under `/etc/systemd/system/`, and enable the service. It runs as `www-data`, listening only on `127.0.0.1:8766`.

The hostname-specific nginx config is in `deploy/nginx.gtelem.com.conf`. Proxy `/api/command` to the local service, preserving the existing HTTPS configuration. Do not replace other virtual hosts.

The runner uses fixed argv arrays, never a shell. Each process has a four-second deadline and a 16 KiB output cap. Request bodies are capped at 256 bytes. The systemd service has read-only system access, private temporary files, and memory, CPU, and task limits. The public endpoint intentionally exposes these three outputs, including interface information from `ifconfig`.
