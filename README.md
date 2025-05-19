## SonarCloud Analysis

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=Kelompok-5-PPL-A_MAAMS-NG-BE&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=Kelompok-5-PPL-A_MAAMS-NG-BE)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=Kelompok-5-PPL-A_MAAMS-NG-BE&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=Kelompok-5-PPL-A_MAAMS-NG-BE)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=Kelompok-5-PPL-A_MAAMS-NG-BE&metric=coverage)](https://sonarcloud.io/summary/new_code?id=Kelompok-5-PPL-A_MAAMS-NG-BE)


## Codecov

[![codecov](https://codecov.io/gh/Kelompok-5-PPL-A/MAAMS-NG-BE/branch/ci-cd/graph/badge.svg?token=55GK61BZGJ)](https://codecov.io/gh/Kelompok-5-PPL-A/MAAMS-NG-BE)

## MAAMS-NG

**Kelompok-5 PPL A**

## Members

1. Muhammad Hilal Darul Fauzan - 2206830542
2. Ryandhika Al Afzal - 2206081502 
3. Fikri Dhiya Ramadhana - 2206819533
4. Steven Faustin Orginata - 2206030855
5. Arya Lesmana - 2206081603
6. Ariana Nurlayla Syabandini - 2206081950
7. Lidwina Eurora Firsta Nobella - 2206083615

# MAAMS-NG Backend

## Deployment & Environment Management

### Versioning
This project uses semantic versioning (v{major}.{minor}.{patch}) managed through python-semantic-release. The versioning follows these rules:
- Major version: Breaking changes
- Minor version: New features
- Patch version: Bug fixes

### Deployment Process
The application is deployed to Google Cloud Run using a CI/CD pipeline. The deployment process includes:
1. Building a multi-stage Docker image
2. Running tests
3. Semantic versioning
4. Deployment to staging/production environment
5. Monitoring and health checks

Deployments are limited to specific branches:
- `staging` branch: Deploys to staging environment
- `main` branch: Deploys to production environment

### Manual Data Operations
The project includes a manual data operations workflow that can be triggered from GitHub Actions. This workflow supports:
- Database migrations
- Migration rollbacks
- Data seeding
- Seeding rollbacks

To trigger manual data operations:
1. Go to GitHub Actions
2. Select "Manual Data Operations"
3. Choose the target environment (staging/production)
4. Choose the operation type
5. Select the target table (for seeding operations)
6. Run the workflow

### Rollback Process

### Manual Rollback

The application supports manual rollback through a dedicated GitHub Actions workflow. This process allows you to rollback both the application and database to a previous state.

#### Prerequisites

1. Access to GitHub Actions
2. Google Cloud Run permissions
3. Database migration history

#### Steps to Perform Manual Rollback

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Manual Rollback" workflow
3. Click "Run workflow"
4. Fill in the required information:
   - **Environment**: Choose between staging or production
   - **Revision Name**: Specify the Cloud Run revision to rollback to
   - **Migration Name**: (Optional) Specify the migration to rollback the database to

#### What Happens During Rollback

1. **Application Rollback**:
   - Verifies the existence of the specified revision
   - Updates traffic to point to the specified revision
   - Maintains service availability during rollback

2. **Database Rollback** (if migration name provided):
   - Rolls back database migrations to the specified point
   - Uses Django's migration system for safe rollback
   - Maintains data integrity

3. **Metadata Tracking**:
   - Records rollback details including:
     - Timestamp
     - User who performed the rollback
     - Environment
     - Revision name
     - Migration name
   - Stores metadata as an artifact for 30 days

#### Best Practices

1. Always verify the revision exists before attempting rollback
2. Test rollback procedures in staging before production
3. Keep track of database migrations and their dependencies
4. Document any manual database changes that might affect rollback
5. Consider the impact on connected services and APIs

### Autoscaling
Google Cloud Run provides automatic scaling with these features:
- Request-based scaling
- CPU utilization-based scaling
- Memory usage-based scaling
- Concurrent request handling
- Cold start optimization

Current configuration:
- Min instances: 2
- Max instances: 20
- CPU throttling: Enabled
- CPU boost: Enabled
- Target concurrency: 80

To modify autoscaling settings:
```bash
gcloud run services update maams-ng-staging \
  --min-instances=2 \
  --max-instances=20 \
  --cpu-throttling \
  --cpu-boost \
  --execution-environment gen2 \
  --platform managed \
  --region asia-southeast1
```

### Monitoring
Google Cloud Run integrates with Cloud Monitoring to provide:
- Request metrics (latency, count, errors)
- Resource metrics (CPU, memory)
- Instance metrics (count, startup time)
- Custom metrics support
- Logging integration
- Alerting capabilities

To view metrics:
1. Go to Google Cloud Console
2. Navigate to Cloud Run
3. Select the service
4. Click on "Monitoring"

### Security
- Private network isolation through VPC
- Container sandboxing
- Automatic TLS encryption
- IAM authentication
- Secret management
- Network policies

### Best Practices
1. Multi-stage builds to minimize image size
2. Layer optimization in Dockerfile
3. Health checks for container readiness
4. Resource limits and requests
5. Automatic rollback on failed deployments
6. Regular security scanning
7. Automated testing before deployment