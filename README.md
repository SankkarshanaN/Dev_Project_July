# 🧑‍⚖️ Online Judge Platform

A Django-based **Online Judge** system where users can submit code, run against test cases, and view results in real-time.  
This project also integrates AI (Google Generative AI) for assistance and includes Docker support for deployment.

---

## 🚀 Features
- User authentication & profiles
- Problem statements with input/output test cases
- Code submission & evaluation
- Real-time feedback on correctness
- Leaderboard & submission history
- AI-assisted coding help (via Google GenAI)
- Admin panel for managing problems & users
- Dockerized for easy deployment

---

## 📂 Project Structure
```
online_judge/
│── problems/         # App for problem statements
│── submissions/      # App for code submissions
│── users/            # App for authentication & profiles
│── templates/        # HTML templates
│── static/           # Static assets (CSS, JS, images)
│── media/            # User-uploaded files (ignored in git)
│── manage.py
```

---

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/SankkarshanaN/Dev_Project_July.git
cd Dev_Project_July
```

### 2. Create a virtual environment & install dependencies
```bash
python -m venv venv
source venv/bin/activate   # (Linux/Mac)
venv\Scripts\activate      # (Windows)

pip install -r requirements.txt
```

### 3. Apply migrations & create superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Run the development server
```bash
python manage.py runserver
```

The app will be available at: `http://127.0.0.1:8000/`

---

## 🐳 Docker Setup
Build & run with Docker:
```bash
docker build -t online-judge .
docker run -p 8000:8000 online-judge
```

---


## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to improve.

---

## 📜 License
This project is licensed under the MIT License.  
Feel free to use and modify for your own projects.
