resource "aws_s3_bucket" "iceberg_data" {
  bucket = var.bucket_name
  
  # Enable versioning for Iceberg metadata
  versioning {
    enabled = true
  }

  # Enable server-side encryption
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  # Lifecycle rules for Iceberg metadata
  lifecycle_rule {
    id      = "iceberg-metadata"
    enabled = true

    prefix = "metadata/"
    
    expiration {
      days = 90
    }
  }

  # Lifecycle rules for data files
  lifecycle_rule {
    id      = "iceberg-data"
    enabled = true

    prefix = "data/"
    
    expiration {
      days = 365
    }
  }

  tags = {
    Name        = var.bucket_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "iceberg_data" {
  bucket = aws_s3_bucket.iceberg_data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "iceberg_data" {
  bucket = aws_s3_bucket.iceberg_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "iceberg_data" {
  bucket = aws_s3_bucket.iceberg_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "iceberg_data" {
  bucket = aws_s3_bucket.iceberg_data.id

  rule {
    id     = "cleanup-old-versions"
    status = "Enabled"

    filter {
      prefix = ""
    }

    noncurrent_version_expiration {
      noncurrent_days = 30
    }
  }
}

# IAM policy for Iceberg access
resource "aws_iam_policy" "iceberg_access" {
  name        = "iceberg-access-${var.environment}"
  description = "Policy for Iceberg table access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket",
          "s3:GetBucketLocation"
        ]
        Resource = [
          aws_s3_bucket.iceberg_data.arn,
          "${aws_s3_bucket.iceberg_data.arn}/*"
        ]
      }
    ]
  })
} 