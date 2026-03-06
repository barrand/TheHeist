#!/bin/bash
set -euo pipefail

# ============================================================================
# One-time GCP setup for The Heist
# Run this once to create all cloud resources, then CI/CD handles the rest.
#
# Prerequisites:
#   - gcloud CLI installed and authenticated (gcloud auth login)
#   - A GCP project created (gcloud projects create my-project-id)
#   - Billing enabled on the project
#
# Usage:
#   ./deploy/setup-gcp.sh <PROJECT_ID> <GEMINI_API_KEY>
#
# Example:
#   ./deploy/setup-gcp.sh theheist-prod AIzaSy...
# ============================================================================

PROJECT_ID="${1:?Usage: $0 <PROJECT_ID> <GEMINI_API_KEY>}"
GEMINI_API_KEY="${2:?Usage: $0 <PROJECT_ID> <GEMINI_API_KEY>}"

REGION="us-west1"
BUCKET="theheist-generated"
BACKEND_SERVICE="heist-backend"
FRONTEND_SERVICE="heist-frontend"

echo "============================================================"
echo "  Setting up GCP for The Heist"
echo "  Project: $PROJECT_ID"
echo "  Region:  $REGION"
echo "============================================================"
echo ""

# Set project
gcloud config set project "$PROJECT_ID"

# Enable required APIs
echo ">> Enabling APIs..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com \
  storage.googleapis.com

# Create GCS bucket for generated files
echo ">> Creating GCS bucket: $BUCKET..."
if gsutil ls -b "gs://$BUCKET" 2>/dev/null; then
  echo "   Bucket already exists, skipping."
else
  gsutil mb -l "$REGION" "gs://$BUCKET"
  # 30-day lifecycle rule: auto-delete old generated files
  cat > /tmp/lifecycle.json <<'EOF'
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }
  ]
}
EOF
  gsutil lifecycle set /tmp/lifecycle.json "gs://$BUCKET"
  rm /tmp/lifecycle.json
  echo "   Bucket created with 30-day lifecycle rule."
fi

# Store Gemini API key in Secret Manager
echo ">> Storing GEMINI_API_KEY in Secret Manager..."
if gcloud secrets describe GEMINI_API_KEY --project="$PROJECT_ID" 2>/dev/null; then
  echo "   Secret exists, adding new version..."
  echo -n "$GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
else
  echo -n "$GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --data-file=- --replication-policy=automatic
fi

# Grant Cloud Run service account access to secrets and bucket
echo ">> Granting IAM permissions..."
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')
SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
  --member="serviceAccount:$SA" \
  --role="roles/secretmanager.secretAccessor" \
  --project="$PROJECT_ID" --quiet

gsutil iam ch "serviceAccount:$SA:objectAdmin" "gs://$BUCKET"

# Grant Cloud Build permission to deploy to Cloud Run
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/run.admin" --quiet

gcloud iam service-accounts add-iam-policy-binding "$SA" \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/iam.serviceAccountUser" --quiet

# Disable org policy that blocks unauthenticated Cloud Run access (if applicable)
gcloud resource-manager org-policies reset constraints/iam.allowedPolicyMemberDomains \
  --project="$PROJECT_ID" 2>/dev/null || true

echo ""
echo "============================================================"
echo "  Setup complete!"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Connect your GitHub repo to Cloud Build:"
echo "     gcloud builds triggers create github \\"
echo "       --repo-name=TheHeist --repo-owner=<YOUR_GITHUB_USER> \\"
echo "       --branch-pattern='^main$' \\"
echo "       --build-config=cloudbuild.yaml \\"
echo "       --substitutions=_REGION=$REGION,_BACKEND_SERVICE=$BACKEND_SERVICE,_FRONTEND_SERVICE=$FRONTEND_SERVICE,_GCS_BUCKET=$BUCKET"
echo ""
echo "  2. Or trigger a manual build now:"
echo "     gcloud builds submit --config=cloudbuild.yaml \\"
echo "       --substitutions=SHORT_SHA=manual"
echo ""
echo "  3. After first deploy, get your URLs:"
echo "     gcloud run services describe $FRONTEND_SERVICE --region=$REGION --format='value(status.url)'"
echo "     gcloud run services describe $BACKEND_SERVICE --region=$REGION --format='value(status.url)'"
echo ""
