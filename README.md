# System Design From Zero to Hero

> A project-based roadmap to become a **Senior Systems Engineer** by building systems from first principles and progressively evolving them into scalable, distributed, and cloud-native architectures.

---

## 🎯 Final Goal

The goal of this roadmap is to develop the ability to:

- Understand how computer systems work from the network and OS level upward.
- Design and build production-grade backend systems.
- Understand databases, caching, messaging, distributed systems, and cloud infrastructure.
- Reason about scalability, reliability, consistency, availability, and performance.
- Design systems such as URL shorteners, chat platforms, search engines, video platforms, marketplaces, and event-driven enterprise systems.
- Deploy and operate systems using Docker and Kubernetes.
- Approach senior-level system design interviews with implementation experience rather than theory alone.
- Progress toward architect-level thinking by eventually building platform components such as schedulers, service discovery, load balancing, and monitoring.

---

# 🧭 Learning Philosophy

This roadmap is intentionally **project-first**.

We do not learn a large amount of theory first and then try to apply it later.

Instead:

```text
Problem
   ↓
Build a simple solution
   ↓
Understand the bottleneck
   ↓
Learn the concept that solves it
   ↓
Improve the architecture
   ↓
Test / Measure
   ↓
Productionize it
   ↓
Design for larger scale
```

Every project should answer:

> What problem does this architectural component solve?

---

# 🗺️ Roadmap Overview

```text
Phase 0
Foundations
    │
    ▼
Phase 1
Single Server Systems
    │
    ▼
Phase 2
Distributed Systems
    │
    ▼
Phase 3
Scalability
    │
    ▼
Phase 4
Event-Driven Systems
    │
    ▼
Phase 5
Cloud Native
    │
    ▼
Phase 6
Real-World Large-Scale Systems
    │
    ▼
Phase 7
Architect-Level Systems
```

---

# 📊 Progress Tracker

| Phase | Project | Status |
|---|---|---|
| Phase 0 | Web Server | ⬜ Not Started |
| Phase 0 | HTTP Server | 🔒 Locked |
| Phase 1 | URL Shortener | 🔒 Locked |
| Phase 1 | Pastebin | 🔒 Locked |
| Phase 1 | File Upload Service | 🔒 Locked |
| Phase 2 | Distributed Cache | 🔒 Locked |
| Phase 2 | API Rate Limiter | 🔒 Locked |
| Phase 2 | Notification System | 🔒 Locked |
| Phase 3 | Chat Application | 🔒 Locked |
| Phase 3 | News Feed | 🔒 Locked |
| Phase 3 | Search Engine | 🔒 Locked |
| Phase 4 | Mini Kafka | 🔒 Locked |
| Phase 4 | Analytics Pipeline | 🔒 Locked |
| Phase 5 | Kubernetes Platform | 🔒 Locked |
| Phase 5 | GitOps Platform | 🔒 Locked |
| Phase 6 | Uber | 🔒 Locked |
| Phase 6 | YouTube | 🔒 Locked |
| Phase 6 | Netflix | 🔒 Locked |
| Phase 6 | Amazon | 🔒 Locked |
| Phase 6 | AML Monitoring Platform | 🔒 Locked |
| Phase 7 | Mini Cloud | 🔒 Locked |

### Status Definitions

```text
⬜ NOT_STARTED
🟡 IN_PROGRESS
🔵 IMPLEMENTED
🟣 REVIEWED
🟢 MASTERED
🔒 LOCKED
```

A project remains locked until the previous project has been understood and reviewed.

---

# 🧑‍🏫 Learning Method

Every project follows the same structure:

1. Goal
2. Why it matters
3. Concepts required
4. Architecture
5. Step-by-step implementation
6. Experiments
7. Exercises
8. Production-grade version
9. Common mistakes
10. System design discussion
11. Interview questions
12. Mastery test
13. Mastery checklist

---

# 🏗️ Phase 0 — Foundations

## Objective

Understand what happens underneath modern backend frameworks.

Before using FastAPI, Redis, Kafka, Kubernetes, etc., understand the lower-level mechanisms they are built on.

