from pydantic import BaseModel


class LoginRequest(BaseModel):
    loginName: str
    password: str
    activeBrandId: str | None = None


class UserProfile(BaseModel):
    userId: str
    tenantId: str
    tenantName: str
    loginName: str
    displayName: str
    roles: list[str]
    permissions: list[str]
    isSuperAdmin: bool
    allowedBrandIds: list[str] = []
    activeBrandId: str | None = None


class LoginResponse(BaseModel):
    accessToken: str
    user: UserProfile
