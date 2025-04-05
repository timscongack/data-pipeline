# Data Pipeline Project

## Overview
This project implements a high-performance data pipeline for processing and storing event data using Apache Iceberg tables. The pipeline consists of a mock data generator and a Lambda-based processor that handles event ingestion and storage.

## Architecture

### Components
1. **Mock Data Generator**
   - Generates realistic event data with various attributes
   - Supports high-throughput event generation
   - Includes session, user agent, location, and engagement metrics

2. **Lambda Processor**
   - Processes incoming events in real-time
   - Flattens nested event structures
   - Optimized for high throughput (100+ events/second)
   - Uses Apache Iceberg for efficient data storage

3. **Storage Layer**
   - Apache Iceberg tables for efficient data management
   - Supports schema evolution and time travel
   - Optimized for analytical queries
   - Partitioned by event date for efficient querying

## Key Design Decisions

### 1. Storage Choice: Apache Iceberg
- **Why Iceberg?**
  - Schema evolution support
  - Time travel capabilities
  - Efficient partitioning and compaction
  - Better query performance for analytics
  - ACID transactions
  - Reduced storage costs compared to raw S3

### 2. Performance Optimizations
- **Event Processing**
  - Concurrent processing with ThreadPoolExecutor
  - Memory-efficient data structures
  - Batch processing capabilities
  - Compression for reduced storage footprint

- **Storage Optimizations**
  - Partitioning by event date
  - Automatic compaction
  - Columnar storage format
  - Efficient metadata management

### 3. Data Model
- **Event Structure**
  - Flattened schema for efficient querying
  - Nested data preserved in _doc field
  - Standardized event types
  - Rich metadata for analytics

## Implementation Notes

### Performance Requirements
- Process 100+ events per second
- Support concurrent processing
- Memory efficient (max 50MB per 100 events)
- Compression ratio of at least 2:1

### Testing Strategy
- Unit tests for all components
- Performance benchmarks
- Memory usage monitoring
- Compression ratio validation
- Concurrent processing tests

## Setup Instructions

### Prerequisites
- Python 3.9+
- Docker
- Localstack
- AWS CLI configured for Localstack

### Environment Setup
1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Localstack Setup
1. Start Localstack:
   ```bash
   docker-compose -f docker/localstack/docker-compose.yml up -d
   ```

2. Verify Localstack:
   ```bash
   aws --endpoint-url=http://localhost:4566 s3 ls
   ```

### Iceberg Setup
1. Create Iceberg catalog:
   ```bash
   aws --endpoint-url=http://localhost:4566 glue create-database --database-name events_db
   ```

2. Initialize Iceberg tables:
   ```bash
   python scripts/init_iceberg_tables.py
   ```

## Running the Pipeline

### Start Mock Generator
```bash
python apps/mock_generator/main.py
```

### Monitor Processing
```bash
python scripts/monitor_processing.py
```

## Development

### Testing
```bash
python -m pytest
```

## Performance Monitoring

### Metrics
- Events processed per second
- Memory usage
- Compression ratios
- Processing latency

### Monitoring Tools
- Localstack CloudWatch metrics
- Custom performance dashboards
- Iceberg table statistics

## Troubleshooting

### Common Issues
1. Localstack not starting
   - Check Docker status
   - Verify port availability
   - Check Localstack logs

2. Iceberg table issues
   - Verify catalog configuration
   - Check table metadata
   - Monitor compaction status

3. Performance issues
   - Check memory usage
   - Monitor concurrent processing
   - Verify compression ratios

## Future Improvements
1. Implement CDC (Change Data Capture)
2. Add real-time analytics capabilities
3. Enhance monitoring and alerting
4. Implement data quality checks
5. Add support for more event types

# Data Pipeline Project

A comprehensive data pipeline solution using AWS services (emulated with Localstack), Terraform, and Python.

## Project Structure

