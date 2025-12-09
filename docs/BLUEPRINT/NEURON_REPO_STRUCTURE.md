# Neuron Repository Structure Blueprint

## Overview

This document defines the canonical structure for the Neuron repository, establishing clear organization principles for code, documentation, configuration, and resources. This structure supports the modular architecture of the Neuron Operating System while maintaining clarity and ease of navigation.

## Root Directory Structure

```
Neuron/
├── README.md                           # Project overview and quick start
├── LICENSE                             # Software license
├── .gitignore                          # Git ignore patterns
├── .github/                            # GitHub-specific configurations
├── docs/                               # All documentation
├── src/                                # Source code
├── tests/                              # Test suites
├── scripts/                            # Build and deployment scripts
├── config/                             # Configuration files
├── data/                               # Data files and schemas
├── assets/                             # Static assets
├── tools/                              # Development tools
├── docker/                             # Docker configurations
├── k8s/                                # Kubernetes manifests
├── terraform/                          # Infrastructure as code
└── .env.example                        # Environment variables template
```

## Documentation Structure (`docs/`)

### Primary Documentation Directories

```
docs/
├── README.md                           # Documentation index
├── GETTING_STARTED.md                  # Quick start guide
├── CONTRIBUTING.md                     # Contribution guidelines
├── CHANGELOG.md                        # Version history
├── BLUEPRINT/                          # System architecture and design
├── governance/                         # Governance documents
├── legal/                              # Legal knowledge base
├── api/                                # API documentation
├── user/                               # User guides and manuals
├── developer/                          # Developer documentation
├── operations/                         # Operations and deployment
├── security/                           # Security documentation
├── compliance/                         # Compliance and regulatory
└── assets/                             # Documentation assets
```

### BLUEPRINT Directory (`docs/BLUEPRINT/`)

```
docs/BLUEPRINT/
├── README.md                           # Blueprint overview
├── 01_system_overview.md               # High-level system architecture
├── 02_core_principles.md               # Foundational principles
├── 03_data_architecture.md             # Data models and flow
├── 04_service_architecture.md          # Microservices design
├── 05_user_interface_design.md         # UI/UX architecture
├── 06_integration_patterns.md          # External integrations
├── 07_security_architecture.md         # Security design
├── 08_deployment_architecture.md       # Deployment and infrastructure
├── 09_ai_agents_and_orchestration.md   # AI agent architecture
├── 10_workflow_engine.md               # Business process workflows
├── 11_notification_system.md           # Communication architecture
├── 12_reporting_and_analytics.md       # Analytics and reporting
├── 13_mobile_architecture.md           # Mobile application design
├── 14_performance_and_scalability.md   # Performance requirements
├── 15_disaster_recovery.md             # Business continuity
└── NEURON_REPO_STRUCTURE.md           # This document
```

### Governance Directory (`docs/governance/`)

```
docs/governance/
├── README.md                           # Governance overview
├── NEURON_OS_GOVERNANCE.md             # Main governance constitution
├── ENGINEERING_HANDBOOK.md             # Engineering practices
├── AGENT_HANDBOOK.md                   # AI agent guidelines
├── OPS_HANDBOOK.md                     # Operations procedures
├── AM_COMMANDMENTS.md                  # Immutable system laws
├── CODE_OF_CONDUCT.md                  # Community standards
├── DECISION_MAKING.md                  # Decision processes
├── ROLES_AND_RESPONSIBILITIES.md       # Team roles
└── COMPLIANCE_FRAMEWORK.md             # Regulatory compliance
```

### Legal Knowledge Base (`docs/legal/`)

