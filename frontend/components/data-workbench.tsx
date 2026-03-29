"use client";

import { useEffect, useState } from "react";
import type { ChangeEvent } from "react";

import { apiRequest, DEMO_PROJECT_ID } from "./api";
import { useDemoSession } from "./demo-context";

type Brand = {
  id: string;
  code: string;
  name: string;
  status: string;
};

type Dataset = {
  id: string;
  projectId: string;
  brandId: string;
  datasetName: string;
  datasetType: string;
  status: string;
};

type ImportBatchSummary = {
  id: string;
  datasetId: string;
  sourceFileName: string;
  status: string;
  versionBundleId: string;
  createdAt: string;
};

type ImportBatchDetail = {
  importBatchId: string;
  datasetId: string;
  brandId: string;
  sourceFileName: string;
  status: string;
  rowCount: number;
  columnCount: number;
  columns: Array<{ sourceName: string; sampleValue?: string | null }>;
  fieldMappings: Array<{ sourceName: string; targetName: string }>;
  primaryKeyColumn?: string | null;
  identifierType?: string | null;
  createdSubjectCount: number;
  reusedSubjectCount: number;
  missingPrimaryKeyRows: number[];
  publishedDatasetVersionId?: string | null;
  publishedVersionNo?: string | null;
};

type DatasetVersion = {
  id: string;
  datasetId: string;
  versionNo: string;
  status: string;
  rowCount: number;
  columnCount: number;
  publishedAt?: string | null;
};

type UploadBatchResponse = {
  importBatchId: string;
};

type PrimaryKeyMappingResponse = {
  status: string;
  createdSubjectCount: number;
  reusedSubjectCount: number;
};

type DatasetVersionPublishResponse = {
  versionNo: string;
};

function toTargetName(sourceName: string) {
  return sourceName.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "") || "field";
}

