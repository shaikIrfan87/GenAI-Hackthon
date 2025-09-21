from docx import Document
from flask_mail import Mail
from services.email_service import init_mail, send_bulk_shortlist_emails, send_shortlist_email
import re
# --- Helper Functions ---
def extract_text_from_docx(file_path):
    """Extracts text from a DOCX file."""
    try:
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""
import os
import json
import pdfplumber
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from database import db, Job, Candidate, AnalysisResult
from services.gemini_service import get_gemini_analysis

# --- App Configuration ---
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///resumematch.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Initialize Flask-Mail
mail = init_mail(app)

# --- Helper Function ---
def extract_text_from_pdf(file_path):
    """Extracts text from a PDF file."""
    try:
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(page.extract_text() or "" for page in pdf.pages)
    except Exception as e:
        print(f"Error extracting text from {file_path}: {e}")
        return ""

# --- HTML Page Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    try:
        # --- 1. Query the database for key statistics ---
        total_jobs = Job.query.count()
        total_apps_processed = Candidate.query.count()

        # --- 2. Get all jobs and calculate summary data for each ---
        jobs = Job.query.order_by(Job.id.desc()).all()
        jobs_summary = []
        for job in jobs:
            try:
                shortlisted_count = 0
                rejected_count = 0
                total_applicants = len(job.candidates)
                scores = []
                for candidate in job.candidates:
                    try:
                        if candidate.analysis:
                            verdict = candidate.analysis.verdict.lower()
                            score = candidate.analysis.score
                            if isinstance(score, int):
                                scores.append(score)
                                # Use 65% threshold for shortlisting
                                if score >= 65:
                                    shortlisted_count += 1
                                else:
                                    rejected_count += 1
                    except Exception as e:
                        print(f"Error processing candidate {candidate.id}: {e}")
                        continue
                avg_score = round(sum(scores)/len(scores), 1) if scores else 0
                jobs_summary.append({
                    'id': job.id,
                    'title': job.title,
                    'shortlisted_count': shortlisted_count,
                    'rejected_count': rejected_count,
                    'total_applicants': total_applicants,
                    'avg_score': avg_score
                })
            except Exception as e:
                print(f"Error processing job {job.id}: {e}")
                continue

        # --- 3. Pass all the data to the template ---
        return render_template(
            'dasbord.html',
            total_jobs=total_jobs,
            total_apps=total_apps_processed,
            jobs_summary=jobs_summary
        )
    except Exception as e:
        print(f"Error in dashboard route: {e}")
        return render_template(
            'dasbord.html',
            total_jobs=0,
            total_apps=0,
            jobs_summary=[],
            error="Failed to load dashboard data. Please try again."
        )

@app.route('/jobs')
def jobs_page():
    return render_template('job.html')

@app.route('/resumes')
def resumes_page():
    return render_template('resume.html')

@app.route('/letters', methods=['GET', 'POST'])
def letters_page():
    if request.method == 'POST':
        job_description = request.form.get('job_description')
        resume_text = request.form.get('resume_text')
        
        if not job_description or not resume_text:
            return render_template('letter.html', error='Both job description and resume text are required.')
        
        # Get AI Analysis for cover letter
        analysis_data = get_gemini_analysis(job_description, resume_text)
        
        if "error" not in analysis_data:
            return render_template('letter.html', result=analysis_data)
        else:
            return render_template('letter.html', error='Analysis failed. Please try again.')
    
    return render_template('letter.html')

# --- API Endpoints ---

