# Backend Architecture

## 1. Introduction: Escaping the Big Ball of Mud

The good thing about working on FastAPI projects is that you can run a simple command like `uv add fastapi`, write a few routes, and get a server running in minutes.

The bad thing is that almost immediately after, you are left entirely to your own devices to figure out how to structure the project. You need a backend that enforces:

- **High Cohesion & Colocation:** Features that change together should live together, allowing for rapid iterations without constant context switching.
- **Low Coupling:** Modules must remain strictly independent so a change in one domain doesn't trigger a cascade of bugs in another.
- **Dependency Inversion:** Core business rules must be entirely isolated from external I/O, databases, or frameworks.
- **Boundary Enforcement:** The architecture must physically prevent developers from taking shortcuts that degrade the codebase into a tangled mess over time.

This document embarks on the journey of overseeing current architectural patterns, breaking down their trade-offs, and establishing a clear, defensible path forward in order to achieve these goals.

If you are staring at an empty repository—or a rapidly tangling one—then this guide is for you. By the end of this document, you will be able to:

1. Understand core architecture types, internal design patterns, and their respective trade-offs.
2. Confidently make and defend architectural decisions with strong arguments.
3. Visually see how these abstract concepts map to a real, production-ready directory structure.

### 1.1 Our Goal

Throughout this guide, I will not only walk you through what I believe are the core concepts of software architecture and design, but also explain and defend my choices along the way.

This application's architecture is built as a **Feature-Driven Modular Monolith**. It utilizes **Vertical Slice Architecture (VSA)** to organize business features, while applying a lightweight **Hexagonal (Ports & Adapters) pattern** to isolate external infrastructure.

If you have no idea what that means, then you are in the right place. If you do know what it means but are unsure about why I chose it, then you are in the right place as well.

The goal of this document is to:

1. Explain the core architectural problems we are solving.
2. Compare the trade-offs of common architectural patterns.
3. Detail how a Modular Monolith provides the optimal balance of speed and scalability.
4. Define the strict boundaries required to prevent the codebase from deteriorating.

### 1.2 Architecture Philosophy

<Image src="image_agent_tag_9558555793354571007" alt="A dense, unreadable graph of interconnected dependencies representing a Big Ball of Mud architecture" caption="The Big Ball of Mud Anti-Pattern" />

What we fundamentally want to solve is the natural tendency of codebases to devolve into a "Big Ball of Mud"—a haphazardly structured, sprawling, sloppy, spaghetti-code jungle where everything depends on everything else.

To prevent this, our architectural philosophy is built on balancing two fundamental, often competing forces:

- **High Cohesion:** Code that changes together should live together. If you are modifying how a user profile is updated, you should not have to hunt across five different directories to find the route, the schema, the database model, and the business logic.
- **Low Coupling:** Sometimes referred to alongside **Dependency Inversion**, this states that modules should be strictly independent. High-level modules (your business logic) should not depend on low-level modules (your database or framework), but rather on abstractions. A change in the "Billing" feature should never accidentally break or require changes in the "Search" feature.

Balancing these two forces is the primary objective of every decision that follows.

### 1.3 The Challenge: Codebase Rot

Knowing the foundations and philosophy of software architecture, as well as our project goals, is a great first step. However, knowing the theory versus actually preventing a system from degrading in practice are two completely different things.

Choosing an architecture that does not eventually degrade into a tangled mess is incredibly hard. Without deliberate boundaries, applications naturally entropy over time. Shortcuts are taken to meet deadlines, domains bleed into one another, and suddenly, a simple feature request requires untangling hundreds of interrelated files. We treat architecture not just as a folder structure, but as a defense mechanism against this inevitable decay.

With that in mind, let's dive right into the options.

## 2. Macro Architecture: Deployment & Boundaries

### 2.1 The Monolith

### 2.2 A Note on Microservices

### 2.3 The Verdict: The Modular Monolith

## 3. Meso Architecture: Application Design Patterns

### 3.1 The Spectrum of Patterns

### 3.2 Horizontal Slicing (Layered Architecture)

### 3.3 Pure Clean Architecture / DDD

### 3.4 The Verdict: Vertical Slicing + Hexagonal I/O

