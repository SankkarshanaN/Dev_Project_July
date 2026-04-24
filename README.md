# CodeFun — Online Judge Platform

A competitive programming online judge built with Django. Users can solve algorithmic problems, submit code in multiple languages, get AI-powered hints, and compete on a global leaderboard.

---

## Features

- **Problem Catalog** — Browse problems filtered by difficulty, tag, or full-text search
- **Tags & Recommendations** — Problems are tagged (arrays, dp, greedy, etc.); the list page surfaces personalized recommendations based on the tags of problems you've already solved
- **Code Execution** — Run and submit code in Python, C++, C, and Java inside isolated Docker containers
- **Run vs. Submit** — "Run" tests only sample cases without saving; "Submit" runs all hidden test cases and records results
- **AI Hints** — Get hints, code review, or complexity analysis powered by Google Gemini (10 hints per 24 hours)
- **Leaderboard** — Global rankings based on points earned from solved problems
- **User Profiles** — Custom avatars, stats, and submission history per user
- **Dark / Light Mode** — Theme toggle with `localStorage` persistence; respects OS `prefers-color-scheme` on first visit
- **Rate Limiting** — IP-based limits on login / register / password reset; user-based limits on submit / run / AI hint
- **Password Reset** — Email-based password reset flow
- **Staff Authoring UI** — Dedicated problem-authoring interface for staff users with inline test case management and tag auto-creation

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| Frontend | Tailwind CSS (CDN) + vanilla JS |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Code Execution | Docker (sandboxed containers) |
| AI Hints | Google Gemini API |
| Rate Limiting | django-ratelimit |
| Static Files | WhiteNoise |
| Image Handling | Pillow |
| Production Server | Gunicorn |

---

## Project Structure

```
online_judge/
├── accounts/          # Auth: login, register, dashboard, password reset
├── problems/          # Problem catalog and test cases
├── submissions/       # Code execution, submission results, AI hints
├── profiles/          # User profiles, leaderboard
├── templates/         # HTML templates
├── static/            # CSS, JS, images
├── online_judge/      # Django project settings and URLs
├── manage.py
├── requirements.txt
└── Dockerfile
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (required for code execution)
- A Google Gemini API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SankkarshanaN/Dev_Project_July.git
   cd Dev_Project_July
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux/macOS
   venv\Scripts\activate         # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create a `.env` file** in the project root:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   DEBUG=True
   GEMINI_API_KEY=your-gemini-api-key-here

   # Email (optional — defaults to console backend which prints reset links to terminal)
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=you@gmail.com
   EMAIL_HOST_PASSWORD=your-gmail-app-password
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000`.

---

## Docker (Production)

Build and run using Docker:

```bash
docker build -t codefun .
docker run -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -e GEMINI_API_KEY=your-gemini-api-key \
  -e DATABASE_URL=postgres://user:pass@host/db \
  -e DJANGO_SUPERUSER_USERNAME=admin \
  -e DJANGO_SUPERUSER_EMAIL=admin@example.com \
  -e DJANGO_SUPERUSER_PASSWORD=adminpassword \
  -v /var/run/docker.sock:/var/run/docker.sock \
  codefun
```

> The Docker socket mount (`/var/run/docker.sock`) is required so the app can spawn sandboxed containers for code execution.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Set to `True` for development (default: `False`) |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI hints |
| `DATABASE_URL` | Prod only | PostgreSQL connection string |
| `EMAIL_BACKEND` | No | `smtp` backend for prod; defaults to console backend in dev |
| `EMAIL_HOST_USER` | If SMTP | SMTP username (e.g., Gmail address) |
| `EMAIL_HOST_PASSWORD` | If SMTP | SMTP password (use a [Gmail App Password](https://myaccount.google.com/apppasswords) if using Gmail) |
| `ALLOWED_HOSTS` | Prod | Comma-separated list of allowed hostnames |
| `DJANGO_SUPERUSER_USERNAME` | Docker only | Auto-created superuser username |
| `DJANGO_SUPERUSER_EMAIL` | Docker only | Auto-created superuser email |
| `DJANGO_SUPERUSER_PASSWORD` | Docker only | Auto-created superuser password |

---

## Scoring

| Difficulty | Points |
|---|---|
| Easy | 10 |
| Medium | 20 |
| Hard | 30 |

Leaderboard ranks users by total points, then by number of problems solved.

---

## Supported Languages

- Python 3
- C++
- C
- Java

Code runs in isolated Docker containers with the following resource limits:
- **Memory:** 256 MB
- **CPU:** 0.5 cores
- **Max PIDs:** 50
- **Timeout:** 15 seconds

---

## Rate Limits

Requests exceeding these limits return a friendly error message:

| Endpoint | Limit | Scope |
|---|---|---|
| `POST /login/` | 10 / minute | per IP |
| `POST /accounts/register/` | 5 / hour | per IP |
| `POST /password-reset/` | 3 / hour | per IP |
| `POST /submissions/<id>/submit/` | 20 / minute | per user |
| `POST /submissions/.../run-custom/` | 30 / minute | per user |
| `POST /submissions/.../ai-hint/` | 10 / minute | per user |

> **Note:** `django-ratelimit` uses Django's cache backend. The default `LocMemCache` is per-process, so in production with multiple Gunicorn workers each worker counts independently. For accurate global limits, configure Redis as the cache backend.

---

## Managing Problems

CodeFun provides two ways to manage problems:

### 1. Built-in Staff UI (recommended for content authors)

Staff users see a **Manage** link in the navbar (`/problems/manage/`) which opens a dedicated authoring interface:

- Create, edit, and delete problems
- Inline test case management with an "Add Test Case" button
- Tags entered as comma-separated text (new tags auto-created)
- Mark individual test cases as samples (shown in the problem statement)
- Delete confirmation with a warning about cascading submission deletion

### 2. Django Admin Panel

Access `/admin/` for full model access — useful for bulk edits, user management, and inspecting submission results.

---

## Theme

CodeFun supports both dark and light modes with a toggle button in the navbar:

- First visit respects the OS `prefers-color-scheme`
- Choice is persisted in `localStorage` across sessions
- Theme preload script prevents flash of wrong theme on page load
