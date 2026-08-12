## Project structure

The project follows a feature-based structure, as an in-between option between flat-based folder structure and DDD.
Examples:

- Flat folder structure: https://oneuptime.com/blog/post/2026-01-26-fastapi-production-ready/view#project-structure
- DDD: Not sure
- Feature-based: https://github.com/benavlabs/FastAPI-boilerplate/tree/main/backend/src (closest)

This architecture combines the best from hexagonal architecture and ... fill

> Your architecture is a Pragmatic Modular Monolith with Vertical Slice (Feature-Driven) Design, incorporating a light Hexagonal (Ports & Adapters) separation for external infrastructure.

```python
backend/
├── alembic/                          # Database migration scripts
│   ├── env.py                        # Imports Base from src.infrastructure.postgres.base
│   └── versions/
│
├── docker/                           # Container configs & deployment scripts
│   ├── Dockerfile                    # Production multi-stage build
│   ├── Dockerfile.dev                # Development build with hot-reload
│   └── docker-compose.yml            # Local orchestration (API, Postgres, Redis, Qdrant)
│
├── src/
│   ├── __init__.py
│   ├── main.py                       # App factory, middleware, CORS, lifespan events
│   ├── config.py                     # Global settings & env vars (pydantic-settings)
│   ├── dependencies.py               # Global dependencies & type aliases (SessionDep, CurrentUserDep)
│   │
│   ├── api/                          # ROUTING & API VERSIONING LAYER
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py             # GET /api/v1/health liveness probe
│   │       └── router.py             # Central aggregator for all v1 module routers
│   │
│   ├── core/                         # CROSS-CUTTING SYSTEM LOGIC (NO HARD EXTERNAL IO)
│   │   ├── __init__.py
│   │   ├── security.py               # Password hashing & JWT token validation/generation
│   │   ├── exceptions.py             # Custom exception classes & global handlers
│   │   ├── middleware.py             # Custom request logging, timing, security headers
│   │   └── rate_limit.py             # Rate-limiting middleware/dependency logic
│   │
│   ├── infrastructure/               # OUTBOUND EXTERNAL SYSTEM DRIVERS & CLIENTS
│   │   ├── __init__.py
│   │   ├── postgres/                 # Relational database driver
│   │   │   ├── __init__.py
│   │   │   ├── session.py            # Async engine, session factory, & get_db dependency
│   │   │   └── base.py               # Base SQLAlchemy Declarative Model & model registry
│   │   ├── qdrant/                   # Vector database driver
│   │   │   ├── __init__.py
│   │   │   └── client.py             # QdrantClient instance & connection lifecycle
│   │   ├── redis/                    # Caching & rate-limiting storage
│   │   │   ├── __init__.py
│   │   │   └── client.py             # Redis connection pool & client wrapper
│   │   └── storage/                  # Object storage driver
│   │       ├── __init__.py
│   │       └── s3.py                 # Boto3 / MinIO client wrapper
│   │
│   └── modules/                      # FEATURE / DOMAIN MODULES
│       ├── __init__.py
│       ├── auth/                     # Feature module: Authentication
│       │   ├── __init__.py
│       │   ├── router.py             # Endpoints relative to /auth
│       │   ├── schemas.py            # Login, token, password reset schemas
│       │   └── service.py            # Authentication business logic
│       │
│       ├── users/                    # Feature module: User management
│       │   ├── __init__.py
│       │   ├── router.py             # Endpoints relative to /users
│       │   ├── schemas.py            # User request/response Pydantic models
│       │   ├── models.py             # User SQLAlchemy ORM models
│       │   ├── service.py            # User CRUD & business logic
│       │   ├── dependencies.py       # Domain dependencies (e.g., get_user_or_404)
│       │   └── exceptions.py         # User-specific domain exceptions
│       │
│       ├── billing/                  # Feature module: Payments & Subscriptions
│       │   ├── __init__.py
│       │   ├── router.py             # Endpoints relative to /billing
│       │   ├── schemas.py            # Invoice & subscription schemas
│       │   ├── models.py             # Billing SQLAlchemy ORM models
│       │   ├── service.py            # Payment processor integrations & logic
│       │   └── dependencies.py       # Billing-specific dependencies
│       │
│       └── search/                   # Feature module: Vector & Semantic Search
│           ├── __init__.py
│           ├── router.py             # Endpoints relative to /search
│           ├── schemas.py            # Search request & vector query schemas
│           └── service.py            # Search logic (calls infrastructure.qdrant.client)
│
├── tests/                            # Parallels src structure
│   ├── __init__.py
│   ├── conftest.py                   # Global fixtures (async client, test database)
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
│
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

The Three Pillars of This Architecture:

1. Vertical Slice Architecture (src/modules/)
   Instead of slicing code horizontally across the entire app by file type (e.g., all models together, all routers together), you slice vertically by business domain. Everything needed to understand, run, or delete the users feature lives inside src/modules/users/.

2. Modular Monolith Boundaries
   The application deploys as a single unit, but the features maintain strict boundary discipline. Modules don't reach into each other's ORM models directly; they communicate through service functions (UserService) or domain events. This makes it trivial to extract any single module (like billing or search) into its own independent microservice in the future if scale requires it.

3. Pragmatic Infrastructure Isolation (src/infrastructure/)
   This is where the Hexagonal influence lives. By isolating external I/O drivers (Postgres, Redis connection pools, Qdrant vector clients, S3 storage) into src/infrastructure/, your business modules inside src/modules/ remain clean and focused purely on domain logic rather than socket management or connection pooling.

If someone asks what architecture you're using on this project, you can describe it as:

"A Feature-Driven Modular Monolith. We isolate external I/O like Postgres, Redis, and Qdrant in infrastructure/, but inside modules/ we use vertical slices so each domain owns its own routers, schemas, models, and logic."
