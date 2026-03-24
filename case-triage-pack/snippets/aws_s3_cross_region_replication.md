# AWS S3 Cross-Region Replication Commands

Use this runbook if a customer needs a manual AWS CLI fallback for on-demand S3
cross-region replication between buckets.

Important:
- Live replication only applies to new or updated objects written after the
  replication rule is created.
- Existing objects require a one-time S3 Batch Replication job.
- The examples below assume both buckets are in the same AWS account. For
  cross-account replication, add the optional destination bucket policy shown
  later in this file.
- If the buckets use SSE-KMS, additional KMS key permissions are required.

## 1) Set variables

Replace the placeholders before running:
- `<SOURCE_BUCKET>`
- `<SOURCE_REGION>`
- `<DEST_BUCKET>`
- `<DEST_REGION>`
- `<ROLE_NAME>`
- `<REPORT_PREFIX>`

```bash
export SOURCE_BUCKET="<SOURCE_BUCKET>"
export SOURCE_REGION="<SOURCE_REGION>"
export DEST_BUCKET="<DEST_BUCKET>"
export DEST_REGION="<DEST_REGION>"
export ROLE_NAME="<ROLE_NAME>"
export REPORT_PREFIX="batch-replication-report"

export ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
export ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
```

## 2) Check the source bucket and create the destination bucket if needed

```bash
aws s3api head-bucket --bucket "${SOURCE_BUCKET}"

if aws s3api head-bucket --bucket "${DEST_BUCKET}" 2>/dev/null; then
  echo "Destination bucket already exists: ${DEST_BUCKET}"
else
  if [ "${DEST_REGION}" = "us-east-1" ]; then
    aws s3api create-bucket --bucket "${DEST_BUCKET}" --region "${DEST_REGION}"
  else
    aws s3api create-bucket \
      --bucket "${DEST_BUCKET}" \
      --region "${DEST_REGION}" \
      --create-bucket-configuration "LocationConstraint=${DEST_REGION}"
  fi
fi
```

## 3) Enable versioning on both buckets

```bash
aws s3api put-bucket-versioning \
  --bucket "${SOURCE_BUCKET}" \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-versioning \
  --bucket "${DEST_BUCKET}" \
  --versioning-configuration Status=Enabled
```

## 4) Create the IAM role if one was not provided

If the customer already has a suitable replication role, skip this section and
set `ROLE_ARN` to that existing role ARN.

This example uses a least-privilege inline policy that covers:
- the live replication rule
- the one-time S3 Batch Replication backfill job
- the completion report written by the batch job

### 4a) Create the trust policy

```bash
cat > /tmp/s3-replication-trust-policy.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": [
          "s3.amazonaws.com",
          "batchoperations.s3.amazonaws.com"
        ]
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
JSON
```

### 4b) Create the permissions policy

```bash
cat > /tmp/s3-replication-permissions-policy.json <<JSON
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadSourceBucketConfig",
      "Effect": "Allow",
      "Action": [
        "s3:GetReplicationConfiguration",
        "s3:ListBucket",
        "s3:PutInventoryConfiguration"
      ],
      "Resource": [
        "arn:aws:s3:::${SOURCE_BUCKET}"
      ]
    },
    {
      "Sid": "ReadAndReplicateSourceObjects",
      "Effect": "Allow",
      "Action": [
        "s3:GetObjectVersionForReplication",
        "s3:GetObjectVersionAcl",
        "s3:GetObjectVersionTagging",
        "s3:GetObjectRetention",
        "s3:GetObjectLegalHold",
        "s3:InitiateReplication"
      ],
      "Resource": [
        "arn:aws:s3:::${SOURCE_BUCKET}/*"
      ]
    },
    {
      "Sid": "WriteReplicasToDestination",
      "Effect": "Allow",
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete",
        "s3:ReplicateTags"
      ],
      "Resource": [
        "arn:aws:s3:::${DEST_BUCKET}/*"
      ]
    },
    {
      "Sid": "WriteBatchReports",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::${DEST_BUCKET}/${REPORT_PREFIX}*"
      ]
    }
  ]
}
JSON
```

### 4c) Create the role and attach the inline policy

```bash
if aws iam get-role --role-name "${ROLE_NAME}" >/dev/null 2>&1; then
  echo "Role already exists: ${ROLE_NAME}"
else
  aws iam create-role \
    --role-name "${ROLE_NAME}" \
    --assume-role-policy-document file:///tmp/s3-replication-trust-policy.json
fi

aws iam put-role-policy \
  --role-name "${ROLE_NAME}" \
  --policy-name "${ROLE_NAME}-inline-policy" \
  --policy-document file:///tmp/s3-replication-permissions-policy.json

aws iam wait role-exists --role-name "${ROLE_NAME}"
```

## 5) Apply the bucket replication rule

