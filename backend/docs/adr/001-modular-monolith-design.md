# 1. Modular Monolith vs Microservices

**Date:** 2026-09-17
**Status:** Accepted

## Context

We need to structure the FastAPI backend to support multiple ETL pipelines (Ingestion, Vectorization) and standard REST endpoints without turning into a distributed ball of mud.

## Decision

We will adopt a Modular Monolith architecture based on Hexagonal/Vertical Slice principles. Each feature domain will live in its own module inside `src/modules/`. Modules will not share database models directly unless explicitly exposed via a DTO contract.

## Consequences

- **Positive:** Strict boundaries prevent spaghetti code. The system is easily deployable as a single Docker container.
- **Negative:** Slightly more boilerplate per feature (explicit imports, schemas).
