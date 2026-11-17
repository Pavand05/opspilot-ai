# GCP deployment

Do not run these commands until you intentionally want billable resources. Create a GCP project, enable Cloud Run, Cloud Build, Artifact Registry, Secret Manager, Cloud SQL Admin, and Firebase. Create a private Cloud SQL PostgreSQL instance and a least-privilege service account. Put `DATABASE_URL`, `JWT_SECRET`, Firebase configuration and Gemini/Vertex configuration in Secret Manager.

```bash
gcloud auth login
gcloud config set project PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com secretmanager.googleapis.com
gcloud builds submit --config infra/cloudbuild.yaml --substitutions _REGION=asia-south1
gcloud run deploy opspilot-api --image asia-south1-docker.pkg.dev/PROJECT_ID/opspilot/api:TAG --region asia-south1 --service-account opspilot-runtime@PROJECT_ID.iam.gserviceaccount.com
```

Cloud Run deployments and Cloud SQL must be in compatible regions. Use Cloud Run service-account permissions, not downloaded service-account keys. Firebase Admin verifies the ID token sent via HTTPS with `firebase_admin.auth.verify_id_token`; local JWT auth must be disabled in production. See the official [Cloud Run FastAPI guide](https://docs.cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-fastapi-service) and [Firebase verification guide](https://firebase.google.com/docs/auth/admin/verify-id-tokens).
