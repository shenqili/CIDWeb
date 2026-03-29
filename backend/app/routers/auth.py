from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text

from ..db import SessionLocal
from ..deps import DemoAuthContext, get_demo_auth_context, load_real_auth_context
from ..schemas import LoginRequest, LoginResponse, UserProfile
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _build_user_profile(context: DemoAuthContext) -> UserProfile:
    return UserProfile(
        userId=context.user_id,
        tenantId=context.tenant_id,
        tenantName=context.tenant_name,
        loginName=context.login_name,
        displayName=context.display_name,
        roles=context.roles,
        permissions=context.permissions,
        isSuperAdmin=context.is_super_admin,
        allowedBrandIds=context.allowed_brand_codes,
        activeBrandId=context.preferred_brand_code,
    )


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest) -> LoginResponse:
    login_name = payload.loginName.strip().lower()
    requested_brand_code = payload.activeBrandId.strip().lower() if payload.activeBrandId else None

    with SessionLocal() as db:
        credential_row = db.execute(
            text(
                """
                select
                  ou.user_id,
                  ou.tenant_id,
                  ou.status as user_status,
                  ulc.login_name,
                  ulc.password_hash,
                  ulc.is_enabled
                from user_login_credential ulc
                join organization_user ou on ou.user_id = ulc.user_id
                where lower(ulc.login_name) = :login_name
                """
            ),
            {"login_name": login_name},
        ).mappings().first()

    if credential_row is None or credential_row["user_status"] != "active" or not credential_row["is_enabled"]:
        raise HTTPException(status_code=401, detail="账号或密码错误")

    if not verify_password(payload.password, credential_row["password_hash"]):
        raise HTTPException(status_code=401, detail="账号或密码错误")

    context = load_real_auth_context(
        user_id=str(credential_row["user_id"]),
        login_name=login_name,
        requested_brand_code=requested_brand_code,
    )
    return LoginResponse(
        accessToken=create_access_token(context.user_id, context.tenant_id, context.login_name),
        user=_build_user_profile(context),
    )


@router.get("/me", response_model=UserProfile)
def get_me(context: DemoAuthContext = Depends(get_demo_auth_context)) -> UserProfile:
    return _build_user_profile(context)
