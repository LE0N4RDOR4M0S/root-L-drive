from datetime import datetime, timedelta, timezone
from hashlib import sha256
import secrets

from fastapi import HTTPException, status

from app.domain.entities.machine import MachineEntity
from app.domain.repositories.machine_repository import MachineRepository


class MachineService:
    def __init__(self, machine_repo: MachineRepository) -> None:
        self.machine_repo = machine_repo

    async def create_machine(self, owner_id: str, name: str, allowed_paths: list[str], expires_in_days: int | None) -> tuple[MachineEntity, str]:
        clean_name = name.strip()
        if not clean_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Machine name is required")

        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)

        raw_token = f"mch_{secrets.token_urlsafe(32)}"
        token_hash = sha256(raw_token.encode("utf-8")).hexdigest()
        machine = await self.machine_repo.create(
            owner_id=owner_id,
            name=clean_name,
            allowed_paths=allowed_paths,
            token_hash=token_hash,
            token_prefix=raw_token[:12],
            token_last4=raw_token[-4:],
            expires_at=expires_at,
        )
        return machine, raw_token

    async def list_machines(self, owner_id: str, limit: int = 200) -> list[MachineEntity]:
        return await self.machine_repo.list_by_owner(owner_id=owner_id, limit=limit)

    async def revoke_machine(self, owner_id: str, machine_id: str) -> MachineEntity:
        machine = await self.machine_repo.get_by_id(machine_id, owner_id)
        if machine is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        revoked = await self.machine_repo.revoke(machine_id=machine_id, owner_id=owner_id)
        if not revoked:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")

        refreshed = await self.machine_repo.get_by_id(machine_id, owner_id)
        if refreshed is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Machine not found")
        return refreshed

    @staticmethod
    def hash_token(raw_token: str) -> str:
        return sha256(raw_token.encode("utf-8")).hexdigest()
