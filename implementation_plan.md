# AgriLink Nigeria — Backend Implementation Plan

## Overview

**AgriLink Nigeria** is an AI-powered farm-to-market platform inspired by Kenya's Twiga Foods model. Nigeria loses **35–40 million metric tonnes** of food annually — not due to underproduction, but due to poor coordination: fragmented markets, weak cold-chain logistics, and slow payments. AgriLink addresses this by digitally aggregating smallholder farmers, applying AI-powered quality grading, demand forecasting, and route optimization — then guaranteeing fast mobile payments to farmers.

The AI layer is built on **Google Gemma 4** (open-weight, Apache 2.0), chosen because it:
- Runs offline on cheap Android phones (E2B/E4B variants — 2–4B params)
- Is natively multilingual (Hausa, Yoruba, Igbo, Pidgin — no translation layer needed)
- Is natively multimodal (image + voice/text in one model pass)
- Keeps sensitive farmer/price data on-device (data sovereignty)

> **Hackathon Scope**: Backend only. We are building the API server, AI integration services, data models, and business logic — NOT the mobile/web frontend.

---

## Problem → System Mapping

| Problem | AgriLink Solution | Backend Component |
|---|---|---|
| Farmers have no market access, rely on brokers | Digital produce listing via voice/text | Farmer & Produce APIs |
| Produce spoils before reaching market | AI quality grading from photos | Gemma Vision Grading Service |
| Oversupply/undersupply mismatches | Demand forecasting + smart matching | Forecasting Engine + Matching Service |
| Bad logistics, long delivery times | Route optimization + dispatch planning | Routing Service |
| Farmers paid weeks late | Same-day mobile money payout | Payments Integration Layer |

---

## System Architecture

```
                        ┌─────────────────────────────────────────┐
                        │            AgriLink Backend              │
                        │           (Django REST Framework)        │
                        └─────────────────────────────────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
    ┌─────────▼──────────┐    ┌────────────▼──────────┐    ┌───────────▼────────────┐
    │  Farmer & Produce  │    │   AI / Intelligence   │    │  Logistics & Payments  │
    │      Module        │    │       Module          │    │       Module           │
    │                    │    │                       │    │                        │
    │ • Farmer profiles  │    │ • Gemma 4 voice agent │    │ • Route optimization   │
    │ • Produce listings │    │ • Quality grading     │    │ • Dispatch management  │
    │ • Orders           │    │ • Demand forecasting  │    │ • Mobile money payout  │
    │ • Collection pts   │    │ • Market matching     │    │ • Payment tracking     │
    └────────────────────┘    └───────────────────────┘    └────────────────────────┘
              │                            │                            │
              └────────────────────────────┴────────────────────────────┘
                                           │
                                ┌──────────▼──────────┐
                                │    PostgreSQL DB      │
                                │  + Redis (cache/     │
                                │    task queue)       │
                                └─────────────────────┘
```

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| **API Framework** | Django + Django REST Framework | Battle-tested, excellent ORM, fast to scaffold REST APIs |
| **Database** | PostgreSQL | Relational data (farmers, orders, routes), PostGIS extension for geo queries |
| **Geo / Routing** | PostGIS + OR-Tools (Google) | Real route optimization (constraint solver), not LLM guessing |
| **AI — Language / Voice** | Gemma 4 via Ollama (local) or Google AI Studio API | On-device/low-cost LLM for farmer voice interface & report generation |
| **AI — Vision / Quality** | Gemma 4 multimodal (image+text) | Produce photo grading without extra encoder models |
| **Forecasting** | Prophet (Meta) or scikit-learn | Time-series demand forecasting per crop/region |
| **Task Queue** | Celery + Redis | Async AI inference, scheduled forecast jobs, payment retries |
| **Auth** | DRF SimpleJWT | JWT-based auth; separate roles for farmers, buyers, dispatchers, admins |
| **Storage** | AWS S3 / Cloudinary | Produce quality photos uploaded by farmers/aggregators |
| **Payments** | Flutterwave or Paystack API | Nigerian mobile money + bank transfer rails |
| **Voice STT** | Whisper (OpenAI, open-source) | Transcribe Hausa/Yoruba/Igbo voice input to text before Gemma processes it |
| **Containerization** | Docker + Docker Compose | Reproducible dev environment for hackathon demo |
| **API Docs** | drf-spectacular (OpenAPI 3) | Auto-generated Swagger docs for frontend/judges |

