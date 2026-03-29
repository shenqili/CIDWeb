from dataclasses import dataclass

from fastapi import Header, HTTPException
from sqlalchemy import text

from .db import DEMO_TENANT_ID, SessionLocal
from .security import decode_access_token

DEMO_USER_ID = "22222222-2222-2222-2222-222222222222"
DEFAULT_BRAND_CODE = "brand-bdf"
VALID_ROLES = {"super_admin", "tenant_admin", "brand_manager", "analyst"}


@dataclass
class DemoAuthContext:
    user_id: str
    tenant_id: str
    tenant_name: str
    login_name: str
    display_name: str
    roles: list[str]
    permissions: list[str]
    is_super_admin: bool
    allowed_brand_codes: list[str]
    preferred_brand_code: str | None


def _load_all_brand_codes(db, tenant_id: str) -> list[str]:
    return db.execute(
        text("select brand_code from brand where tenant_id = :tenant_id order by brand_code"),
        {"tenant_id": tenant_id},
    ).scalars().all()


def load_real_auth_context(user_id: str, login_name: str, requested_brand_code: str | None) -> DemoAuthContext:
    with SessionLocal() as db:
        user_row = db.execute(
            text(
                """
                select
                  ou.user_id,
                  ou.tenant_id,
                  t.tenant_name,
                  ou.display_name,
                  ou.is_super_admin,
                  ulc.login_name,
                  ulc.is_enabled
                from organization_user ou
                join tenant t on t.tenant_id = ou.tenant_id
                join user_login_credential ulc on ulc.user_id = ou.user_id
                where ou.user_id = :user_id
                  and ulc.login_name = :login_name
                  and ou.status = 'active'
                """
            ),
            {"user_id": user_id, "login_name": login_name},
        ).mappings().first()

        if user_row is None or not user_row["is_enabled"]:
            raise HTTPException(status_code=401, detail="账号不存在、已停用或登录态已失效")

        tenant_id = str(user_row["tenant_id"])
        all_brand_codes = _load_all_brand_codes(db, tenant_id)
        role_rows = db.execute(
            text(
                """
                select distinct r.role_name
                from project_member pm
                join role r on r.role_id = pm.role_id
                where pm.user_id = :user_id
                order by r.role_name
                """
            ),
            {"user_id": user_id},
        ).scalars().all()

        permission_rows = db.execute(
            text(
                """
                select distinct p.permission_code
                from project_member pm
                join role r on r.role_id = pm.role_id
                join role_permission rp on rp.role_id = r.role_id
                join permission p on p.permission_id = rp.permission_id
                where pm.user_id = :user_id
                order by p.permission_code
                """
            ),
            {"user_id": user_id},
        ).scalars().all()

        allowed_brand_codes: list[str]
        if user_row["is_super_admin"]:
            allowed_brand_codes = list(all_brand_codes)
            permissions = permission_rows or db.execute(
                text("select permission_code from permission order by permission_code")
            ).scalars().all()
        else:
            brand_rows = db.execute(
                text(
                    """
                    with scoped_members as (
                      select project_member_id, project_id, brand_scope_mode
                      from project_member
                      where user_id = :user_id
                    ),
                    allowed_brands as (
                      select distinct b.brand_code
                      from scoped_members sm
                      join project_brand_binding pbb on pbb.project_id = sm.project_id
                      join brand b on b.brand_id = pbb.brand_id
                      where sm.brand_scope_mode = 'all_bound_brands'
                      union
                      select distinct b.brand_code
                      from scoped_members sm
                      join project_member_brand_access pmba on pmba.project_member_id = sm.project_member_id
                      join brand b on b.brand_id = pmba.brand_id
                      where sm.brand_scope_mode = 'assigned_brands'
                    )
                    select brand_code from allowed_brands order by brand_code
                    """
                ),
                {"user_id": user_id},
            ).scalars().all()
            allowed_brand_codes = list(brand_rows)
            permissions = permission_rows

        if not allowed_brand_codes and not user_row["is_super_admin"]:
            raise HTTPException(status_code=403, detail="当前账号未配置任何品牌访问范围")

        preferred_brand_code = requested_brand_code or DEFAULT_BRAND_CODE
        if preferred_brand_code not in allowed_brand_codes:
            preferred_brand_code = allowed_brand_codes[0] if allowed_brand_codes else None

        return DemoAuthContext(
            user_id=str(user_row["user_id"]),
            tenant_id=tenant_id,
            tenant_name=user_row["tenant_name"],
            login_name=user_row["login_name"],
            display_name=user_row["display_name"],
            roles=list(role_rows),
            permissions=list(permissions),
            is_super_admin=bool(user_row["is_super_admin"]),
            allowed_brand_codes=allowed_brand_codes,
            preferred_brand_code=preferred_brand_code,
        )