export function DataWorkbench() {
  const session = useDemoSession();
  const canCreateDataset = session.permissions.includes("dataset.create");
  const canUpload = session.permissions.includes("dataset.upload");
  const canSaveMappings = session.permissions.includes("dataset.map_fields");
  const canRunPrimaryKeyMapping = session.permissions.includes("dataset.map_primary_keys");
  const canPublishDataset = session.permissions.includes("dataset.publish");
  const [brands, setBrands] = useState<Brand[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [selectedBrandCode, setSelectedBrandCode] = useState("");
  const [selectedDatasetId, setSelectedDatasetId] = useState("");
  const [selectedBatchId, setSelectedBatchId] = useState("");
  const [datasetName, setDatasetName] = useState("phase1-browser-dataset");
  const [batches, setBatches] = useState<ImportBatchSummary[]>([]);
  const [batchDetail, setBatchDetail] = useState<ImportBatchDetail | null>(null);
  const [versions, setVersions] = useState<DatasetVersion[]>([]);
  const [fieldMappings, setFieldMappings] = useState<Array<{ sourceName: string; targetName: string }>>([]);
  const [primaryKeyColumn, setPrimaryKeyColumn] = useState("RD");
  const [message, setMessage] = useState("请先选择或创建数据集。");
  const [error, setError] = useState("");
  const [isBusy, setIsBusy] = useState(false);

  async function loadBaseData() {
    setError("");
    const [brandData, datasetData] = await Promise.all([
      apiRequest<{ items: Brand[] }>("/brands", session),
      apiRequest<{ items: Dataset[] }>(`/projects/${DEMO_PROJECT_ID}/datasets`, session),
    ]);

    setBrands(brandData.items);
    setDatasets(datasetData.items);

    const resolvedBrandCode = selectedBrandCode || brandData.items[0]?.code || session.brandCode;
    setSelectedBrandCode(resolvedBrandCode);

    const preferredDataset = datasetData.items.find((dataset) => dataset.brandId === resolvedBrandCode) ?? datasetData.items[0];
    setSelectedDatasetId((current) =>
      current && datasetData.items.some((dataset) => dataset.id === current) ? current : preferredDataset?.id || "",
    );
  }

  async function loadDatasetArtifacts(datasetId: string) {
    if (!datasetId) {
      setBatches([]);
      setBatchDetail(null);
      setVersions([]);
      return;
    }

    const [batchData, versionData] = await Promise.all([
      apiRequest<{ items: ImportBatchSummary[] }>(`/projects/datasets/${datasetId}/import-batches`, session),
      apiRequest<{ items: DatasetVersion[] }>(`/projects/datasets/${datasetId}/versions`, session),
    ]);
    setBatches(batchData.items);
    setVersions(versionData.items);
    const newestBatchId = batchData.items[0]?.id || "";
    setSelectedBatchId((current) =>
      current && batchData.items.some((batch) => batch.id === current) ? current : newestBatchId,
    );
  }

  async function loadBatchDetail(importBatchId: string) {
    if (!importBatchId) {
      setBatchDetail(null);
      setFieldMappings([]);
      return;
    }

    const detail = await apiRequest<ImportBatchDetail>(`/projects/import-batches/${importBatchId}`, session);
    setBatchDetail(detail);
    setPrimaryKeyColumn(detail.primaryKeyColumn || detail.columns[0]?.sourceName || "RD");
    setFieldMappings(
      detail.fieldMappings.length > 0
        ? detail.fieldMappings
        : detail.columns.map((column) => ({ sourceName: column.sourceName, targetName: toTargetName(column.sourceName) })),
    );
  }

  useEffect(() => {
    void loadBaseData();
  }, [session.role, session.brandCode]);

  useEffect(() => {
    void loadDatasetArtifacts(selectedDatasetId);
  }, [selectedDatasetId, session.role, session.brandCode]);

  useEffect(() => {
    void loadBatchDetail(selectedBatchId);
  }, [selectedBatchId, session.role, session.brandCode]);

  async function handleCreateDataset() {
    setIsBusy(true);
    setError("");
    try {
      const createdDataset = await apiRequest<Dataset>(`/projects/${DEMO_PROJECT_ID}/datasets`, session, {
        method: "POST",
        body: JSON.stringify({
          brandId: selectedBrandCode || session.brandCode,
          datasetName,
          datasetType: "instrument",
        }),
      });
      await loadBaseData();
      setSelectedDatasetId(createdDataset.id);
      setMessage(`已创建数据集 ${datasetName}。`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "创建数据集失败");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleUploadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file || !selectedDatasetId) {
      return;
    }

    setIsBusy(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const uploaded = await apiRequest<UploadBatchResponse>(
        `/projects/datasets/${selectedDatasetId}/uploads`,
        session,
        {
          method: "POST",
          body: formData,
        },
      );
      await loadDatasetArtifacts(selectedDatasetId);
      setSelectedBatchId(uploaded.importBatchId);
      setMessage(`已上传文件 ${file.name}。`);
      event.target.value = "";
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "文件上传失败");
    } finally {
      setIsBusy(false);
    }
  }

  async function handleSaveMappings() {
    if (!selectedBatchId) {
      return;
    }
    setIsBusy(true);
    setError("");
    try {
      const detail = await apiRequest<ImportBatchDetail>(`/projects/import-batches/${selectedBatchId}/field-mappings`, session, {
        method: "POST",
        body: JSON.stringify({ mappings: fieldMappings }),
      });
      setBatchDetail(detail);
      setMessage(`字段映射已保存，共 ${detail.fieldMappings.length} 项。`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "字段映射失败");
    } finally {
      setIsBusy(false);
    }
  }

  async function handlePrimaryKeyMapping() {
    if (!selectedBatchId) {
      return;
    }
    setIsBusy(true);
    setError("");
    try {
      const result = await apiRequest<PrimaryKeyMappingResponse>(
        `/projects/import-batches/${selectedBatchId}/primary-key-mapping`,
        session,
        {
          method: "POST",
          body: JSON.stringify({ primaryKeyColumn, identifierType: "rd" }),
        },
      );
      await loadBatchDetail(selectedBatchId);
      setMessage(`主键映射已完成，创建 ${result.createdSubjectCount} 个受试者，复用 ${result.reusedSubjectCount} 个。`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "主键映射失败");
    } finally {
      setIsBusy(false);
    }
  }

  async function handlePublishVersion() {
    if (!selectedBatchId || !selectedDatasetId) {
      return;
    }
    setIsBusy(true);
    setError("");
    try {
      const result = await apiRequest<DatasetVersionPublishResponse>(
        `/projects/import-batches/${selectedBatchId}/publish-version`,
        session,
        {
          method: "POST",
        },
      );
      await loadDatasetArtifacts(selectedDatasetId);
      await loadBatchDetail(selectedBatchId);
      setMessage(`数据版本已发布为 ${result.versionNo}。`);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "数据版本发布失败");
    } finally {
      setIsBusy(false);
    }
  }

  return (
    <main className="page">
      <div className="page-heading">
        <div>
          <h1>数据</h1>
          <p className="lead">用同一条页面链路完成数据集创建、文件上传、字段映射、主键映射和数据版本发布。</p>
        </div>
      </div>

      {error ? (
        <div className="notice error" data-testid="data-notice">
          {error}
        </div>
      ) : (
        <div className="notice success" data-testid="data-notice">
          {message}
        </div>
      )}

      <section className="layout-two">
        <article className="panel">
          <h2>阶段 1 数据集</h2>
          <div className="form-grid">
            <label className="field-block">
              <span>品牌</span>
              <select
                data-testid="dataset-brand-select"
                value={selectedBrandCode}
                onChange={(event) => setSelectedBrandCode(event.target.value)}
              >
                {brands.map((brand) => (
                  <option key={brand.id} value={brand.code}>
                    {brand.name} ({brand.code})
                  </option>
                ))}
              </select>
            </label>
            <label className="field-block">
              <span>数据集名称</span>
              <input data-testid="dataset-name-input" value={datasetName} onChange={(event) => setDatasetName(event.target.value)} />
            </label>
          </div>
          <div className="toolbar">
            <button
              className="button"
              data-testid="create-dataset-button"
              onClick={handleCreateDataset}
              disabled={isBusy || !canCreateDataset}
            >
              创建数据集
            </button>
            <label className="button secondary file-button">
              上传文件
              <input
                data-testid="upload-file-input"
                type="file"
                accept=".csv,.txt,.xlsx"
                onChange={handleUploadFile}
                disabled={!canUpload}
              />
            </label>
          </div>
          <table className="data-table" data-testid="dataset-table">
            <thead>
              <tr>
                <th>数据集</th>
                <th>品牌</th>
                <th>状态</th>
              </tr>
            </thead>
            <tbody>
              {datasets.map((dataset) => (
                <tr
                  key={dataset.id}
                  className={dataset.id === selectedDatasetId ? "is-selected" : undefined}
                  onClick={() => setSelectedDatasetId(dataset.id)}
                >
                  <td>{dataset.datasetName}</td>
                  <td>{dataset.brandId}</td>
                  <td>{dataset.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </article>

        <article className="panel">
          <h2>导入批次</h2>
          <ul className="interactive-list" data-testid="import-batch-list">
            {batches.map((batch) => (
              <li key={batch.id}>
                <button
                  className={batch.id === selectedBatchId ? "list-button active" : "list-button"}
                  onClick={() => setSelectedBatchId(batch.id)}
                >
                  <span>{batch.sourceFileName}</span>
                  <span>{batch.status}</span>
                </button>
              </li>
            ))}
          </ul>

          <h3>数据版本</h3>
          <ul className="token-list" data-testid="dataset-version-list">
            {versions.map((version) => (
              <li key={version.id} className="token">
                {version.versionNo} / {version.status}
              </li>
            ))}
          </ul>
        </article>
      </section>

      <section className="layout-two">
        <article className="panel">
          <h2>字段映射</h2>
          <div className="stack">
            {fieldMappings.map((mapping, index) => (
              <div key={mapping.sourceName} className="field-row">
                <span>{mapping.sourceName}</span>
                <input
                  aria-label={`字段映射-${mapping.sourceName}`}
                  value={mapping.targetName}
                  onChange={(event) =>
                    setFieldMappings((current) =>
                      current.map((item, currentIndex) =>
                        currentIndex === index ? { ...item, targetName: event.target.value } : item,
                      ),
                    )
                  }
                />
              </div>
            ))}
          </div>
          <button
            className="button"
            data-testid="save-field-mappings-button"
            onClick={handleSaveMappings}
            disabled={!batchDetail || isBusy || !canSaveMappings}
          >
            保存字段映射
          </button>
        </article>

        <article className="panel">
          <h2>主键映射与版本发布</h2>
          <label className="field-block">
            <span>主键字段</span>
            <select
              data-testid="primary-key-select"
              value={primaryKeyColumn}
              onChange={(event) => setPrimaryKeyColumn(event.target.value)}
            >
              {batchDetail?.columns.map((column) => (
                <option key={column.sourceName} value={column.sourceName}>
                  {column.sourceName}
                </option>
              ))}
            </select>
          </label>
          <div className="toolbar">
            <button
              className="button secondary"
              data-testid="run-primary-key-mapping-button"
              onClick={handlePrimaryKeyMapping}
              disabled={!batchDetail || isBusy || !canRunPrimaryKeyMapping}
            >
              执行主键映射
            </button>
            <button
              className="button"
              data-testid="publish-dataset-version-button"
              onClick={handlePublishVersion}
              disabled={!batchDetail || isBusy || !canPublishDataset}
            >
              发布数据版本
            </button>
          </div>
          <div className="stack compact">
            <div className="kv">
              <span>导入批次状态</span>
              <strong>{batchDetail?.status ?? "-"}</strong>
            </div>
            <div className="kv">
              <span>记录数 / 字段数</span>
              <strong>
                {batchDetail?.rowCount ?? 0} / {batchDetail?.columnCount ?? 0}
              </strong>
            </div>
            <div className="kv">
              <span>已发布版本</span>
              <strong>{batchDetail?.publishedVersionNo ?? "-"}</strong>
            </div>
          </div>
        </article>
      </section>
    </main>
  );
}
