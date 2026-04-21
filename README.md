# CodeFun — Online Judge Platform

A competitive programming online judge built with Django. Users can solve algorithmic problems, submit code in multiple languages, get AI-powered hints, and compete on a global leaderboard.

---

## Features

- **Problem Catalog** — Browse problems filtered by difficulty (Easy / Medium / Hard)
- **Code Execution** — Run and submit code in Python, C++, C, and Java inside isolated Docker containers
- **Run vs. Submit** — "Run" tests only sample cases without saving; "Submit" runs all hidden test cases and records results
- **AI Hints** — Get hints, code review, or complexity analysis powered by Google Gemini (10 hints per 24 hours)
- **Leaderboard** — Global rankings based on points earned from solved problems
- **User Profiles** — Custom avatars, stats, and submission history per user
- **Password Reset** — Email-based password reset flow

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2 |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Code Execution | Docker (sandboxed containers) |
| AI Hints | Google Gemini API |
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
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GEMINI_API_KEY=your-gemini-api-key-here
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
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Set to `True` for development (default: `False`) |
| `GEMINI_API_KEY` | Yes | Google Gemini API key for AI hints |
| `DATABASE_URL` | Prod only | PostgreSQL connection string |
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

## Admin

Access the Django admin panel at `/admin/` to manage problems, test cases, users, and submissions.
