# Architecture

The API is the policy-enforcement boundary. The UI never selects a tenant; tenant and role come from a verified token. Agent functions only invoke scoped service/database logic and every execution writes `agent_runs`. PostgreSQL owns business data; Firestore is optional for notifications only.
