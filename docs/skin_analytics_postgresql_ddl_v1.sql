-- CIDWeb PostgreSQL DDL v1
-- Scope: demo-ready schema for local Docker Compose environment

create extension if not exists "pgcrypto";

create or replace function set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

-- 1. Identity & access

create table if not exists tenant (
  tenant_id uuid primary key default gen_random_uuid(),
  tenant_code varchar(64) not null unique,
  tenant_name varchar(255) not null,
  status varchar(32) not null default 'active',
  data_isolation_mode varchar(32) not null default 'shared_control_plane',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists organization_user (
  user_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(tenant_id),
  email varchar(255),
  phone varchar(64),
  display_name varchar(255) not null,
  status varchar(32) not null default 'active',
  is_super_admin boolean not null default false,
  created_at timestamptz not null default now()
);

create unique index if not exists uq_org_user_tenant_email
  on organization_user(tenant_id, email)
  where email is not null;

create table if not exists role (
  role_id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenant(tenant_id),
  role_name varchar(128) not null,
  role_scope varchar(32) not null,
  created_at timestamptz not null default now()
);

create table if not exists permission (
  permission_id uuid primary key default gen_random_uuid(),
  permission_code varchar(128) not null unique,
  permission_name varchar(255) not null
);

create table if not exists role_permission (
  role_permission_id uuid primary key default gen_random_uuid(),
  role_id uuid not null references role(role_id) on delete cascade,
  permission_id uuid not null references permission(permission_id) on delete cascade,
  unique(role_id, permission_id)
);

create table if not exists project (
  project_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(tenant_id),
  project_code varchar(64) not null,
  project_name varchar(255) not null,
  project_type varchar(64),
  import_mode_default varchar(32) not null default 'batch',
  status varchar(32) not null default 'active',
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(tenant_id, project_code)
);

create table if not exists project_member (
  project_member_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  user_id uuid not null references organization_user(user_id) on delete cascade,
  role_id uuid not null references role(role_id),
  brand_scope_mode varchar(32) not null default 'all_bound_brands',
  created_at timestamptz not null default now(),
  unique(project_id, user_id, role_id)
);

-- 2. Brand config & questionnaire domain

create table if not exists brand (
  brand_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(tenant_id),
  brand_code varchar(64) not null,
  brand_name varchar(255) not null,
  status varchar(32) not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(tenant_id, brand_code)
);

create table if not exists brand_config_version (
  brand_config_version_id uuid primary key default gen_random_uuid(),
  brand_id uuid not null references brand(brand_id) on delete cascade,
  version_no varchar(32) not null,
  status varchar(32) not null default 'draft',
  base_version_id uuid references brand_config_version(brand_config_version_id),
  created_by uuid references organization_user(user_id),
  published_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(brand_id, version_no)
);

create table if not exists metric_catalog (
  metric_catalog_id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenant(tenant_id),
  catalog_name varchar(255) not null,
  catalog_scope varchar(32) not null default 'platform',
  created_at timestamptz not null default now()
);

create table if not exists metric_catalog_version (
  metric_catalog_version_id uuid primary key default gen_random_uuid(),
  metric_catalog_id uuid not null references metric_catalog(metric_catalog_id) on delete cascade,
  version_no varchar(32) not null,
  status varchar(32) not null default 'draft',
  base_version_id uuid references metric_catalog_version(metric_catalog_version_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(metric_catalog_id, version_no)
);

create table if not exists metric_alias (
  metric_alias_id uuid primary key default gen_random_uuid(),
  metric_catalog_version_id uuid not null references metric_catalog_version(metric_catalog_version_id) on delete cascade,
  raw_field_name varchar(255) not null,
  standard_metric_code varchar(255) not null,
  instrument_family varchar(128),
  body_site varchar(128),
  variable_type varchar(64),
  is_analyzable boolean not null default true,
  is_default_visible boolean not null default false,
  unique(metric_catalog_version_id, raw_field_name)
);

create table if not exists questionnaire_template (
  questionnaire_template_id uuid primary key default gen_random_uuid(),
  tenant_id uuid references tenant(tenant_id),
  template_name varchar(255) not null,
  template_scope varchar(32) not null default 'brand',
  created_at timestamptz not null default now()
);

create table if not exists questionnaire_template_version (
  questionnaire_template_version_id uuid primary key default gen_random_uuid(),
  questionnaire_template_id uuid not null references questionnaire_template(questionnaire_template_id) on delete cascade,
  version_no varchar(32) not null,
  status varchar(32) not null default 'draft',
  base_version_id uuid references questionnaire_template_version(questionnaire_template_version_id),
  scoring_rule_json jsonb,
  logic_rule_json jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(questionnaire_template_id, version_no)
);

create table if not exists questionnaire_question (
  question_id uuid primary key default gen_random_uuid(),
  questionnaire_template_version_id uuid not null references questionnaire_template_version(questionnaire_template_version_id) on delete cascade,
  question_code varchar(128) not null,
  question_text text not null,
  question_type varchar(64) not null,
  is_reverse_scored boolean not null default false,
  dimension_code varchar(128),
  display_order integer not null default 0,
  unique(questionnaire_template_version_id, question_code)
);

create table if not exists questionnaire_option (
  option_id uuid primary key default gen_random_uuid(),
  question_id uuid not null references questionnaire_question(question_id) on delete cascade,
  option_code varchar(128) not null,
  option_label text not null,
  option_score numeric(18,6),
  display_order integer not null default 0,
  unique(question_id, option_code)
);

create table if not exists questionnaire_campaign (
  questionnaire_campaign_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  questionnaire_template_version_id uuid not null references questionnaire_template_version(questionnaire_template_version_id),
  access_mode varchar(32) not null default 'internal_login',
  campaign_token varchar(128) not null unique,
  status varchar(32) not null default 'draft',
  expires_at timestamptz,
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now()
);

create table if not exists version_bundle (
  version_bundle_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  brand_config_version_id uuid not null references brand_config_version(brand_config_version_id),
  metric_catalog_version_id uuid not null references metric_catalog_version(metric_catalog_version_id),
  questionnaire_template_version_id uuid not null references questionnaire_template_version(questionnaire_template_version_id),
  is_active boolean not null default true,
  effective_from timestamptz not null default now(),
  effective_to timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create unique index if not exists uq_version_bundle_active
  on version_bundle(project_id, brand_id, brand_config_version_id, metric_catalog_version_id, questionnaire_template_version_id);

create table if not exists project_brand_binding (
  project_brand_binding_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  default_version_bundle_id uuid not null references version_bundle(version_bundle_id),
  status varchar(32) not null default 'active',
  unique(project_id, brand_id)
);

-- 3. Data asset domain

create table if not exists dataset (
  dataset_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  dataset_name varchar(255) not null,
  dataset_type varchar(64),
  status varchar(32) not null default 'active',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists import_batch (
  import_batch_id uuid primary key default gen_random_uuid(),
  dataset_id uuid not null references dataset(dataset_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  version_bundle_id uuid not null references version_bundle(version_bundle_id),
  source_file_name varchar(255) not null,
  storage_path text not null,
  import_mode varchar(32) not null,
  status varchar(32) not null default 'draft',
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now()
);

create table if not exists dataset_version (
  dataset_version_id uuid primary key default gen_random_uuid(),
  dataset_id uuid not null references dataset(dataset_id) on delete cascade,
  version_no varchar(32) not null,
  parent_version_id uuid references dataset_version(dataset_version_id),
  source_import_batch_id uuid references import_batch(import_batch_id),
  status varchar(32) not null default 'draft',
  is_derived boolean not null default false,
  row_count integer not null default 0,
  column_count integer not null default 0,
  dataset_hash varchar(128),
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  published_at timestamptz,
  unique(dataset_id, version_no)
);

create table if not exists dataset_version_lineage (
  dataset_version_lineage_id uuid primary key default gen_random_uuid(),
  from_dataset_version_id uuid not null references dataset_version(dataset_version_id),
  to_dataset_version_id uuid not null references dataset_version(dataset_version_id),
  lineage_type varchar(32) not null,
  source_analysis_job_id uuid,
  created_at timestamptz not null default now(),
  unique(from_dataset_version_id, to_dataset_version_id, lineage_type)
);

create table if not exists subject (
  subject_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  subject_status varchar(32) not null default 'active',
  created_at timestamptz not null default now()
);

create table if not exists subject_identifier (
  subject_identifier_id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references subject(subject_id) on delete cascade,
  project_id uuid not null references project(project_id) on delete cascade,
  identifier_type varchar(64) not null,
  identifier_value varchar(255) not null,
  is_primary boolean not null default false,
  source varchar(64),
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now(),
  unique(project_id, identifier_type, identifier_value)
);

create table if not exists visit_record (
  visit_id uuid primary key default gen_random_uuid(),
  subject_id uuid not null references subject(subject_id) on delete cascade,
  dataset_version_id uuid not null references dataset_version(dataset_version_id) on delete cascade,
  import_batch_id uuid references import_batch(import_batch_id),
  business_visit_date date,
  system_batch_seq integer,
  visit_label varchar(128),
  created_at timestamptz not null default now()
);

create table if not exists derived_variable_set (
  derived_variable_set_id uuid primary key default gen_random_uuid(),
  analysis_job_id uuid unique,
  source_dataset_version_id uuid not null references dataset_version(dataset_version_id),
  target_dataset_version_id uuid references dataset_version(dataset_version_id),
  publish_status varchar(32) not null default 'draft',
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now(),
  published_at timestamptz
);

create table if not exists variable_meta (
  variable_meta_id uuid primary key default gen_random_uuid(),
  dataset_version_id uuid not null references dataset_version(dataset_version_id) on delete cascade,
  standard_metric_code varchar(255),
  display_name varchar(255) not null,
  raw_field_name varchar(255),
  variable_type varchar(64),
  instrument_family varchar(128),
  body_site varchar(128),
  is_derived boolean not null default false,
  source_derived_set_id uuid references derived_variable_set(derived_variable_set_id)
);

-- 4. Analysis domain

create table if not exists cohort_rule (
  cohort_rule_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  rule_name varchar(255) not null,
  rule_json jsonb not null,
  status varchar(32) not null default 'draft',
  created_by uuid references organization_user(user_id),
  created_at timestamptz not null default now()
);

create table if not exists analysis_template (
  analysis_template_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid references brand(brand_id),
  template_name varchar(255) not null,
  template_scope varchar(32) not null default 'project',
  template_json jsonb not null,
  status varchar(32) not null default 'draft',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists analysis_job (
  analysis_job_id uuid primary key default gen_random_uuid(),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  version_bundle_id uuid not null references version_bundle(version_bundle_id),
  dataset_version_id uuid not null references dataset_version(dataset_version_id),
  cohort_rule_id uuid references cohort_rule(cohort_rule_id),
  analysis_template_id uuid references analysis_template(analysis_template_id),
  analysis_type varchar(64) not null,
  status varchar(32) not null default 'draft',
  idempotency_key varchar(255),
  submitted_by uuid references organization_user(user_id),
  submitted_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz,
  updated_at timestamptz not null default now()
);

create unique index if not exists uq_analysis_job_idempotency
  on analysis_job(project_id, idempotency_key)
  where idempotency_key is not null;

create table if not exists execution_manifest (
  execution_manifest_id uuid primary key default gen_random_uuid(),
  analysis_job_id uuid not null unique references analysis_job(analysis_job_id) on delete cascade,
  tenant_id uuid not null references tenant(tenant_id),
  project_id uuid not null references project(project_id),
  brand_id uuid not null references brand(brand_id),
  version_bundle_id uuid not null references version_bundle(version_bundle_id),
  brand_config_version_id uuid not null references brand_config_version(brand_config_version_id),
  metric_catalog_version_id uuid not null references metric_catalog_version(metric_catalog_version_id),
  questionnaire_template_version_id uuid not null references questionnaire_template_version(questionnaire_template_version_id),
  dataset_version_id uuid not null references dataset_version(dataset_version_id),
  dataset_version_hash varchar(128) not null,
  analysis_template_version varchar(64),
  analysis_method varchar(64) not null,
  runtime_parameters_hash varchar(128),
  engine_version varchar(64) not null,
  library_lock jsonb,
  random_seed integer,
  timezone varchar(64) not null,
  export_template_version varchar(64),
  manifest_hash varchar(128) not null,
  created_at timestamptz not null default now()
);

create table if not exists analysis_result (
  analysis_result_id uuid primary key default gen_random_uuid(),
  analysis_job_id uuid not null references analysis_job(analysis_job_id) on delete cascade,
  result_type varchar(64) not null,
  result_summary_json jsonb,
  result_table_path text,
  narrative_text text,
  created_at timestamptz not null default now()
);

create table if not exists chart_config (
  chart_config_id uuid primary key default gen_random_uuid(),
  analysis_job_id uuid not null references analysis_job(analysis_job_id) on delete cascade,
  chart_type varchar(64) not null,
  config_json jsonb not null,
  preview_path text,
  export_png_path text,
  export_svg_path text
);

alter table dataset_version_lineage
  add constraint fk_dataset_version_lineage_analysis_job
  foreign key (source_analysis_job_id)
  references analysis_job(analysis_job_id);

alter table derived_variable_set
  add constraint fk_derived_variable_set_analysis_job
  foreign key (analysis_job_id)
  references analysis_job(analysis_job_id);

-- 5. Questionnaire response domain

create table if not exists questionnaire_response (
  questionnaire_response_id uuid primary key default gen_random_uuid(),
  questionnaire_campaign_id uuid references questionnaire_campaign(questionnaire_campaign_id),
  project_id uuid not null references project(project_id) on delete cascade,
  brand_id uuid not null references brand(brand_id),
  dataset_version_id uuid references dataset_version(dataset_version_id),
  subject_id uuid references subject(subject_id),
  visit_id uuid references visit_record(visit_id),
  questionnaire_template_version_id uuid not null references questionnaire_template_version(questionnaire_template_version_id),
  status varchar(32) not null default 'draft',
  submission_channel varchar(32) not null default 'internal',
  is_anonymous boolean not null default false,
  respondent_meta jsonb,
  submitted_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists questionnaire_response_item (
  questionnaire_response_item_id uuid primary key default gen_random_uuid(),
  questionnaire_response_id uuid not null references questionnaire_response(questionnaire_response_id) on delete cascade,
  question_id uuid not null references questionnaire_question(question_id),
  raw_answer_json jsonb,
  normalized_answer_json jsonb,
  is_missing boolean not null default false,
  logic_warning_flag boolean not null default false
);

create table if not exists questionnaire_scoring_result (
  questionnaire_scoring_result_id uuid primary key default gen_random_uuid(),
  questionnaire_response_id uuid not null references questionnaire_response(questionnaire_response_id) on delete cascade,
  score_type varchar(32) not null,
  score_code varchar(128) not null,
  score_value numeric(18,6),
  derived_label varchar(255),
  unique(questionnaire_response_id, score_type, score_code)
);

-- 6. Export & approval domain

create table if not exists export_package (
  export_package_id uuid primary key default gen_random_uuid(),
  analysis_job_id uuid not null references analysis_job(analysis_job_id) on delete cascade,
  package_type varchar(64) not null,
  package_path text not null,
  package_hash varchar(128),
  contains_sensitive_data boolean not null default false,
  status varchar(32) not null default 'draft',
  created_at timestamptz not null default now(),
  expired_at timestamptz
);

create table if not exists export_approval_request (
  export_approval_request_id uuid primary key default gen_random_uuid(),
  export_package_id uuid not null references export_package(export_package_id) on delete cascade,
  tenant_id uuid not null references tenant(tenant_id),
  requester_user_id uuid not null references organization_user(user_id),
  approver_user_id uuid references organization_user(user_id),
  approval_status varchar(32) not null default 'pending_approval',
  reason text not null,
  decision_note text,
  approved_at timestamptz,
  expired_at timestamptz,
  download_limit integer not null default 1,
  download_count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- 7. Audit domain

create table if not exists audit_log (
  audit_log_id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null references tenant(tenant_id),
  project_id uuid references project(project_id),
  brand_id uuid references brand(brand_id),
  object_type varchar(64) not null,
  object_id varchar(128) not null,
  action_type varchar(64) not null,
  actor_user_id uuid references organization_user(user_id),
  ip_address inet,
  user_agent text,
  result_status varchar(32) not null,
  detail_json jsonb,
  created_at timestamptz not null default now()
);

-- 8. Key indexes

create index if not exists idx_dataset_project_brand on dataset(project_id, brand_id);
create index if not exists idx_dataset_version_dataset on dataset_version(dataset_id, status);
create index if not exists idx_subject_project_brand on subject(project_id, brand_id);
create index if not exists idx_visit_subject_dataset_version on visit_record(subject_id, dataset_version_id);
create index if not exists idx_analysis_job_project_brand on analysis_job(project_id, brand_id, status);
create index if not exists idx_export_approval_status on export_approval_request(approval_status, expired_at);
create index if not exists idx_audit_tenant_project_created on audit_log(tenant_id, project_id, created_at desc);
create index if not exists idx_questionnaire_response_project_brand on questionnaire_response(project_id, brand_id, status);

alter table tenant add constraint chk_tenant_status
  check (status in ('active','inactive','suspended'));
alter table organization_user add constraint chk_org_user_status
  check (status in ('active','inactive','locked'));
alter table role add constraint chk_role_scope
  check (role_scope in ('platform','tenant','project'));
alter table project add constraint chk_project_import_mode
  check (import_mode_default in ('batch','one_off'));
alter table brand add constraint chk_brand_status
  check (status in ('active','inactive'));
alter table brand_config_version add constraint chk_brand_config_version_status
  check (status in ('draft','published','deprecated'));
alter table metric_catalog_version add constraint chk_metric_catalog_version_status
  check (status in ('draft','published','deprecated'));
alter table questionnaire_template_version add constraint chk_questionnaire_template_version_status
  check (status in ('draft','published','deprecated'));
alter table questionnaire_campaign add constraint chk_questionnaire_campaign_access_mode
  check (access_mode in ('internal_login','public_anonymous'));
alter table questionnaire_campaign add constraint chk_questionnaire_campaign_status
  check (status in ('draft','published','closed','expired'));
alter table import_batch add constraint chk_import_batch_mode
  check (import_mode in ('append','merge','replace','patch'));
alter table dataset_version add constraint chk_dataset_version_status
  check (status in ('draft','published','frozen','archived'));
alter table derived_variable_set add constraint chk_derived_variable_set_publish_status
  check (publish_status in ('draft','published','discarded'));
alter table analysis_job add constraint chk_analysis_job_status
  check (status in ('draft','queued','running','partial_success','succeeded','failed','cancelled','expired'));
alter table questionnaire_response add constraint chk_questionnaire_response_status
  check (status in ('draft','submitted','invalid','scored','pending_match'));
alter table questionnaire_response add constraint chk_questionnaire_submission_channel
  check (submission_channel in ('internal','public_link','qr_code','excel_import'));
alter table export_package add constraint chk_export_package_status
  check (status in ('draft','ready','expired','deleted'));
alter table export_approval_request add constraint chk_export_approval_status
  check (approval_status in ('pending_approval','approved','rejected','expired'));

create or replace trigger trg_project_updated_at
before update on project
for each row execute function set_updated_at();

create or replace trigger trg_brand_updated_at
before update on brand
for each row execute function set_updated_at();

create or replace trigger trg_brand_config_version_updated_at
before update on brand_config_version
for each row execute function set_updated_at();

create or replace trigger trg_metric_catalog_version_updated_at
before update on metric_catalog_version
for each row execute function set_updated_at();

create or replace trigger trg_questionnaire_template_version_updated_at
before update on questionnaire_template_version
for each row execute function set_updated_at();

create or replace trigger trg_version_bundle_updated_at
before update on version_bundle
for each row execute function set_updated_at();

create or replace trigger trg_dataset_updated_at
before update on dataset
for each row execute function set_updated_at();

create or replace trigger trg_dataset_version_updated_at
before update on dataset_version
for each row execute function set_updated_at();

create or replace trigger trg_analysis_template_updated_at
before update on analysis_template
for each row execute function set_updated_at();

create or replace trigger trg_analysis_job_updated_at
before update on analysis_job
for each row execute function set_updated_at();

create or replace trigger trg_export_approval_request_updated_at
before update on export_approval_request
for each row execute function set_updated_at();
