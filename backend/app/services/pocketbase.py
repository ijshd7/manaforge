from datetime import datetime, timedelta

import httpx

from ..config import settings


class PocketBaseClient:
    def __init__(self):
        self._token: str | None = None
        self._token_expires: datetime = datetime.min
        self._client = httpx.AsyncClient(
            base_url=settings.pocketbase_url,
            timeout=30.0,
        )

    async def _ensure_auth(self) -> None:
        if self._token and datetime.utcnow() < self._token_expires:
            return

        # PocketBase uses /api/collections/_superusers/auth-with-password for admin auth
        resp = await self._client.post(
            "/api/collections/_superusers/auth-with-password",
            json={
                "identity": settings.pocketbase_superuser_email,
                "password": settings.pocketbase_superuser_password,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        self._token = data["token"]
        self._token_expires = datetime.utcnow() + timedelta(hours=23)

    async def _auth_headers(self) -> dict:
        await self._ensure_auth()
        return {"Authorization": self._token}

    async def create_asset(
        self,
        asset_type: str,
        name: str,
        prompt: str,
        style: str | None = None,
        file_bytes: bytes | None = None,
        filename: str | None = None,
        content: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        headers = await self._auth_headers()

        fields = {
            "type": asset_type,
            "name": name,
            "prompt": prompt,
        }
        if style:
            fields["style"] = style
        if content:
            fields["content"] = content
        if metadata:
            import json
            fields["metadata"] = json.dumps(metadata)

        if file_bytes and filename:
            resp = await self._client.post(
                "/api/collections/assets/records",
                data=fields,
                files={"file": (filename, file_bytes)},
                headers=headers,
            )
        else:
            resp = await self._client.post(
                "/api/collections/assets/records",
                data=fields,
                headers=headers,
            )

        resp.raise_for_status()
        return resp.json()

    async def list_assets(
        self,
        page: int = 1,
        per_page: int = 24,
        filter_type: str | None = None,
    ) -> dict:
        headers = await self._auth_headers()
        params: dict = {
            "page": page,
            "perPage": per_page,
            "sort": "-name",
        }
        if filter_type:
            params["filter"] = f'type="{filter_type}"'

        resp = await self._client.get(
            "/api/collections/assets/records",
            params=params,
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()

    async def get_asset(self, record_id: str) -> dict:
        headers = await self._auth_headers()
        resp = await self._client.get(
            f"/api/collections/assets/records/{record_id}",
            headers=headers,
        )
        resp.raise_for_status()
        return resp.json()

    async def delete_asset(self, record_id: str) -> None:
        headers = await self._auth_headers()
        resp = await self._client.delete(
            f"/api/collections/assets/records/{record_id}",
            headers=headers,
        )
        resp.raise_for_status()

    def get_file_url(self, record_id: str, filename: str) -> str:
        return f"{settings.pocketbase_url}/api/files/assets/{record_id}/{filename}"


pb_client = PocketBaseClient()