```
.
├── README.md
├── infrastructure/          # Terraform and Terragrunt configurations
│   ├── modules/             # Reusable Terraform modules
│   │   ├── networking/      # VPC, subnets, routing tables
│   │   ├── storage/         # S3 buckets
│   │   └── compute/         # Lambda functions
│   └── environments/        # Environment-specific configurations
│       ├── dev/             # Development environment
│       └── prod/            # Production environment
├── apps/                    # Python applications
│   ├── mock-generator/      # Mock API data generator
│   └── lambda/              # Lambda function code
├── docker/                  # Docker-related files
│   ├── localstack/          # Localstack configuration
│   └── apps/                # Application Dockerfiles
└── scripts/                 # Utility and transformation scripts
    └── data/                # Data transformation scripts
```

## Prerequisites

- Python 3.9+
- Docker and Docker Compose
- Terraform 1.0+
- Terragrunt
- AWS CLI (for local development)
- Localstack

## Getting Started

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd data-pipeline
   ```

2. Set up Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start Localstack:
   ```bash
   docker-compose -f docker/localstack/docker-compose.yml up -d
   ```

4. Initialize Terraform:
   ```bash
   cd infrastructure/environments/dev
   terragrunt init
   ```

## Development Workflow

1. **Infrastructure Development**
   - Create/modify Terraform modules in `infrastructure/modules/`
   - Update environment configurations in `infrastructure/environments/`

2. **Application Development**
   - Develop mock data generator in `apps/mock-generator/`
   - Implement Lambda functions in `apps/lambda/`

3. **Testing**
   - Run unit tests: `python -m pytest`
   - Test infrastructure changes: `terragrunt plan`
   - Test end-to-end flow with Localstack

## Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## License

[Add your license information here]

# Local Data Pipeline Project Guide

This guide outlines a comprehensive 5-month roadmap for building a local data pipeline project. The project will emulate AWS resources (using Localstack) including network resources (VPCs, subnets, routing), ingest mock API events via a Python Lambda function, and process data through layered storage (raw in PostgreSQL, silver for transformed data, and gold in DuckDB for analytics). The system will be containerized using Docker/Docker Compose, include CI/CD for automated deployments, support multi-developer collaboration, and integrate a lightweight dashboarding tool (such as [Streamlit](https://streamlit.io)) for analytics visualization.

---

## Project Components

- **Data Ingestion:**
  - **Python Lambda Function:** Simulated locally (via Localstack) to receive API events and write data in Parquet format to an S3 bucket.
  - **Mock API Data Generator:** A Python application that generates mock API events to test and simulate the data flow.

- **Storage & Processing Layers:**
  - **Raw Layer:** PostgreSQL database that ingests Parquet files from the S3 bucket.
  - **Silver Layer:** Transformation scripts to unflatten and normalize the raw data into structured, cleaned tables.
  - **Gold Layer:** A DuckDB instance connecting to PostgreSQL to execute analytical queries and generate summary reports.

- **Infrastructure:**
  - **AWS Resource Emulation:** Use Localstack to simulate AWS services (S3, Lambda).
  - **Networking:** Provision VPCs, subnets, and related network resources using Terraform/Terragrunt.
  - **Containerization:** Docker and Docker Compose will be used to run Localstack, PostgreSQL, DuckDB, the Lambda function, and additional processing scripts.
  - **CI/CD:** Implement a CI/CD pipeline (e.g., GitHub Actions, Jenkins) for automated testing, deployment, and multi-developer collaboration.
  - **Permissions & Multi-Developer Support:** Configure database roles and network permissions to allow secure, collaborative development.

- **Dashboarding:**
  - **Dashboard Tool:** Use a lightweight and codable tool like [Streamlit](https://streamlit.io) to build interactive dashboards for analytics.

---

## Detailed Timeline

### **Month 1: Environment Setup & Infrastructure Provisioning**
- **Week 1: Project Initialization**
  - Initialize a monorepo with Git and define the project directory structure for Terraform, Python apps, Dockerfiles, and transformation scripts.
  
- **Week 2: Local AWS Emulation & Networking**
  - Install and configure Localstack to emulate AWS services (S3, Lambda).
  - Set up Terraform modules to provision network resources: VPCs, subnets, and routing tables.
  - Start building Terragrunt configurations to manage environments and infrastructure as code.

- **Week 3: Infrastructure Deployment**
  - Deploy network resources (VPC, subnets) and AWS resources (S3 bucket, Lambda function) using Terraform/Terragrunt.
  - Validate network connectivity and resource accessibility within Localstack.

- **Week 4: Mock API Data Generator & Lambda Prototype**
  - Develop a Python application to generate and send mock API events.
  - Create a prototype Python Lambda function that processes API events and writes Parquet files to S3.
  - Test the end-to-end data ingestion process locally.

### **Month 2: Building the Core Data Pipeline**
- **Week 5: Enhance Data Ingestion**
  - Refine the Python Lambda to handle realistic event payloads and ensure proper serialization to Parquet.
  - Verify that data is correctly written to the emulated S3 bucket.

- **Week 6: Raw Layer Setup**
  - Deploy a PostgreSQL container.
  - Develop scripts to ingest Parquet files from S3 into PostgreSQL, creating a raw data table that mirrors the initial Prisma schema.

- **Week 7: Data Transformation to Silver Layer**
  - Build transformation scripts to unflatten and normalize the raw data into structured silver tables.
  - Implement transformation logic and test for data integrity.

- **Week 8: Automation & Testing for the Silver Layer**
  - Automate the silver layer transformation process.
  - Develop tests to validate the accuracy and consistency of the transformed data.

### **Month 3: Analytics, Integration, & CI/CD Initiation**
- **Week 9: Gold Layer Implementation with DuckDB**
  - Deploy a DuckDB instance in a container.
  - Set up connections between DuckDB and PostgreSQL.
  - Write initial analytical queries to aggregate data from the silver layer.

- **Week 10: Develop Analytical Queries**
  - Expand the suite of analytical queries for generating summary metrics and reports.
  - Optimize query performance and validate results against the gold layer.

- **Week 11: Docker Integration & Orchestration**
  - Integrate all components (Localstack, PostgreSQL, DuckDB, Lambda function, and transformation scripts) using Docker Compose.
  - Conduct end-to-end integration tests to ensure seamless data flow and connectivity.

- **Week 12: CI/CD Pipeline Setup**
  - Implement a CI/CD workflow (using GitHub Actions, Jenkins, etc.) for automated testing, deployment, and infrastructure provisioning.
  - Document the CI/CD process and integrate automated tests into the pipeline.

### **Month 4: Dashboarding, Permissions, & Multi-Developer Support**
- **Week 13: Dashboard Implementation**
  - Integrate [Streamlit](https://streamlit.io) as the dashboarding tool.
  - Develop initial interactive dashboards to visualize key analytics and summary data from DuckDB.

- **Week 14: Database Permissions & Virtualization**
  - Configure fine-grained database permissions and roles to support multiple developers.
  - Virtualize the entire project within a dedicated VPC to enhance network isolation and security.

- **Week 15: Enhanced CI/CD & Collaboration Tools**
  - Expand the CI/CD pipeline to include multi-developer workflows, ensuring smooth collaboration and deployment.
  - Incorporate automated testing for permissions and security compliance.

- **Week 16: Final Integration & Documentation**
  - Finalize integration of the dashboard, permissions, and CI/CD systems.
  - Update documentation to reflect new components and workflows, ensuring clear instructions for onboarding new developers.

### **Month 5: Expanding Data Sources & Final Optimization**
- **Week 17: CDC (Change Data Capture) Source Integration**
  - Research and select a CDC tool or library to capture changes from a data source.
  - Develop a connector to ingest CDC data into the PostgreSQL raw layer.

- **Week 18: Kinesis Source Integration**
  - Simulate or emulate a Kinesis stream locally.
  - Implement integration logic to ingest data from the Kinesis-like source into the pipeline.

- **Week 19: Unified Data Transformation**
  - Extend transformation scripts to handle data from multiple sources (API, CDC, Kinesis).
  - Ensure data consistency and integrity across all sources during the transformation process.

- **Week 20: Final Testing, Optimization & Deployment**
  - Conduct comprehensive end-to-end testing of the entire data pipeline.
  - Optimize system performance, resource utilization, and security.
  - Finalize the deployment process and document best practices for future scaling and multi-developer contributions.

---

## Architecture Diagram

<img width="760" alt="image" src="https://github.com/user-attachments/assets/17a4e790-f844-4efa-95fc-c07de9f5cc03" />

