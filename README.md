# Weather Data Drift Detection and Alert System

This project provides a full-stack weather monitoring application for detecting statistically significant distributional drift and anomalous behavior in historical weather observations.

## Overview

The platform supports searching global weather stations, examining historical observations, and running drift analysis using a backend pipeline built with FastAPI and a React frontend. Local development uses SQLite; PostgreSQL is the intended Azure deployment database.

## Features

- Global weather station search and selection
- Current and historical weather views
- Drift analysis with KS test, PSI, and Isolation Forest
- Alert generation and status tracking
- Role-based authentication with ADMIN, ANALYST, and VIEWER roles
- SQLAlchemy-backed storage (SQLite locally; PostgreSQL deployment target)
- Azure-focused deployment architecture and security documentation

## Architecture

- Frontend: React + Vite + Recharts
- Backend: FastAPI + SQLAlchemy + Pydantic
- Database: SQLite locally; PostgreSQL deployment target
- Analytics: NumPy, pandas, SciPy, scikit-learn
- Auth: JWT with hashed passwords

## Local Setup

1. Use Python 3.12, create a virtual environment, and install backend dependencies:
   ```bash
   py -3.12 -m venv backend/.venv
   backend/.venv/Scripts/python -m pip install -r backend/requirements.txt
   ```
2. Configure backend environment variables by copying the example file and editing it:
   ```bash
   copy backend\.env.example backend\.env
   ```
3. Start the backend:
   ```bash
   cd backend
   .venv\Scripts\python -m uvicorn app.main:app --reload
   ```
4. Start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Testing

```bash
cd backend
.venv\Scripts\python -m pytest
```

## Azure deployment

This project is designed for Azure App Service, Azure Static Web Apps, Azure Database for PostgreSQL Flexible Server, and Azure Application Insights / Azure Monitor.

## Limitations

This repository contains a production-style architecture and a working local MVP, but actual production deployment still requires Azure environment configuration, PostgreSQL provisioning, domain/DNS setup, and operational secrets management.
