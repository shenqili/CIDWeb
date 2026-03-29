from datetime import datetime, timezone
from pathlib import Path as FilePath
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from sqlalchemy import text

from ..config import get_settings
from ..db import SessionLocal
from ..deps import DemoAuthContext, ensure_brand_allowed, ensure_permission, get_demo_auth_context
from ..import_workflow import (
    build_manifest,
    compute_rows_hash,
    load_manifest,
    next_dataset_version_no,
    save_manifest,
)
from ..schemas import (
    CreateDatasetRequest,
    DatasetItem,
    DatasetListResponse,
    DatasetVersionItem,
    DatasetVersionListResponse,
    DatasetVersionPublishResponse,
    FieldMappingRequest,
    ImportBatchColumn,
    ImportBatchDetailResponse,
    ImportBatchItem,
    ImportBatchListResponse,
    PrimaryKeyMappingRequest,
    PrimaryKeyMappingResponse,
    ProjectPortfolioBrandSummaryItem,
    ProjectPortfolioSummaryResponse,
    ProjectBrandBindingItem,
    ProjectBrandBindingListResponse,
    ProjectItem,
    ProjectListResponse,
    UploadBatchResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])
settings = get_settings()


def _filtered_brand_codes(context: DemoAuthContext, brand_codes: list[str]) -> list[str]:
    if context.is_super_admin:
        return list(brand_codes)
    return [brand_code for brand_code in brand_codes if brand_code in context.allowed_brand_codes]


