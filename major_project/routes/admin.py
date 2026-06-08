from flask import render_template, request, redirect, session
from bson import ObjectId
from db import (
    users_collection,
    jobs_collection,
    admin_collection
)

def register_admin_routes(app):

    # =====================
    # ADMIN LOGIN
    # =====================
    @app.route('/admin/login', methods=['GET', 'POST'])
    def admin_login():

        if request.method == "POST":

            email = request.form['email']
            password = request.form['password']

            admin = admin_collection.find_one({
                "email": email,
                "password": password
            })

            if admin:
                session['admin'] = email
                return redirect('/admin/dashboard')

            return "Invalid Admin Login"

        return render_template('admin_login.html')

    # =====================
    # ADMIN DASHBOARD
    # =====================
    @app.route('/admin/dashboard')
    def admin_dashboard():

        if 'admin' not in session:
            return redirect('/admin/login')

        total_students = users_collection.count_documents({})
        total_jobs = jobs_collection.count_documents({})
        skill_count = {}

        for job in jobs_collection.find():

          skills = job.get("Skills Required", "")

          for skill in skills.split(","):

            skill = skill.strip()

            if skill:
                skill_count[skill] = skill_count.get(skill, 0) + 1

        popular_skills = sorted(
        skill_count.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

        return render_template(
            'admin_dashboard.html',
            total_students=total_students,
            total_jobs=total_jobs,
            popular_skills=popular_skills
            
        )

    # =====================
    # VIEW STUDENTS
    # =====================
    @app.route('/admin/students')
    def students():

        if 'admin' not in session:
            return redirect('/admin/login')

        students = list(users_collection.find())

        return render_template(
            'students.html',
            students=students
        )

    # =====================
    # SEARCH STUDENT
    # =====================
    @app.route('/admin/search_student', methods=['POST'])
    def search_student():

        keyword = request.form['keyword']

        students = list(users_collection.find({
            "$or": [
                {
                    "username": {
                        "$regex": keyword,
                        "$options": "i"
                    }
                },
                {
                    "email": {
                        "$regex": keyword,
                        "$options": "i"
                    }
                }
            ]
        }))

        return render_template(
            'students.html',
            students=students
        )

    # =====================
    # DELETE STUDENT
    # =====================
    @app.route('/admin/delete_student/<id>')
    def delete_student(id):

        if 'admin' not in session:
            return redirect('/admin/login')

        users_collection.delete_one({
            "_id": ObjectId(id)
        })

        return redirect('/admin/students')

    # =====================
    # VIEW JOBS
    # =====================
    @app.route('/admin/jobs')
    def jobs():

        if 'admin' not in session:
            return redirect('/admin/login')

        jobs = list(jobs_collection.find())

        return render_template(
            'jobs.html',
            jobs=jobs
        )

    # =====================
    # ADD JOB
    # =====================
    @app.route('/admin/add_job', methods=['GET', 'POST'])
    def add_job():

        if 'admin' not in session:
            return redirect('/admin/login')

        if request.method == 'POST':

            jobs_collection.insert_one({

                "Job Title": request.form['job_title'],
                "Company": request.form['company'],
                "Skills Required": request.form['skills_required'],
                "Location": request.form['location'],
                "Salary": request.form['salary']
            })

            return redirect('/admin/jobs')

        return render_template('add_job.html')

    # =====================
    # UPDATE JOB
    # =====================
    @app.route('/admin/update_job/<id>', methods=['GET', 'POST'])
    def update_job(id):

        if 'admin' not in session:
            return redirect('/admin/login')

        job = jobs_collection.find_one({
            "_id": ObjectId(id)
        })

        if request.method == 'POST':

            jobs_collection.update_one(
                {"_id": ObjectId(id)},
                {
                    "$set": {
                        "Job Title": request.form['job_title'],
                        "Company": request.form['company'],
                        "Skills Required": request.form['skills_required'],
                        "Location": request.form['location'],
                        "Salary": request.form['salary']
                    }
                }
            )

            return redirect('/admin/jobs')

        return render_template(
            'update_job.html',
            job=job
        )

    # =====================
    # DELETE JOB
    # =====================
    @app.route('/admin/delete_job/<id>')
    def delete_job(id):

        if 'admin' not in session:
            return redirect('/admin/login')

        jobs_collection.delete_one({
            "_id": ObjectId(id)
        })

        return redirect('/admin/jobs')

    # =====================
    # ADMIN LOGOUT
    # =====================
    @app.route('/admin/logout')
    def admin_logout():

        session.pop('admin', None)

        return redirect('/admin/login')