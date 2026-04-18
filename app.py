from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "jobs.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class Job(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    company     = db.Column(db.String(100), nullable=False)
    location    = db.Column(db.String(100), nullable=False)
    category    = db.Column(db.String(50),  nullable=False)
    job_type    = db.Column(db.String(50),  nullable=False)
    salary      = db.Column(db.String(50),  nullable=True)
    description = db.Column(db.Text,        nullable=False)
    email       = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime,    default=datetime.utcnow)

@app.route("/")
def home():
    search   = request.args.get("search", "")
    category = request.args.get("category", "")
    jobs     = Job.query
    if search:
        jobs = jobs.filter(Job.title.ilike(f"%{search}%"))
    if category:
        jobs = jobs.filter_by(category=category)
    jobs = jobs.order_by(Job.date_posted.desc()).all()
    categories = db.session.query(Job.category).distinct().all()
    print(f"DEBUG: Found {len(jobs)} jobs")   # ← debug line
    return render_template("home.html", jobs=jobs,
                           categories=categories,
                           search=search,
                           selected_category=category)

@app.route("/job/<int:id>")
def job_detail(id):
    job = Job.query.get_or_404(id)
    return render_template("job_detail.html", job=job)

@app.route("/post", methods=["GET", "POST"])
def post_job():
    if request.method == "POST":
        job = Job(
            title       = request.form["title"],
            company     = request.form["company"],
            location    = request.form["location"],
            category    = request.form["category"],
            job_type    = request.form["job_type"],
            salary      = request.form["salary"],
            description = request.form["description"],
            email       = request.form["email"]
        )
        db.session.add(job)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("post_job.html")

@app.route("/delete/<int:id>")
def delete_job(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()
    if Job.query.count() == 0:
        sample_jobs = [
            Job(title="Python Developer", company="STC", location="Riyadh",
                category="Technology", job_type="Full Time",
                salary="15,000 SAR", email="hr@stc.com",
                description="We are looking for an experienced Python developer to join our team in Riyadh."),
            Job(title="WordPress Developer", company="Saudi Aramco", location="Dhahran",
                category="Technology", job_type="Full Time",
                salary="12,000 SAR", email="careers@aramco.com",
                description="Looking for a skilled WordPress developer with PHP and JavaScript experience."),
            Job(title="Data Analyst", company="Vision 2030 Fund", location="Riyadh",
                category="Data Science", job_type="Full Time",
                salary="18,000 SAR", email="hr@vision2030.gov.sa",
                description="Join our data team to analyze key economic indicators."),
            Job(title="UI/UX Designer", company="Noon", location="Riyadh",
                category="Design", job_type="Full Time",
                salary="10,000 SAR", email="jobs@noon.com",
                description="Design beautiful user interfaces for our e-commerce platform."),
            Job(title="Marketing Manager", company="Jarir Bookstore", location="Riyadh",
                category="Marketing", job_type="Full Time",
                salary="14,000 SAR", email="hr@jarir.com",
                description="Lead our digital marketing campaigns across social media and SEO."),
        ]
        db.session.add_all(sample_jobs)
        db.session.commit()
        print("Sample data added!")

if __name__ == "__main__":
    app.run(debug=True)