from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy import text

from ..db import SessionLocal
from ..deps import DemoAuthContext, ensure_brand_allowed, ensure_permission, get_demo_auth_context
from ..import_workflow import next_brand_config_version_no
from ..schemas import (
    BrandConfigVersionItem,
    BrandConfigVersionListResponse,
    BrandItem,
    BrandListResponse,
    BrandPublishResponse,
    VersionBundleItem,
    VersionBundleListResponse,
)

router = APIRouter(tags=["brands-config"])


@router.get("/brands", response_model=BrandListResponse)
def list_brands(context: DemoAuthContext = Depends(get_demo_auth_context)) -> BrandListResponse:
    ensure_permission(context, "brand.read")
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select brand_id, brand_code, brand_name, status
                from brand
                order by brand_code
                """
            )
        ).mappings().all()
        items = [
            BrandItem(
                id=str(row["brand_id"]),
                code=row["brand_code"],
                name=row["brand_name"],
                status=row["status"],
            )
            for row in rows
            if context.is_super_admin or row["brand_code"] in context.allowed_brand_codes
        ]
    return BrandListResponse(items=items)


@router.get("/brands/{brand_id}/config-versions", response_model=BrandConfigVersionListResponse)
def list_brand_config_versions(
    brand_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> BrandConfigVersionListResponse:
    ensure_permission(context, "brand.read")
    with SessionLocal() as db:
        brand_row = db.execute(
            text(
                """
                select brand_code
                from brand
                where brand_id = :brand_id
                """
            ),
            {"brand_id": brand_id},
        ).mappings().first()
        if brand_row is None:
            raise HTTPException(status_code=404, detail="品牌不存在")

        ensure_brand_allowed(context, brand_row["brand_code"])

        rows = db.execute(
            text(
                """
                select
                  brand_config_version_id,
                  brand_id,
                  version_no,
                  status,
                  published_at
                from brand_config_version
                where brand_id = :brand_id
                order by created_at desc
                """
            ),
            {"brand_id": brand_id},
        ).mappings().all()
        items = [
            BrandConfigVersionItem(
                id=str(row["brand_config_version_id"]),
                brandId=str(row["brand_id"]),
                versionNo=row["version_no"],
                status=row["status"],
                publishedAt=row["published_at"].isoformat() if row["published_at"] else None,
            )
            for row in rows
        ]
    return BrandConfigVersionListResponse(items=items)


@router.post("/brands/{brand_id}/config-versions/minimal-publish", response_model=BrandPublishResponse)
def publish_brand_config_minimal(
    brand_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> BrandPublishResponse:
    ensure_permission(context, "brand.config.publish")

    with SessionLocal.begin() as db:
        brand_row = db.execute(
            text(
                """
                select brand_id, brand_code
                from brand
                where brand_id = :brand_id
                """
            ),
            {"brand_id": brand_id},
        ).mappings().first()
        if brand_row is None:
            raise HTTPException(status_code=404, detail="品牌不存在")

        ensure_brand_allowed(context, brand_row["brand_code"])

        latest_version = db.execute(
            text(
                """
                select brand_config_version_id, version_no
                from brand_config_version
                where brand_id = :brand_id
                order by created_at desc
                limit 1
                """
            ),
            {"brand_id": brand_id},
        ).mappings().first()

        next_version_no = next_brand_config_version_no(latest_version["version_no"] if latest_version else None)
        new_brand_config_version_id = str(uuid4())
        published_at = datetime.now(timezone.utc)

        db.execute(
            text(
                """
                insert into brand_config_version (
                  brand_config_version_id,
                  brand_id,
                  version_no,
                  status,
                  base_version_id,
                  created_by,
                  published_at
                )
                values (
                  :brand_config_version_id,
                  :brand_id,
                  :version_no,
                  'published',
                  :base_version_id,
                  :created_by,
                  :published_at
                )
                """
            ),
            {
                "brand_config_version_id": new_brand_config_version_id,
                "brand_id": brand_id,
                "version_no": next_version_no,
                "base_version_id": latest_version["brand_config_version_id"] if latest_version else None,
                "created_by": context.user_id,
                "published_at": published_at,
            },
        )

        binding_rows = db.execute(
            text(
                """
                select
                  pbb.project_id,
                  pbb.project_brand_binding_id,
                  pbb.default_version_bundle_id,
                  vb.metric_catalog_version_id,
                  vb.questionnaire_template_version_id
                from project_brand_binding pbb
                join version_bundle vb on vb.version_bundle_id = pbb.default_version_bundle_id
                where pbb.brand_id = :brand_id
                """
            ),
            {"brand_id": brand_id},
        ).mappings().all()

        new_version_bundle_ids: list[str] = []
        for binding_row in binding_rows:
            new_version_bundle_id = str(uuid4())
            db.execute(
                text("update version_bundle set is_active = false where project_id = :project_id and brand_id = :brand_id"),
                {"project_id": binding_row["project_id"], "brand_id": brand_id},
            )
            db.execute(
                text(
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
                    values (
                      :version_bundle_id,
                      :project_id,
                      :brand_id,
                      :brand_config_version_id,
                      :metric_catalog_version_id,
                      :questionnaire_template_version_id,
                      true
                    )
                    """
                ),
                {
                    "version_bundle_id": new_version_bundle_id,
                    "project_id": binding_row["project_id"],
                    "brand_id": brand_id,
                    "brand_config_version_id": new_brand_config_version_id,
                    "metric_catalog_version_id": binding_row["metric_catalog_version_id"],
                    "questionnaire_template_version_id": binding_row["questionnaire_template_version_id"],
                },
            )
            db.execute(
                text(
                    """
                    update project_brand_binding
                    set default_version_bundle_id = :default_version_bundle_id
                    where project_brand_binding_id = :project_brand_binding_id
                    """
                ),
                {
                    "default_version_bundle_id": new_version_bundle_id,
                    "project_brand_binding_id": binding_row["project_brand_binding_id"],
                },
            )
            new_version_bundle_ids.append(new_version_bundle_id)

    return BrandPublishResponse(
        brandId=brand_id,
        brandCode=brand_row["brand_code"],
        brandConfigVersionId=new_brand_config_version_id,
        versionNo=next_version_no,
        status="published",
        affectedProjectCount=len(new_version_bundle_ids),
        affectedVersionBundleIds=new_version_bundle_ids,
    )


@router.get("/projects/{project_id}/version-bundles", response_model=VersionBundleListResponse)
def list_project_version_bundles(
    project_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> VersionBundleListResponse:
    ensure_permission(context, "project.read")
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  vb.version_bundle_id,
                  vb.project_id,
                  b.brand_code,
                  vb.brand_config_version_id,
                  vb.metric_catalog_version_id,
                  vb.questionnaire_template_version_id,
                  vb.is_active
                from version_bundle vb
                join brand b on b.brand_id = vb.brand_id
                where vb.project_id = :project_id
                order by vb.created_at
                """
            ),
            {"project_id": project_id},
        ).mappings().all()
        items = [
            VersionBundleItem(
                id=str(row["version_bundle_id"]),
                projectId=str(row["project_id"]),
                brandId=row["brand_code"],
                brandConfigVersionId=str(row["brand_config_version_id"]),
                metricCatalogVersionId=str(row["metric_catalog_version_id"]),
                questionnaireTemplateVersionId=str(row["questionnaire_template_version_id"]),
                isActive=bool(row["is_active"]),
            )
            for row in rows
            if context.is_super_admin or row["brand_code"] in context.allowed_brand_codes
        ]
    return VersionBundleListResponse(items=items)