### Core Learning Areas

- Operating systems
- Processes
- Threads
- Memory
- TCP/IP
- Sockets
- Client-server architecture
- HTTP
- Request/response lifecycle
- Basic concurrency

---

# Project 0.1 — Build a Web Server

## Goal

Build a basic network server using low-level sockets.

### Architecture

```text
Client
   │
   │ TCP Connection
   ▼
Socket Server
   │
   ▼
Request Handler
```

### Concepts

- What is a server?
- What is a socket?
- IP address
- Port
- TCP connection
- `socket()`
- `bind()`
- `listen()`
- `accept()`
- `recv()`
- `send()`
- Client-server communication
- Blocking vs non-blocking behavior
- Basic concurrency

### Initial Implementation

```python
socket()
bind()
listen()
accept()
recv()
send()
```

### Learning Outcome

You should be able to explain what happens when a client connects to a server without using a web framework.

---

# Project 0.2 — Build an HTTP Server

## Goal

Build an HTTP server without FastAPI or Flask.

### Architecture

```text
Client
   │
   │ HTTP Request
   ▼
HTTP Server
   │
   ├── Request Parser
   ├── Router
   └── Response Builder
   │
   ▼
HTTP Response
```

### Concepts

- HTTP request
- HTTP response
- HTTP methods
- Headers
- Status codes
- Request body
- Response body
- Routing
- HTTP parsing
- Keep-alive connections
- Basic concurrency

### Example APIs

```text
GET  /hello
GET  /users
POST /users
```

### Learning Outcome

Understand what frameworks such as FastAPI are doing underneath the abstraction.

---

# 📦 Phase 1 — Single Server Systems

## Objective

Learn how to design practical backend services before introducing distributed complexity.

### Core Learning Areas

- API design
- Database design
- SQL
- Transactions
- Indexes
- Caching
- Object storage
- Expiration
- Read/write patterns
- Basic scalability

---

# Project 1 — URL Shortener

Examples:

```text
TinyURL
Bitly
```

## Goal

Convert a long URL into a short identifier.

```text
https://example.com/a/very/long/url
              │
              ▼
           abc123
```

### Basic Architecture

```text
Client
   │
   ▼
FastAPI
   │
   ▼
PostgreSQL
```

### Concepts

- REST API
- Database schema design
- Primary key
- Unique constraints
- Indexes
- Base62 encoding
- Short-code generation
- Redirects
- Read/write patterns

### Production Evolution

```text
Client
   │
   ▼
Load Balancer
   │
   ▼
API Servers
   │
   ├──────────► Redis
   │
   ▼
PostgreSQL
   │
   ▼
Analytics / Events
```

### Additional Learning

- Redis
- Cache-aside pattern
- Click analytics
- Rate limiting
- Horizontal scaling
- Database replication
- Partitioning
- Sharding concepts

---

# Project 2 — Pastebin

## Goal

Build a service where users can create and retrieve text pastes.

### Architecture

```text
Client
   │
   ▼
Paste Service
   │
   ▼
Storage
```

### Concepts

- API design
- Text storage
- Paste identifiers
- Expiration
- TTL
- Read-heavy workloads
- Caching
- Data lifecycle

### Production Evolution

```text
Client
   │
   ▼
API
   │
   ├──► Cache
   │
   └──► Database
```

### Additional Learning

- CDN
- Compression
- Background cleanup
- Expired-data deletion
- Storage optimization

---

# Project 3 — File Upload Service

Examples:

```text
Google Drive
Dropbox
```

## Goal

Build a service capable of uploading and retrieving large files.

### Architecture

```text
Client
   │
   ▼
Upload API
   │
   ├──────────► Metadata DB
   │
   ▼
Object Storage
```

### Concepts

- File metadata
- Blob/object storage
- Multipart upload
- Large file handling
- Streaming
- Upload/download APIs
- Metadata vs file data

### Production Evolution

```text
Client
   │
   ▼
API
   │
   ├──────────► PostgreSQL
   │
   └──────────► Object Storage
                     │
                     ▼
                    CDN
```

