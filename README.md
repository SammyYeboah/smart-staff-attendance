# Smart Staff Attendance System


Access Site using this link: https://smart-staff-attendance.onrender.com/web/login

An enterprise-grade attendance tracking system built with **FastAPI**, **PostgreSQL 18**, **SQLAlchemy**, and **JWT authentication**.  
Includes a **web frontend** (Jinja2 templates + vanilla JS) for staff and admins to interact with the system.

---

## 🚀 Features

- **User Management**
  - Register staff and admin accounts
  - Secure login with JWT tokens
  - Role-based access control (RBAC)

- **Attendance Tracking**
  - Clock-in and clock-out endpoints
  - View logs per user or institution-wide
  - Daily summaries and range queries

- **Reporting**
  - Export attendance logs to CSV
  - Admin dashboard for monitoring staff activity

- **Web Frontend**
  - Login and registration page
  - Staff dashboard for clock-in/out and viewing logs
  - Admin dashboard for managing users and reports

---

## 📂 Project Structure

GeoClock_AIT/
├── app/
│   ├── main.py                            # FastAPI entrypoint
│   ├── config.py                        # Environment configuration
│   ├── database.py                    # DB connection and session
│   ├── models.py                        # SQLAlchemy models
│   ├── schemas.py                      # Pydantic schemas
│   ├── security.py                    # Password hashing & JWT
│   ├── dependencies.py            # Auth dependencies
│   ├── routes/              # API routes
│   │   ├── auth.py                    # Register/login
│   │   ├── users.py                  # User endpoints
│   │   ├── attendance.py        # Attendance endpoints
│   │   ├── reports.py              # Reporting endpoints
│   │   ├── web.py                      # Web frontend routes
│   ├── web/                 # Frontend assets
│   │   ├── templates/       # Jinja2 HTML templates
│   │   └── static/          # CSS/JS
├── requirements.txt                  # Python dependencies
├── .env                     # Environment variables

Code

---

## ⚙️ Prerequisites

- Python 3.11+
- PostgreSQL 18 installed and running
- Node.js (optional, only if you want to extend frontend tooling)

---

## 🔧 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/GeoClock_AIT.git
   cd GeoClock_AIT
Create and activate a virtual environment

bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
Install dependencies

bash
pip install -r requirements.txt
Configure environment variables  
Create a .env file in the project root:

env
DATABASE_URL=postgresql://postgres:guggisburg@localhost:5432/smart_staff_attendance_db
SECRET_KEY=replace_with_a_long_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=120
Initialize the database  
Ensure PostgreSQL is running and create the database:

sql
CREATE DATABASE smart_staff_attendance_db;
Run the server

bash
uvicorn app.main:app --reload
🌐 Access Points
Swagger API Docs → http://127.0.0.1:8000/docs

Web Login → http://127.0.0.1:8000/web/login

Staff Dashboard → http://127.0.0.1:8000/web/dashboard

Admin Dashboard → http://127.0.0.1:8000/web/admin

Access Site using this link: https://smart-staff-attendance.onrender.com/web/login

🧑‍💻 Usage Flow
Register a user

Admin or staff can be registered via /web/login or API /users/register.

Login

Obtain a JWT token via /users/token (API) or login form (web).

Token is stored in browser localStorage for frontend use.

Staff actions

Clock-in/out via dashboard

View personal logs

Admin actions

View all users

View all attendance logs

Generate daily summaries

Export CSV reports

📊 Example API Calls
Register User

http
POST /users/register
Content-Type: application/json

{
  "name": "Samuel",
  "username": "samuel",
  "password": "mypassword",
  "role": "staff"
}
Login

http
POST /users/token
Content-Type: application/x-www-form-urlencoded

username=samuel&password=mypassword&grant_type=password
Clock In

http
POST /attendance/clock-in
Authorization: Bearer <token>
Content-Type: application/json

{ "user_id": 1 }
🛡️ Security Notes
Passwords are hashed with bcrypt.

JWT tokens expire after ACCESS_TOKEN_EXPIRE_MINUTES.

Admin-only endpoints enforce RBAC via dependency injection.

📌 Next Steps
Add GPS validation for on-site attendance

Add lateness/absence rules

Extend frontend with modern JS framework (React/Vue) if desired

👥 Contributors
Built by Samuel Adjei-Yeboah and collaborators