```
docs/legal/
├── README.md                           # Legal KB overview
├── ircc/                               # IRCC-specific information
│   ├── _README.md                      # IRCC section overview
│   ├── programs/                       # Immigration programs
│   │   ├── _TEMPLATE.md                # Program template
│   │   ├── express_entry.md            # Express Entry details
│   │   ├── provincial_nominee.md       # PNP information
│   │   ├── family_class.md             # Family sponsorship
│   │   ├── business_immigration.md     # Business programs
│   │   └── temporary_residence.md      # Temporary programs
│   ├── regulations/                    # Regulations and policies
│   │   ├── _TEMPLATE.md                # Regulation template
│   │   ├── immigration_refugee_protection_act.md
│   │   ├── immigration_refugee_protection_regulations.md
│   │   └── ministerial_instructions.md
│   ├── forms/                          # Official forms
│   │   ├── _README.md                  # Forms overview
│   │   └── [form_number].md            # Individual form guides
│   ├── fees/                           # Fee schedules
│   │   ├── _README.md                  # Fee overview
│   │   └── current_fees.md             # Current fee schedule
│   ├── processing_times/               # Processing time data
│   │   ├── _README.md                  # Processing times overview
│   │   └── current_times.md            # Current processing times
│   └── changelog/                      # Policy change tracking
│       ├── _TEMPLATE.md                # Change template
│       ├── 2024/                       # Year-based organization
│       └── archive/                    # Historical changes
├── provincial/                         # Provincial programs
│   ├── alberta/                        # Alberta-specific
│   ├── british_columbia/               # BC-specific
│   ├── ontario/                        # Ontario-specific
│   └── [other_provinces]/              # Other provinces
├── case_law/                           # Relevant case law
│   ├── _README.md                      # Case law overview
│   ├── federal_court/                  # Federal Court decisions
│   ├── immigration_appeal_division/    # IAD decisions
│   └── immigration_refugee_board/      # IRB decisions
└── templates/                          # Legal document templates
    ├── _README.md                      # Templates overview
    ├── letters/                        # Letter templates
    ├── forms/                          # Form templates
    └── agreements/                     # Agreement templates
```

## Source Code Structure (`src/`)

### Application Architecture

```
src/
├── README.md                           # Source code overview
├── api/                                # API layer
│   ├── controllers/                    # Request handlers
│   ├── middleware/                     # Express middleware
│   ├── routes/                         # Route definitions
│   ├── validators/                     # Input validation
│   └── swagger/                        # API documentation
├── services/                           # Business logic layer
│   ├── immigration/                    # Immigration-specific services
│   ├── case-management/                # Case management services
│   ├── document/                       # Document processing
│   ├── notification/                   # Notification services
│   ├── user/                           # User management
│   ├── billing/                        # Billing and payments
│   └── reporting/                      # Analytics and reporting
├── data/                               # Data access layer
│   ├── models/                         # Database models
│   ├── repositories/                   # Data repositories
│   ├── migrations/                     # Database migrations
│   ├── seeds/                          # Database seeds
│   └── schemas/                        # Data validation schemas
├── ai/                                 # AI and ML components
│   ├── agents/                         # AI agents
│   ├── models/                         # ML models
│   ├── training/                       # Training scripts
│   └── inference/                      # Inference engines
├── web/                                # Web application
│   ├── components/                     # React components
│   ├── pages/                          # Page components
│   ├── hooks/                          # Custom hooks
│   ├── contexts/                       # React contexts
│   ├── utils/                          # Utility functions
│   ├── styles/                         # CSS and styling
│   └── assets/                         # Web assets
├── mobile/                             # Mobile application
│   ├── screens/                        # Mobile screens
│   ├── components/                     # Mobile components
│   ├── navigation/                     # Navigation setup
│   └── utils/                          # Mobile utilities
├── shared/                             # Shared utilities
│   ├── types/                          # TypeScript types
│   ├── constants/                      # Application constants
│   ├── utils/                          # Utility functions
│   ├── validators/                     # Validation functions
│   └── errors/                         # Error definitions
├── integrations/                       # External integrations
│   ├── ircc/                           # IRCC API integration
│   ├── payment/                        # Payment processors
│   ├── email/                          # Email services
│   ├── sms/                            # SMS services
│   └── storage/                        # Cloud storage
└── workers/                            # Background workers
    ├── email/                          # Email workers
    ├── document/                       # Document processing
    ├── notification/                   # Notification workers
    └── sync/                           # Data synchronization
```

## Test Structure (`tests/`)

