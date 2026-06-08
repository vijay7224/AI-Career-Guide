from flask import render_template,request,redirect,session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from db import jobs_collection
from utils.pdf_utils import extract_pdf_text

def register_recommend_routes(app):

    def recommend_jobs(resume_text):

        jobs_data=list(
            jobs_collection.find()
        )

        for job in jobs_data:
            job["_id"]=str(job["_id"])

        job_texts=[
            job.get("Skills Required","")
            for job in jobs_data
        ]

        all_texts=[resume_text]+job_texts

        vectorizer=TfidfVectorizer()

        vectors=vectorizer.fit_transform(
            all_texts
        )

        scores=cosine_similarity(
            vectors[0],
            vectors[1:]
        )[0]

        for i,job in enumerate(jobs_data):
            job["Match Score (%)"]=round(
                scores[i]*100,2
            )

        return sorted(
            jobs_data,
            key=lambda x:x["Match Score (%)"],
            reverse=True
        )[:8]

    @app.route('/dashboard')
    def dashboard():

        if 'user' not in session:
            return redirect('/login')

        return render_template(
            'dashboard.html',
            username=session['user'],
            email=session['email']
        )

    @app.route('/recommend',methods=['GET','POST'])
    def recommend():

        if request.method=="POST":

            file=request.files['resume']

            resume_text=extract_pdf_text(file)

            jobs=recommend_jobs(
                resume_text
            )

            return render_template(
                'result.html',
                jobs=jobs
            )

        return render_template(
            'recommend.html'
        )