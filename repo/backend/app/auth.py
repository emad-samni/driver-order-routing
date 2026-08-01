"""Simple header-based API key auth for the prototype.

Roles:
- admin: full access.
- driver: restricted to driver and status endpoints.

Configuration via environment variables:
- API_KEY_ADMIN
- API_KEY_DRIVER
"""

from __future__ import annotations

import os
from typing import Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

ADMIN_KEY = os.getenv("API_KEY_ADMIN", "admin-key")
DRIVER_KEY = os.getenv("API_KEY_DRIVER", "driver-key")

ADMIN_ROLE = "admin"
DRIVER_ROLE = "driver"


class AuthError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=401, detail="Missing or invalid API key")


def _extract_api_key(request: Request) -> str | None:
    return request.headers.get("x-api-key") or request.headers.get("X-API-Key")


def _role_for_key(api_key: str | None) -> str | None:
    if api_key is None:
        return None
    if api_key == ADMIN_KEY:
        return ADMIN_ROLE
    if api_key == DRIVER_KEY:
        return DRIVER_ROLE
    return None


def require_role(required_role: str) -> Callable[[Request], None]:
    def dependency(request: Request) -> None:
        api_key = _extract_api_key(request)
        role = _role_for_key(api_key)
        if role is None:
            raise AuthError()
        if role != required_role and role != ADMIN_ROLE:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
    return dependency