def _load_demo_auth_context(role: str, preferred_brand_code: str) -> DemoAuthContext:
    with SessionLocal() as db:
        all_brand_codes = _load_all_brand_codes(db, DEMO_TENANT_ID)
        tenant_name = db.execute(
            text("select tenant_name from tenant where tenant_id = :tenant_id"),
            {"tenant_id": DEMO_TENANT_ID},
        ).scalar_one_or_none() or "演示租户"

    if not all_brand_codes:
        raise HTTPException(status_code=500, detail="演示品牌数据尚未初始化")

    if role == "brand_manager":
        if preferred_brand_code not in all_brand_codes:
            raise HTTPException(status_code=404, detail="指定品牌不存在")
        allowed_brand_codes = [preferred_brand_code]
        display_name = f"品牌管理员（{preferred_brand_code}）"
        permissions = [
            "project.read",
            "brand.read",
            "dataset.read",
            "brand.config.publish",
            "dataset.create",
            "dataset.upload",
            "dataset.map_fields",
            "dataset.map_primary_keys",
            "dataset.publish",
        ]
        roles = ["brand_manager"]
        is_super_admin = False
    elif role == "analyst":
        if preferred_brand_code not in all_brand_codes:
            raise HTTPException(status_code=404, detail="指定品牌不存在")
        allowed_brand_codes = [preferred_brand_code]
        display_name = f"分析师（{preferred_brand_code}）"
        permissions = ["project.read", "brand.read", "dataset.read"]
        roles = ["analyst"]
        is_super_admin = False
    elif role == "tenant_admin":
        allowed_brand_codes = list(all_brand_codes)
        display_name = "租户管理员"
        permissions = [
            "project.read",
            "brand.read",
            "dataset.read",
            "brand.config.publish",
            "dataset.create",
            "dataset.upload",
            "dataset.map_fields",
            "dataset.map_primary_keys",
            "dataset.publish",
        ]
        roles = ["tenant_admin"]
        is_super_admin = False
    else:
        allowed_brand_codes = list(all_brand_codes)
        display_name = "超级管理员"
        permissions = [
            "project.read",
            "brand.read",
            "dataset.read",
            "brand.config.publish",
            "dataset.create",
            "dataset.upload",
            "dataset.map_fields",
            "dataset.map_primary_keys",
            "dataset.publish",
        ]
        roles = ["super_admin"]
        is_super_admin = True

    resolved_preferred_brand_code = (
        preferred_brand_code if preferred_brand_code in allowed_brand_codes else allowed_brand_codes[0]
    )

    return DemoAuthContext(
        user_id=DEMO_USER_ID,
        tenant_id=DEMO_TENANT_ID,
        tenant_name=tenant_name,
        login_name=f"demo.{role}@local",
        display_name=display_name,
        roles=roles,
        permissions=permissions,
        is_super_admin=is_super_admin,
        allowed_brand_codes=allowed_brand_codes,
        preferred_brand_code=resolved_preferred_brand_code,
    )


def get_demo_auth_context(
    authorization: str | None = Header(default=None),
    x_active_brand_code: str | None = Header(default=None),
    x_demo_user_role: str | None = Header(default=None),
    x_demo_brand_code: str | None = Header(default=None),
) -> DemoAuthContext:
    requested_brand_code = (x_active_brand_code or x_demo_brand_code or DEFAULT_BRAND_CODE).strip().lower()

    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        payload = decode_access_token(token)
        return load_real_auth_context(
            user_id=payload.user_id,
            login_name=payload.login_name,
            requested_brand_code=requested_brand_code,
        )

    if not x_demo_user_role:
        raise HTTPException(status_code=401, detail="未登录或登录已过期")

    role = x_demo_user_role.strip().lower()
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的演示角色: {role}，可用角色为 {', '.join(sorted(VALID_ROLES))}",
        )
    return _load_demo_auth_context(role, requested_brand_code)


def ensure_permission(context: DemoAuthContext, permission_code: str) -> None:
    if context.is_super_admin:
        return
    if permission_code not in context.permissions:
        raise HTTPException(status_code=403, detail=f"当前账号缺少权限: {permission_code}")


def ensure_brand_allowed(context: DemoAuthContext, brand_code: str) -> None:
    if context.is_super_admin:
        return
    if brand_code not in context.allowed_brand_codes:
        raise HTTPException(status_code=403, detail="当前账号无权访问该品牌")
