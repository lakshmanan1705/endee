<div align="center">

# Expanse Tracker

<p><strong>A modern single-page finance tracker for managing income, expenses, balance insights, and PDF reporting.</strong></p>

<p>
  <img src="https://img.shields.io/badge/Frontend-React-0ea5e9?style=for-the-badge" alt="React Badge" />
  <img src="https://img.shields.io/badge/Backend-Flask-1f2937?style=for-the-badge" alt="Flask Badge" />
  <img src="https://img.shields.io/badge/Database-SQLite-2563eb?style=for-the-badge" alt="SQLite Badge" />
  <img src="https://img.shields.io/badge/Reports-PDF-f59e0b?style=for-the-badge" alt="PDF Badge" />
</p>

</div>

---

## <img src="https://img.shields.io/badge/Project_Overview-0f172a?style=for-the-badge" alt="Project Overview" />

Expanse Tracker is a full-stack financial tracking application built for simple and efficient day-to-day money management. It allows users to record both income and expense transactions, monitor totals in real time, and generate professional PDF reports directly from the dashboard.

The project is designed as a single-page application with a React frontend, a Flask backend, and SQLite for lightweight local persistence.

## <img src="https://img.shields.io/badge/Core_Features-1d4ed8?style=for-the-badge" alt="Core Features" />

- Record income and expense transactions
- View all transactions in a single dashboard
- Track total income, total expense, and balance
- Delete transactions instantly
- Generate downloadable PDF reports
- Use a responsive interface for desktop and mobile devices

## <img src="https://img.shields.io/badge/Technology_Stack-0f766e?style=for-the-badge" alt="Technology Stack" />

| Layer | Technology |
| --- | --- |
| Frontend | React + Vite |
| Backend | Python + Flask |
| Database | SQLite |
| Reporting | ReportLab |

## <img src="https://img.shields.io/badge/Project_Structure-7c3aed?style=for-the-badge" alt="Project Structure" />

```text
expanse_tracker/
  backend/
    app.py
    requirements.txt
  frontend/
    index.html
    package.json
    vite.config.js
    src/
      App.jsx
      main.jsx
      styles.css
  .gitignore
  README.md
```

## <img src="https://img.shields.io/badge/Getting_Started-2563eb?style=for-the-badge" alt="Getting Started" />

### Prerequisites

- Python 3.10 or later
- Node.js 18 or later
- npm

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Backend URL: `http://127.0.0.1:5000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:5173`

## <img src="https://img.shields.io/badge/Application_Flow-f59e0b?style=for-the-badge" alt="Application Flow" />

1. The user creates an income or expense entry from the React dashboard.
2. The frontend sends the transaction data to the Flask API.
3. Flask validates and stores the record in SQLite.
4. The dashboard refreshes and updates totals automatically.
5. The report endpoint generates a PDF using the saved transaction data.

## <img src="https://img.shields.io/badge/API_Reference-111827?style=for-the-badge" alt="API Reference" />

### Health Check

`GET /api/health`

Example response:

```json
{
  "status": "ok"
}
```

### Get All Transactions

`GET /api/expenses`

### Create a Transaction

`POST /api/expenses`

Example request body:

```json
{
  "title": "Salary",
  "amount": 50000,
  "transaction_type": "income",
  "category": "Monthly Income",
  "expense_date": "2026-04-14",
  "notes": "April salary"
}
```

### Delete a Transaction

`DELETE /api/expenses/<id>`

### Generate PDF Report

`GET /api/report`

## <img src="https://img.shields.io/badge/Database_Details-334155?style=for-the-badge" alt="Database Details" />

The application uses a local SQLite database file created automatically inside the `backend` directory. No separate database server or external configuration is required.

The backend also supports automatic schema updates for existing databases, including the `transaction_type` field used for income and expense tracking.

## <img src="https://img.shields.io/badge/Future_Enhancements-059669?style=for-the-badge" alt="Future Enhancements" />

- Edit and update existing transactions
- Filter by category, type, or date
- Monthly and yearly analytics
- Search and sorting support
- Authentication and user profiles
- Dashboard charts and visual summaries

## <img src="https://img.shields.io/badge/License-475569?style=for-the-badge" alt="License" />

This project is currently intended for personal or internal use unless a separate license is added.
