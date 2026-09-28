@'
# Insurance Claim Processing and Fraud Insight Platform

A full-stack DBMS project for insurance claim processing, fraud-risk analysis, role-based authentication, semantic document search, and event-driven notifications.

The platform combines PostgreSQL, MongoDB, Qdrant Vector Database, FastAPI microservices, JWT authentication, Kafka, and a web frontend.

---

## Project Overview

Insurance claim processing involves managing customers, policies, claims, authentication, and fraud-analysis information.

This project provides a modular platform that supports:

- Customer and policy management using PostgreSQL
- Insurance claim processing
- Rule-based fraud-risk analysis
- Fraud-analysis storage using MongoDB
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Microservice-based backend architecture
- Kafka-based claim notification events
- Semantic document search using Qdrant and FastEmbed
- Web-based claim dashboard

---

## Objectives

1. Develop a centralized insurance claim processing platform.
2. Store structured transactional data using PostgreSQL.
3. Store flexible fraud-analysis results using MongoDB.
4. Implement rule-based fraud-risk detection.
5. Implement REST APIs using FastAPI.
6. Implement JWT-based authentication.
7. Implement role-based authorization.
8. Decompose backend functionality into microservices.
9. Implement Kafka-based notification events.
10. Implement a basic RAG/semantic-search layer using vector embeddings.
11. Provide a web dashboard for claim monitoring and fraud analysis.
12. Maintain a scalable architecture for future enhancements.

---

# System Architecture

```text
                         +-----------------------------+
                         |          Frontend           |
                         |       HTML / CSS / JS       |
                         +--------------+--------------+
                                        |
                                        | REST + JWT
                                        v
                         +-----------------------------+
                         |        API Gateway          |
                         |        FastAPI :8000        |
                         +--------------+--------------+
                                        |
              +-------------------------+-------------------------+
              |                         |                         |
              v                         v                         v
     +----------------+       +----------------+       +----------------+
     |  Auth Service  |       | Claim Service  |       | Fraud Service  |
     |     :8001      |       |     :8002      |       |     :8003      |
     +-------+--------+       +-------+--------+       +-------+--------+
             |                        |                        |
             v                        v                        v
        PostgreSQL              PostgreSQL                 MongoDB
             |                        |                        |
             +------------------------+------------------------+
                                      |
                                      v
                           +--------------------+
                           |    Kafka Broker    |
                           |      :9092         |
                           +---------+----------+
                                     |
                                     v
                           +--------------------+
                           | Notification       |
                           | Service :8004      |
                           +--------------------+

                         +--------------------+
                         |    RAG Service     |
                         |       :8005         |
                         +---------+----------+
                                   |
                                   v
                         +--------------------+
                         | Qdrant Vector DB   |
                         | + FastEmbed        |
                         +--------------------+