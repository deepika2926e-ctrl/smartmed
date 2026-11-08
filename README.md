# SmartMed – Advanced Medicine Schedule Reminder System

SmartMed is a modern, full-stack medication schedule reminder and healthcare tracking SaaS platform built with **Python FastAPI**, **MySQL / SQLAlchemy**, and a **Responsive Healthcare UI**.

Designed to replace outdated PHP/XAMPP stacks, SmartMed delivers high-performance REST APIs, verified educational drug monographs (sourced from MedlinePlus and NHS), multi-time daily scheduling, synthesized Web Audio reminders, prescription document management, adherence analytics, and PDF reports.

---

## 🌟 Key Features

1. **Patient Authentication & Strict Privacy Isolation**
   - JWT authentication (`HS256`) with secure `bcrypt` password hashing.
   - Strict database tenant separation (`user_id = current_user.id`) on all endpoints: User A never sees or modifies User B's medications or schedules.

2. **Medicine Management**
   - Add, edit, delete, and view prescribed medications.
   - Specify dosage, formulation (tablet, capsule, syrup, inhaler, drops, etc.), frequency, physician, start/end dates, and food relation instructions.
   - Upload and attach physical prescription scans (JPG, PNG, PDF).

3. **Intelligent Multi-Time Scheduling**
   - Morning, Afternoon, Evening, Night, and Custom reminder time slots.
   - Multi-dose scheduling per day with custom days-of-the-week selections.
   - 1-click dose actions: **Mark Taken**, **Mark Skipped**, or **Snooze (15m, 30m, 1h)**.

4. **Reminders & Alerts**
   - HTML5 Web Browser Notifications API integration.
   - Synthesized Web Audio API medical chime (E5 &bull; B5 chime) that works without missing external audio files.
   - In-app notification center with live unread badge counters.

5. **Verified Educational Drug Monograph**
   - Preloaded drug library with indications, mechanism of action, available formulations, common side effects, serious red-flag warnings, drug interactions, and storage guidelines.
   - Clinical educational disclaimer distinguishing general education from medical prescription advice.

6. **Adherence Reports & Analytics**
   - 7-day, 30-day, and 90-day adherence rate calculations (`%`).
   - Active streak tracking (consecutive days of 80%+ adherence).
   - Interactive charts via Chart.js.
   - Export printable PDF reports formatted for clinical doctor visits via `html2pdf.js`.

---

## 🏗️ Project Folder Structure

```
smartmed/
│
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point & CORS
│   │   ├── config.py            # Pydantic Settings configuration
│   │   ├── database.py          # SQLAlchemy engine, connection pool & fallback
│   │   ├── models/              # SQLAlchemy database models
│   │   │   ├── user.py
│   │   │   ├── medicine.py
│   │   │   ├── schedule.py
│   │   │   ├── log.py
│   │   │   ├── notification.py
│   │   │   ├── prescription.py
│   │   │   ├── settings.py
│   │   │   └── medicine_info.py
│   │   ├── schemas/             # Pydantic v2 validation models
│   │   ├── routes/              # Modular REST API endpoints
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── medicines.py
│   │   │   ├── medicine_info.py
│   │   │   ├── schedules.py
│   │   │   ├── logs.py
│   │   │   ├── notifications.py
│   │   │   ├── prescriptions.py
│   │   │   ├── reports.py
│   │   │   └── settings.py
│   │   ├── services/            # Reminder engine, seed data, adherence stats
│   │   └── security/            # Bcrypt hashing & JWT bearer token validation
│   ├── requirements.txt
│   ├── .env.example
│   └── .env
│
├── frontend/
│   ├── index.html               # 1. Home landing page
│   ├── login.html               # 2. Login page
│   ├── register.html            # 3. Registration page
│   ├── dashboard.html           # 4. Main interactive dashboard
│   ├── add-medicine.html        # 5. Add medicine module
│   ├── medicines.html           # 6. My medicines list & management
│   ├── medicine-details.html    # 7. Educational medicine details & monograph
│   ├── medicine-search.html     # 8. Educational medicine search & filters
│   ├── schedule.html            # 9. Medicine schedule manager
│   ├── today.html               # 10. Today's medicines checklist
│   ├── upcoming.html            # 11. Upcoming reminders feed
│   ├── notifications.html       # 12. In-app notifications center
│   ├── history.html             # 13. Dose history & tracking logs
│   ├── reports.html             # 14. Adherence reports & PDF export
│   ├── profile.html             # 15. User profile & password management
│   ├── settings.html            # 16. Preferences, audio, & timezone settings
│   ├── about.html               # 17. About Us & clinical advisory
│   ├── contact.html             # 18. Contact Us & FAQs
│   ├── css/
│   │   └── styles.css           # Premium healthcare styling & dark mode
│   └── js/
│       ├── api.js               # Central API client & error toasts
│       ├── auth.js              # Route guard & navbar UI state
│       └── notifications.js     # Web Audio chime & browser notifications
│
├── database/
│   └── smartmed.sql             # Complete MySQL DDL schema & sample data
│
├── uploads/                     # Uploaded prescription storage
├── render.yaml                  # Render deployment configuration
├── Dockerfile                   # Containerized production deployment
└── README.md
```