```
tests/
├── README.md                           # Testing overview
├── unit/                               # Unit tests
│   ├── services/                       # Service layer tests
│   ├── data/                           # Data layer tests
│   ├── utils/                          # Utility tests
│   └── ai/                             # AI component tests
├── integration/                        # Integration tests
│   ├── api/                            # API integration tests
│   ├── database/                       # Database tests
│   └── external/                       # External service tests
├── e2e/                                # End-to-end tests
│   ├── web/                            # Web application tests
│   ├── mobile/                         # Mobile application tests
│   └── api/                            # API workflow tests
├── performance/                        # Performance tests
│   ├── load/                           # Load testing
│   ├── stress/                         # Stress testing
│   └── benchmarks/                     # Performance benchmarks
├── security/                           # Security tests
│   ├── authentication/                 # Auth tests
│   ├── authorization/                  # Access control tests
│   └── vulnerability/                  # Security scanning
├── fixtures/                           # Test data
│   ├── users/                          # User test data
│   ├── cases/                          # Case test data
│   └── documents/                      # Document test data
└── helpers/                            # Test utilities
    ├── setup/                          # Test setup
    ├── mocks/                          # Mock objects
    └── factories/                      # Data factories
```

## Configuration Structure (`config/`)

```
config/
├── README.md                           # Configuration overview
├── environments/                       # Environment-specific configs
│   ├── development.yml                 # Development configuration
│   ├── staging.yml                     # Staging configuration
│   ├── production.yml                  # Production configuration
│   └── test.yml                        # Test configuration
├── database/                           # Database configurations
│   ├── postgres.yml                    # PostgreSQL config
│   ├── redis.yml                       # Redis config
│   └── elasticsearch.yml               # Elasticsearch config
├── services/                           # Service configurations
│   ├── api.yml                         # API service config
│   ├── workers.yml                     # Worker configurations
│   └── ai.yml                          # AI service config
├── integrations/                       # Integration configurations
│   ├── ircc.yml                        # IRCC integration
│   ├── payment.yml                     # Payment services
│   └── email.yml                       # Email services
├── security/                           # Security configurations
│   ├── auth.yml                        # Authentication config
│   ├── encryption.yml                  # Encryption settings
│   └── cors.yml                        # CORS configuration
└── monitoring/                         # Monitoring configurations
    ├── logging.yml                     # Logging configuration
    ├── metrics.yml                     # Metrics collection
    └── alerts.yml                      # Alert configurations
```

## Scripts Directory (`scripts/`)

```
scripts/
├── README.md                           # Scripts overview
├── build/                              # Build scripts
│   ├── build.sh                        # Main build script
│   ├── docker-build.sh                 # Docker build
│   └── assets.sh                       # Asset compilation
├── deploy/                             # Deployment scripts
│   ├── deploy.sh                       # Main deployment
│   ├── rollback.sh                     # Rollback script
│   └── health-check.sh                 # Health verification
├── database/                           # Database scripts
│   ├── migrate.sh                      # Run migrations
│   ├── seed.sh                         # Seed database
│   ├── backup.sh                       # Database backup
│   └── restore.sh                      # Database restore
├── development/                        # Development scripts
│   ├── setup.sh                        # Development setup
│   ├── start.sh                        # Start development
│   └── reset.sh                        # Reset environment
├── testing/                            # Testing scripts
│   ├── test.sh                         # Run all tests
│   ├── coverage.sh                     # Generate coverage
│   └── e2e.sh                          # End-to-end tests
└── maintenance/                        # Maintenance scripts
    ├── cleanup.sh                      # Cleanup tasks
    ├── update.sh                       # Update dependencies
    └── security-scan.sh                # Security scanning
```

## Infrastructure Structure

### Docker Configuration (`docker/`)

```
docker/
├── README.md                           # Docker overview
├── Dockerfile                          # Main application image
├── Dockerfile.dev                      # Development image
├── docker-compose.yml                  # Local development
├── docker-compose.prod.yml             # Production setup
├── services/                           # Service-specific Dockerfiles
│   ├── api/                            # API service
│   ├── workers/                        # Worker services
│   ├── web/                            # Web application
│   └── ai/                             # AI services
└── scripts/                            # Docker scripts
    ├── build.sh                        # Build images
    ├── push.sh                         # Push to registry
    └── cleanup.sh                      # Cleanup images
```

