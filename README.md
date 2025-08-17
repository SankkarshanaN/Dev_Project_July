# 🧑‍⚖️ Django Online Judge

A full-stack **Online Judge system** built with Django.  
Users can register, solve coding problems, submit solutions, and view results instantly.  
This platform also supports AI-assisted guidance and is ready for Docker-based deployment.

---

## 🚀 Features
- 👤 **User Accounts** (login, signup, profiles)
- 📚 **Problem Management** (create, edit, list coding problems)
- 📝 **Submissions** (run code, evaluate against test cases)
- 📊 **Profiles & Leaderboard**
- 🎨 **Frontend** with Django Templates + CSS (in `static/`)
- 🖼 **Media support** for user uploads
- 🐳 **Dockerized** for easy deployment
- ⚡ **AI integration** (Google Generative AI for hints/assistance)

---

## 📂 Project Structure
```
online_judge/
│── accounts/        # Authentication & user management
│── problems/        # Problem statements & test cases
│── submissions/     # Submission handling & evaluation
│── profiles/        # User profiles & leaderboard
│── templates/       # HTML templates
│── static/          # CSS, JS, images
│── media/           # User-uploaded files (ignored in git)
│── online_judge/    # Core Django project settings
│── manage.py        # Django management script
│── requirements.txt # Python dependencies
│── Dockerfile       # Docker support
```

---

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/SankkarshanaN/Dev_Project_July.git
cd Dev_Project_July/online_judge
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
```

### 3. Setup environment variables
Create a `.env` file in the root folder:
```ini
SECRET_KEY=your_django_secret_key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

### 4. Apply migrations & create superuser
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run the development server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000/` 🎉

---

## 🐳 Docker Setup
Build & run using Docker:
```bash
docker build -t online-judge .
docker run -p 8000:8000 online-judge
```

---

## 📸 Screenshots (to be added)
- Problem listing page
- Submission form & results
- User profile & leaderboard

---

## 🤝 Contributing
Contributions are welcome!  
1. Fork the repo  
2. Create a feature branch  
3. Commit changes  
4. Open a Pull Request  

---