---

## Proposed Changes

---

### Project Scaffold

#### [NEW] Project root (`agrilink/`)

Standard Django project created via `django-admin startproject`. Split into focused Django apps:

```
agrilink/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── agrilink/             # project config
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
├── apps/
│   ├── accounts/         # User auth, roles
│   ├── farmers/          # Farmer profiles, produce listings
│   ├── buyers/           # Buyer profiles, orders
│   ├── grading/          # AI quality grading service
│   ├── forecasting/      # Demand forecasting engine
│   ├── matching/         # Farm-to-buyer matching
│   ├── logistics/        # Route optimization, dispatch
│   ├── payments/         # Flutterwave/Paystack integration
│   └── ai_assistant/     # Gemma 4 voice/chat agent
└── shared/
    ├── utils.py
    ├── permissions.py
    └── pagination.py
```

---

### Module 1: Accounts (`apps/accounts/`)

Authentication and role-based access control.

**Models:**
- `User` (extends AbstractUser) — `role` field: `farmer | buyer | dispatcher | admin`
- `FarmerProfile` — location (PostGIS `PointField`), phone, preferred_language (`ha | yo | ig | pcm`)
- `BuyerProfile` — business name, location, verified status

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register farmer, buyer, or dispatcher |
| POST | `/api/auth/login/` | JWT token pair |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/PUT | `/api/auth/me/` | Get/update own profile |

---

### Module 2: Farmers & Produce (`apps/farmers/`)

Core marketplace data — what's available for sale, where, when.

**Models:**
- `CollectionPoint` — name, location (PointField), has_cold_storage (bool), solar_powered (bool)
- `ProduceListing` — farmer, crop_type, quantity_kg, price_per_kg, harvest_date, status (`pending | graded | matched | sold`), collection_point, quality_grade (set by grading service)
- `CropType` — name, typical_shelf_life_days, perishability_score

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/produce/listings/` | Browse listings / farmer creates listing |
| GET/PUT/DELETE | `/api/produce/listings/{id}/` | Detail, update, remove listing |
| GET | `/api/produce/listings/?crop=tomato&region=kano` | Filter by crop, region, grade |
| GET/POST | `/api/collection-points/` | List/create collection points |
| POST | `/api/produce/listings/{id}/upload-photo/` | Upload produce photo (triggers grading) |

---

### Module 3: AI Quality Grading (`apps/grading/`)

Farmers or aggregation staff photograph produce at the collection point. The backend sends the image + a structured prompt to Gemma 4 multimodal, which returns a quality grade.

**How it works:**
1. Frontend (mobile) uploads image to S3 → sends `listing_id` + `image_url` to `/api/grading/assess/`
2. Backend queues a Celery task
3. Celery worker sends image + prompt to Gemma 4 (via Ollama API or Google AI Studio)
4. Gemma returns structured JSON: `{ "grade": "A|B|C|rejected", "issues": [...], "estimated_shelf_days": int, "confidence": float }`
5. `ProduceListing.quality_grade` is updated; farmer gets a push notification

**Gemma Prompt Template (system prompt):**
```
You are an agricultural quality inspector for Nigerian produce. Analyze the provided image 
of [crop_type] and return ONLY valid JSON with these fields:
- grade: "A" (premium), "B" (standard), "C" (below standard), or "rejected"
- issues: list of observed defects (e.g. ["early_mold", "bruising"])
- estimated_shelf_days: integer estimate of remaining shelf life
- confidence: float 0.0–1.0
```

**Models:**
- `GradingResult` — listing (FK), grade, issues (JSONField), shelf_days, confidence, graded_at, image_url

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/grading/assess/` | Submit image for AI grading (async) |
| GET | `/api/grading/results/{listing_id}/` | Get grading result for a listing |

---

### Module 4: Demand Forecasting (`apps/forecasting/`)

Predicts how much of each crop each market/region will need over the next 7–14 days, using historical order data.