## 4. Implementation: The Physical Anatomy

### 4.1 The Directory Tree

### 4.2 Core Traits

## 5. Boundary Enforcement

### 5.1 No Cross-Module Database Joins

### 5.2 Strict DTO Contracts

### 5.3 Infrastructure Isolation

### 5.4 Absolute Imports

## 6. Outro: DX & Scalability

## 7. References

### Old draft

A Rag pipeline using FastAPI backend and [TBD] frontend

Temp:

# System Architecture

Our backend is built as a **Feature-Driven Modular Monolith**. It utilizes **Vertical Slice Architecture (VSA)** to organize business features, while applying a lightweight **Hexagonal (Ports & Adapters) pattern** to isolate external infrastructure.

The goal of this document is to:

1. Explain the core architectural problems we are solving.
2. Compare the trade-offs of common architectural patterns.
3. Detail how a Modular Monolith provides the optimal balance of speed and scalability.
4. Define the strict boundaries required to prevent the codebase from deteriorating.

## 1. The Core Problem: Cohesion vs. Coupling

At the heart of sustainable software design lie two fundamental, often competing principles:

- **High Cohesion:** Code that changes together should live together. If you are modifying how a user profile is updated, you should not have to hunt across five different directories to find the route, the schema, the database model, and the business logic.
- **Low Coupling:** Modules should be independent. A change in the "Billing" feature should never accidentally break or require changes in the "Search" feature.

There are a wide range of architecture patterns in software design, some of which enforce these traits better than others. A project’s folder structure is the physical embodiment of these principles, dictating whether the codebase will scale smoothly or degrade over time.

Note: I feel like the second sentence of this paragraph above is very random. Like, what does it have to do with architecture or what we'll talk about? I think it'd be much more clear if we

## 2. Exploring Alternatives

Before landing on a Modular Monolith, it is important to understand why common alternatives fall short for our current operational scale.