def _load_import_batch_row(import_batch_id: str) -> dict:
    with SessionLocal() as db:
        row = db.execute(
            text(
                """
                select
                  ib.import_batch_id,
                  ib.dataset_id,
                  b.brand_code,
                  ib.version_bundle_id,
                  ib.source_file_name,
                  ib.status,
                  ib.created_at
                from import_batch ib
                join brand b on b.brand_id = ib.brand_id
                where ib.import_batch_id = :import_batch_id
                """
            ),
            {"import_batch_id": import_batch_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="导入批次不存在")
    return dict(row)


def _load_dataset_row(dataset_id: str) -> dict:
    with SessionLocal() as db:
        row = db.execute(
            text(
                """
                select
                  d.dataset_id,
                  d.project_id,
                  b.brand_code,
                  d.brand_id
                from dataset d
                join brand b on b.brand_id = d.brand_id
                where d.dataset_id = :dataset_id
                """
            ),
            {"dataset_id": dataset_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
    return dict(row)


def _build_import_batch_detail(row: dict, manifest: dict) -> ImportBatchDetailResponse:
    published_version_id = manifest.get("publishedDatasetVersionId")
    published_version_no = manifest.get("publishedVersionNo")
    return ImportBatchDetailResponse(
        importBatchId=str(row["import_batch_id"]),
        datasetId=str(row["dataset_id"]),
        brandId=row["brand_code"],
        sourceFileName=row["source_file_name"],
        status=row["status"],
        rowCount=int(manifest.get("rowCount", 0)),
        columnCount=int(manifest.get("columnCount", 0)),
        columns=[
            ImportBatchColumn(
                sourceName=column,
                sampleValue=manifest["rows"][0].get(column) if manifest.get("rows") else None,
            )
            for column in manifest.get("detectedColumns", [])
        ],
        fieldMappings=manifest.get("fieldMappings", []),
        primaryKeyColumn=manifest.get("primaryKeyColumn"),
        identifierType=manifest.get("identifierType"),
        createdSubjectCount=int(manifest.get("createdSubjectCount", 0)),
        reusedSubjectCount=int(manifest.get("reusedSubjectCount", 0)),
        missingPrimaryKeyRows=list(manifest.get("missingPrimaryKeyRows", [])),
        publishedDatasetVersionId=published_version_id,
        publishedVersionNo=published_version_no,
    )


@router.get("", response_model=ProjectListResponse)
def list_projects(context: DemoAuthContext = Depends(get_demo_auth_context)) -> ProjectListResponse:
    ensure_permission(context, "project.read")
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  p.project_id,
                  p.tenant_id,
                  p.project_name,
                  p.status,
                  p.import_mode_default
                from project p
                order by p.created_at desc
                """
            )
        ).mappings().all()
        items = []
        for row in rows:
            brand_rows = db.execute(
                text(
                    """
                    select b.brand_code
                    from project_brand_binding pbb
                    join brand b on b.brand_id = pbb.brand_id
                    where pbb.project_id = :project_id
                    order by b.brand_code
                    """
                ),
                {"project_id": row["project_id"]},
            ).scalars().all()
            visible_brand_codes = _filtered_brand_codes(context, list(brand_rows))
            if not visible_brand_codes:
                continue
            items.append(
                ProjectItem(
                    id=str(row["project_id"]),
                    tenantId=str(row["tenant_id"]),
                    name=row["project_name"],
                    status=row["status"],
                    allowedBrandIds=visible_brand_codes,
                    defaultImportMode=row["import_mode_default"],
                    highSensitivityExportPolicy="approval_required",
                )
            )
    return ProjectListResponse(items=items)


@router.get("/{project_id}/brand-bindings", response_model=ProjectBrandBindingListResponse)
def get_project_brand_bindings(
    project_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> ProjectBrandBindingListResponse:
    ensure_permission(context, "project.read")
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  b.brand_code,
                  pbb.default_version_bundle_id,
                  pbb.status
                from project_brand_binding pbb
                join brand b on b.brand_id = pbb.brand_id
                where pbb.project_id = :project_id
                order by b.brand_code
                """
            ),
            {"project_id": project_id},
        ).mappings().all()
        items = [
            ProjectBrandBindingItem(
                brandId=row["brand_code"],
                defaultVersionBundleId=str(row["default_version_bundle_id"]),
                status=row["status"],
            )
            for row in rows
            if context.is_super_admin or row["brand_code"] in context.allowed_brand_codes
        ]
    return ProjectBrandBindingListResponse(items=items)


@router.get("/{project_id}/portfolio-summary", response_model=ProjectPortfolioSummaryResponse)
def get_project_portfolio_summary(
    project_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> ProjectPortfolioSummaryResponse:
    ensure_permission(context, "project.read")
    with SessionLocal() as db:
        db.execute(
            text(
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
                """
            )
        )
        rows = db.execute(
            text(
                """
                with metric_counts as (
                  select brand_id, count(distinct raw_field_name) as metric_count
                  from brand_metric_mapping
                  group by brand_id
                ),
                dataset_counts as (
                  select
                    d.brand_id,
                    count(distinct d.dataset_id) as dataset_count,
                    count(distinct dv.dataset_version_id) as dataset_version_count,
                    coalesce(max(dv.row_count), 0) as max_row_count,
                    coalesce(max(dv.column_count), 0) as max_column_count
                  from dataset d
                  left join dataset_version dv on dv.dataset_id = d.dataset_id
                  where d.project_id = :project_id
                  group by d.brand_id
                )
                select
                  b.brand_id,
                  b.brand_code,
                  b.brand_name,
                  coalesce(mc.metric_count, 0) as metric_count,
                  coalesce(dc.dataset_count, 0) as dataset_count,
                  coalesce(dc.dataset_version_count, 0) as dataset_version_count,
                  coalesce(dc.max_row_count, 0) as max_row_count,
                  coalesce(dc.max_column_count, 0) as max_column_count
                from project_brand_binding pbb
                join brand b on b.brand_id = pbb.brand_id
                left join metric_counts mc on mc.brand_id = b.brand_id
                left join dataset_counts dc on dc.brand_id = b.brand_id
                where pbb.project_id = :project_id
                order by b.brand_code
                """
            ),
            {"project_id": project_id},
        ).mappings().all()

    items = [
        ProjectPortfolioBrandSummaryItem(
            brandId=str(row["brand_id"]),
            brandCode=row["brand_code"],
            brandName=row["brand_name"],
            metricCount=int(row["metric_count"]),
            datasetCount=int(row["dataset_count"]),
            datasetVersionCount=int(row["dataset_version_count"]),
            maxRowCount=int(row["max_row_count"]),
            maxColumnCount=int(row["max_column_count"]),
        )
        for row in rows
        if context.is_super_admin or row["brand_code"] in context.allowed_brand_codes
    ]

    return ProjectPortfolioSummaryResponse(
        projectId=project_id,
        totalBrands=len(items),
        totalMetricMappings=sum(item.metricCount for item in items),
        totalDatasets=sum(item.datasetCount for item in items),
        totalDatasetVersions=sum(item.datasetVersionCount for item in items),
        items=items,
    )


@router.get("/{project_id}/datasets", response_model=DatasetListResponse)
def list_project_datasets(
    project_id: str = Path(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> DatasetListResponse:
    ensure_permission(context, "dataset.read")
    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  d.dataset_id,
                  d.project_id,
                  b.brand_code,
                  d.dataset_name,
                  d.dataset_type,
                  d.status
                from dataset d
                join brand b on b.brand_id = d.brand_id
                where d.project_id = :project_id
                order by d.created_at desc
                """
            ),
            {"project_id": project_id},
        ).mappings().all()
        items = [
            DatasetItem(
                id=str(row["dataset_id"]),
                projectId=str(row["project_id"]),
                brandId=row["brand_code"],
                datasetName=row["dataset_name"],
                datasetType=row["dataset_type"] or "instrument",
                status=row["status"],
            )
            for row in rows
            if context.is_super_admin or row["brand_code"] in context.allowed_brand_codes
        ]
    return DatasetListResponse(items=items)


@router.post("/{project_id}/datasets", response_model=DatasetItem)
def create_project_dataset(
    project_id: str = Path(...),
    payload: CreateDatasetRequest | None = None,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> DatasetItem:
    ensure_permission(context, "dataset.create")
    if payload is None:
        raise HTTPException(status_code=422, detail="缺少数据集创建参数")

    ensure_brand_allowed(context, payload.brandId)

    with SessionLocal.begin() as db:
        brand_row = db.execute(
            text(
                """
                select brand_id, brand_code
                from brand
                where brand_code = :brand_code
                """
            ),
            {"brand_code": payload.brandId},
        ).mappings().first()
        if brand_row is None:
            raise HTTPException(status_code=404, detail="品牌不存在")

        dataset_id = str(uuid4())
        db.execute(
            text(
                """
                insert into dataset (dataset_id, project_id, brand_id, dataset_name, dataset_type, status)
                values (:dataset_id, :project_id, :brand_id, :dataset_name, :dataset_type, 'active')
                """
            ),
            {
                "dataset_id": dataset_id,
                "project_id": project_id,
                "brand_id": str(brand_row["brand_id"]),
                "dataset_name": payload.datasetName,
                "dataset_type": payload.datasetType,
            },
        )

    return DatasetItem(
        id=dataset_id,
        projectId=project_id,
        brandId=payload.brandId,
        datasetName=payload.datasetName,
        datasetType=payload.datasetType,
        status="active",
    )


@router.post("/datasets/{dataset_id}/uploads", response_model=UploadBatchResponse)
async def upload_dataset_file(
    dataset_id: str,
    file: UploadFile = File(...),
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> UploadBatchResponse:
    ensure_permission(context, "dataset.upload")
    dataset_row = _load_dataset_row(dataset_id)
    ensure_brand_allowed(context, dataset_row["brand_code"])

    import_batch_id = str(uuid4())
    target_dir = FilePath(settings.raw_storage_root) / dataset_id
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / file.filename
    content = await file.read()
    target_path.write_bytes(content)

    manifest = build_manifest(
        import_batch_id=import_batch_id,
        dataset_id=dataset_id,
        source_file_name=file.filename,
        file_name=file.filename,
        content=content,
    )
    save_manifest(manifest)

    with SessionLocal.begin() as db:
        row = db.execute(
            text(
                """
                select d.brand_id, pbb.default_version_bundle_id
                from dataset d
                join project_brand_binding pbb
                  on pbb.project_id = d.project_id and pbb.brand_id = d.brand_id
                where d.dataset_id = :dataset_id
                """
            ),
            {"dataset_id": dataset_id},
        ).mappings().first()

        if row is None:
            raise HTTPException(status_code=404, detail="数据集不存在")

        db.execute(
            text(
                """
                insert into import_batch (
                  import_batch_id,
                  dataset_id,
                  brand_id,
                  version_bundle_id,
                  source_file_name,
                  storage_path,
                  import_mode,
                  status,
                  created_by
                )
                values (
                  :import_batch_id,
                  :dataset_id,
                  :brand_id,
                  :version_bundle_id,
                  :source_file_name,
                  :storage_path,
                  'append',
                  'draft',
                  :created_by
                )
                """
            ),
            {
                "import_batch_id": import_batch_id,
                "dataset_id": dataset_id,
                "brand_id": str(row["brand_id"]),
                "version_bundle_id": str(row["default_version_bundle_id"]),
                "source_file_name": file.filename,
                "storage_path": str(target_path),
                "created_by": context.user_id,
            },
        )

    return UploadBatchResponse(
        importBatchId=import_batch_id,
        datasetId=dataset_id,
        sourceFileName=file.filename,
        status="draft",
        rowCount=manifest["rowCount"],
        columnCount=manifest["columnCount"],
    )


@router.get("/datasets/{dataset_id}/import-batches", response_model=ImportBatchListResponse)
def list_import_batches(
    dataset_id: str,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> ImportBatchListResponse:
    ensure_permission(context, "dataset.read")
    dataset_row = _load_dataset_row(dataset_id)
    ensure_brand_allowed(context, dataset_row["brand_code"])

    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  import_batch_id,
                  dataset_id,
                  source_file_name,
                  status,
                  version_bundle_id,
                  created_at
                from import_batch
                where dataset_id = :dataset_id
                order by created_at desc
                """
            ),
            {"dataset_id": dataset_id},
        ).mappings().all()
        items = [
            ImportBatchItem(
                id=str(row["import_batch_id"]),
                datasetId=str(row["dataset_id"]),
                sourceFileName=row["source_file_name"],
                status=row["status"],
                versionBundleId=str(row["version_bundle_id"]),
                createdAt=row["created_at"].isoformat(),
            )
            for row in rows
        ]
    return ImportBatchListResponse(items=items)


@router.get("/import-batches/{import_batch_id}", response_model=ImportBatchDetailResponse)
def get_import_batch_detail(
    import_batch_id: str,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> ImportBatchDetailResponse:
    ensure_permission(context, "dataset.read")
    row = _load_import_batch_row(import_batch_id)
    ensure_brand_allowed(context, row["brand_code"])
    manifest = load_manifest(import_batch_id)
    return _build_import_batch_detail(row, manifest)


@router.post("/import-batches/{import_batch_id}/field-mappings", response_model=ImportBatchDetailResponse)
def save_field_mapping(
    import_batch_id: str,
    payload: FieldMappingRequest,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> ImportBatchDetailResponse:
    ensure_permission(context, "dataset.map_fields")
    row = _load_import_batch_row(import_batch_id)
    ensure_brand_allowed(context, row["brand_code"])
    manifest = load_manifest(import_batch_id)

    valid_columns = set(manifest.get("detectedColumns", []))
    if not payload.mappings:
        raise HTTPException(status_code=422, detail="字段映射不能为空")

    for mapping in payload.mappings:
        if mapping.sourceName not in valid_columns:
            raise HTTPException(status_code=422, detail=f"字段不存在: {mapping.sourceName}")

    manifest["fieldMappings"] = [mapping.model_dump() for mapping in payload.mappings]
    manifest["fieldMappingStatus"] = "completed"
    save_manifest(manifest)

    with SessionLocal.begin() as db:
        db.execute(
            text("update import_batch set status = 'field_mapped' where import_batch_id = :import_batch_id"),
            {"import_batch_id": import_batch_id},
        )

    row["status"] = "field_mapped"
    return _build_import_batch_detail(row, manifest)


@router.post("/import-batches/{import_batch_id}/primary-key-mapping", response_model=PrimaryKeyMappingResponse)
def save_primary_key_mapping(
    import_batch_id: str,
    payload: PrimaryKeyMappingRequest,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> PrimaryKeyMappingResponse:
    ensure_permission(context, "dataset.map_primary_keys")
    row = _load_import_batch_row(import_batch_id)
    ensure_brand_allowed(context, row["brand_code"])
    manifest = load_manifest(import_batch_id)

    if payload.primaryKeyColumn not in manifest.get("detectedColumns", []):
        raise HTTPException(status_code=422, detail=f"主键字段不存在: {payload.primaryKeyColumn}")
    if manifest.get("fieldMappingStatus") != "completed":
        raise HTTPException(status_code=409, detail="请先完成字段映射")

    dataset_row = _load_dataset_row(row["dataset_id"])
    missing_rows: list[int] = []
    created_subject_count = 0
    reused_subject_count = 0

    with SessionLocal.begin() as db:
        for row_index, record in enumerate(manifest.get("rows", []), start=1):
            identifier_value = str(record.get(payload.primaryKeyColumn, "")).strip()
            if not identifier_value:
                missing_rows.append(row_index)
                continue

            existing_identifier = db.execute(
                text(
                    """
                    select subject_id
                    from subject_identifier
                    where project_id = :project_id
                      and identifier_type = :identifier_type
                      and identifier_value = :identifier_value
                    """
                ),
                {
                    "project_id": dataset_row["project_id"],
                    "identifier_type": payload.identifierType,
                    "identifier_value": identifier_value,
                },
            ).scalar_one_or_none()

            if existing_identifier is None:
                subject_id = str(uuid4())
                db.execute(
                    text(
                        """
                        insert into subject (subject_id, project_id, brand_id, subject_status)
                        values (:subject_id, :project_id, :brand_id, 'active')
                        """
                    ),
                    {
                        "subject_id": subject_id,
                        "project_id": dataset_row["project_id"],
                        "brand_id": dataset_row["brand_id"],
                    },
                )
                db.execute(
                    text(
                        """
                        insert into subject_identifier (
                          subject_identifier_id,
                          subject_id,
                          project_id,
                          identifier_type,
                          identifier_value,
                          is_primary,
                          source,
                          created_by
                        )
                        values (
                          :subject_identifier_id,
                          :subject_id,
                          :project_id,
                          :identifier_type,
                          :identifier_value,
                          true,
                          'import_batch',
                          :created_by
                        )
                        """
                    ),
                    {
                        "subject_identifier_id": str(uuid4()),
                        "subject_id": subject_id,
                        "project_id": dataset_row["project_id"],
                        "identifier_type": payload.identifierType,
                        "identifier_value": identifier_value,
                        "created_by": context.user_id,
                    },
                )
                created_subject_count += 1
            else:
                reused_subject_count += 1

        if missing_rows:
            raise HTTPException(status_code=422, detail=f"主键列存在空值行: {missing_rows}")

        db.execute(
            text("update import_batch set status = 'key_mapped' where import_batch_id = :import_batch_id"),
            {"import_batch_id": import_batch_id},
        )

    manifest["primaryKeyColumn"] = payload.primaryKeyColumn
    manifest["identifierType"] = payload.identifierType
    manifest["primaryKeyMappingStatus"] = "completed"
    manifest["createdSubjectCount"] = created_subject_count
    manifest["reusedSubjectCount"] = reused_subject_count
    manifest["missingPrimaryKeyRows"] = missing_rows
    save_manifest(manifest)

    return PrimaryKeyMappingResponse(
        importBatchId=import_batch_id,
        status="key_mapped",
        createdSubjectCount=created_subject_count,
        reusedSubjectCount=reused_subject_count,
        missingPrimaryKeyRows=missing_rows,
    )


@router.post("/import-batches/{import_batch_id}/publish-version", response_model=DatasetVersionPublishResponse)
def publish_dataset_version(
    import_batch_id: str,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> DatasetVersionPublishResponse:
    ensure_permission(context, "dataset.publish")
    row = _load_import_batch_row(import_batch_id)
    ensure_brand_allowed(context, row["brand_code"])
    manifest = load_manifest(import_batch_id)

    if manifest.get("primaryKeyMappingStatus") != "completed":
        raise HTTPException(status_code=409, detail="请先完成主键映射")

    with SessionLocal.begin() as db:
        existing_version = db.execute(
            text(
                """
                select dataset_version_id, version_no, row_count, column_count
                from dataset_version
                where source_import_batch_id = :source_import_batch_id
                limit 1
                """
            ),
            {"source_import_batch_id": import_batch_id},
        ).mappings().first()
        if existing_version is not None:
            manifest["publishedDatasetVersionId"] = str(existing_version["dataset_version_id"])
            manifest["publishedVersionNo"] = existing_version["version_no"]
            save_manifest(manifest)
            return DatasetVersionPublishResponse(
                importBatchId=import_batch_id,
                datasetVersionId=str(existing_version["dataset_version_id"]),
                versionNo=existing_version["version_no"],
                status="published",
                rowCount=int(existing_version["row_count"]),
                columnCount=int(existing_version["column_count"]),
            )

        latest_versions = db.execute(
            text(
                """
                select dataset_version_id, version_no
                from dataset_version
                where dataset_id = :dataset_id
                order by created_at
                """
            ),
            {"dataset_id": row["dataset_id"]},
        ).mappings().all()

        existing_version_numbers = [version["version_no"] for version in latest_versions]
        version_no = next_dataset_version_no(existing_version_numbers)
        parent_version_id = str(latest_versions[-1]["dataset_version_id"]) if latest_versions else None
        dataset_version_id = str(uuid4())
        now = datetime.now(timezone.utc)
        dataset_hash = compute_rows_hash(manifest.get("rows", []))

        db.execute(
            text(
                """
                insert into dataset_version (
                  dataset_version_id,
                  dataset_id,
                  version_no,
                  parent_version_id,
                  source_import_batch_id,
                  status,
                  is_derived,
                  row_count,
                  column_count,
                  dataset_hash,
                  created_by,
                  published_at
                )
                values (
                  :dataset_version_id,
                  :dataset_id,
                  :version_no,
                  :parent_version_id,
                  :source_import_batch_id,
                  'published',
                  false,
                  :row_count,
                  :column_count,
                  :dataset_hash,
                  :created_by,
                  :published_at
                )
                """
            ),
            {
                "dataset_version_id": dataset_version_id,
                "dataset_id": row["dataset_id"],
                "version_no": version_no,
                "parent_version_id": parent_version_id,
                "source_import_batch_id": import_batch_id,
                "row_count": manifest["rowCount"],
                "column_count": manifest["columnCount"],
                "dataset_hash": dataset_hash,
                "created_by": context.user_id,
                "published_at": now,
            },
        )

        if parent_version_id:
            db.execute(
                text(
                    """
                    insert into dataset_version_lineage (
                      dataset_version_lineage_id,
                      from_dataset_version_id,
                      to_dataset_version_id,
                      lineage_type
                    )
                    values (
                      :dataset_version_lineage_id,
                      :from_dataset_version_id,
                      :to_dataset_version_id,
                      'import_publish'
                    )
                    """
                ),
                {
                    "dataset_version_lineage_id": str(uuid4()),
                    "from_dataset_version_id": parent_version_id,
                    "to_dataset_version_id": dataset_version_id,
                },
            )

        subject_identifier_type = manifest.get("identifierType")
        primary_key_column = manifest.get("primaryKeyColumn")
        for row_index, record in enumerate(manifest.get("rows", []), start=1):
            identifier_value = str(record.get(primary_key_column or "", "")).strip()
            subject_id = db.execute(
                text(
                    """
                    select subject_id
                    from subject_identifier
                    where project_id = (
                      select project_id from dataset where dataset_id = :dataset_id
                    )
                      and identifier_type = :identifier_type
                      and identifier_value = :identifier_value
                    """
                ),
                {
                    "dataset_id": row["dataset_id"],
                    "identifier_type": subject_identifier_type,
                    "identifier_value": identifier_value,
                },
            ).scalar_one()

            db.execute(
                text(
                    """
                    insert into visit_record (
                      visit_id,
                      subject_id,
                      dataset_version_id,
                      import_batch_id,
                      system_batch_seq,
                      visit_label
                    )
                    values (
                      :visit_id,
                      :subject_id,
                      :dataset_version_id,
                      :import_batch_id,
                      :system_batch_seq,
                      :visit_label
                    )
                    """
                ),
                {
                    "visit_id": str(uuid4()),
                    "subject_id": subject_id,
                    "dataset_version_id": dataset_version_id,
                    "import_batch_id": import_batch_id,
                    "system_batch_seq": row_index,
                    "visit_label": identifier_value,
                },
            )

        db.execute(
            text("update import_batch set status = 'published' where import_batch_id = :import_batch_id"),
            {"import_batch_id": import_batch_id},
        )

    manifest["publishedDatasetVersionId"] = dataset_version_id
    manifest["publishedVersionNo"] = version_no
    save_manifest(manifest)

    return DatasetVersionPublishResponse(
        importBatchId=import_batch_id,
        datasetVersionId=dataset_version_id,
        versionNo=version_no,
        status="published",
        rowCount=manifest["rowCount"],
        columnCount=manifest["columnCount"],
    )


@router.get("/datasets/{dataset_id}/versions", response_model=DatasetVersionListResponse)
def list_dataset_versions(
    dataset_id: str,
    context: DemoAuthContext = Depends(get_demo_auth_context),
) -> DatasetVersionListResponse:
    ensure_permission(context, "dataset.read")
    dataset_row = _load_dataset_row(dataset_id)
    ensure_brand_allowed(context, dataset_row["brand_code"])

    with SessionLocal() as db:
        rows = db.execute(
            text(
                """
                select
                  dataset_version_id,
                  dataset_id,
                  version_no,
                  status,
                  row_count,
                  column_count,
                  published_at
                from dataset_version
                where dataset_id = :dataset_id
                order by created_at desc
                """
            ),
            {"dataset_id": dataset_id},
        ).mappings().all()
        items = [
            DatasetVersionItem(
                id=str(row["dataset_version_id"]),
                datasetId=str(row["dataset_id"]),
                versionNo=row["version_no"],
                status=row["status"],
                rowCount=int(row["row_count"]),
                columnCount=int(row["column_count"]),
                publishedAt=row["published_at"].isoformat() if row["published_at"] else None,
            )
            for row in rows
        ]
    return DatasetVersionListResponse(items=items)
