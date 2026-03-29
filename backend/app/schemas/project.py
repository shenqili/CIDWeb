from pydantic import BaseModel, Field


class CreateDatasetRequest(BaseModel):
    brandId: str
    datasetName: str
    datasetType: str = "instrument"


class ProjectItem(BaseModel):
    id: str
    tenantId: str
    name: str
    status: str
    allowedBrandIds: list[str]
    defaultImportMode: str
    highSensitivityExportPolicy: str


class ProjectListResponse(BaseModel):
    items: list[ProjectItem]


class BrandItem(BaseModel):
    id: str
    code: str
    name: str
    status: str


class BrandListResponse(BaseModel):
    items: list[BrandItem]


class BrandConfigVersionItem(BaseModel):
    id: str
    brandId: str
    versionNo: str
    status: str
    publishedAt: str | None = None


class BrandConfigVersionListResponse(BaseModel):
    items: list[BrandConfigVersionItem]


class BrandPublishResponse(BaseModel):
    brandId: str
    brandCode: str
    brandConfigVersionId: str
    versionNo: str
    status: str
    affectedProjectCount: int
    affectedVersionBundleIds: list[str]


class VersionBundleItem(BaseModel):
    id: str
    projectId: str
    brandId: str
    brandConfigVersionId: str
    metricCatalogVersionId: str
    questionnaireTemplateVersionId: str
    isActive: bool


class VersionBundleListResponse(BaseModel):
    items: list[VersionBundleItem]


class ProjectBrandBindingItem(BaseModel):
    brandId: str
    defaultVersionBundleId: str
    status: str


class ProjectBrandBindingListResponse(BaseModel):
    items: list[ProjectBrandBindingItem]


class DatasetItem(BaseModel):
    id: str
    projectId: str
    brandId: str
    datasetName: str
    datasetType: str
    status: str


class DatasetListResponse(BaseModel):
    items: list[DatasetItem]


class UploadBatchResponse(BaseModel):
    importBatchId: str
    datasetId: str
    sourceFileName: str
    status: str
    rowCount: int
    columnCount: int


class ImportBatchItem(BaseModel):
    id: str
    datasetId: str
    sourceFileName: str
    status: str
    versionBundleId: str
    createdAt: str


class ImportBatchListResponse(BaseModel):
    items: list[ImportBatchItem]


class ImportBatchColumn(BaseModel):
    sourceName: str
    sampleValue: str | None = None


class FieldMappingItem(BaseModel):
    sourceName: str
    targetName: str


class FieldMappingRequest(BaseModel):
    mappings: list[FieldMappingItem] = Field(default_factory=list)


class PrimaryKeyMappingRequest(BaseModel):
    primaryKeyColumn: str
    identifierType: str = "rd"


class ImportBatchDetailResponse(BaseModel):
    importBatchId: str
    datasetId: str
    brandId: str
    sourceFileName: str
    status: str
    rowCount: int
    columnCount: int
    columns: list[ImportBatchColumn]
    fieldMappings: list[FieldMappingItem]
    primaryKeyColumn: str | None = None
    identifierType: str | None = None
    createdSubjectCount: int = 0
    reusedSubjectCount: int = 0
    missingPrimaryKeyRows: list[int] = Field(default_factory=list)
    publishedDatasetVersionId: str | None = None
    publishedVersionNo: str | None = None


class PrimaryKeyMappingResponse(BaseModel):
    importBatchId: str
    status: str
    createdSubjectCount: int
    reusedSubjectCount: int
    missingPrimaryKeyRows: list[int]


class DatasetVersionItem(BaseModel):
    id: str
    datasetId: str
    versionNo: str
    status: str
    rowCount: int
    columnCount: int
    publishedAt: str | None = None


class DatasetVersionListResponse(BaseModel):
    items: list[DatasetVersionItem]


class DatasetVersionPublishResponse(BaseModel):
    importBatchId: str
    datasetVersionId: str
    versionNo: str
    status: str
    rowCount: int
    columnCount: int


class ProjectPortfolioBrandSummaryItem(BaseModel):
    brandId: str
    brandCode: str
    brandName: str
    metricCount: int
    datasetCount: int
    datasetVersionCount: int
    maxRowCount: int
    maxColumnCount: int


class ProjectPortfolioSummaryResponse(BaseModel):
    projectId: str
    totalBrands: int
    totalMetricMappings: int
    totalDatasets: int
    totalDatasetVersions: int
    items: list[ProjectPortfolioBrandSummaryItem]