**How it works:**
1. A scheduled Celery beat task runs daily at midnight
2. Pulls historical orders from DB grouped by `crop_type + region + week`
3. Runs **Prophet** (or SARIMA) forecasting model per crop/region pair
4. Stores forecast results in `DemandForecast` table
5. A second Celery task passes forecast results to Gemma 4 to generate a human-readable **coordinator briefing** in English or Hausa/Yoruba

**Models:**
- `DemandForecast` — crop_type, region, forecast_date, predicted_demand_kg, confidence_interval_low/high, generated_at
- `CoordinatorBriefing` — forecast_date, region, narrative_text (Gemma output), language

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/forecasting/demand/?region=kano&crop=tomato` | Get demand forecast |
| GET | `/api/forecasting/briefing/?region=kano&lang=ha` | Get Gemma-generated coordinator briefing |
| POST | `/api/forecasting/trigger/` | Admin: manually trigger forecast run |

---

### Module 5: Market Matching (`apps/matching/`)

Connects available produce listings with buyer orders, prioritizing by shelf life urgency, proximity, and grade requirements.

**Matching Algorithm:**
1. For each unmatched buyer order: find eligible listings (crop, grade ≥ required, quantity, region proximity)
2. Score each candidate: `score = (freshness_weight × shelf_days_remaining) + (proximity_weight × distance_km⁻¹) + (grade_weight × grade_score)`
3. Assign best-scoring listing(s) to the order
4. Update `ProduceListing.status = "matched"` and `Order.status = "matched"`
5. Trigger logistics task

**Models:**
- `BuyerOrder` — buyer, crop_type, quantity_kg, max_price_per_kg, required_grade, delivery_location (PointField), needed_by_date, status
- `Match` — listing (FK), order (FK), match_score, created_at

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| GET/POST | `/api/orders/` | Buyer creates order / lists own orders |
| GET | `/api/orders/{id}/` | Order detail + match status |
| POST | `/api/matching/run/` | Admin: manually trigger matching cycle |
| GET | `/api/matching/results/{order_id}/` | See which listings were matched |

---

### Module 6: Logistics & Route Optimization (`apps/logistics/`)

Once produce is matched, plan efficient pickup + delivery routes across matched listings.

**How it works:**
1. A Celery task groups matched listings by collection point + delivery zone
2. Passes waypoints to **Google OR-Tools** (Vehicle Routing Problem solver) to find optimal routes
3. Stores route plan in `DispatchRoute`
4. Gemma 4 generates a natural-language **route briefing** for the dispatcher ("Pick up tomatoes from Kano Central first, then swing to Zaria before heading to Lagos depot")

**Models:**
- `DispatchRoute` — dispatcher (FK User), matches (M2M), route_waypoints (JSONField), estimated_distance_km, estimated_duration_hrs, status (`planned | in_transit | delivered`), created_at
- `RouteWaypoint` — route (FK), location (PointField), sequence_order, notes

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/logistics/routes/` | Dispatcher sees their assigned routes |
| GET | `/api/logistics/routes/{id}/` | Route detail with waypoints |
| PUT | `/api/logistics/routes/{id}/status/` | Update route status (in_transit, delivered) |
| POST | `/api/logistics/routes/generate/` | Admin: trigger route generation |
| GET | `/api/logistics/routes/{id}/briefing/` | Get Gemma-narrated dispatch briefing |

---

### Module 7: Payments (`apps/payments/`)

Trigger and track farmer payouts via Flutterwave/Paystack once delivery is confirmed.

**How it works:**
1. Dispatcher marks route as `delivered` → webhook/signal triggers payment Celery task
2. Backend calls Flutterwave Transfer API: farmer's bank/phone receives payment in < 24 hrs
3. Payment record created; farmer and buyer both receive SMS/push confirmation