### Additional Learning

- S3-style object storage
- MinIO
- Signed URLs
- Chunked uploads
- Resumable uploads
- CDN

---

# 🌐 Phase 2 — Distributed Systems

## Objective

Move from a single-server mindset to systems composed of multiple independent components.

### Core Learning Areas

- Distributed state
- Caching
- Queues
- Asynchronous processing
- Consistency
- Retries
- Failure handling
- Message delivery
- Backpressure
- Distributed coordination

---

# Project 4 — Distributed Cache

## Goal

Build a simplified Redis-like cache.

### Architecture

```text
Client
   │
   ▼
Cache Server
   │
   ▼
In-Memory Store
```

### Commands

```text
SET
GET
DELETE
EXPIRE
```

### Concepts

- In-memory storage
- Key-value data model
- TTL
- Expiration
- LRU eviction
- Memory management
- Cache hit
- Cache miss

### Production Evolution

```text
Application
     │
     ▼
Cache Cluster
 ┌───┼───┐
 ▼   ▼   ▼
 C1  C2  C3
```

### Additional Learning

- Consistent hashing
- Replication
- Cache invalidation
- Hot keys
- Cache stampede
- Distributed cache

---

# Project 5 — API Rate Limiter

## Goal

Protect an API from excessive traffic.

### Architecture

```text
Client
   │
   ▼
Rate Limiter
   │
   ├── Allowed ──► API
   │
   └── Rejected
```

### Algorithms

- Fixed Window
- Sliding Window
- Token Bucket

### Concepts

- Request quotas
- Counters
- Distributed counters
- Redis-based rate limiting
- Burst traffic
- Per-user limits
- Per-IP limits
- Per-API-key limits

### Production Evolution

```text
Clients
   │
   ▼
Load Balancer
   │
   ▼
Rate Limiter
   │
   ▼
API Cluster
```

---

# Project 6 — Notification System

Examples:

```text
Email
SMS
Push Notification
```

## Goal

Build an asynchronous notification system.

### Architecture

```text
Application
     │
     ▼
Message Queue
     │
     ├──► Email Worker
     ├──► SMS Worker
     └──► Push Worker
```

### Concepts

- Producer
- Consumer
- Queue
- Asynchronous processing
- Retry
- Dead Letter Queue
- Idempotency
- Backpressure
- Delivery guarantees

### Technologies

- RabbitMQ
- Kafka

### Production Evolution

```text
Application
     │
     ▼
Kafka / Queue
     │
     ├──► Worker 1
     ├──► Worker 2
     └──► Worker N
```

### Additional Learning

- Retry policies
- Exponential backoff
- Poison messages
- Consumer scaling
- Dead Letter Queue
- At-least-once processing
- Idempotent consumers

---

# 📈 Phase 3 — Scalability

## Objective

Understand how systems scale when the number of users, requests, connections, and data grows significantly.

### Core Learning Areas

- Horizontal scaling
- Load balancing
- WebSockets
- Pub/Sub
- Fan-out
- Sharding
- Ranking
- Distributed state
- High availability

---

# Project 7 — Chat Application

Examples:

```text
WhatsApp
Slack
```

## Goal

Build a real-time messaging system.

### Architecture

```text
User
 │
 ▼
WebSocket Server
 │
 ▼
Pub/Sub
 │
 ├──► User A
 ├──► User B
 └──► User C
```

### Concepts

- WebSockets
- Persistent connections
- Connection management
- Presence
- Message delivery
- Message ordering
- Pub/Sub
- Online/offline state

### Production Evolution

```text
Clients
   │
   ▼
Load Balancer
   │
   ├──► WS Server 1
   ├──► WS Server 2
   └──► WS Server N
             │
             ▼
          Pub/Sub
             │
             ▼
          Storage
```

---

# Project 8 — News Feed

Examples:

```text
Facebook
LinkedIn
```

## Goal

Build a personalized feed system.

### Architecture

```text
User
 │
 ▼
Feed Service
 │
 ├──► Feed Store
 ├──► Cache
 └──► Ranking
```