# API to manage Jobs
@app.route('/api/jobs', methods=['POST', 'GET'])
def manage_jobs():
    if request.method == 'POST':
        # Accept both file and text fields
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            company = request.form.get('company-name')
            description = request.form.get('job-description')
            file = request.files.get('file-upload')
            title = None
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # Extract text from uploaded file if no description provided
                if not description:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext == '.pdf':
                        description = extract_text_from_pdf(filepath)
                    elif ext == '.docx':
                        description = extract_text_from_docx(filepath)
                    else:
                        description = ''
                # Auto-extract job title from description
                from services.gemini_service import extract_job_title
                try:
                    title = extract_job_title(description)
                except Exception as e:
                    print(f"Error extracting job title: {e}")
                    title = None
            else:
                title = request.form.get('job-title')
            if not title or 'no job title' in (title or '').lower() or 'quota' in (title or '').lower() or '429' in (title or '').lower():
                # Assign default job title if extraction fails or quota exceeded
                job_count = Job.query.count() + 1
                title = f"Job Description {job_count}"
            if not company or not description:
                return jsonify({'error': 'Missing required fields'}), 400
            new_job = Job(title=title, company=company, description=description)
            db.session.add(new_job)
            db.session.commit()
            return jsonify(new_job.to_dict()), 201
        else:
            # Fallback for JSON
            data = request.json
            new_job = Job(
                title=data['title'],
                company=data['company'],
                description=data['description']
            )
            db.session.add(new_job)
            db.session.commit()
            return jsonify(new_job.to_dict()), 201
    
    jobs = Job.query.order_by(Job.id.desc()).all()
    return jsonify([job.to_dict() for job in jobs])

# API to upload Resumes and trigger analysis
@app.route('/api/upload', methods=['POST'])
def upload_resumes():
    if 'resumes' not in request.files:
        return jsonify({"error": "No resume files provided"}), 400
    
    job_id = request.form.get('job_id')
    if not job_id:
        return jsonify({"error": "No job ID provided"}), 400

    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404

    uploaded_files = request.files.getlist('resumes')
    processed_count = 0
    total_files = len([f for f in uploaded_files if f.filename != ''])
    
    for file in uploaded_files:
        if file.filename == '':
            continue
        
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(f"Processing resume {processed_count + 1}/{total_files}: {filename}")

            # Extract text for analysis
            resume_text = extract_text_from_pdf(filepath)
            if not resume_text:
                print(f"Warning: Could not extract text from {filename}")
                continue # Skip if PDF is empty or unreadable

            # Create Candidate record
            candidate_name = os.path.splitext(filename)[0].replace('_', ' ').replace('-', ' ').title()
            candidate = Candidate(name=candidate_name, resume_filename=filename, job_id=job.id)
            db.session.add(candidate)
            db.session.commit()
            print(f"Created candidate record for: {candidate_name}")

            # Get AI Analysis
            print(f"Starting analysis for: {candidate_name}")
            analysis_data = get_gemini_analysis(job.description, resume_text)
            
            if "error" not in analysis_data:
                # Save analysis result to database
                result = AnalysisResult(
                    score=analysis_data.get('relevance_score'),
                    verdict=analysis_data.get('fit_verdict'),
                    summary=analysis_data.get('summary'),
                    feedback=analysis_data.get('personalized_feedback'),
                    missing_skills=json.dumps(analysis_data.get('missing_skills', [])), # Store list as JSON string
                    candidate_id=candidate.id
                )
                db.session.add(result)
                db.session.commit()
                print(f"Analysis completed for {candidate_name}: Score {analysis_data.get('relevance_score')}, Verdict {analysis_data.get('fit_verdict')}")
            else:
                print(f"Analysis failed for {candidate_name}: {analysis_data.get('error')}")
                
            processed_count += 1
            
        except Exception as e:
            db.session.rollback()
            print(f"Error processing candidate {filename}: {e}")
            continue

    return jsonify({
        "message": f"Resumes uploaded and analysis completed. Processed {processed_count} out of {total_files} files.",
        "processed_count": processed_count,
        "total_files": total_files,
        "success": True
    }), 202

