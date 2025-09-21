# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Job(db.Model):
    """Represents a job description in the database."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    company = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    candidates = db.relationship('Candidate', backref='job', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'description': self.description
        }

class Candidate(db.Model):
    """Represents a candidate's resume upload."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    analysis = db.relationship('AnalysisResult', backref='candidate', uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'resume_filename': self.resume_filename,
            'job_id': self.job_id,
            'analysis': self.analysis.to_dict() if self.analysis else None
        }

class AnalysisResult(db.Model):
    """Stores the AI analysis result for a candidate."""
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=False)
    verdict = db.Column(db.String(50), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text, nullable=False)
    missing_skills = db.Column(db.Text, nullable=True) # Storing as JSON string
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False, unique=True)

    def to_dict(self):
        return {
            'id': self.id,
            'score': self.score,
            'verdict': self.verdict,
            'summary': self.summary,
            'feedback': self.feedback,
            'missing_skills': self.missing_skills,
            'candidate_id': self.candidate_id
        }