### Concepts

- Fan-out
- Feed generation
- Push vs pull
- Ranking
- Caching
- Hot users
- Timeline storage

### Important Design Problem

Consider:

```text
User A
  └── follows 10 users

User B
  └── follows 10,000,000 users
```

How should the system generate their feeds?

### Additional Learning

- Fan-out-on-write
- Fan-out-on-read
- Hybrid approach
- Feed pagination
- Ranking pipelines

---

# Project 9 — Search Engine

## Goal

Build a simplified search engine.

### Architecture

```text
Documents
    │
    ▼
Indexer
    │
    ▼
Inverted Index
    │
    ▼
Search API
```

### Concepts

- Inverted index
- Tokenization
- Indexing
- Query processing
- Ranking
- Sharding
- Replication

### Production Evolution

```text
Crawler
   │
   ▼
Indexer
   │
   ▼
Search Cluster
 ┌───┼───┐
 ▼   ▼   ▼
 S1  S2  S3
```

### Additional Learning

- Distributed indexes
- Search ranking
- Query fan-out
- Index replication
- Search partitioning

---

# ⚡ Phase 4 — Event-Driven Systems

## Objective

Understand event streaming and build systems where services communicate through durable events.

### Core Learning Areas

- Event-driven architecture
- Event streaming
- Topics
- Partitions
- Offsets
- Consumer groups
- Streaming pipelines
- Batch processing
- Event replay

---

# Project 10 — Build a Mini Kafka

## Goal

Build a simplified event streaming platform.

### Architecture

```text
Producer
   │
   ▼
Broker
   │
   ├── Partition 0
   ├── Partition 1
   └── Partition 2
   │
   ▼
Consumer Group
```

### Concepts

- Topic
- Partition
- Offset
- Producer
- Consumer
- Consumer Group
- Broker
- Ordering
- Retention
- Replay

### Learning Outcome

Understand why Kafka is different from a traditional queue.

---

# Project 11 — Analytics Pipeline

## Goal

Build an event-driven analytics pipeline.

### Architecture

```text
Applications
     │
     ▼
Kafka
     │
     ▼
Stream Processing
     │
     ├──► Aggregation
     ├──► Transformation
     └──► Enrichment
     │
     ▼
Data Warehouse
```

### Concepts

- ETL
- Streaming
- Batch processing
- Event aggregation
- Data transformation
- Data lake
- Data warehouse

### Technologies

- Kafka
- Spark
- Flink

### Learning Outcome

Understand how large systems transform millions of events into analytical data.

---

# ☁️ Phase 5 — Cloud Native

## Objective

Learn how production systems are deployed, scaled, monitored, and managed in containerized environments.

### Core Learning Areas

- Docker
- Kubernetes
- Pods
- Deployments
- Services
- Ingress
- ConfigMaps
- Secrets
- Service discovery
- Autoscaling
- CI/CD
- GitOps

---

# Project 12 — Kubernetes Platform

## Goal

Deploy previous services on Kubernetes.

### Architecture

```text
              Ingress
                 │
                 ▼
             Service
                 │
        ┌────────┼────────┐
        ▼        ▼        ▼
      Pod 1    Pod 2    Pod 3
```

### Concepts

- Pod
- Deployment
- ReplicaSet
- Service
- Namespace
- ConfigMap
- Secret
- Ingress
- Persistent Volume
- Persistent Volume Claim
- Horizontal Pod Autoscaler

### Learning Outcome

Understand how Kubernetes manages workloads and provides networking and scaling.

---

# Project 13 — GitOps Platform

## Goal

Build a complete deployment workflow using GitOps.

### Architecture

```text
Developer
    │
    ▼
Git Repository
    │
    ▼
CI Pipeline
    │
    ▼
Container Registry
    │
    ▼
ArgoCD
    │
    ▼
Kubernetes
```

### Technologies

- Git
- Docker
- Helm
- ArgoCD
- Kubernetes

### Concepts

- CI/CD
- GitOps
- Declarative deployment
- Helm charts
- Environment management
- Rollbacks
- Deployment strategies

