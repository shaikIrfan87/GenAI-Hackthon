# ResumeMatch AI
#Automated Resume Relevance Check System


<<<<<<< HEAD
=======
#Automated Resume Relevance Check System
>>>>>>> cb48aacac52bb6ca60b1c484f5b6ddf1494f0647
## 🚀 Overview
ResumeMatch AI is an end-to-end, AI-powered recruitment automation platform designed for hackathons and real-world hiring. It streamlines the process of job posting, resume collection, AI-based resume-job matching, shortlisting, and automated candidate communication—all with a beautiful, modern UI.

## 🎯 Key Features
- **AI Resume Relevance Scoring:** Uses Google Gemini API to analyze and score resumes against job descriptions (0-100 scale).
- **Automated Shortlisting:** Candidates scoring ≥65% are automatically shortlisted.
- **Bulk Resume Upload:** Upload multiple resumes (PDF) for instant batch analysis.
- **Job Management:** Create, view, and manage job descriptions (manual entry or file upload).
- **Dashboard Analytics:** Visual summary of jobs, applicants, shortlisting stats, and average scores.
- **Cover Letter Analysis:** AI-powered feedback and gap analysis for cover letters.
- **Shortlisted Candidates Management:** View, edit, and email shortlisted candidates directly from the UI.
- **Automated Email Notifications:** Send personalized congratulation emails to shortlisted candidates (Gmail/SMTP setup).
- **Modern UI:** Built with Tailwind CSS for a hackathon-winning, visually appealing experience.

## 🏆 Why This Project Wins Hackathons
- **End-to-End Automation:** From job posting to candidate communication, everything is automated.
- **AI at the Core:** Real AI (Google Gemini) for resume analysis, not just keyword matching.
- **User-Centric Design:** Intuitive, responsive, and visually stunning interface.
- **Plug-and-Play:** Easy setup with .env and requirements.txt; works out-of-the-box for demos.
- **Extensible:** Modular codebase for easy feature addition (e.g., interview scheduling, analytics).

## 🗂️ Project Structure
```
finalt/
├── app.py                # Main Flask app (routes, API, logic)
├── database.py           # SQLAlchemy models (Job, Candidate, AnalysisResult)
├── init_db.py            # Script to initialize the database
├── requirements.txt      # Python dependencies
├── EMAIL_SETUP.md        # Email configuration guide
├── .env                  # Environment variables (API keys, email)
├── services/
│   ├── gemini_service.py # Google Gemini API integration (AI analysis)
│   └── email_service.py  # Email sending logic (Flask-Mail)
├── templates/
│   ├── index.html        # Landing page
│   ├── dasbord.html      # Dashboard (analytics)
│   ├── job.html          # Job management UI
│   ├── resume.html       # Resume upload & results
│   └── letter.html       # Cover letter & shortlisted UI
├── uploads/              # Uploaded resumes & job files
└── instance/
    └── resumematch.db    # SQLite database
```

## ⚙️ Setup Instructions
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd finalt
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment:**
   - Copy `.env.example` to `.env` and fill in your Google Gemini API key and email credentials (see `EMAIL_SETUP.md`).
4. **Initialize the database:**
   ```sh
   python init_db.py
   ```
5. **Run the app:**
   ```sh
   python app.py
   ```
6. **Open in browser:**
   - Visit [http://localhost:5001](http://localhost:5001)

## 🔑 Environment Variables (.env)
- `GOOGLE_API_KEY`: Your Google Gemini API key
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, etc.: Email credentials (see `EMAIL_SETUP.md`)

## 🧠 How It Works
- **Job Posting:** Add jobs via UI or file upload (PDF/DOCX). AI extracts job title if not provided.
- **Resume Upload:** Upload multiple resumes (PDF). Text is extracted and sent to Gemini for analysis.
- **AI Analysis:** Gemini returns a JSON with relevance score, fit verdict, summary, feedback, and missing skills.
- **Shortlisting:** Candidates with ≥65% score are shortlisted and shown in dashboard/cover letter tab.
- **Emailing:** Send congratulation emails to shortlisted candidates with one click (after email setup).

## 🖥️ Tech Stack
- **Backend:** Python, Flask, Flask-SQLAlchemy, Flask-Mail
- **AI:** Google Gemini API (via `google-generativeai`)
- **Frontend:** Tailwind CSS, HTML5, modern JS (vanilla)
- **Database:** SQLite (default, easy for hackathons)

## 📧 Email Setup
See [`EMAIL_SETUP.md`](EMAIL_SETUP.md) for step-by-step instructions (Gmail, Outlook, Yahoo supported).

## 💡 Hackathon Demo Tips
- Use the dashboard for a live demo of AI shortlisting.
- Upload sample resumes and show instant scoring.
- Show email sending (use a test email account).
- Highlight the beautiful UI and end-to-end automation.

## 🙌 Team & Credits
- Built by [Your Team Name] for [Hackathon Name], 2025.
- Special thanks to Google Gemini, Flask, and the open-source community.

---
**Ready to win your hackathon? Fork, deploy, and impress the judges!**
