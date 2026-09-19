# Insurance Claim Processing and Fraud Insight Platform

A full-stack DBMS project for processing insurance claims, detecting potential fraud using rule-based analysis, and providing role-based access through a FastAPI web application.

The system uses **PostgreSQL for structured transactional data** and **MongoDB for flexible fraud-analysis results**.

---

## 📌 Project Overview

Insurance claim processing involves handling customer information, insurance policies, claim records, and fraud analysis.

Manual claim processing can make it difficult to identify suspicious claims efficiently and maintain a centralized record of fraud-analysis results.

This project provides a web-based platform that allows:

- Customers to submit insurance claims.
- Claim officers to view and process claims.
- Administrators to monitor claims and fraud analysis.
- The system to calculate a fraud risk score.
- Fraud-analysis results to be stored in MongoDB.
- PostgreSQL to maintain structured customer, policy, claim, and user information.
- Role-based authentication and authorization using JWT.

---

## 🎯 Objectives

1. Develop a centralized insurance claim processing system.
2. Store structured insurance data using PostgreSQL.
3. Store fraud-analysis results using MongoDB.
4. Implement rule-based fraud risk detection.
5. Provide REST APIs using FastAPI.
6. Implement JWT-based authentication.
7. Implement role-based access control.
8. Provide a web dashboard for monitoring claims and fraud statistics.
9. Prevent duplicate fraud-analysis records for the same claim.
10. Provide a scalable foundation for future fraud-detection improvements.

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       Frontend       │
                    │     HTML / CSS / JS  │
                    └──────────┬───────────┘
                               │
                               │ REST API + JWT
                               ▼
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │       Backend        │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
       ┌──────────────────┐       ┌──────────────────┐
       │    PostgreSQL    │       │     MongoDB      │
       │                  │       │                  │
       │ Customers        │       │ fraud_analysis   │
       │ Policies         │       │                  │
       │ Claims           │       │ Risk Score       │
       │ Users            │       │ Risk Level       │
       └────────┬─────────┘       │ Reasons          │
                │                 └────────┬─────────┘
                │                          │
                └──────────┬───────────────┘
                           ▼
                  ┌──────────────────┐
                  │ Fraud Detection  │
                  │      Engine      │
                  └──────────────────┘