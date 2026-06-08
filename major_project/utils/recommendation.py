from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from db import jobs_collection

def recommend_jobs(resume_text):

    jobs_data = list(jobs_collection.find())

    job_texts = [
        job.get("Skills Required", "")
        for job in jobs_data
    ]

    all_texts = [resume_text] + job_texts

    vectorizer = TfidfVectorizer()

    vectors = vectorizer.fit_transform(all_texts)

    scores = cosine_similarity(
        vectors[0],
        vectors[1:]
    )[0]

    for i, job in enumerate(jobs_data):
        job["Match Score (%)"] = round(
            scores[i] * 100,
            2
        )

    return sorted(
        jobs_data,
        key=lambda x: x["Match Score (%)"],
        reverse=True
    )[:8]