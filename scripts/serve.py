#!/usr/bin/env python3
"""
Local dev server with live rebuild.

    python scripts/serve.py            # http://localhost:8000
    python scripts/serve.py 8080       # pick a port

Watches papers/, shared/, scripts/ and site.yaml. When anything changes it
rebuilds the site and the open browser tab reloads itself. The reload works by
build.py --dev injecting a small poller that watches /__buildid, so there is no
websocket dependency and nothing to install beyond the normal requirements.

PDFs are not regenerated on every change (they are slow); run
`python scripts/make_pdf.py` when you want to refresh them.
"""
from __future__ import annotations

import http.server
import socketserver
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
SCRIPTS = ROOT / "scripts"

WATCH_DIRS = [ROOT / "papers", ROOT / "shared", SCRIPTS]
WATCH_FILES = [ROOT / "site.yaml"]
IGNORE_SUFFIXES = {".pdf", ".pyc"}
POLL_SECONDS = 0.5


def snapshot() -> dict[str, float]:
    """Map of watched path -> mtime."""
    state: dict[str, float] = {}
    for d in WATCH_DIRS:
        if not d.exists():
            continue
        for p in d.rglob("*"):
            if p.is_file() and p.suffix not in IGNORE_SUFFIXES and "__pycache__" not in p.parts:
                try:
                    state[str(p)] = p.stat().st_mtime
                except OSError:
                    pass
    for f in WATCH_FILES:
        if f.exists():
            state[str(f)] = f.stat().st_mtime
    return state


def run_build() -> bool:
    """Rebuild in-process. Returns True on success."""
    for mod in ("build", "icons"):
        sys.modules.pop(mod, None)
    sys.path.insert(0, str(SCRIPTS))
    saved = sys.argv[:]
    try:
        sys.argv = ["build.py", "--dev"]
        import build  # re-imported fresh each time
        build.main()
        return True
    except Exception as exc:  # keep serving the last good build
        print(f"\n  build failed: {type(exc).__name__}: {exc}\n")
        return False
    finally:
        sys.argv = saved


def watcher() -> None:
    last = snapshot()
    while True:
        time.sleep(POLL_SECONDS)
        now = snapshot()
        if now != last:
            changed = [Path(p).name for p in set(now) ^ set(last)]
            changed += [Path(p).name for p in now
                        if p in last and now[p] != last[p]]
            uniq = sorted(set(changed))[:4]
            print(f"changed: {', '.join(uniq)}" + (" ..." if len(changed) > 4 else ""))
            run_build()
            last = snapshot()


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(SITE), **kw)

    def end_headers(self):
        # never cache during development
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def log_message(self, fmt, *args):  # quieter console
        # log_error routes through here with args like (HTTPStatus, str), so
        # format first instead of assuming args[0] is a string
        try:
            msg = fmt % args if args else fmt
        except TypeError:
            msg = fmt
        if "__buildid" not in msg:
            super().log_message(fmt, *args)


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main() -> None:
    port = 8000
    for a in sys.argv[1:]:
        if a.isdigit():
            port = int(a)

    print("building...")
    run_build()

    threading.Thread(target=watcher, daemon=True).start()

    with Server(("", port), Handler) as httpd:
        print(f"\n  serving  http://localhost:{port}/")
        print(f"  watching {', '.join(d.name for d in WATCH_DIRS)}, site.yaml")
        print("  edit a file and the page reloads.  ctrl-c to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped.")


if __name__ == "__main__":
    main()
