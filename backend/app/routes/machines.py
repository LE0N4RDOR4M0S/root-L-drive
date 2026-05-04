from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect, Body
from typing import Dict, Any
import asyncio
import json
from uuid import uuid4

from app.core.dependencies import get_current_user
from app.db.mongodb import get_database
from app.repositories.mongo_machine_repository import MongoMachineRepository
from app.schemas.machine import CreateMachineRequest, MachineCreateResponse, MachineListItemResponse
from app.services.machine_service import MachineService
from app.core.config import settings
from fastapi.responses import PlainTextResponse
import html


router = APIRouter(prefix="/machines", tags=["machines"])

# In-memory connection manager: machine_id -> WebSocket
_connections: Dict[str, WebSocket] = {}
_pending_responses: Dict[str, Dict[str, asyncio.Future]] = {}


async def send_command_to_machine(machine_id: str, payload: dict, timeout: float = 10.0) -> dict:
    ws = _connections.get(machine_id)
    if ws is None:
        raise RuntimeError("machine-not-connected")

    request_id = str(payload.get("request_id") or uuid4())
    command_payload = dict(payload)
    command_payload["request_id"] = request_id
    machine_pending = _pending_responses.setdefault(machine_id, {})
    if request_id in machine_pending:
        raise RuntimeError("duplicate-request-id")
    future = asyncio.get_running_loop().create_future()
    machine_pending[request_id] = future

    try:
        # Send payload and wait for response correlated by request_id
        await ws.send_text(json.dumps(command_payload))
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise RuntimeError("machine-timeout")
    finally:
        machine_pending.pop(request_id, None)
        if not machine_pending:
            _pending_responses.pop(machine_id, None)


def get_machine_service() -> MachineService:
    return MachineService(machine_repo=MongoMachineRepository(get_database()))


def serialize_machine(machine) -> MachineListItemResponse:
    return MachineListItemResponse(
        id=machine.id,
        name=machine.name,
        allowed_paths=machine.allowed_paths,
        created_at=machine.created_at.isoformat() if getattr(machine, 'created_at', None) is not None else None,
        last_seen=machine.last_seen.isoformat() if getattr(machine, 'last_seen', None) is not None else None,
        is_active=machine.is_active,
    )


@router.get("", response_model=list[MachineListItemResponse])
async def list_machines(current_user=Depends(get_current_user), limit: int = 200):
    service = get_machine_service()
    machines = await service.list_machines(owner_id=current_user.id, limit=limit)
    return [serialize_machine(item) for item in machines]


