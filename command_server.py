import json
import os
import selectors
import subprocess
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

COMMANDS = {
    'whoami': ['/usr/bin/whoami'],
    'ifconfig': ['/usr/sbin/ifconfig'],
    'ping example.com -t 1': ['/usr/bin/ping', '-c', '1', '-W', '2', '-w', '3', 'example.com'],
}
LIMIT = 16384
REFUSAL = 'Permission denied. Necessary cookies do not cover that command.'


def execute(argv):
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, shell=False, cwd='/tmp',
                               env={'PATH': '/usr/bin:/usr/sbin', 'LANG': 'C'})
    chunks = bytearray()
    deadline = time.monotonic() + 4
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    note = ''
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                note = '\n[timeout]'
                break
            events = selector.select(remaining)
            if not events:
                note = '\n[timeout]'
                break
            chunk = os.read(process.stdout.fileno(), min(4096, LIMIT - len(chunks)))
            if not chunk:
                break
            chunks.extend(chunk)
            if len(chunks) >= LIMIT:
                note = '\n[output capped]'
                break
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=1)
        selector.close()
        process.stdout.close()
    return chunks.decode('utf-8', errors='replace') + note, process.returncode


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(2)

    def reply(self, status, output, **extra):
        data = json.dumps({'output': output, **extra}).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != '/api/command':
            return self.reply(404, REFUSAL)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 256 or self.headers.get('Transfer-Encoding'):
                return self.reply(400, REFUSAL)
            data = json.loads(self.rfile.read(size))
            command = data.get('command') if isinstance(data, dict) else None
            if not isinstance(command, str) or command not in COMMANDS:
                return self.reply(403, REFUSAL)
            output, code = execute(COMMANDS[command])
            return self.reply(200, output, exit_code=code)
        except (ValueError, OSError, subprocess.SubprocessError):
            return self.reply(400, REFUSAL)

    def do_GET(self):
        self.reply(405, REFUSAL)


HTTPServer(('127.0.0.1', 8766), Handler).serve_forever()