# API to get candidates and their results for a specific job
@app.route('/api/results/<int:job_id>', methods=['GET'])
def get_results(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
        
    candidates = Candidate.query.filter_by(job_id=job_id).order_by(Candidate.id.desc()).all()
    return jsonify([c.to_dict() for c in candidates])

# API to get all shortlisted candidates across all jobs
@app.route('/api/shortlisted', methods=['GET'])
def get_shortlisted_candidates():
    """Get all shortlisted candidates with their job details."""
    try:
        # Query for candidates with score >= 65% (shortlisting threshold)
        candidates = db.session.query(Candidate, Job, AnalysisResult).join(
            AnalysisResult, Candidate.id == AnalysisResult.candidate_id
        ).join(
            Job, Candidate.job_id == Job.id
        ).filter(
            AnalysisResult.score >= 65
        ).order_by(AnalysisResult.score.desc()).all()
        
        shortlisted_data = []
        for candidate, job, analysis in candidates:
            shortlisted_data.append({
                'id': candidate.id,
                'name': candidate.name,
                'email': candidate.email or '',
                'resume_filename': candidate.resume_filename,
                'job_title': job.title,
                'company': job.company,
                'job_id': job.id,
                'score': analysis.score,
                'verdict': analysis.verdict,
                'summary': analysis.summary
            })
        
        return jsonify(shortlisted_data), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to fetch shortlisted candidates: {str(e)}"}), 500

# API to update candidate email
@app.route('/api/candidate/<int:candidate_id>/email', methods=['PUT'])
def update_candidate_email(candidate_id):
    """Update a candidate's email address."""
    try:
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
            
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({"error": "Invalid email format"}), 400
        
        candidate = db.session.get(Candidate, candidate_id)
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404
        
        candidate.email = email
        db.session.commit()
        
        return jsonify({"message": "Email updated successfully", "email": email}), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to update email: {str(e)}"}), 500

# API to send emails to selected candidates
@app.route('/api/send-emails', methods=['POST'])
def send_emails_to_candidates():
    """Send shortlist notification emails to selected candidates."""
    try:
        data = request.json
        candidate_ids = data.get('candidate_ids', [])
        
        if not candidate_ids:
            return jsonify({"error": "No candidates selected"}), 400
        
        # Get candidate details with job information
        candidates_data = []
        missing_emails = []
        
        for candidate_id in candidate_ids:
            candidate = db.session.query(Candidate, Job).join(
                Job, Candidate.job_id == Job.id
            ).filter(Candidate.id == candidate_id).first()
            
            if not candidate:
                continue
                
            candidate_obj, job_obj = candidate
            
            if not candidate_obj.email:
                missing_emails.append(candidate_obj.name)
                continue
            
            candidates_data.append({
                'name': candidate_obj.name,
                'email': candidate_obj.email,
                'job_title': job_obj.title,
                'company_name': job_obj.company
            })
        
        if missing_emails:
            return jsonify({
                "error": f"Missing email addresses for candidates: {', '.join(missing_emails)}"
            }), 400
        
        if not candidates_data:
            return jsonify({"error": "No valid candidates found"}), 400
        
        # Send emails
        results = send_bulk_shortlist_emails(mail, candidates_data)
        
        success_count = sum(1 for r in results if r['status']['success'])
        total_count = len(results)
        
        return jsonify({
            "message": f"Sent {success_count} out of {total_count} emails successfully",
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to send emails: {str(e)}"}), 500

# API to test email configuration
@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email configuration by sending a test email."""
    try:
        data = request.json
        test_email = data.get('email')
        
        if not test_email:
            return jsonify({"error": "Email address is required"}), 400
        
        # Check if email is configured
        if not app.config.get('MAIL_ENABLED', False):
            return jsonify({
                "error": "Email service not configured. Please set up email credentials in .env file.",
                "instructions": "Check EMAIL_SETUP.md for configuration instructions"
            }), 400
        
        # Send test email
        result = send_shortlist_email(
            mail=mail,
            candidate_email=test_email,
            candidate_name="Test Student",
            job_title="Test Position",
            company_name="Test Company"
        )
        
        if result["success"]:
            return jsonify({
                "success": True,
                "message": f"Test email sent successfully to {test_email}"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": result["message"]
            }), 400
            
    except Exception as e:
        return jsonify({"error": f"Failed to send test email: {str(e)}"}), 500

# --- Main Execution ---
if __name__ == '__main__':
    import sys
    try:
        with app.app_context():
            db.create_all()  # Create database tables if they don't exist
        # Use reloader_type='stat' for better stability on Windows
        app.run(debug=True, port=5001, reloader_type='stat')
    except Exception as e:
        print(f"[Startup Error] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(3)