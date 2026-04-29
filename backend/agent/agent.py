"""
Minimal agent example (Python)

Usage:
  python agent.py --backend http://localhost:8000 --machine-id <id> --token <token>

The agent opens a WebSocket to `/api/v1/machines/ws/{machine_id}?token=<token>` and
responds to simple commands: `list` and `read`.
"""
import argparse
import asyncio
import json
import os
import base64
from pathlib import Path

import websockets


async def handle_connection(uri, machine_id, token):
    ws_uri = f"{uri.rstrip('/')}/api/v1/machines/ws/{machine_id}?token={token}"
    async with websockets.connect(ws_uri) as ws:
        print("Conectado ao servidor como", machine_id)
        try:
            async for msg in ws:
                try:
                    payload = json.loads(msg)
                except Exception:
                    continue

                cmd = payload.get("cmd")
                if cmd == "list":
                    path = payload.get("path") or "."
                    try:
                        items = os.listdir(path)
                        await ws.send(json.dumps({"ok": True, "items": items}))
                    except Exception as e:
                        await ws.send(json.dumps({"ok": False, "error": str(e)}))

                elif cmd == "read":
                    path = payload.get("path")
                    max_bytes = int(payload.get("max_bytes", 65536))
                    try:
                        with open(path, "rb") as fh:
                            data = fh.read(max_bytes)
                        b64 = base64.b64encode(data).decode("ascii")
                        await ws.send(json.dumps({"ok": True, "data_b64": b64}))
                    except Exception as e:
                        await ws.send(json.dumps({"ok": False, "error": str(e)}))
                else:
                    await ws.send(json.dumps({"ok": False, "error": "unknown-cmd"}))
        except websockets.exceptions.ConnectionClosed:
            print("Conexão fechada")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True)
    parser.add_argument("--machine-id", required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()

    asyncio.run(handle_connection(args.backend.replace('http://', 'ws://').replace('https://', 'wss://'), args.machine_id, args.token))


if __name__ == "__main__":
    main()