---

## 🚀 Local Development Setup (Without XAMPP)

### Prerequisites
- Python 3.11+
- Git

### 1. Set Up Python Virtual Environment
Open PowerShell or CMD in the project directory:

```powershell
cd "C:\Users\MY PC\Desktop\smartmed\backend"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

*(On standard Windows CMD: `venv\Scripts\activate.bat`)*

### 2. Install Backend Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Database Configuration

#### Option A: Running with Local or Cloud MySQL
If you have MySQL installed locally or an external cloud MySQL instance (e.g., TiDB Serverless, Aiven, or Railway):
1. Import the schema into MySQL:
   ```bash
   mysql -u root -p < ../database/smartmed.sql
   ```
2. Update `backend/.env` with your MySQL connection string:
   ```env
   DATABASE_URL=mysql+pymysql://root:password@localhost:3306/smartmed?charset=utf8mb4
   ```

#### Option B: Zero-Config Out-of-the-Box Development (Automatic SQLite Fallback)
If MySQL is not installed locally or not currently running, SmartMed automatically activates its built-in fallback engine (`smartmed.db`). Tables are automatically generated and educational data is seeded seamlessly upon launch. No XAMPP required!

### 4. Start the FastAPI Server

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Interactive Swagger API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Frontend Application:** Open `http://localhost:8000/app/index.html` or open `frontend/index.html` in your browser (or via VS Code Live Server).

---

## 🧪 Testing the Application

1. **Create an Account:**
   - Open `http://localhost:8000/app/register.html`.
   - Register a new patient account with name, email, and password.
2. **Explore the Dashboard:**
   - View your personalized metrics, streak counter, and dose checklist.
3. **Add a Medicine:**
   - Navigate to **Add Medicine** (`add-medicine.html`).
   - Add a prescription (e.g., *Amoxicillin 500mg, Twice daily, After meals*).
   - Check the **Auto-create schedule** toggle to schedule morning and evening doses.
4. **Log Today's Doses:**
   - Go to **Today's Doses** (`today.html`).
   - Click **Take** &bull; listen for the Web Audio chime and watch your adherence bar advance!
5. **Search Medicine Information:**
   - Go to **Medicine Search** (`medicine-search.html`).
   - Search for *Metformin* or *Paracetamol*, view side effects, precautions, and click **Prescribe** to link it to your profile.
6. **Download a PDF Adherence Report:**
   - Go to **Reports & Analytics** (`reports.html`).
   - Review your weekly adherence graphs and click **Download PDF Report**.
7. **Verify Multi-User Privacy:**
   - Open an incognito browser window, register a second account (e.g. *User B*).
   - Confirm that User B sees only their own medications and schedule, with zero access to User A's data.

---

## 🌐 Public Render Deployment Guide

Follow these steps to deploy SmartMed live to the internet on Render with a persistent MySQL database:

### Step 1: Provision Free Persistent MySQL Database
Because Render web services have ephemeral local storage, connect to a free persistent cloud MySQL database:
1. **TiDB Cloud (Free Serverless MySQL):** [https://tidbcloud.com](https://tidbcloud.com) (Recommended: 5GB free, instant MySQL 8 compatible).
   *OR* **Aiven MySQL / Railway:** [https://aiven.io](https://aiven.io).
2. Create a cluster named `smartmed`.
3. In the database console, execute the script in `database/smartmed.sql` (or allow FastAPI to create the tables automatically).
4. Copy your MySQL connection URL:
   `mysql+pymysql://<username>:<password>@<host>:<port>/smartmed?ssl_verify_cert=true`

### Step 2: Push Your Project to GitHub
Initialize git and push your repository:

```powershell
cd "C:\Users\MY PC\Desktop\smartmed"
git init
git add .
git commit -m "Initial commit: Complete SmartMed application"
git branch -M main
git remote add origin https://github.com/<your-username>/smartmed.git
git push -u origin main
```

### Step 3: Deploy to Render
1. Log in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** &rarr; **Blueprint** (or **Web Service**).
3. Connect your `smartmed` GitHub repository. Render will automatically read `render.yaml`.
4. Under Environment Variables in the Render dashboard, configure:
   - `DATABASE_URL`: Your persistent cloud MySQL connection string from Step 1.
   - `SECRET_KEY`: A secure random secret string (e.g. 64-char hex).
   - `CORS_ORIGINS`: `*`
   - `APP_ENV`: `production`
5. Click **Apply / Deploy**.

### Step 4: Verification
Render will build the application and issue your public live URLs:
- **Public Website URL:** `https://smartmed-api.onrender.com/app/index.html` (or root `https://smartmed-api.onrender.com/`)
- **FastAPI Swagger URL:** `https://smartmed-api.onrender.com/docs`
- **Health Endpoint:** `https://smartmed-api.onrender.com/api/health`

---

## 🛡️ Medical Disclaimer
SmartMed is a medication reminder and adherence tracking software tool. The monographs contained in the educational library are compiled from verified public health resources (MedlinePlus, NHS UK, FDA) for general informational reference only. SmartMed does not dispense medical advice, diagnosis, or clinical therapy. Patients must always follow the instructions of their licensed physician.
#   s m a r t m e d  
 