### Kubernetes Configuration (`k8s/`)

```
k8s/
├── README.md                           # Kubernetes overview
├── namespaces/                         # Namespace definitions
├── deployments/                        # Deployment manifests
├── services/                           # Service definitions
├── ingress/                            # Ingress configurations
├── configmaps/                         # Configuration maps
├── secrets/                            # Secret templates
├── persistent-volumes/                 # Storage definitions
├── monitoring/                         # Monitoring setup
└── scripts/                            # Kubernetes scripts
    ├── deploy.sh                       # Deploy to cluster
    ├── rollback.sh                     # Rollback deployment
    └── status.sh                       # Check status
```

### Terraform Configuration (`terraform/`)

```
terraform/
├── README.md                           # Terraform overview
├── environments/                       # Environment-specific
│   ├── development/                    # Dev infrastructure
│   ├── staging/                        # Staging infrastructure
│   └── production/                     # Prod infrastructure
├── modules/                            # Reusable modules
│   ├── database/                       # Database module
│   ├── networking/                     # Network module
│   ├── security/                       # Security module
│   └── monitoring/                     # Monitoring module
├── variables/                          # Variable definitions
└── scripts/                            # Terraform scripts
    ├── plan.sh                         # Plan changes
    ├── apply.sh                        # Apply changes
    └── destroy.sh                      # Destroy resources
```

## File Naming Conventions

### General Principles
- Use lowercase with hyphens for directories: `case-management/`
- Use PascalCase for React components: `CaseDetails.tsx`
- Use camelCase for JavaScript/TypeScript files: `userService.ts`
- Use snake_case for database-related files: `user_profiles.sql`
- Use UPPERCASE for constants and environment files: `README.md`, `.ENV`

### Specific Patterns
- **Components**: `ComponentName.tsx` + `ComponentName.test.tsx`
- **Services**: `serviceName.ts` + `serviceName.test.ts`
- **Models**: `ModelName.ts` (singular, PascalCase)
- **Routes**: `routeName.ts` (camelCase)
- **Migrations**: `YYYY_MM_DD_HHMMSS_migration_name.sql`
- **Documentation**: `DOCUMENT_NAME.md` (UPPERCASE with underscores)

## Branch Structure

### Main Branches
- `main`: Production-ready code
- `develop`: Integration branch for features
- `staging`: Pre-production testing

### Feature Branches
- `feature/feature-name`: New features
- `bugfix/bug-description`: Bug fixes
- `hotfix/critical-fix`: Critical production fixes
- `docs/documentation-update`: Documentation changes
- `refactor/component-name`: Code refactoring

### Release Branches
- `release/v1.2.3`: Release preparation
- `support/v1.x`: Long-term support branches

## Version Control Guidelines

### Commit Message Format
```
type(scope): subject

body

footer
```

**Types**: feat, fix, docs, style, refactor, test, chore
**Scope**: component, service, or area affected
**Subject**: Brief description (50 chars max)

### Tag Format
- **Releases**: `v1.2.3` (semantic versioning)
- **Pre-releases**: `v1.2.3-alpha.1`, `v1.2.3-beta.2`
- **Hotfixes**: `v1.2.3-hotfix.1`

## Maintenance and Evolution

### Regular Reviews
- **Monthly**: Review and update documentation structure
- **Quarterly**: Assess and refactor code organization
- **Annually**: Major structure review and optimization

### Structure Changes
- All structural changes require RFC (Request for Comments)
- Breaking changes require migration guides
- Deprecation notices for removed structures
- Version control for structure documentation

### Compliance Monitoring
- Automated checks for structure compliance
- Regular audits of file organization
- Metrics on structure adherence
- Training on structure guidelines

---

**Document Control:**
- Version: 1.0
- Last Updated: [Current Date]
- Owner: Architecture Team
- Review Cycle: Quarterly

**Related Documents:**
- [System Overview](./01_system_overview.md)
- [Engineering Handbook](../governance/ENGINEERING_HANDBOOK.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
- [Development Setup](../developer/SETUP.md)