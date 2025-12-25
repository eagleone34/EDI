# EDI.email

> **Transform complex EDI files into human-readable formats through email automation.**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 🎯 What is EDI.email?

EDI.email is a SaaS platform that converts EDI (Electronic Data Interchange) files into human-readable formats (PDF, Excel, HTML) with a unique email-first approach. Simply forward your EDI files to your personal email address and receive beautifully formatted documents back in seconds.

### The Problem

- 97.5% of SMBs struggle with EDI compliance
- Current solutions require 60-90 day implementation timelines
- Setup fees range from $500-$5,000
- Technical expertise required for SFTP/AS2 configuration

### Our Solution

**"Forward EDI files. Get readable PDFs. That's it."**

- ⚡ **5-minute setup** vs 60-90 days with competitors
- 📧 **Email-first automation** - no portals, no logins required
- 📄 **Multi-format output** - PDF, Excel, HTML
- 💰 **Transparent pricing** - $99/month unlimited, no hidden fees

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.11+, FastAPI |
| **Frontend** | Next.js 15, React 19, Tailwind CSS |
| **Database** | PostgreSQL |
| **Cache** | Redis |
| **Auth** | NextAuth.js |
| **Email** | AWS SES |
| **Storage** | AWS S3 |
| **Infrastructure** | Docker, AWS |

## 📁 Project Structure

```
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API endpoints
│   │   ├── parsers/  # EDI parsing logic
│   │   ├── generators/ # PDF/Excel/HTML generators
│   │   ├── models/   # Database models
│   │   └── services/ # Business logic
│   └── tests/
├── frontend/         # Next.js frontend
│   ├── app/          # App router pages
│   ├── components/   # React components
│   └── lib/          # Utilities
├── infrastructure/   # Docker & Terraform
├── docs/             # Documentation
└── samples/          # Sample EDI files
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/eagleone34/EDI.git
   cd EDI
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Or run services separately:**

   Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

   Frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📋 Supported EDI Transaction Sets

### Phase 1 (MVP)
- **850** - Purchase Order
- **810** - Invoice
- **856** - Advance Ship Notice (ASN)
- **855** - Purchase Order Acknowledgment
- **997** - Functional Acknowledgment

### Phase 2 (Coming Soon)
- 812, 820, 824, 846, 945, 940, and more...

## 🔒 Security

- All files encrypted at rest and in transit
- GDPR compliant
- Regular security audits
- SOC 2 Type II (planned)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

---

**EDI.email** - The Mailchimp of EDI. Dead simple automation that just works.
