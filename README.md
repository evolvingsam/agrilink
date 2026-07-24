# AgriLink Nigeria - Backend

**AgriLink Nigeria** is an AI-powered farm-to-market platform built for the Nigerian agricultural sector. Inspired by Kenya's Twiga Foods model, AgriLink aims to solve Nigeria's post-harvest coordination crisis by connecting smallholder farmers directly to urban markets using AI, digital aggregation, and optimized logistics.

This repository contains the **Backend API** built with Django REST Framework (DRF), powered by **Google Gemma 4** for multilingual farmer communication and automated multimodal produce quality grading.

---

## 🚀 Features Currently Implemented (MVP)

1. **Authentication & Roles** (`accounts`)
   - JWT-based authentication.
   - Role-based access: `farmer`, `buyer`, `dispatcher`, `admin`.
   - Extended profiles for farmers capturing location and preferred language (Hausa, Yoruba, Igbo, Pidgin, English).

2. **Produce Marketplace** (`farmers`)
   - Crop reference data with perishability scores and shelf life.
   - Collection point management.
   - Produce listings with state tracking (pending, graded, matched, sold).

3. **AI Quality Grading** (`grading`)
   - Natively multimodal produce inspection.
   - Farmers upload a photo of their harvest, and Gemma 4 automatically assigns a grade (A, B, C, rejected), identifies issues, and estimates remaining shelf life.
   - *Includes a local mock mode for development without API keys.*

4. **AI Voice Assistant** (`ai_assistant`)
   - Multilingual conversational agent powered by Gemma 4.
   - Understands intent and extracts structured actions (e.g., automatically creating a produce listing from a chat message).
   - *Includes a local mock mode for development without API keys.*

---

## 🛠️ Tech Stack

- **Framework**: Django 6.0 + Django REST Framework 3.17
- **Database**: SQLite (Development) -> PostgreSQL (Production)
- **AI Models**: Google Gemma 4 (via Google AI Studio API)
- **Authentication**: DRF SimpleJWT
- **Documentation**: Swagger UI / drf-spectacular

---

## ⚙️ Local Development Setup

### 1. Prerequisites
- Python 3.10+
- pip

### 2. Clone and Install
```bash
# Navigate to the project directory
cd agrilink

# Install dependencies (virtual environment recommended)
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the example environment file:
```bash
cp .env.example .env
```
Edit `.env` and add your **Google AI Studio API Key** to enable real AI responses:
```
GOOGLE_AI_API_KEY=your-api-key-here
```
*(If you leave this blank, the app will gracefully fall back to mock AI responses).*

### 4. Database Setup & Seeding
Apply migrations and load the initial Nigerian crop data:
```bash
python manage.py migrate
python manage.py shell < seed.py
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Run the Server
```bash
python manage.py runserver
```
The API is now running at `http://127.0.0.1:8000/`.

---

## 📚 API Documentation

Interactive Swagger documentation is auto-generated and available at:
👉 **[http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)**

Use this to explore all endpoints, view request/response schemas, and test the API directly from your browser.

---

## 🏗️ System Architecture

AgriLink is built as a modern, decoupled web application:
- **Frontend**: A React single-page application (SPA) built with Vite. It communicates with the backend via REST APIs and is hosted on **Vercel**.
- **Backend**: A Django application providing RESTful APIs via Django REST Framework (DRF). It handles business logic, database operations (SQLite for dev, PostgreSQL for prod), and AI orchestration. It is hosted on **Render**.
- **AI Integration**: Deep integration with **Google's Gemma 4** (via Google AI Studio) for text processing (Voice Assistant) and multimodal vision tasks (Produce Grading).
- **Logistics Engine**: Uses **Google OR-Tools** to solve Vehicle Routing Problems (VRP) and dynamically generate dispatch routes based on orders and farm locations.

---

## 🔑 Test Accounts

You can test the application using the following pre-configured accounts:

| Role | Username | Password |
|---|---|---|
| **Buyer** | `godsown` | `mikky123` |
| **Farmer** | `mrv_farmer` | `mikky123` |

*(To test the Dispatcher features, create a user with the `dispatcher` role in the Django Admin panel).*

---

## 🔮 Future Roadmap (On Hold for Hackathon MVP)

- **Market Matching**: Algorithm to automatically connect buyer orders with graded produce listings based on proximity and shelf-life urgency.
- **Logistics & Routing**: Integration with Google OR-Tools for optimal dispatch routing.
- **Demand Forecasting**: Time-series ML (Prophet) to predict urban demand.
- **Payments**: Flutterwave/Paystack integration for same-day mobile money payouts to farmers upon delivery confirmation.
- **Cloud Storage**: AWS S3 integration for robust media hosting.
- **Background Tasks**: Celery + Redis for async AI processing and scheduled forecasting.
