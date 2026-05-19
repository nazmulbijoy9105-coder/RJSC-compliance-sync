# ComplianceSync

**Real-Time Corporate Compliance Dashboard for Bangladesh**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)]()
[![Next.js](https://img.shields.io/badge/Next.js-000000?logo=next.js&logoColor=white)]()
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)]()
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)]()

## Overview

ComplianceSync is a deterministic compliance rules engine and dashboard for Bangladesh companies. It automatically calculates all RJSC, NBR tax, and BSEC corporate governance deadlines based on company metadata, tracks filing status, and alerts stakeholders before penalties accrue.

### Key Features

- **Deterministic Rules Engine**: 30+ Bangladesh corporate compliance rules encoded as deterministic functions
- **Auto-Generated Compliance Calendar**: All deadlines calculated from incorporation date and fiscal year
- **Penalty Calculator**: Real-time penalty estimation for overdue filings
- **Multi-Entity Management**: Track compliance across multiple companies
- **Document Repository**: Centralized storage for compliance documents
- **Risk Heatmap**: Visual compliance status across all entities
- **BSEC Governance Tracking**: Public company corporate governance compliance

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ComplianceSync v1.0-beta                 │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Next.js 15)      │  Backend (FastAPI)             │
│  ├─ React Query             │  ├─ Deterministic Rules      │
│  ├─ Tailwind CSS            │  │   Engine                   │
│  ├─ shadcn/ui               │  ├─ PostgreSQL + AsyncPG     │
│  └─ Zustand Auth            │  ├─ JWT Security              │
│                             │  ├─ File Upload              │
│                             │  └─ Celery Tasks             │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **FastAPI** - High-performance async Python web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Pydantic** - Data validation and settings management
- **python-jose** - JWT token handling
- **Celery + Redis** - Background task processing
- **Alembic** - Database migrations

### Frontend
- **Next.js 15** - React framework with App Router
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Re-usable component primitives
- **TanStack Query** - Server state management
- **Zustand** - Client state management
- **Lucide React** - Icon library

### Infrastructure
- **PostgreSQL 16** - Primary database
- **Redis 7** - Caching and task queue
- **Docker + Docker Compose** - Containerization
- **Vercel** - Frontend hosting (free tier)
- **Render/Railway** - Backend hosting (free tier)

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/compliancesync.git
cd compliancesync

# Copy environment
cp .env.example .env

# Start all services
docker-compose up -d

# Backend will be at http://localhost:8000
# Frontend will be at http://localhost:3000
# API docs at http://localhost:8000/docs
```

### Manual Setup

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup database
alembic upgrade head

# Run server
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Compliance Rules Engine

The deterministic rules engine calculates:

| Category | Rules | Deadlines |
|----------|-------|-----------|
| **RJSC** | 13 | AGM (180d), Schedule X (21d after AGM), Balance Sheet (30d), Director Changes (14d), Share Transfers (60d), etc. |
| **NBR Tax** | 10 | Corporate Tax (15 Mar), Advance Tax (quarterly), VAT (monthly), TDS (quarterly) |
| **BSEC** | 7 | Q1/Q2/Q3 Reports (45d), CG Certificate (30d after AGM), Director Shareholding (30d) |
| **Penalties** | 5 | Daily fines, interest calculations, BSEC penalties |

### Deterministic Properties

1. **Same inputs → Same outputs**: Given identical company metadata, the engine produces identical compliance calendars
2. **Traceable**: Every deadline can be traced to specific Bangladesh law provisions
3. **Versioned**: Rules are versioned; historical compliance can be recalculated
4. **Auditable**: All calculations logged with reasoning trace

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Current user

### Companies
- `POST /api/v1/companies/` - Create company
- `GET /api/v1/companies/` - List companies
- `GET /api/v1/companies/{id}` - Company detail
- `POST /api/v1/companies/{id}/directors` - Add director
- `POST /api/v1/companies/{id}/shareholders` - Add shareholder
- `POST /api/v1/companies/{id}/regenerate-calendar` - Regenerate compliance calendar

### Compliance
- `GET /api/v1/compliance/events` - List compliance events
- `GET /api/v1/compliance/events/{id}` - Event detail
- `PATCH /api/v1/compliance/events/{id}` - Update event status
- `GET /api/v1/compliance/risk-heatmap` - Risk heatmap data

### Dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/compliance-scores` - Compliance scores

### Documents
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/` - List documents

## Deployment

### Frontend (Vercel - Free Tier)
```bash
cd frontend
vercel --prod
```

### Backend (Render - Free Tier)
1. Connect GitHub repo to Render
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`

### Database (Supabase/Neon - Free Tier)
- Create PostgreSQL instance
- Update `DATABASE_URL` in environment variables

## Pricing

| Tier | Price | Features |
|------|-------|----------|
| **Starter** | BDT 3,000/month | 1 company, basic compliance calendar, email alerts |
| **Professional** | BDT 15,000/month | 5 companies, BSEC governance, multi-user, priority support |
| **Enterprise** | BDT 50,000/month | Unlimited companies, API access, custom integrations, dedicated manager |

## Roadmap

### Phase 1 (Current)
- [x] Core compliance rules engine
- [x] RJSC deadline calculation
- [x] NBR tax deadline calculation
- [x] Basic dashboard
- [x] Document upload

### Phase 2 (Q3 2026)
- [ ] BSEC full governance tracking
- [ ] Email/SMS reminder system
- [ ] RJSC portal API integration
- [ ] NBR e-filing integration
- [ ] Mobile app (React Native)

### Phase 3 (Q4 2026)
- [ ] AI-powered document extraction
- [ ] Predictive compliance analytics
- [ ] Multi-jurisdiction (UK, Singapore)
- [ ] White-label for law firms
- [ ] Open API for third-party integrations

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## License

MIT License - see [LICENSE](LICENSE) file

## Contact

**ComplianceSync**  
Built with determination in Dhaka, Bangladesh

For support: support@compliancesync.io

---

**Disclaimer**: ComplianceSync provides compliance tracking and deadline calculation based on publicly available Bangladesh corporate law. It does not constitute legal advice. Always consult with a qualified company secretary or legal professional for specific compliance matters.
# RJSC-compliance-sync