---

# 🏢 Phase 6 — Real-World Large-Scale Systems

## Objective

Apply everything learned so far to realistic large-scale systems.

At this phase, the focus shifts from implementing individual components to making architectural decisions.

---

# Project 14 — Uber-Style System

## Goal

Design a ride-hailing platform.

### Core Architecture

```text
Rider
  │
  ▼
Ride Service
  │
  ├──► Driver Location Service
  ├──► Matching Engine
  ├──► Pricing
  └──► Trip Service
```

### Concepts

- Geo-spatial indexing
- Real-time location
- Driver matching
- WebSockets
- Event streaming
- Location updates
- Distributed state

### Key Questions

- How do we find nearby drivers?
- How do we match drivers and riders?
- How do we handle millions of location updates?
- How do we maintain trip state?

---

# Project 15 — YouTube-Style System

## Goal

Design a video-sharing platform.

### Architecture

```text
User
 │
 ▼
Upload Service
 │
 ▼
Object Storage
 │
 ▼
Video Processing
 │
 ├──► 360p
 ├──► 720p
 ├──► 1080p
 └──► 4K
 │
 ▼
CDN
 │
 ▼
Viewer
```

### Concepts

- Large file uploads
- Object storage
- Video transcoding
- Queues
- CDN
- Metadata storage
- Streaming

---

# Project 16 — Netflix-Style System

## Goal

Design a large-scale video streaming platform.

### Concepts

- Video streaming
- CDN
- Edge caching
- Content delivery
- Recommendation systems
- Metadata services
- Distributed storage
- Adaptive bitrate streaming

### Architecture

```text
User
 │
 ▼
API
 │
 ├──► Recommendation Service
 ├──► Metadata Service
 └──► Content Service
             │
             ▼
            CDN
             │
             ▼
           Video
```

---

# Project 17 — Amazon-Style E-Commerce System

## Goal

Design a large-scale e-commerce platform.

### Core Architecture

```text
User
 │
 ▼
API Gateway
 │
 ├──► Product Service
 ├──► Cart Service
 ├──► Inventory Service
 ├──► Order Service
 ├──► Payment Service
 └──► Notification Service
```

### Concepts

- Inventory consistency
- Cart management
- Orders
- Payments
- Distributed transactions
- Idempotency
- Event-driven architecture
- Saga pattern

---

# Project 18 — AML Monitoring Platform

## Goal

Design an enterprise transaction monitoring and investigation platform.

### Architecture

```text
Transactions
     │
     ▼
Transaction Ingestion
     │
     ▼
Event Streaming
     │
     ▼
Rule Engine
     │
     ▼
Alert Generation
     │
     ▼
Case Management
     │
     ▼
Investigator
     │
     ▼
AI / ML Investigation
```

### Core Concepts

- Event-driven architecture
- Kafka
- Rules engine
- Transaction processing
- Alert generation
- Case management
- Audit trails
- Data retention
- Compliance architecture
- AI-assisted investigation

### Advanced Topics

- Idempotency
- Exactly-once considerations
- Event replay
- Auditability
- Data lineage
- High availability
- Disaster recovery
- Security

---

# 🏛️ Phase 7 — Architect Level

## Objective

Move from designing applications to designing infrastructure platforms.

The final project combines concepts learned throughout the roadmap.

---

# Project 19 — Build a Mini Cloud

## Goal

Build a simplified cloud platform.

### Major Architecture

```text
                    ┌──────────────────┐
                    │   API Gateway    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Load Balancer    │
                    └────────┬─────────┘
                             │
             ┌───────────────┼───────────────┐
             ▼               ▼               ▼
          Node 1           Node 2          Node 3
             │               │               │
             └───────────────┼───────────────┘
                             │
                             ▼
                        Scheduler
                             │
                             ▼
                      Service Discovery
                             │
                             ▼
                         Monitoring
```

### Components

- Load balancer
- Scheduler
- Service discovery
- Container runtime abstraction
- Health checking
- Monitoring
- Resource management
- Node management

### Concepts

