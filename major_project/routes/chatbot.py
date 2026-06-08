
from flask import render_template, request, jsonify
import google.generativeai as genai
import os
import PyPDF2
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# -----------------------------
# Gemini Configuration
# -----------------------------
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

# -----------------------------
# Extract PDF Text
# -----------------------------
def extract_text(file):

    text = ""

    try:
        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + " "

    except Exception as e:
        print("PDF Error:", e)

    return text


# -----------------------------
# Text Preprocessing (No NLTK)
# -----------------------------
def preprocess(text):

    stop_words = {
        "a", "an", "the", "is", "are", "was", "were",
        "and", "or", "but", "if", "then", "of", "to",
        "for", "with", "on", "in", "at", "from", "by",
        "this", "that", "these", "those", "it", "as",
        "be", "have", "has", "had", "will", "shall",
        "can", "could", "would", "should"
    }

    words = re.findall(r"\w+", text.lower())

    filtered_words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(filtered_words)


# -----------------------------
# ATS Score
# -----------------------------
def calculate_score(resume, jd):

    tfidf = TfidfVectorizer()

    vectors = tfidf.fit_transform(
        [resume, jd]
    )

    score = cosine_similarity(
        vectors[0:1],
        vectors[1:2]
    )

    return round(
        score[0][0] * 100,
        2
    )


# -----------------------------
# Missing Keywords
# -----------------------------
def missing_keywords(resume, jd):

    resume_words = set(
        re.findall(r"\w+", resume.lower())
    )

    jd_words = set(
        re.findall(r"\w+", jd.lower())
    )

    missing = jd_words - resume_words

    return list(missing)[:20]


# -----------------------------
# ATS Suggestions
# -----------------------------
def get_suggestions(score):

    if score >= 80:

        return [
            "Excellent ATS Score",
            "Resume is highly optimized",
            "Ready for job applications",
            "Keep resume updated regularly"
        ]

    elif score >= 60:

        return [
            "Add more job-specific keywords",
            "Improve project descriptions",
            "Include certifications",
            "Highlight achievements"
        ]

    else:

        return [
            "Add missing technical skills",
            "Improve resume content",
            "Use ATS-friendly format",
            "Add projects and certifications",
            "Match keywords from job description"
        ]


# -----------------------------
# Register Routes
# -----------------------------
def register_chatbot_routes(app):

    # -------------------------
    # Chatbot Page
    # -------------------------
    @app.route('/chatbot')
    def chatbot():
        return render_template('chat.html')


    # -------------------------
    # Chat API
    # -------------------------
    @app.route('/chat', methods=['POST'])
    def chat():

        data = request.json

        user_message = data.get("message", "")

        try:

            response = model.generate_content(
                user_message
            )

            return jsonify({
                "reply": response.text
            })

        except Exception as e:

            return jsonify({
                "reply": f"Error: {str(e)}"
            })


    # -------------------------
    # ATS Checker
    # -------------------------
    @app.route('/ats', methods=['GET', 'POST'])
    def ats():

        score = None
        missing = []
        suggestions = []
        analysis = ""

        if request.method == "POST":

            file = request.files.get("resume")
            jd = request.form.get("jd", "")

            if file and jd:

                # Resume Text
                resume_text = extract_text(file)

                # Preprocess
                processed_resume = preprocess(
                    resume_text
                )

                processed_jd = preprocess(
                    jd
                )

                # ATS Score
                score = calculate_score(
                    processed_resume,
                    processed_jd
                )

                # Missing Keywords
                missing = missing_keywords(
                    processed_resume,
                    processed_jd
                )

                # Suggestions
                suggestions = get_suggestions(
                    score
                )

                # AI Analysis
                try:

                    prompt = f"""
                    Analyze this resume.

                    Resume:
                    {resume_text}

                    Job Description:
                    {jd}

                    ATS Score:
                    {score}

                    Give:

                    1. Resume Strengths
                    2. Resume Weaknesses
                    3. Missing Skills
                    4. ATS Improvement Suggestions
                    5. Final Recommendation
                    """

                    ai_response = model.generate_content(
                        prompt
                    )

                    analysis = ai_response.text

                except Exception as e:

                    analysis = (
                        "AI analysis unavailable."
                    )

        return render_template(
            "ats.html",
            score=score,
            missing=missing,
            suggestions=suggestions,
            analysis=analysis
        )


    # -------------------------
    # HR Questions
    # -------------------------
    @app.route('/hr')
    def hr():

        return render_template(
            "hr.html"
        )


    # -------------------------
    # Resume Builder
    # -------------------------
    @app.route('/resume-builder')
    def resume_builder():

        return render_template(
            "resume_builder.html"
        )

