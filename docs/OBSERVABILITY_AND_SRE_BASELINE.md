# Observability & SRE Baseline (M4.4)

## Overview
Milestone 4.4 adds a lightweight observability layer on top of the secured, tenant-aware platform (post-M4.3). The goal is to improve debuggability and operational readiness without changing any domain behavior.

## Structured Logging
- Middleware attaches a `request_id` (UUID) to every request and returns it via `X-Request-ID`.
- Structured log fields: `request_id`, `tenant_id` (when authenticated), `user_id`, `path`, `method`, `status_code`, `duration_ms`, `component`, `log_level`, `message`.
- PII is excluded; only IDs are logged.
- Logging helpers live in `backend/src/app/observability/logging.py` and are used in key flows (case evaluation, lifecycle, history, admin config).

## Metrics
- In-process counters (`backend/src/app/observability/metrics.py`):
  - `requests_total` by method+path
  - `requests_failed_total` by method+path (5xx)
- Populated by the request middleware.

## Health & Readiness
- Internal router (`backend/src/app/api/routes/internal.py`) exposes:
  - `GET /internal/healthz` (liveness)
  - `GET /internal/readyz` (DB connectivity; returns 503 if unavailable)
  - `GET /internal/metrics` (JSON snapshot of metrics)
- These endpoints are intended for internal use and should be firewalled by infra.

## Instrumented Flows
- Case evaluation: logs `case_evaluation` component with request/user/tenant context.
- Case lifecycle: logs transitions with from/to status and user role under `case_lifecycle`.
- Case history: logs access under `case_history`.
- Admin config: logs reads under `admin_config`.

## Future Direction
- Integrate with external telemetry backends (Prometheus/Grafana/Loki).
- Add tracing (OpenTelemetry), SLOs/alerts, richer latency buckets, per-tenant dashboards.
