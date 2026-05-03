# Azure Cost Intelligence Simulator

## Overview

Azure Cost Intelligence Simulator is a production-style SaaS analytics platform that simulates Azure cloud cost management locally using synthetic billing and resource consumption data.

The platform provides:

* Cost trend analytics
* Service-wise spending insights
* Subscription breakdowns
* Forecasting and anomaly detection
* Cost optimization recommendations
* Background analytics processing
* Distributed task execution using Celery
* Dockerized deployment architecture

This project was designed as a portfolio-grade implementation for:

* DevOps engineering
* Platform engineering
* FinOps analytics
* Cloud cost optimization
* AI-assisted operational analytics
* Full-stack system design

---

# Key Features

## Cost Analytics Dashboard

* Daily cost trends
* Service-level cost analysis
* Subscription cost breakdown
* Top expensive resources
* Time range filtering

## Intelligence Layer

### Anomaly Detection

Implemented using:

* Z-score analysis
* Rolling moving averages
* Seasonal day-of-week adjustment
* Statistical confidence scoring

### Forecasting

* Historical trend analysis
* Forecast confidence intervals
* Predicted future spend
* Trend direction analysis

### Recommendation Engine

* Idle resource identification
* High-cost service analysis
* Optimization suggestions
* Estimated monthly savings

---

# Tech Stack

## Frontend

* React
* Recharts
* Vite
* Context API
* Axios

## Backend

* FastAPI
* SQLAlchemy
* Pydantic
* Celery
* Redis

## Database

* PostgreSQL

## Analytics

* NumPy
* Pandas
* Statistical anomaly detection

## Infrastructure

* Docker
* Docker Compose
* Nginx

---

# Architecture Diagram

```text
                         ┌─────────────────────┐
                         │     React UI        │
                         │  Cost Dashboard     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │       Nginx         │
                         │ Reverse Proxy Layer │
                         └──────────┬──────────┘
                                    │
                 ┌──────────────────┴──────────────────┐
                 ▼                                     ▼
      ┌─────────────────────┐             ┌─────────────────────┐
      │     FastAPI API     │             │    Celery Worker    │
      │  REST Analytics     │             │ Background Jobs     │
      └──────────┬──────────┘             └──────────┬──────────┘
                 │                                   │
                 ▼                                   ▼
      ┌─────────────────────┐             ┌─────────────────────┐
      │        Redis        │◄───────────►│    Celery Beat      │
      │ Message Broker      │             │ Task Scheduler       │
      └──────────┬──────────┘             └─────────────────────┘
                 │
                 ▼
      ┌─────────────────────┐
      │    PostgreSQL       │
      │ Cost & Usage Data   │
      └─────────────────────┘
```

---

# Backend Architecture

```text
app/
├── api/
│   ├── routes/
│   └── dependencies/
│
├── analytics/
│   ├── anomaly_detector.py
│   ├── forecaster.py
│   └── recommender.py
│
├── repositories/
│   ├── cost_repository.py
│   └── resource_repository.py
│
├── services/
│   ├── analytics_service.py
│   ├── alert_service.py
│   ├── cost_service.py
│   └── resource_service.py
│
├── schemas/
├── models/
├── database.py
├── config.py
└── main.py
```

---

# Frontend Architecture

```text
src/
├── components/
├── charts/
├── pages/
├── hooks/
├── context/
├── services/
└── styles/
```

---

# Database Schema

## Core Tables

### subscriptions

Stores Azure subscription metadata.

### resource_groups

Represents logical Azure resource groups.

### services

Azure service catalog:

* Virtual Machines
* Storage Accounts
* SQL Databases
* App Services
* Networking

### resources

Individual cloud resources.

### cost_usage

Daily usage and billing records.

---

# Synthetic Data Engine

The simulator generates:

* 60–90 days of historical data
* Randomized cost fluctuations
* Simulated anomalies and spikes
* Multi-subscription environments
* Regional resource distributions
* Environment tagging (prod/dev/test)

Features include:

* Time-series generation
* Statistical variance
* Realistic cloud spending behavior
* Usage growth simulation

---

# Background Job System

## Celery + Redis Architecture

### Celery Worker

Processes:

* anomaly detection
* forecasting
* analytics refresh
* scheduled data generation

### Celery Beat

Schedules periodic jobs:

| Job                             | Frequency |
| ------------------------------- | --------- |
| Daily synthetic data generation | Every 24h |
| Anomaly refresh                 | Every 1h  |
| Forecast refresh                | Every 6h  |

---

# API Endpoints

## Cost APIs

| Endpoint                         | Description            |
| -------------------------------- | ---------------------- |
| GET /api/v1/cost/summary         | Cost summary metrics   |
| GET /api/v1/cost/trend           | Daily trend analytics  |
| GET /api/v1/cost/by-service      | Service cost breakdown |
| GET /api/v1/cost/by-subscription | Subscription analysis  |

## Resource APIs

| Endpoint                            | Description         |
| ----------------------------------- | ------------------- |
| GET /api/v1/resources/top-expensive | Expensive resources |

## Alert APIs

| Endpoint                     | Description            |
| ---------------------------- | ---------------------- |
| GET /api/v1/alerts/anomalies | Cost anomaly detection |

## Analytics APIs

| Endpoint                              | Description                  |
| ------------------------------------- | ---------------------------- |
| GET /api/v1/analytics/forecast        | Future spend prediction      |
| GET /api/v1/analytics/recommendations | Optimization recommendations |

---

# Local Development Setup

## Prerequisites

* Docker
* Docker Compose
* Python 3.11+
* Node.js 20+

---

# Run Using Docker

## Start Containers

```bash
docker compose up --build
```

## Services

| Service  | URL                                                      |
| -------- | -------------------------------------------------------- |
| Frontend | [http://localhost:5173](http://localhost:5173)           |
| Backend  | [http://localhost:8000](http://localhost:8000)           |
| API Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

# Manual Development Setup

## Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Celery Worker

```bash
cd backend
celery -A tasks.celery_app worker --loglevel=info
```

## Celery Beat

```bash
cd backend
celery -A tasks.celery_app beat --loglevel=info
```

---

# Example API Calls

## Cost Summary

```bash
curl http://localhost:8000/api/v1/cost/summary
```

## Cost Trends

```bash
curl http://localhost:8000/api/v1/cost/trend?days=30
```

## Forecast

```bash
curl http://localhost:8000/api/v1/analytics/forecast
```

## Anomalies

```bash
curl http://localhost:8000/api/v1/alerts/anomalies
```

---

# Engineering Highlights

## Platform Engineering Concepts

* Distributed task execution
* Background job orchestration
* Reverse proxy architecture
* Containerized deployment
* Service separation
* Async analytics processing

## Analytics Concepts

* Statistical anomaly detection
* Moving averages
* Forecast confidence intervals
* Trend analysis
* Time-series analytics

## DevOps Concepts

* Dockerized services
* Multi-container orchestration
* Redis message broker
* Celery worker architecture
* Environment configuration management

---

# Future Enhancements

* Kubernetes deployment
* Prometheus + Grafana monitoring
* JWT authentication
* Role-based access control
* AI-powered forecasting
* LLM-powered FinOps assistant
* Multi-tenant architecture
* Real Azure Cost Management integration

---

# Project Value

This project demonstrates:

* Full-stack engineering
* Cloud-native architecture
* Background processing systems
* Analytics engineering
* Production-grade Dockerization
* SaaS platform design
* FinOps platform concepts
* DevOps + AI integration

---

# License

This project is intended for educational, portfolio, and learning purposes.