- Distributed scheduling
- Leader election
- Service discovery
- Health checks
- Resource allocation
- Fault tolerance
- Load balancing
- Observability
- Control plane vs data plane

### Final Learning Outcome

Understand the architecture behind modern cloud platforms and container orchestration systems.

---

# 🧠 Cross-Cutting Concepts

These concepts should appear repeatedly throughout the roadmap.

## Scalability

```text
Vertical Scaling
       ↓
Horizontal Scaling
       ↓
Sharding
       ↓
Distributed Architecture
```

---

## Availability

Learn:

- Replication
- Failover
- Health checks
- Redundancy
- Multi-node systems
- Disaster recovery

---

## Reliability

Learn:

- Retries
- Timeouts
- Circuit breakers
- Idempotency
- Dead Letter Queues
- Backpressure

---

## Performance

Learn:

- Latency
- Throughput
- CPU utilization
- Memory utilization
- Network bandwidth
- Database performance
- Caching

---

## Consistency

Learn:

- Strong consistency
- Eventual consistency
- Read-after-write consistency
- Replication lag
- Conflict resolution

---

## Databases

Learn:

- Transactions
- ACID
- Isolation levels
- Locks
- Indexes
- Query optimization
- Replication
- Partitioning
- Sharding

---

## Caching

Learn:

- Cache-aside
- Write-through
- Write-back
- TTL
- LRU
- Cache invalidation
- Hot keys
- Cache stampede

---

## Messaging

Learn:

- Queue
- Pub/Sub
- Kafka
- Consumer groups
- Ordering
- Retry
- DLQ
- Idempotency

---

## Observability

Learn:

```text
Logs
Metrics
Traces
```

Also:

- Health checks
- Alerting
- Dashboards
- Distributed tracing

---

# 🧪 Project Methodology

Every project follows the same development cycle.

```text
1. Understand the Problem
          ↓
2. Define Requirements
          ↓
3. Design Basic Architecture
          ↓
4. Implement Minimum Version
          ↓
5. Test the System
          ↓
6. Find Bottlenecks
          ↓
7. Improve Architecture
          ↓
8. Load Test
          ↓
9. Productionize
          ↓
10. System Design Interview
          ↓
11. Mastery Test
```

---

# 🎓 Mastery Levels

Every project has five mastery levels.

## Level 1 — Understand

You can explain:

- Why the system exists
- What problem it solves
- Major components
- Request flow
- Data flow

---

## Level 2 — Build

You can implement a working version.

Requirements:

- APIs work
- Database works
- Core functionality works
- Tests pass

---

## Level 3 — Scale

You can answer:

```text
What happens if traffic becomes 10x?

What happens if traffic becomes 100x?

What happens if one server fails?

What happens if the database becomes the bottleneck?
```

---

## Level 4 — Productionize

You can add:

- Docker
- Logging
- Metrics
- Monitoring
- Health checks
- CI/CD
- Kubernetes
- Failure handling

---

## Level 5 — Design

You can independently design the system.

Examples:

```text
Design Bitly
Design WhatsApp
Design YouTube
Design Uber
Design Netflix
```

You should be able to explain:

- Requirements
- Capacity
- APIs
- Data model
- Architecture
- Scaling
- Failure handling
- Trade-offs

---

# 📝 Mastery Checklist

A project is considered **MASTERED** only when:

- [ ] I understand the problem.
- [ ] I can explain the architecture.
- [ ] I can explain every major component.
- [ ] I implemented the basic version.
- [ ] I wrote tests.
- [ ] I understand the database design.
- [ ] I understand the request/data flow.
- [ ] I identified bottlenecks.
- [ ] I implemented at least one scalability improvement.
- [ ] I understand failure scenarios.
- [ ] I understand the production architecture.
- [ ] I can explain the major trade-offs.
- [ ] I can answer interview questions.
- [ ] I can design the system without following a tutorial.

---

# 🎯 Senior Systems Engineer Skill Map

