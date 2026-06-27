# 🚀 Application Service (Labora Backend)

A Django-based backend service built as part of a microservice architecture. This service handles core application logic and integrates with authentication using JWT.

---

## 📌 Features

* 🔐 JWT Authentication (Public/Private key based)
* 🧩 Modular Django apps
* 🐳 Docker support
* 🔒 Secure environment configuration using `.env`
* ⚙️ Scalable microservice-ready structure

---

## 🏗️ Tech Stack

* **Backend:** Django, Django REST Framework
* **Authentication:** JWT (RS256)
* **Database:** SQLite (development)
* **Containerization:** Docker

---

## 📁 Project Structure

```
Application Service/
│
├── auth_service/        # Authentication service
├── myapp/               # Core application logic
├── jwt_keys/            # JWT keys (ignored in git)
├── manage.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/ApplicationService_labora.git
cd ApplicationService_labora
```

### 2️⃣ Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Setup environment variables

Create a `.env` file:

```
SECRET_KEY=your_secret_key
DEBUG=True
```

---

### 5️⃣ Run migrations

```bash
python manage.py migrate
```

---

### 6️⃣ Start server

```bash
python manage.py runserver
```

---

## 🐳 Run with Docker

```bash
docker build -t application-service .
docker run -p 8000:8000 application-service
```

---

## 🔐 Security Notes

* `.env`, `venv/`, `db.sqlite3`, and `jwt_keys/` are ignored using `.gitignore`
* Never commit private keys (`.pem`) or secrets

---

### Notifications
This service sends notifications for application events using the centralized Notification Service via labora_shared.notification_client.send_notification().

Emitted notification events:
- application_received: title="New Application", message="A freelancer applied to your job."
- proposal_accepted: title="Proposal Accepted", message="Your proposal has been accepted."
- proposal_rejected: title="Proposal Rejected", message="Your proposal was rejected."

Environment variables required:
- NOTIFICATION_SERVICE_URL
- SERVICE_API_KEY

Notification failures are logged and do not interrupt the primary application flow.

---

## 📌 Future Improvements

* Add PostgreSQL support
* API Gateway integration
* Service-to-service communication
* Deployment (AWS / Docker Compose)

---