@router.post("", response_model=MachineCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_machine(payload: CreateMachineRequest, current_user=Depends(get_current_user)):
    service = get_machine_service()
    machine, raw_token = await service.create_machine(
        owner_id=current_user.id,
        name=payload.name,
        allowed_paths=payload.allowed_paths,
        expires_in_days=payload.expires_in_days,
    )
    # generate a one-file installer script embedding token and config
    backend_url = settings.backend_public_url
    backend_ws_base = backend_url.rstrip('/')
    if backend_ws_base.startswith("https://"):
        backend_ws_base = "wss://" + backend_ws_base[len("https://"):]
    elif backend_ws_base.startswith("http://"):
        backend_ws_base = "ws://" + backend_ws_base[len("http://"):]
    elif not backend_ws_base.startswith(("ws://", "wss://")):
        backend_ws_base = "ws://" + backend_ws_base

    installer_template = '''#!/usr/bin/env python3
"""
Auto-generated installer for machine {machine_name}
Run this on the target machine to start the agent.
"""
import asyncio
import argparse
import base64
from datetime import datetime
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import websockets

MACHINE_ID = "{machine_id}"
TOKEN = "{raw_token}"
BACKEND_WS = "{backend_ws}"


def _log(event, detail=""):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if detail:
        print("[%s] %s | %s" % (ts, event, detail))
    else:
        print("[%s] %s" % (ts, event))


def _normalize(path):
    return os.path.abspath(os.path.expanduser(path))


def _read_allowed_paths():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--allow', action='append', dest='allowed', default=[])
    parser.add_argument('--no-ui', action='store_true', dest='no_ui')
    args, _ = parser.parse_known_args()

    # Easy runtime config: python install_x.py --allow "L:/root" --allow "D:/docs"
    allowed = [p.strip() for p in args.allowed if p and p.strip()]

    if not allowed and not args.no_ui:
        try:
            root = tk.Tk()
            root.withdraw()
            root.update()

            selected = []
            while True:
                path = filedialog.askdirectory(title='Selecione um diretorio autorizado')
                if path:
                    selected.append(path)
                    add_more = messagebox.askyesno('Diretorios autorizados', 'Adicionar outro diretorio?')
                    if add_more:
                        continue
                break

            root.destroy()
            allowed = selected
        except Exception:
            # Fallback for environments without GUI
            allowed = []

    if not allowed:
        raw = input('Diretorios autorizados (separados por ;, vazio = diretorio atual): ').strip()
        if raw:
            allowed = [p.strip() for p in raw.split(';') if p.strip()]

    if not allowed:
        allowed = [os.getcwd()]

    normalized = []
    for p in allowed:
        np = _normalize(p)
        if os.path.isdir(np):
            normalized.append(np)

    if not normalized:
        normalized = [os.getcwd()]

    return normalized


ALLOWED_PATHS = _read_allowed_paths()


def _is_allowed(target_path):
    target = _normalize(target_path)
    for base in ALLOWED_PATHS:
        try:
            if os.path.commonpath([target, base]) == base:
                return True
        except ValueError:
            # Ignore mixed-drive paths on Windows
            continue
    return False


def _resolve_requested_path(requested_path):
    if not requested_path or requested_path in ('.', './', '.\\\\'):
        return ALLOWED_PATHS[0]
    if os.path.isabs(requested_path):
        return _normalize(requested_path)
    return _normalize(os.path.join(ALLOWED_PATHS[0], requested_path))


async def run():
    _log('AGENT_START', 'machine_id=%s' % MACHINE_ID)
    _log('WS_CONNECTING', BACKEND_WS)
    _log('ALLOWED_PATHS', '; '.join(ALLOWED_PATHS))
    _log('INFO', 'Agente em modo continuo. Use Ctrl+C para encerrar.')

    try:
        async with websockets.connect(BACKEND_WS) as ws:
            _log('WS_CONNECTED')
            try:
                async for msg in ws:
                    payload = json.loads(msg)
                    cmd = payload.get('cmd')
                    request_id = payload.get('request_id')
                    _log('CMD_RECEIVED', str(cmd))
                    if cmd == 'list':
                        requested_path = payload.get('path')
                        path = _resolve_requested_path(requested_path)
                        try:
                            if not _is_allowed(path):
                                raise PermissionError('path not allowed')
                            items = os.listdir(path)
                            await ws.send(json.dumps({{"ok": True, "items": items, "path": path, "request_id": request_id}}))
                            _log('CMD_DONE', 'list %s (%s itens)' % (path, len(items)))
                        except Exception as e:
                            await ws.send(json.dumps({{"ok": False, "error": str(e), "request_id": request_id}}))
                            _log('CMD_ERROR', 'list %s: %s' % (path, e))
                    elif cmd == 'read':
                        requested_path = payload.get('path')
                        max_bytes = int(payload.get('max_bytes', 65536))
                        try:
                            if not requested_path:
                                raise ValueError('path is required')
                            path = _resolve_requested_path(requested_path)
                            if not _is_allowed(path):
                                raise PermissionError('path not allowed')
                            with open(path, 'rb') as fh:
                                data = fh.read(max_bytes)
                            b64 = base64.b64encode(data).decode('ascii')
                            await ws.send(json.dumps({{"ok": True, "data_b64": b64, "path": path, "request_id": request_id}}))
                            _log('CMD_DONE', 'read %s (%s bytes)' % (path, len(data)))
                        except Exception as e:
                            await ws.send(json.dumps({{"ok": False, "error": str(e), "request_id": request_id}}))
                            _log('CMD_ERROR', 'read %s: %s' % (requested_path, e))
                    else:
                        await ws.send(json.dumps({{"ok": False, "error": 'unknown-cmd', "request_id": request_id}}))
                        _log('CMD_ERROR', 'unknown-cmd=%s' % cmd)
            except websockets.exceptions.ConnectionClosed:
                _log('WS_CLOSED')
    except Exception as exc:
        _log('FATAL', str(exc))
        raise
    finally:
        _log('AGENT_STOP')

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        _log('INTERRUPTED_BY_USER')
        sys.exit(0)
'''

    installer = installer_template.format(
        machine_name=html.escape(machine.name),
        machine_id=machine.id,
        raw_token=raw_token,
        backend_ws=backend_ws_base + f"/api/v1/machines/ws/{machine.id}?token={raw_token}",
    )

    return MachineCreateResponse(**serialize_machine(machine).model_dump(), token=raw_token, installer_script=installer)


@router.patch("/{machine_id}/revoke", response_model=MachineListItemResponse)
async def revoke_machine(machine_id: str, current_user=Depends(get_current_user)):
    service = get_machine_service()
    machine = await service.revoke_machine(owner_id=current_user.id, machine_id=machine_id)
    return serialize_machine(machine)


@router.websocket("/ws/{machine_id}")
async def machine_ws(websocket: WebSocket, machine_id: str, token: str | None = None):
    # Accept the connection then validate token
    await websocket.accept()

    # token expected in query param `token`
    if token is None:
        await websocket.close(code=1008)
        return

    # validate token
    db = get_database()
    repo = MongoMachineRepository(db)
    token_hash = MachineService.hash_token(token)
    record = await repo.get_active_by_hash(token_hash)
    if record is None or record.id != machine_id:
        await websocket.close(code=1008)
        return

    # register connection
    _connections[machine_id] = websocket
    _pending_responses.setdefault(machine_id, {})
    await repo.touch_last_seen(record.id)

    try:
        while True:
            message = await websocket.receive_text()
            try:
                payload = json.loads(message)
                if not isinstance(payload, dict):
                    continue
                req_id = payload.get("request_id")
                if req_id:
                    future = _pending_responses.get(machine_id, {}).get(req_id)
                    if future and not future.done():
                        future.set_result(payload)
            except Exception:
                pass
    except WebSocketDisconnect:
        pass
    finally:
        _connections.pop(machine_id, None)
        pending = _pending_responses.pop(machine_id, {})
        for fut in pending.values():
            if not fut.done():
                fut.set_exception(RuntimeError("machine-disconnected"))


@router.post("/{machine_id}/command")
async def post_command(machine_id: str, payload: dict = Body(...), current_user=Depends(get_current_user)):
    """
    Send a command to a connected machine and wait for response.
    Payload example: {"cmd":"list","path":"C:/Users/..."}
    """
    # ensure ownership
    service = get_machine_service()
    machine = await service.list_machines(owner_id=current_user.id)
    # check machine exists for user
    if not any(m.id == machine_id for m in machine):
        return {"error": "not-found-or-not-owner"}

    try:
        resp = await send_command_to_machine(machine_id, payload)
        return {"ok": True, "result": resp}
    except RuntimeError as exc:
        return {"ok": False, "error": str(exc)}
