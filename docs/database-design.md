# Database design

All business records are tenant-scoped UUID entities. `users`, `employees`, `projects`, `tasks`, `milestones`, `approvals`, `approval_history`, `releases`, `agent_runs`, `audit_logs`, `notifications`, and `idempotency_keys` are represented in SQLAlchemy. Production migrations should be generated with Alembic before the first Cloud SQL deployment.