```bash
cat > /tmp/s3-replication-config.json <<JSON
{
  "Role": "${ROLE_ARN}",
  "Rules": [
    {
      "ID": "cross-region-replication",
      "Status": "Enabled",
      "Priority": 1,
      "DeleteMarkerReplication": {
        "Status": "Enabled"
      },
      "Filter": {
        "Prefix": ""
      },
      "Destination": {
        "Bucket": "arn:aws:s3:::${DEST_BUCKET}",
        "StorageClass": "STANDARD"
      }
    }
  ]
}
JSON

aws s3api put-bucket-replication \
  --bucket "${SOURCE_BUCKET}" \
  --replication-configuration file:///tmp/s3-replication-config.json \
  --region "${SOURCE_REGION}"
```

Check the applied rule:

```bash
aws s3api get-bucket-replication \
  --bucket "${SOURCE_BUCKET}" \
  --region "${SOURCE_REGION}"
```

## 6) Start a one-time S3 Batch Replication job for existing objects

Use this step only if the customer needs objects that already existed in the
source bucket to be copied to the destination bucket.

Important:
- Run the `create-job` call in the source bucket region.
- This example uses an S3-generated manifest and does not save the manifest
  output.
- The completion report is written to the destination bucket under
  `${REPORT_PREFIX}`.

```bash
export JOB_ID="$(
  aws s3control create-job \
    --account-id "${ACCOUNT_ID}" \
    --operation '{"S3ReplicateObject":{}}' \
    --report "{
      \"Bucket\":\"arn:aws:s3:::${DEST_BUCKET}\",
      \"Format\":\"Report_CSV_20180820\",
      \"Enabled\":true,
      \"Prefix\":\"${REPORT_PREFIX}\",
      \"ReportScope\":\"AllTasks\"
    }" \
    --manifest-generator "{
      \"S3JobManifestGenerator\": {
        \"ExpectedBucketOwner\": \"${ACCOUNT_ID}\",
        \"SourceBucket\": \"arn:aws:s3:::${SOURCE_BUCKET}\",
        \"EnableManifestOutput\": false,
        \"Filter\": {
          \"EligibleForReplication\": true,
          \"ObjectReplicationStatuses\": [
            \"NONE\",
            \"FAILED\"
          ]
        }
      }
    }" \
    --priority 10 \
    --role-arn "${ROLE_ARN}" \
    --no-confirmation-required \
    --region "${SOURCE_REGION}" \
    --query 'JobId' \
    --output text
)"

echo "Batch Replication job created: ${JOB_ID}"
```

Monitor the batch job:

```bash
aws s3control describe-job \
  --account-id "${ACCOUNT_ID}" \
  --job-id "${JOB_ID}" \
  --region "${SOURCE_REGION}"
```

## 7) Quick validation commands

```bash
aws s3api get-bucket-versioning --bucket "${SOURCE_BUCKET}"
aws s3api get-bucket-versioning --bucket "${DEST_BUCKET}"

aws s3api get-bucket-replication \
  --bucket "${SOURCE_BUCKET}" \
  --region "${SOURCE_REGION}"

aws s3control describe-job \
  --account-id "${ACCOUNT_ID}" \
  --job-id "${JOB_ID}" \
  --region "${SOURCE_REGION}"
```

## 8) Optional cross-account destination bucket policy

If the source and destination buckets are in different AWS accounts, the
destination account must allow the source replication role to write replicas.

Replace:
- `<SOURCE_ACCOUNT_ROLE_ARN>`
- `<DEST_BUCKET>`

```bash
cat > /tmp/destination-bucket-policy.json <<'JSON'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowReplicaWrites",
      "Effect": "Allow",
      "Principal": {
        "AWS": "<SOURCE_ACCOUNT_ROLE_ARN>"
      },
      "Action": [
        "s3:ReplicateObject",
        "s3:ReplicateDelete"
      ],
      "Resource": "arn:aws:s3:::<DEST_BUCKET>/*"
    },
    {
      "Sid": "AllowBucketLevelChecks",
      "Effect": "Allow",
      "Principal": {
        "AWS": "<SOURCE_ACCOUNT_ROLE_ARN>"
      },
      "Action": [
        "s3:ListBucket",
        "s3:GetBucketVersioning",
        "s3:PutBucketVersioning"
      ],
      "Resource": "arn:aws:s3:::<DEST_BUCKET>"
    }
  ]
}
JSON

aws s3api put-bucket-policy \
  --bucket "<DEST_BUCKET>" \
  --policy file:///tmp/destination-bucket-policy.json
```

## 9) Notes for the AWS-supplied scripts

AWS's supplied Python and Bash scripts automate the same high-level flow:
1. Confirm the source bucket exists.
2. Confirm the destination bucket exists, or create it and enable versioning.
3. Create or reuse an IAM role.
4. Apply the replication configuration to the source bucket.
5. Start the S3 Batch Replication job.

If the customer chooses the scripts instead of the manual CLI path above, use
the same bucket names, regions, and role details, and follow the script README
that AWS provided with the attachments.