Note: Somewhere here add the quyote programmers know the benefits of everything and the tradeoffs of nothing by [can't remember the author]

- **The Flat Structure (Horizontal Slicing):** Traditional frameworks default to folders named `routers/`, `services/`, and `models/`. This organizes code by technical type, resulting in near-zero cohesion. As the application grows, services begin importing each other haphazardly, leading to a highly coupled "Big Ball of Mud."
- **Pure Clean Architecture / DDD:** Emphasizing heavy decoupling through interfaces and domain entities is incredibly robust, but introduces significant boilerplate. For teams needing to move quickly, creating a use-case interactor, a domain model, and a repository just to read a database row throttles development speed.

Note: You still need to add microservices here, however briefly it may be! I liked the "Microservices from Day One" title

![Architectural Comparison](https://substackcdn.com/image/fetch/$s_!7DMP!,f_auto,q_auto:good,fl_progressive:steep/https%3A%2F%2Fsubstack-post-media.s3.amazonaws.com%2Fpublic%2Fimages%2F66d12ddc-2abe-4a98-82d5-ee177e80487c_1470x1600.png)

_(Image source: ByteByteGo)_

### 2.3 A Note on Microservices

The conversation around microservices often skips an important question: _what problem are you actually solving?_ For most teams, the operational overhead of microservices—distributed tracing, independent deploys, network failures, service meshes—creates more problems than it solves.

Martin Fowler’s [_MonolithFirst_](https://martinfowler.com/bliki/MonolithFirst.html) makes the argument at length: almost all successful microservice stories started with a monolith that got too big and was subsequently broken up, while systems built as microservices from scratch often end up in serious trouble.

Architectural expert Mark Richards echoes this, emphasizing that **microservices are an optimization, not a baseline.** Defining microservice boundaries too early almost always results in incorrect boundaries, leading to distributed monoliths where services constantly chatter over HTTP just to resolve a single request.

Recently, massive engineering teams (like Shopify and Amazon Prime Video) have published case studies on cutting down exorbitant infrastructure costs and reducing complexity by moving away from microservices back to well-structured monoliths. A modular monolith is frequently the right default: a single deployable unit, strong internal boundaries, and easy to evolve.

Note: This last parapgraph is not enough. We need to go broad then cite in bulletpoints. Something like:
"Recently, large-scale organizations have ...

1.  [Shopify (article title)](url)
2.  etc
3.  etc
    "
    Cite between 2 and 4 case studies with articles from official blog sources (aka Shopify from Shopify, etc)

![Microservices Journey](https://dz2cdn1.dzone.com/storage/temp/18632591-journey.jpg)
_(Image source: DZone)_

## 3. The Modular Monolith

We need the boundary protection of microservices but with the deployment simplicity and execution speed of a monolithic codebase. We achieve this by slicing the application **vertically by feature** rather than horizontally by layer.

### 3.1 The Building Block: A Module

A module is an independent, cohesive vertical slice of the application.

It owns its own storage access, business logic, domain models, and APIs (for both internal and external consumption). Everything required for a specific business capability lives entirely within its own boundary.

![Module Architecture](https://dz2cdn1.dzone.com/storage/temp/18632588-module.jpg)
_(Image source: DZone)_

### 3.2 The Delivery Mechanism: A Monolith

A monolith simply means the application is deployed as a single, unified unit (e.g., one Docker container, one process). It shares memory, a single database connection pool, and executes locally without network hops between domains.

![Monolith Architecture](https://dz2cdn1.dzone.com/storage/temp/18632589-monolith.jpg)
_(Image source: DZone)_

### 3.3 The Convergence: The Modular Monolith

By combining these concepts, we create a Modular Monolith. The application deploys as a single unit, but internally, the code behaves as if it were a network of microservices. If a feature (like Billing) is deprecated tomorrow, we can delete that single folder, and the application will compile and run perfectly.

![Modular Monolith Architecture](https://dz2cdn1.dzone.com/storage/temp/18632590-modulith.jpg)
_(Image source: DZone)_

### 3.4 The Full System Architecture

When mapped out, the architecture provides the logical separation and team autonomy of microservices without sacrificing data consistency and system performance.

<Image src="image_agent_tag_17390358707787352350" alt="Diagram comparing Monolith, Microservices, and Modular Monolith architectures" caption="Architectural Comparison" />

## 4. Implementing the Modular Monolith

Here is how these theoretical concepts physically map to our directory tree in our FastAPI project.

The architecture is driven by three core traits:

- **Vertical Slices:** Features live in `src/modules/` and own their entire stack (routes, schemas, models, logic).
- **Pragmatic Isolation:** External I/O (Databases, Caches, Object Storage) is completely isolated in `src/infrastructure/`.
- **Cross-Cutting Core:** Global middleware, rate-limiting, and security logic live in `src/core/`.

Note: Create a more realistic architecture of a real app, say Airbnb or Spotify or whatever. But something that's verified ish, not random imaginary code

```text
backend/
├── src/
│   ├── api/                          # ROUTING LAYER: Top-level API aggregators
│   ├── core/                         # CROSS-CUTTING: Middleware, auth, etc
│   │
│   ├── infrastructure/               # PORTS & ADAPTERS: External I/O
│   │   ├── postgres/                 # DB connections & base models
│   │   ├── qdrant/                   # Vector DB client
│   │   └── redis/                    # Caching client
│   │
│   └── modules/                      # VERTICAL SLICES: Feature domains
│       ├── auth/
│       ├── billing/
│       ├── search/
│       └── users/                    # Everything User-related lives here:
│           ├── __init__.py
│           ├── router.py             # FastAPI routes specific to /users
│           ├── schemas.py            # Pydantic DTOs for requests/responses
│           ├── models.py             # SQLAlchemy entities (strictly internal)
│           ├── service.py            # Core business logic
│           ├── dependencies.py       # Domain-specific FastAPI dependencies
│           └── exceptions.py         # Custom user-domain errors
```

Notice how you can immediately tell what the system _does_ just by looking at `src/modules/`

By isolating the `infrastructure` from the `modules`, our business logic remains entirely agnostic to the underlying database engine or connection pooling logic. Inside `modules/`, the vertical slices own their entire stack from the route down to the database model.

_(If you are interested in how to bootstrap this exact directory structure automatically, see the [One-Shotting a Modular Monolith in FastAPI](../guides/scaffolding.md) guide)._

## 5. Enforcing Boundaries

An architecture is only as good as its boundaries.

Up to this point, **this architecture is realistically just a folder structure.** No matter how well we explain this structure to developers, nothing stops them from taking shortcuts, cross-importing models, talking to the database directly, and creating a mess to meet deadlines.

Therefore, **we do not rely on code reviews to police this.** We treat boundary enforcement as a first-class citizen and **enforce it programmatically** using static analysis tools, linters, and CI/CD pipelines.

For an in-depth guide on how to write code within these boundaries, see the [Writing Modules](../guides/writing-modules.md) guide.

### 5.1 No Cross-Module Database Joins (`import-linter`)

Even though the monolith shares a single database, modules must act as if they logically own their own isolated databases. **If you execute a SQL `JOIN` across tables owned by different modules (e.g., joining `billing_invoices` with `users`), you tightly couple them at the database level.** If you ever need to extract `Billing` into a microservice later, that database join will instantly break the system.

To prevent this, a module (e.g., `Billing`) **cannot** import a SQLAlchemy model (e.g., `User`) from another module. Because the models cannot be imported, SQL joins across boundaries become virtually impossible by design.

We enforce this programmatically using `import-linter`. In our `.importlinter` configuration, we define an "independence" contract:

```ini
[importlinter:contract:modules-are-independent]
name = Feature modules should not import each other directly
type = independence
modules =
    src.modules.users
    src.modules.billing
    src.modules.search
    src.modules.auth
```

If a developer writes `from src.modules.users.models import User` inside the billing module, the `prek` pipeline will fail.

### 5.2 Strict DTO Contracts (Design Pattern)

Because modules cannot import each other's models, data sharing is handled strictly via Service-to-Service communication. The service layer acts as the public API for that module and must return a strictly typed Pydantic model (a Data Transfer Object).

```python
# ✅ GOOD: Communicate via the domain service to get a strict DTO
from src.modules.users.service import UserService

async def generate_invoice(user_id: UUID, user_service: UserService):
    # Returns a UserDTO (Pydantic), NOT a SQLAlchemy model
    user = await user_service.get_user(user_id)
    return Invoice(email=user.email, amount=100.00)
```

### 5.3 Infrastructure Isolation (`import-linter` layers)

Feature modules contain business logic, not connection drivers. You should never see `psycopg`, `boto3`, or `redis` directly imported inside `src/modules/`.

We enforce this using a "layers" contract in `import-linter`:

```ini
[importlinter:contract:infrastructure-isolation]
name = Modules cannot import external drivers directly, and Infrastructure cannot depend on Modules
type = layers
layers =
    src.api
    src.modules
    src.infrastructure
```

### 5.4 Absolute Imports (`ruff`)

To ensure our boundaries are highly visible and grep-able, we ban relative imports that span across top-level packages. We enforce this using `ruff` by enabling the `TID252` rule in our `pyproject.toml`.

```toml
[tool.ruff.lint]
select = ["E", "F", "TID252"]
```

This forces developers to write `from src.modules.users...` instead of `from ...users`, making import-linter configurations highly effective and codebase traversal explicit.

## 6. Outro

The ultimate goal of this architecture is **Developer Experience (DX) and Scalability**.

When a developer is tasked with adding a new endpoint to the search system, they do not need to hold the entire application in their head. They open `src/modules/search/`, and everything they need is right there. It provides the psychological safety of knowing that changes made inside one boundary will not trigger catastrophic failures in another.

We optimize for deleting code just as much as writing it.

## 7. References

- [Modular Monolith Architecture Overview (DZone)](https://dzone.com/articles/modular-monolith-architecture-overview)
- [MonolithFirst (Martin Fowler)](https://martinfowler.com/bliki/MonolithFirst.html)
- [Lesson 159: Modular Monoliths (Mark Richards - DeveloperToArchitect)](https://developertoarchitect.com/lessons/lesson159.html)
- [What Modular Actually Means (Dave Amit)](https://daveamit.com/posts/2026-02-13-modular-monolith/)
- [Monolith vs Microservices vs Modular Monolith (ByteByteGo)](https://blog.bytebytego.com/p/monolith-vs-microservices-vs-modular?has_completed_unsubscribed_unlock=true)
