#!/bin/bash
set -e

# Navigate to the script directory
cd "$(dirname "$0")"

# Initialize Terraform offline (no providers required as we use terraform_data)
terraform init

# Apply the recovery configuration
terraform apply -auto-approve \
  -var="ledger_path=/app/corrupted_ledger.csv" \
  -var="output_dir=/app/output"