```text
                 Senior Systems Engineer
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
    Backend            Distributed         Cloud
    Systems              Systems           Native
       │                  │                  │
       ▼                  ▼                  ▼
   FastAPI              Kafka            Kubernetes
   PostgreSQL           Redis            Docker
   APIs                 Queues           Helm
   SQL                  Pub/Sub          ArgoCD
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                          ▼
                 System Architecture
                          │
                          ▼
             Scalability / Reliability
                          │
                          ▼
                  Senior Design Level
```

---

# 🛠️ Primary Technology Stack

## Programming

- Python

## Backend

- FastAPI
- REST APIs
- WebSockets

## Databases

- PostgreSQL
- SQL
- Redis

## Messaging

- Kafka
- RabbitMQ

## Storage

- MinIO
- S3-style object storage

## Containers

- Docker

## Orchestration

- Kubernetes

## Deployment

- Helm
- ArgoCD

## Observability

- Prometheus
- Grafana
- Logs
- Distributed tracing

## Testing

- pytest
- Unit testing
- Integration testing
- Load testing

---

# 📂 Suggested Repository Structure

```text
system-design-from-zero-to-hero/
│
├── README.md
├── progress.md
│
├── phase-00-foundations/
│   ├── project-01-web-server/
│   └── project-02-http-server/
│
├── phase-01-single-server/
│   ├── project-01-url-shortener/
│   ├── project-02-pastebin/
│   └── project-03-file-upload/
│
├── phase-02-distributed-systems/
│   ├── project-04-distributed-cache/
│   ├── project-05-rate-limiter/
│   └── project-06-notification-system/
│
├── phase-03-scalability/
│   ├── project-07-chat/
│   ├── project-08-news-feed/
│   └── project-09-search-engine/
│
├── phase-04-event-driven/
│   ├── project-10-mini-kafka/
│   └── project-11-analytics-pipeline/
│
├── phase-05-cloud-native/
│   ├── project-12-kubernetes-platform/
│   └── project-13-gitops-platform/
│
├── phase-06-real-world-systems/
│   ├── project-14-uber/
│   ├── project-15-youtube/
│   ├── project-16-netflix/
│   ├── project-17-amazon/
│   └── project-18-aml-monitoring/
│
└── phase-07-architect-level/
    └── project-19-mini-cloud/
```

---

# 📈 Overall Progress

```text
Phase 0  ── Foundations                 ⬜
Phase 1  ── Single Server              ⬜
Phase 2  ── Distributed Systems        ⬜
Phase 3  ── Scalability                ⬜
Phase 4  ── Event Driven               ⬜
Phase 5  ── Cloud Native               ⬜
Phase 6  ── Real World Systems         ⬜
Phase 7  ── Architect Level            ⬜
```

---

# 🚦 Current Position

```text
Goal:
Senior Systems Engineer

Current Phase:
Phase 0 — Foundations

Current Project:
Project 0.1 — Build a Web Server

Status:
NOT_STARTED

Next:
Build Web Server from raw TCP sockets
```

---

# 🔐 Progression Rule

We do **not** move to the next project simply because the implementation is complete.

The current project must reach:

```text
Understand
     ↓
Implement
     ↓
Experiment
     ↓
Scale
     ↓
Productionize
     ↓
Interview
     ↓
Mastery
```

Only after mastery is demonstrated do we unlock the next project.

---

# 🏆 Final Outcome

After completing the entire roadmap, the target is to move from:

```text
"I know system design concepts."
```

to:

```text
"I can build a system,
understand its bottlenecks,
scale it,
handle failures,
operate it in production,
and explain the architectural trade-offs."
```

That is the target of this roadmap.

---

# 🚀 Start Here

## Phase 0 → Project 0.1

### Build a Web Server From Scratch

Start with:

```text
Client
   │
   ▼
TCP
   │
   ▼
Socket
   │
   ▼
Server
```

Then progressively understand:

```text
TCP
 ↓
Socket
 ↓
Server
 ↓
HTTP
 ↓
Web Framework
 ↓
Database
 ↓
Cache
 ↓
Distributed System
 ↓
Cloud Native System
```

**The journey starts from the socket and ends at architect-level distributed systems.**

