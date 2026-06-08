from flask import render_template, request, redirect, url_for, session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from db import users_collection,jobs_collection

def register_auth_routes(app):

    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():

        if request.method == "POST":

            username = request.form['username']
            email = request.form['email']
            password = generate_password_hash(
                request.form['password']
            )

            if users_collection.find_one({"email": email}):
                return "Email already exists"

            users_collection.insert_one({
                "username": username,
                "email": email,
                "password": password
            })

            return redirect(url_for('login'))

        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():

        if request.method == "POST":

            email = request.form['email']
            password = request.form['password']

            user = users_collection.find_one(
                {"email": email}
            )

            if user and check_password_hash(
                user['password'],
                password
            ):

                session['user'] = user['username']
                session['email'] = user['email']

                return redirect('/dashboard')

            return "Invalid Login"

        return render_template('login.html')

    @app.route('/job')
    def job():
        return render_template("job.html")
    
    @app.route('/api/jobs')
    def get_jobs():
      jobs = list(jobs_collection.find())

    # Convert ObjectId to string
      for job in jobs:
        job["_id"] = str(job["_id"])

      return jsonify(jobs)

    @app.route('/logout')
    def logout():

        session.clear()

        return redirect('/')