**Models:**
- `Payment` — farmer (FK), order (FK), amount_ngn, status (`pending | processing | completed | failed`), transaction_ref, provider (`flutterwave | paystack`), paid_at

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/payments/` | Farmer/admin lists payments |
| GET | `/api/payments/{id}/` | Payment detail |
| POST | `/api/payments/webhook/` | Flutterwave/Paystack webhook receiver |
| POST | `/api/payments/retry/{id}/` | Admin: retry failed payment |

---

### Module 8: AI Voice Assistant (`apps/ai_assistant/`)

Farmer-facing conversational agent. Farmers send voice notes or text (in any Nigerian language) and get responses in their language. Powered by Whisper (STT) + Gemma 4.

**Supported intents:**
- List produce for sale → creates `ProduceListing`
- Check order status → queries orders
- Get price quotes → queries recent market prices
- Ask agronomy questions → Gemma answers from its training knowledge

**How it works:**
1. Farmer sends voice audio file or text message to `/api/assistant/chat/`
2. If audio: Whisper transcribes it (language auto-detected)
3. Transcription + conversation history sent to Gemma 4 with system prompt (role: AgriLink farmer assistant)
4. Gemma returns a text response + optional structured action (`{"action": "create_listing", "data": {...}}`)
5. Backend executes the action (if any) and returns both the text reply and action result
6. Response can be TTS'd back to the farmer (optional, uses gTTS or a local model)

**Models:**
- `Conversation` — farmer (FK), created_at
- `Message` — conversation (FK), role (`farmer | assistant`), content, audio_url (if voice), language, timestamp

**Endpoints:**
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/assistant/chat/` | Send message (text or audio file) |
| GET | `/api/assistant/history/{conversation_id}/` | Get conversation history |
| POST | `/api/assistant/new/` | Start a new conversation session |

---

## Data Flow — End-to-End

```
Farmer (voice/photo)
       │
       ▼
[ai_assistant] Whisper STT → Gemma 4 agent
       │ creates listing
       ▼
[farmers] ProduceListing created (status: pending)
       │ photo uploaded
       ▼
[grading] Gemma 4 vision → quality_grade set (status: graded)
       │
       ▼
[matching] Algorithm matches listing ↔ BuyerOrder (status: matched)
       │
       ▼
[logistics] OR-Tools generates DispatchRoute
       │             │
       │         Gemma 4 writes dispatcher briefing
       ▼
[delivery confirmed]
       │
       ▼
[payments] Flutterwave Transfer API → farmer paid < 24h
```

---

## Open Questions

> [!IMPORTANT]
> **Gemma 4 deployment model**: Will we run Gemma locally via Ollama (slower inference, no API cost, works offline) or use Google AI Studio API (fast, requires internet)? For the hackathon demo, AI Studio API is recommended. Production would use on-device Ollama.

> [!IMPORTANT]
> **Forecasting bootstrap**: Prophet needs historical order data to produce meaningful forecasts. For the hackathon, should we seed the DB with synthetic historical data, or stub the forecasting endpoint with mock results?

> [!NOTE]
> **Payments sandbox**: Flutterwave and Paystack both have sandbox/test environments. For the hackathon demo we'll use test credentials — no real money moves.

> [!NOTE]
> **Voice/TTS response**: Should the assistant return text only, or also return an audio file (TTS) so the farmer hears the reply? TTS adds complexity but makes the demo more compelling.

---

## Verification Plan

### Automated Tests
```bash
python manage.py test apps.accounts
python manage.py test apps.farmers
python manage.py test apps.grading
python manage.py test apps.matching
python manage.py test apps.payments
python manage.py test apps.ai_assistant
```

### Manual Verification (Hackathon Demo Flow)
1. Register a farmer, a buyer, a dispatcher via `/api/auth/register/`
2. Farmer sends voice note in Yoruba → assistant lists produce
3. Upload produce photo → grading returns quality grade
4. Buyer creates an order → matching runs and connects to farmer listing
5. Route is generated → dispatcher sees briefing
6. Mark delivery complete → payment triggers and farmer receives confirmation

### API Documentation
Swagger UI auto-generated at `/api/docs/` via `drf-spectacular`.

---

## Hackathon Priorities (MVP Cut)

Given time constraints, the following order of implementation is recommended:

| Priority | Module | Justification |
|---|---|---|
| 🔴 P0 | Accounts + Farmers + Produce | Core data without which nothing else works |
| 🔴 P0 | AI Grading | Most visually impressive for a demo |
| 🔴 P0 | AI Voice Assistant | Differentiating feature — shows multimodal + multilingual |
| 🟡 P1 | Matching + Orders | Completes the marketplace loop |
| 🟡 P1 | Payments | Shows the farmer payment guarantee |
| 🟢 P2 | Forecasting | Impressive analytics feature but needs seeded data |
| 🟢 P2 | Logistics/Routing | Adds depth but OR-Tools integration takes time |
