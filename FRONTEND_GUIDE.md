# AgriLink Nigeria — Frontend Implementation Guide

This is the definitive integration guide for frontend developers building the AgriLink Nigeria mobile or web application. It documents every backend endpoint available today, the exact request and response shapes, authentication rules, role behaviour, and a roadmap of future endpoints that should be anticipated in the frontend architecture.

---

## Table of Contents

1. [Tech Stack Recommendation](#1-tech-stack-recommendation)
2. [User Personas & Flows](#2-user-personas--flows)
3. [Global API Conventions](#3-global-api-conventions)
4. [Authentication Endpoints](#4-authentication-endpoints)
5. [Produce & Marketplace Endpoints](#5-produce--marketplace-endpoints)
6. [AI Grading Endpoints](#6-ai-grading-endpoints)
7. [AI Assistant Endpoints](#7-ai-assistant-endpoints)
8. [UI/UX Guidelines](#8-uiux-guidelines)
9. [Market Matching & Orders Endpoints](#9-market-matching--orders-endpoints)
10. [Logistics & Routing Endpoints](#10-logistics--routing-endpoints)
11. [Payments Endpoints](#11-payments-endpoints)
12. [Future Endpoints (Coming Soon)](#12-future-endpoints-coming-soon)
---

## 1. Tech Stack Recommendation

Given the target demographic — rural Nigerian farmers with low-end Android phones and patchy connectivity — the frontend must be lightweight, offline-capable, and voice-friendly.

| Layer | Recommended Option | Reason |
|---|---|---|
| **Framework** | React Native (Expo) **or** Next.js PWA | Expo for native app; Next.js PWA avoids app store friction for hackathon |
| **Styling** | Tailwind CSS | Rapid, consistent UI development |
| **State Management** | Zustand | Lightweight, no boilerplate |
| **Data Fetching** | TanStack Query (React Query) | Built-in caching, offline mutations, retry logic |
| **Forms** | React Hook Form + Zod | Type-safe form validation |
| **Voice Input** | `expo-av` (RN) or Web Audio API (PWA) | Recording voice notes for AI chat |
| **HTTP Client** | Axios with an interceptor | Attaches JWT automatically to every request |

---

## 2. User Personas & Flows

The backend supports three roles. The UI must show different screens depending on the `role` returned in the user profile.

### A. Farmer (Priority: P0)
*Dead-simple, voice-first interface.*
1. **Register / Login** → lands on their personal dashboard.
2. **Chat with AI** → WhatsApp-like screen, text or hold-to-speak voice.
3. **Create Listing** → via chat intent OR a simple manual form.
4. **Upload Photo** → take a photo of harvest → AI grading fires automatically.
5. **My Listings Dashboard** → card list with live status badges (Pending → Graded → Matched → Sold).

### B. Buyer (Priority: P1)
*B2B marketplace interface.*
1. **Browse Marketplace** → filterable listing grid (by crop, region, grade).
2. **View Listing Detail** → see grade, shelf life, price, collection point.
3. **Place Order** *(future)* → request specific quantity.

### C. Dispatcher (Priority: P2 — Future)
*Logistics map dashboard.*
1. **View Assigned Routes** → map with waypoints.
2. **Update Route Status** → tap to mark pickup / delivery done.

---

## 3. Global API Conventions

### Base URL
```
http://127.0.0.1:8001/api/   ← Local development (port 8001)
```
*Production base URL will be provided separately once deployed.*

### Authentication
- **All endpoints require authentication** except `POST /auth/register/` and `POST /auth/login/`.
- Attach the access token to every request in the `Authorization` header:
  ```
  Authorization: Bearer <access_token>
  ```

### Axios Interceptor Setup (Recommended)
```javascript
// lib/api.js
import axios from 'axios';

const api = axios.create({ baseURL: 'http://127.0.0.1:8001/api/' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token'); // or SecureStore in RN
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;
```

### Pagination
List endpoints return paginated responses (20 items per page):
```json
{
  "count": 120,
  "next": "http://127.0.0.1:8001/api/produce/listings/?page=2",
  "previous": null,
  "results": [ ...array of objects... ]
}
```

### Error Responses
All validation errors follow DRF's standard format:
```json
{
  "field_name": ["Error message here."],
  "non_field_errors": ["Password do not match."]
}
```
HTTP status codes to handle: `400` (validation), `401` (unauthenticated), `403` (permission denied), `404` (not found).

### Interactive Docs
Test every endpoint live in the browser at:
👉 **`http://127.0.0.1:8001/api/docs/`**

---

## 4. Authentication Endpoints

**Prefix:** `/api/auth/`

---

### `POST /api/auth/register/`
Register a new user. Use `role` to identify the user type.

**Auth required:** ❌ No

**Request Body:**
```json
{
  "username": "aminu_kano",
  "email": "aminu@example.com",
  "password": "SecurePass123!",
  "password2": "SecurePass123!",
  "first_name": "Aminu",
  "last_name": "Musa",
  "role": "farmer",
  "phone": "08012345678",

  // Farmer-only fields (ignored for other roles):
  "state": "Kano",
  "lga": "Kano Municipal",
  "preferred_language": "ha"
}
```

**`role` choices:** `farmer` | `buyer` | `dispatcher`

**`preferred_language` choices:** `ha` (Hausa) | `yo` (Yoruba) | `ig` (Igbo) | `pcm` (Pidgin) | `en` (English)

**Response `201 Created`:**
```json
{
  "username": "aminu_kano",
  "email": "aminu@example.com",
  "first_name": "Aminu",
  "last_name": "Musa",
  "role": "farmer",
  "phone": "08012345678"
}
```
> ⚠️ Passwords are **write-only** and never returned. After registration, immediately call `/auth/login/` to obtain tokens.

---

### `POST /api/auth/login/`
Obtain JWT access and refresh tokens.

**Auth required:** ❌ No

**Request Body:**
```json
{
  "username": "aminu_kano",
  "password": "SecurePass123!"
}
```

**Response `200 OK`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs...",
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```
> **Frontend task:** Store both tokens securely. Use `access` for API calls. When it expires (after 12 hours), use the `refresh` token to get a new one without asking the user to log in again.

---

### `POST /api/auth/token/refresh/`
Get a new access token using a valid refresh token.

**Auth required:** ❌ No

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response `200 OK`:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIs..."
}
```
> **Frontend task:** Build an Axios response interceptor that catches `401` errors, automatically calls this endpoint, stores the new `access` token, and retries the original request. This creates a seamless session for users.

---

### `GET /api/auth/me/`
Get the currently authenticated user's full profile.

**Auth required:** ✅ Yes

**Response `200 OK`:**
```json
{
  "id": 5,
  "username": "aminu_kano",
  "email": "aminu@example.com",
  "first_name": "Aminu",
  "last_name": "Musa",
  "role": "farmer",
  "phone": "08012345678",
  "farmer_profile": {
    "state": "Kano",
    "lga": "Kano Municipal",
    "preferred_language": "ha",
    "farm_size_hectares": "2.50"
  }
}
```
> `farmer_profile` is `null` for buyers and dispatchers.
> **Frontend task:** Call this immediately after login to determine `role` and render the correct dashboard.

---

### `PUT /api/auth/me/`
Update the authenticated user's profile fields.

**Auth required:** ✅ Yes

**Request Body (all fields optional — partial update):**
```json
{
  "first_name": "Aminu",
  "phone": "08099999999"
}
```

**Response `200 OK`:** Returns the updated user object (same shape as `GET /auth/me/`).

---

## 5. Produce & Marketplace Endpoints

**Prefix:** `/api/produce/`

---

### `GET /api/produce/crops/`
Fetch the list of all crop types. Use this to populate dropdowns in the "Create Listing" form.

**Auth required:** ✅ Yes

**Response `200 OK` (paginated):**
```json
{
  "count": 8,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Tomato",
      "typical_shelf_life_days": 7,
      "perishability_score": 9
    },
    {
      "id": 2,
      "name": "Cassava",
      "typical_shelf_life_days": 14,
      "perishability_score": 4
    }
    // ... 6 more
  ]
}
```
> **Frontend task:** Cache this list aggressively (it rarely changes). Use it to populate dropdowns in both the manual listing form and the buyer marketplace filter.

**Search:** Add `?search=tom` to filter by name.

---

### `GET /api/produce/collection-points/`
List all known collection/aggregation points where farmers drop off produce.

**Auth required:** ✅ Yes

**Response `200 OK` (paginated):**
```json
{
  "results": [
    {
      "id": 1,
      "name": "Kano Central Market Hub",
      "state": "Kano",
      "lga": "Kano Municipal",
      "address": "Off Bompai Road, Kano",
      "has_cold_storage": true,
      "solar_powered": true,
      "latitude": "12.000400",
      "longitude": "8.592200"
    }
  ]
}
```
> **Frontend task:** Let farmers choose a collection point when listing produce. Show `has_cold_storage` as a badge — cold storage is a selling point for perishables.

**Search:** Add `?search=kano` to filter by name, state, or LGA.

---

### `GET /api/produce/listings/`
Fetch produce listings. **Behaviour differs by role:**

- **Farmer** → Returns only that farmer's own listings (all statuses).
- **Buyer / Dispatcher / Admin** → Returns all listings that have been graded (excludes `pending` and `expired`).

**Auth required:** ✅ Yes

**Query Parameters (for Buyers/Admins only):**

| Parameter | Type | Example | Description |
|---|---|---|---|
| `crop` | string | `?crop=tomato` | Filter by crop name (case-insensitive, partial match) |
| `region` | string | `?region=kano` | Filter by collection point state |
| `grade` | string | `?grade=A` | Filter by grade (`A`, `B`, `C`) |
| `search` | string | `?search=cassava` | Full-text search on crop name and state |
| `page` | integer | `?page=2` | Pagination |

**Response `200 OK` (paginated):**
```json
{
  "results": [
    {
      "id": 12,
      "farmer": 5,
      "farmer_name": "aminu_kano",
      "crop_type": 1,
      "crop_name": "Tomato",
      "collection_point": 1,
      "collection_point_name": "Kano Central Market Hub",
      "quantity_kg": "150.00",
      "price_per_kg": "450.00",
      "harvest_date": "2026-07-20",
      "status": "graded",
      "quality_grade": "A",
      "photo": "http://127.0.0.1:8001/media/produce/photos/tomato_abc.jpg",
      "notes": "Freshly harvested, no chemical spray",
      "created_at": "2026-07-22T10:30:00Z",
      "updated_at": "2026-07-22T11:00:00Z"
    }
  ]
}
```

---

### `POST /api/produce/listings/`
Farmer creates a new produce listing. The `farmer` is auto-assigned from the JWT — do not send it.

**Auth required:** ✅ Yes (Farmer role)

**Request Body:**
```json
{
  "crop_type": 1,
  "collection_point": 1,
  "quantity_kg": "150.00",
  "price_per_kg": "450.00",
  "harvest_date": "2026-07-20",
  "notes": "Freshly harvested, no chemical spray"
}
```

> `collection_point` is optional. `notes` is optional.

**Response `201 Created`:** Returns the full listing object with `status: "pending"` and `quality_grade: "ungraded"`.

---

### `GET /api/produce/listings/{id}/`
Get a single listing's full detail.

**Auth required:** ✅ Yes

**Response `200 OK`:** Same shape as items in the list response above.

---

### `PUT /api/produce/listings/{id}/`
Update a listing. Only the owning farmer can do this.

**Auth required:** ✅ Yes (Owner farmer only)

**Request Body (partial update — send only what changed):**
```json
{
  "quantity_kg": "120.00",
  "price_per_kg": "480.00"
}
```

**Response `200 OK`:** Returns the updated listing object.

---

### `DELETE /api/produce/listings/{id}/`
Remove a listing. Only the owning farmer can do this.

**Auth required:** ✅ Yes (Owner farmer only)

**Response `204 No Content`**

---

### `POST /api/produce/listings/{id}/upload-photo/`
Upload a produce photo for a listing. **This automatically triggers AI quality grading** — no separate grading call is needed after this.

**Auth required:** ✅ Yes (Owner farmer only)

**Content-Type:** `multipart/form-data`

**Request Form Fields:**
| Field | Type | Description |
|---|---|---|
| `photo` | File (image) | JPEG, PNG, or WebP. Max ~10MB practical limit. |

**Example (JavaScript fetch):**
```javascript
const formData = new FormData();
formData.append('photo', imageFile); // imageFile from file picker or camera

const response = await api.post(
  `/produce/listings/${listingId}/upload-photo/`,
  formData,
  { headers: { 'Content-Type': 'multipart/form-data' } }
);
```

**Response `200 OK`:**
```json
{
  "message": "Photo uploaded. Grading complete.",
  "listing_id": 12,
  "grading": {
    "grade": "A",
    "issues": [],
    "estimated_shelf_days": 6,
    "confidence": 0.92
  }
}
```
> **`grade`** → `"A"`, `"B"`, `"C"`, or `"rejected"`
> **`issues`** → Array of strings e.g. `["early_mold", "bruising"]`. Empty array means no defects found.
> **`estimated_shelf_days`** → Integer. Days before produce is no longer saleable.
> **`confidence`** → Float 0.0–1.0. How certain the AI is.

> **Frontend task:** After uploading, poll or use the returned data to update the listing card's status badge from "Pending Grading" to the actual grade. Show a scanning animation while the upload + grading is in progress.

---

## 6. AI Grading Endpoints

**Prefix:** `/api/grading/`

These endpoints are used when you need to trigger grading or fetch its result separately (e.g., if the photo was already uploaded but grading failed, or you want to re-display past results).

---

### `POST /api/grading/assess/`
Manually trigger AI grading for a listing that already has a photo attached.

**Auth required:** ✅ Yes (Owner farmer or Admin)

**Request Body:**
```json
{
  "listing_id": 12
}
```

**Response `200 OK`:**
```json
{
  "grade": "B",
  "issues": ["minor_bruising"],
  "estimated_shelf_days": 4,
  "confidence": 0.88
}
```

---

### `GET /api/grading/results/{listing_id}/`
Fetch the stored grading result for a specific listing.

**Auth required:** ✅ Yes

**URL parameter:** `listing_id` — the ID of the produce listing.

**Response `200 OK`:**
```json
{
  "id": 7,
  "listing_id": 12,
  "crop_name": "Tomato",
  "grade": "A",
  "issues": [],
  "estimated_shelf_days": 6,
  "confidence": 0.92,
  "graded_at": "2026-07-22T11:00:00Z"
}
```

**Response `404 Not Found`:** Returned if the listing has not been graded yet.

---

## 7. AI Assistant Endpoints

**Prefix:** `/api/assistant/`

The AI assistant speaks Hausa, Yoruba, Igbo, Nigerian Pidgin, and English. It can understand a farmer's intent from natural language and automatically execute actions (like creating a produce listing).

---

### `POST /api/assistant/new/`
Explicitly start a fresh conversation session. Use this when the farmer opens a new chat screen.

**Auth required:** ✅ Yes

**Request Body:** *(empty)*

**Response `201 Created`:**
```json
{
  "conversation_id": 3
}
```
> Save `conversation_id` in local state. Pass it in every subsequent `/chat/` call to keep conversational context.

---

### `POST /api/assistant/chat/`
Send a message to the AI assistant. This is the core endpoint for the entire farmer chat interface.

**Auth required:** ✅ Yes

**Request Body:**
```json
{
  "message": "I wan sell 50kg of tomato",
  "conversation_id": 3,
  "language": "en"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | ✅ Yes | The farmer's text message (max 2000 chars) |
| `conversation_id` | integer | ❌ Optional | If omitted, a new conversation is started automatically |
| `language` | string | ❌ Optional | Hint to the AI (`ha`, `yo`, `ig`, `pcm`, `en`). Default: `en`. The AI detects language automatically but this helps. |

**Response `200 OK`:**
```json
{
  "conversation_id": 3,
  "reply": "Okay! I've created a tomato listing for 50kg. What price per kg are you asking for?",
  "action_result": {
    "created_listing_id": 14,
    "crop": "Tomato"
  }
}
```

> **`reply`** → The AI's natural language response in the farmer's language. Display this as a chat bubble.
> **`action_result`** → `null` if no action was taken. Contains an object if the AI created a listing, etc. Use this to update the UI immediately (e.g., show a new listing card) without a separate API call.
> **`conversation_id`** → Always returned. Store this for the next message.

**Frontend task (Voice Flow):**
1. Farmer holds the mic button → record audio with `expo-av` / Web Audio API.
2. Send the audio blob to Whisper STT (or browser `SpeechRecognition` API for the PWA) to get the transcript.
3. Send the transcript text to `POST /assistant/chat/`.
4. Display the `reply` as a chat bubble and optionally play it via TTS.

---

### `GET /api/assistant/history/{conversation_id}/`
Retrieve the full message history for a past conversation.

**Auth required:** ✅ Yes (Owner farmer only — returns 403 if someone else's conversation ID is requested)

**URL parameter:** `conversation_id` — the ID of the conversation.

**Response `200 OK`:**
```json
{
  "id": 3,
  "farmer_name": "aminu_kano",
  "created_at": "2026-07-22T10:00:00Z",
  "messages": [
    {
      "id": 1,
      "role": "farmer",
      "content": "I wan sell 50kg of tomato",
      "language": "en",
      "timestamp": "2026-07-22T10:00:05Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "Okay! I've created a tomato listing for 50kg...",
      "language": "en",
      "timestamp": "2026-07-22T10:00:08Z"
    }
  ]
}
```

> **`role`** → `"farmer"` or `"assistant"`. Use this to align messages left/right in the chat UI.

---

## 8. UI/UX Guidelines

1. **Language Toggle**: Provide a prominent flag/language selector on the Farmer home screen. The `preferred_language` field in their profile pre-selects this. UI chrome (buttons, labels) should also localize.

2. **Voice Over Text**: For farmers, show a large "Hold to Speak" mic button as the primary input method. Keyboard input should be secondary.

3. **Grade Badges**: Represent quality grades visually:
   - 🟢 **Grade A** — Premium (green badge)
   - 🟡 **Grade B** — Standard (yellow badge)
   - 🟠 **Grade C** — Processing only (orange badge)
   - 🔴 **Rejected** (red badge)

4. **AI Grading Animation**: When a photo is uploading, show a scanning / AI-processing animation to communicate that something intelligent is happening.

5. **Status Lifecycle**: The produce listing `status` moves through a clear pipeline. Show this as a stepper or progress indicator in the farmer dashboard:
   ```
   Pending Grading → Graded → Matched to Buyer → Sold
   ```

6. **Offline Awareness**: Display a banner when the device is offline. Queue chat messages and listing creates locally and sync when reconnected. TanStack Query's `useMutation` with offline support handles this well.

---

## 9. Market Matching & Orders Endpoints

**Prefix:** `/api/orders/` and `/api/matching/`

### `POST /api/orders/`
Buyer places an order.
**Request Body:**
```json
{
  "crop_type": 1,
  "quantity_kg": "50.00",
  "max_price_per_kg": "600.00",
  "required_grade": "A"
}
```

### `GET /api/orders/`
Buyer views their orders.

### `GET /api/orders/{id}/`
Order detail + match status.

### `POST /api/matching/run/`
*(Admin Only)* Trigger the matching cycle algorithm to match orders with available farmer produce.

### `GET /api/matching/results/{order_id}/`
View the list of matched listings for a specific order.

---

## 10. Logistics & Routing Endpoints

**Prefix:** `/api/logistics/`

### `GET /api/logistics/routes/`
Dispatcher views their assigned routes.

### `GET /api/logistics/routes/{id}/`
Route detail with waypoints.

### `PUT /api/logistics/routes/{id}/status/`
Mark route in-transit or delivered.

### `POST /api/logistics/routes/generate/`
*(Admin Only)* Triggers OR-Tools to solve the Vehicle Routing Problem (VRP) for pending matches and generate optimal routes.

### `GET /api/logistics/routes/{id}/briefing/`
Fetch the Gemma 4 AI-narrated friendly dispatch instructions for the specific route.

---

## 11. Payments Endpoints

**Prefix:** `/api/payments/`

### `GET /api/payments/`
Farmer views their payment history.

### `GET /api/payments/{id}/`
Payment detail (status, transaction ref).

### `POST /api/payments/trigger/{match_id}/`
*(Admin Only)* Trigger the mock payment flow to simulate a successful payout and update statuses to `Sold`/`Completed`.

---

## 12. Market Trends & Demand Forecasting Endpoints

**Prefix:** `/api/market/`

### `GET /api/market/trends/`
Fetch top commodities experiencing price surges or high demand across regional hubs. Returns an AI-generated briefing and trend statistics.
**Query Parameters:** `region_id` (optional, filter by state)

### `GET /api/market/prices/`
Fetch a paginated list of daily commodity prices.
**Query Parameters:** `crop_id` (optional), `hub_id` (optional)

---

## 13. Future Endpoints (Coming Soon)

These are not yet in the backend but will be built. Architect your frontend routing and state management to accommodate them.

### Real-Time Chat
```
WS    /ws/chat/room_id/                                 → WebSocket for real time messaging
```
