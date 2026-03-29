from sqlalchemy import Connection, create_engine, text
from sqlalchemy.orm import sessionmaker

from .config import get_settings
from .security import hash_password


def _normalize_database_url(raw: str) -> str:
    if raw.startswith("postgresql://"):
        return raw.replace("postgresql://", "postgresql+psycopg://", 1)
    return raw


settings = get_settings()
engine = create_engine(_normalize_database_url(settings.database_url), future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

DEMO_TENANT_ID = "11111111-1111-1111-1111-111111111111"
DEMO_PROJECT_ID = "33333333-3333-3333-3333-333333333333"
DEFAULT_PASSWORD = "CidWeb#2026"
BRAND_IDS = {
    "brand-bdf": "44444444-4444-4444-4444-444444444444",
    "brand-estee": "55555555-5555-5555-5555-555555555555",
    "brand-jiaoyunshi": "55555555-5555-5555-5555-555555555556",
    "brand-wanmei": "55555555-5555-5555-5555-555555555557",
    "brand-ximuyuan": "55555555-5555-5555-5555-555555555558",
    "brand-yunnanbaiyao": "55555555-5555-5555-5555-555555555559",
    "brand-lafang": "55555555-5555-5555-5555-555555555560",
    "brand-hangao": "55555555-5555-5555-5555-555555555561",
    "brand-huanya": "55555555-5555-5555-5555-555555555562",
}
ROLE_DEFINITIONS = {
    "super_admin": {"id": "90000000-0000-0000-0000-000000000001", "scope": "platform"},
    "tenant_admin": {"id": "90000000-0000-0000-0000-000000000002", "scope": "tenant"},
    "brand_manager": {"id": "90000000-0000-0000-0000-000000000003", "scope": "project"},
    "analyst": {"id": "90000000-0000-0000-0000-000000000004", "scope": "project"},
}
PERMISSION_DEFINITIONS = {
    "project.read": {"id": "91000000-0000-0000-0000-000000000001", "name": "Read project data"},
    "brand.read": {"id": "91000000-0000-0000-0000-000000000002", "name": "Read brand config"},
    "dataset.read": {"id": "91000000-0000-0000-0000-000000000003", "name": "Read dataset assets"},
    "brand.config.publish": {"id": "91000000-0000-0000-0000-000000000004", "name": "Publish brand config"},
    "dataset.create": {"id": "91000000-0000-0000-0000-000000000005", "name": "Create dataset"},
    "dataset.upload": {"id": "91000000-0000-0000-0000-000000000006", "name": "Upload source files"},
    "dataset.map_fields": {"id": "91000000-0000-0000-0000-000000000007", "name": "Save field mappings"},
    "dataset.map_primary_keys": {"id": "91000000-0000-0000-0000-000000000008", "name": "Run primary key mapping"},
    "dataset.publish": {"id": "91000000-0000-0000-0000-000000000009", "name": "Publish dataset versions"},
}
ROLE_PERMISSIONS = {
    "super_admin": list(PERMISSION_DEFINITIONS.keys()),
    "tenant_admin": list(PERMISSION_DEFINITIONS.keys()),
    "brand_manager": list(PERMISSION_DEFINITIONS.keys()),
    "analyst": ["project.read", "brand.read", "dataset.read"],
}
SEEDED_USERS = [
    {
        "user_id": "22222222-2222-2222-2222-222222222222",
        "email": "superadmin@cid.local",
        "display_name": "平台超级管理员",
        "is_super_admin": True,
        "roles": [("super_admin", "all_bound_brands", [])],
    },
    {
        "user_id": "22222222-2222-2222-2222-222222222223",
        "email": "tenantadmin@demo.local",
        "display_name": "租户管理员",
        "is_super_admin": False,
        "roles": [("tenant_admin", "all_bound_brands", [])],
    },
    {
        "user_id": "22222222-2222-2222-2222-222222222224",
        "email": "analyst.multi@demo.local",
        "display_name": "多品牌分析师",
        "is_super_admin": False,
        "roles": [("analyst", "assigned_brands", ["brand-bdf", "brand-estee"])],
    },
]
for index, brand_code in enumerate(BRAND_IDS.keys(), start=1):
    SEEDED_USERS.append(
        {
            "user_id": f"22222222-2222-2222-2222-{300 + index:012d}",
            "email": f"manager.{brand_code}@demo.local",
            "display_name": f"{brand_code} 品牌管理员",
            "is_super_admin": False,
            "roles": [("brand_manager", "assigned_brands", [brand_code])],
        }
    )


def check_database() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
        return True
    except Exception:
        return False


def _seed_identity_access(conn: Connection) -> None:
    conn.execute(
        text(
            """
            create table if not exists user_login_credential (
              credential_id uuid primary key default gen_random_uuid(),
              user_id uuid not null unique references organization_user(user_id) on delete cascade,
              login_name varchar(255) not null unique,
              password_hash text not null,
              is_enabled boolean not null default true,
              created_at timestamptz not null default now(),
              updated_at timestamptz not null default now()
            )
            """
        )
    )
    conn.execute(
        text(
            """
            create table if not exists project_member_brand_access (
              project_member_brand_access_id uuid primary key default gen_random_uuid(),
              project_member_id uuid not null references project_member(project_member_id) on delete cascade,
              brand_id uuid not null references brand(brand_id) on delete cascade,
              created_at timestamptz not null default now(),
              unique(project_member_id, brand_id)
            )
            """
        )
    )

    for role_name, role_meta in ROLE_DEFINITIONS.items():
        conn.execute(
            text(
                """
                insert into role (role_id, tenant_id, role_name, role_scope)
                values (:role_id, :tenant_id, :role_name, :role_scope)
                on conflict (role_id) do update
                set tenant_id = excluded.tenant_id,
                    role_name = excluded.role_name,
                    role_scope = excluded.role_scope
                """
            ),
            {
                "role_id": role_meta["id"],
                "tenant_id": DEMO_TENANT_ID,
                "role_name": role_name,
                "role_scope": role_meta["scope"],
            },
        )

    for permission_code, permission_meta in PERMISSION_DEFINITIONS.items():
        conn.execute(
            text(
                """
                insert into permission (permission_id, permission_code, permission_name)
                values (:permission_id, :permission_code, :permission_name)
                on conflict (permission_code) do update
                set permission_name = excluded.permission_name
                """
            ),
            {
                "permission_id": permission_meta["id"],
                "permission_code": permission_code,
                "permission_name": permission_meta["name"],
            },
        )

    for role_name, permission_codes in ROLE_PERMISSIONS.items():
        role_id = ROLE_DEFINITIONS[role_name]["id"]
        for permission_code in permission_codes:
            conn.execute(
                text(
                    """
                    insert into role_permission (role_permission_id, role_id, permission_id)
                    values (gen_random_uuid(), :role_id, :permission_id)
                    on conflict (role_id, permission_id) do nothing
                    """
                ),
                {
                    "role_id": role_id,
                    "permission_id": PERMISSION_DEFINITIONS[permission_code]["id"],
                },
            )

    password_hash = hash_password(DEFAULT_PASSWORD)
    for user in SEEDED_USERS:
        conn.execute(
            text(
                """
                insert into organization_user (user_id, tenant_id, email, display_name, status, is_super_admin)
                values (:user_id, :tenant_id, :email, :display_name, 'active', :is_super_admin)
                on conflict (user_id) do update
                set tenant_id = excluded.tenant_id,
                    email = excluded.email,
                    display_name = excluded.display_name,
                    status = 'active',
                    is_super_admin = excluded.is_super_admin
                """
            ),
            {
                "user_id": user["user_id"],
                "tenant_id": DEMO_TENANT_ID,
                "email": user["email"],
                "display_name": user["display_name"],
                "is_super_admin": user["is_super_admin"],
            },
        )
        conn.execute(
            text(
                """
                insert into user_login_credential (credential_id, user_id, login_name, password_hash, is_enabled)
                values (gen_random_uuid(), :user_id, :login_name, :password_hash, true)
                on conflict (login_name) do update
                set user_id = excluded.user_id,
                    password_hash = excluded.password_hash,
                    is_enabled = true,
                    updated_at = now()
                """
            ),
            {
                "user_id": user["user_id"],
                "login_name": user["email"],
                "password_hash": password_hash,
            },
        )

        for role_index, (role_name, brand_scope_mode, brand_codes) in enumerate(user["roles"], start=1):
            project_member_id = conn.execute(
                text(
                    """
                    select project_member_id
                    from project_member
                    where project_id = :project_id
                      and user_id = :user_id
                      and role_id = :role_id
                    """
                ),
                {
                    "project_id": DEMO_PROJECT_ID,
                    "user_id": user["user_id"],
                    "role_id": ROLE_DEFINITIONS[role_name]["id"],
                },
            ).scalar_one_or_none()
            if project_member_id is None:
                project_member_id = conn.execute(
                    text(
                        """
                        insert into project_member (project_member_id, project_id, user_id, role_id, brand_scope_mode)
                        values (gen_random_uuid(), :project_id, :user_id, :role_id, :brand_scope_mode)
                        returning project_member_id
                        """
                    ),
                    {
                        "project_id": DEMO_PROJECT_ID,
                        "user_id": user["user_id"],
                        "role_id": ROLE_DEFINITIONS[role_name]["id"],
                        "brand_scope_mode": brand_scope_mode,
                    },
                ).scalar_one()
            else:
                conn.execute(
                    text(
                        """
                        update project_member
                        set brand_scope_mode = :brand_scope_mode
                        where project_member_id = :project_member_id
                        """
                    ),
                    {
                        "project_member_id": project_member_id,
                        "brand_scope_mode": brand_scope_mode,
                    },
                )

            conn.execute(
                text("delete from project_member_brand_access where project_member_id = :project_member_id"),
                {"project_member_id": project_member_id},
            )

            for brand_code in brand_codes:
                conn.execute(
                    text(
                        """
                        insert into project_member_brand_access (project_member_brand_access_id, project_member_id, brand_id)
                        values (gen_random_uuid(), :project_member_id, :brand_id)
                        on conflict (project_member_id, brand_id) do nothing
                        """
                    ),
                    {
                        "project_member_id": project_member_id,
                        "brand_id": BRAND_IDS[brand_code],
                    },
                )


def init_demo_seed() -> None:
    statements = [
        """
        create table if not exists brand_metric_mapping (
          brand_metric_mapping_id uuid primary key default gen_random_uuid(),
          brand_id uuid not null references brand(brand_id) on delete cascade,
          metric_catalog_version_id uuid not null references metric_catalog_version(metric_catalog_version_id) on delete cascade,
          raw_field_name varchar(255) not null,
          instrument_family varchar(128),
          body_site varchar(64),
          source_sheet varchar(128),
          created_at timestamptz not null default now(),
          unique(brand_id, metric_catalog_version_id, raw_field_name)
        )
        """,
        """
        insert into tenant (tenant_id, tenant_code, tenant_name, status, data_isolation_mode)
        values (
          '11111111-1111-1111-1111-111111111111',
          'demo-tenant-001',
          '演示租户',
          'active',
          'shared_control_plane'
        )
        on conflict (tenant_code) do nothing
        """,
        """
        insert into organization_user (user_id, tenant_id, email, display_name, status, is_super_admin)
        values (
          '22222222-2222-2222-2222-222222222222',
          '11111111-1111-1111-1111-111111111111',
          'analyst@demo.local',
          '演示分析师',
          'active',
          false
        )
        on conflict do nothing
        """,
        """
        insert into project (project_id, tenant_id, project_code, project_name, project_type, import_mode_default, status, created_by)
        values (
          '33333333-3333-3333-3333-333333333333',
          '11111111-1111-1111-1111-111111111111',
          'proj-demo-001',
          '多品牌演示项目',
          'demo',
          'batch',
          'active',
          '22222222-2222-2222-2222-222222222222'
        )
        on conflict (tenant_id, project_code) do nothing
        """,
        """
        insert into brand (brand_id, tenant_id, brand_code, brand_name, status)
        values
          (
            '44444444-4444-4444-4444-444444444444',
            '11111111-1111-1111-1111-111111111111',
            'brand-bdf',
            'BDF',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555555',
            '11111111-1111-1111-1111-111111111111',
            'brand-estee',
            '雅诗兰黛',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555556',
            '11111111-1111-1111-1111-111111111111',
            'brand-jiaoyunshi',
            '娇韵诗',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555557',
            '11111111-1111-1111-1111-111111111111',
            'brand-wanmei',
            '丸美',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555558',
            '11111111-1111-1111-1111-111111111111',
            'brand-ximuyuan',
            '溪木源',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555559',
            '11111111-1111-1111-1111-111111111111',
            'brand-yunnanbaiyao',
            '云南白药',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555560',
            '11111111-1111-1111-1111-111111111111',
            'brand-lafang',
            '拉芳',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555561',
            '11111111-1111-1111-1111-111111111111',
            'brand-hangao',
            '汉高',
            'active'
          ),
          (
            '55555555-5555-5555-5555-555555555562',
            '11111111-1111-1111-1111-111111111111',
            'brand-huanya',
            '环亚',
            'active'
          )
        on conflict (tenant_id, brand_code) do nothing
        """,
        """
        insert into brand_config_version (brand_config_version_id, brand_id, version_no, status, created_by)
        values
          (
            '66666666-6666-6666-6666-666666666661',
            '44444444-4444-4444-4444-444444444444',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666662',
            '55555555-5555-5555-5555-555555555555',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666663',
            '55555555-5555-5555-5555-555555555556',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666664',
            '55555555-5555-5555-5555-555555555557',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666665',
            '55555555-5555-5555-5555-555555555558',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666666',
            '55555555-5555-5555-5555-555555555559',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666667',
            '55555555-5555-5555-5555-555555555560',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666668',
            '55555555-5555-5555-5555-555555555561',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          ),
          (
            '66666666-6666-6666-6666-666666666669',
            '55555555-5555-5555-5555-555555555562',
            '1.0.0',
            'published',
            '22222222-2222-2222-2222-222222222222'
          )
        on conflict (brand_id, version_no) do nothing
        """,
        """
        insert into metric_catalog (metric_catalog_id, catalog_name, catalog_scope)
        values (
          '77777777-7777-7777-7777-777777777777',
          '默认指标目录',
          'platform'
        )
        on conflict do nothing
        """,
        """
        insert into metric_catalog_version (metric_catalog_version_id, metric_catalog_id, version_no, status)
        values (
          '88888888-8888-8888-8888-888888888888',
          '77777777-7777-7777-7777-777777777777',
          '1.0.0',
          'published'
        )
        on conflict (metric_catalog_id, version_no) do nothing
        """,
        """
        insert into questionnaire_template (questionnaire_template_id, template_name, template_scope)
        values (
          '99999999-9999-9999-9999-999999999999',
          '默认问卷模板',
          'brand'
        )
        on conflict do nothing
        """,
        """
        insert into questionnaire_template_version (questionnaire_template_version_id, questionnaire_template_id, version_no, status)
        values (
          'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
          '99999999-9999-9999-9999-999999999999',
          '1.0.0',
          'published'
        )
        on conflict (questionnaire_template_id, version_no) do nothing
        """,
        """
        insert into version_bundle (
          version_bundle_id,
          project_id,
          brand_id,
          brand_config_version_id,
          metric_catalog_version_id,
          questionnaire_template_version_id,
          is_active
        )
        values
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1',
            '33333333-3333-3333-3333-333333333333',
            '44444444-4444-4444-4444-444444444444',
            '66666666-6666-6666-6666-666666666661',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555555',
            '66666666-6666-6666-6666-666666666662',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555556',
            '66666666-6666-6666-6666-666666666663',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555557',
            '66666666-6666-6666-6666-666666666664',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb5',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555558',
            '66666666-6666-6666-6666-666666666665',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb6',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555559',
            '66666666-6666-6666-6666-666666666666',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb7',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555560',
            '66666666-6666-6666-6666-666666666667',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb8',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555561',
            '66666666-6666-6666-6666-666666666668',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          ),
          (
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb9',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555562',
            '66666666-6666-6666-6666-666666666669',
            '88888888-8888-8888-8888-888888888888',
            'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
            true
          )
        on conflict do nothing
        """,
        """
        insert into project_brand_binding (project_brand_binding_id, project_id, brand_id, default_version_bundle_id, status)
        values
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc1',
            '33333333-3333-3333-3333-333333333333',
            '44444444-4444-4444-4444-444444444444',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc2',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555555',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb2',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc3',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555556',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb3',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc4',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555557',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc5',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555558',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb5',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc6',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555559',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb6',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc7',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555560',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb7',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc8',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555561',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb8',
            'active'
          ),
          (
            'cccccccc-cccc-cccc-cccc-ccccccccccc9',
            '33333333-3333-3333-3333-333333333333',
            '55555555-5555-5555-5555-555555555562',
            'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb9',
            'active'
          )
        on conflict (project_id, brand_id) do nothing
        """,
        """
        insert into dataset (dataset_id, project_id, brand_id, dataset_name, dataset_type, status)
        values (
          'dddddddd-dddd-dddd-dddd-dddddddddddd',
          '33333333-3333-3333-3333-333333333333',
          '44444444-4444-4444-4444-444444444444',
          'BDF 演示数据集',
          'instrument',
          'active'
        )
        on conflict do nothing
        """,
    ]

    with engine.begin() as conn:
        for statement in statements:
            conn.execute(text(statement))
        _seed_identity_access(conn)
