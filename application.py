from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import joblib
import pandas as pd
import numpy as np
import csv
from sklearn.metrics.pairwise import cosine_similarity
import os
from time import time

# === Load the bundled model and components ===
bundle = joblib.load(r"cineversity\models\cineversity_recommender_model.pkl")
tfidf_vectorizer = bundle["tfidf"]
tfidf_matrix = bundle["tfidf_matrix"]
rating_model = bundle["model"]
movies = bundle["movies"]

movies["original_index"] = movies.index
if 'log_rating_count' not in movies.columns:
    movies["log_rating_count"] = np.log1p(movies["rating_count"])

# === Load cohort-major combinations ===
cohort_major = pd.read_csv(r"cineversity\data\cohort_major_recommendations.csv", usecols=["cohort", "major"])
movies["key"] = 1
cohort_major["key"] = 1
movies = pd.merge(movies, cohort_major, on="key").drop("key", axis=1)

# === Map frontend slugs to major names ===
major_map = {
    "computer-science": "Computer Science",
    "information-systems": "Information Systems",
    "visual-communication-design": "Visual Communication Design",
    "mechanical-engineering": "Mechanical Engineering",
    "industrial-engineering": "Industrial Engineering",
    "management": "Management",
    "accounting": "Accounting",
    "english-education": "English Education",
    "psychology": "Psychology"
}

# === Flask app setup ===
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/recommendation.html")
def recommendation():
    return render_template("recommendation.html")

@app.route("/result.html")
def result():
    return render_template("result.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

@app.route("/recommend")
def recommend():
    title = request.args.get("title")
    major_key = request.args.get("major")
    cohort = request.args.get("cohort")

    if not title or not major_key or not cohort:
        return jsonify({"error": "Please provide movie title, major, and cohort."}), 400

    major = major_map.get(major_key)
    if not major:
        return jsonify({"error": "Invalid major selected."}), 400

    try:
        cohort = int(cohort)
    except ValueError:
        return jsonify({"error": "Cohort must be a number."}), 400

    filtered = movies[(movies["major"] == major) & (movies["cohort"] == cohort)]
    if filtered.empty:
        return jsonify({"error": "No movies found for this major and cohort."}), 404

    matched = filtered[filtered["title"].str.contains(title, case=False, na=False)]
    if matched.empty:
        return jsonify({"error": "Movie not found in this major/cohort."}), 404

    try:
        movie_idx = matched["original_index"].values[0]
    except IndexError:
        return jsonify({"error": "Movie index not found."}), 404

    sim_scores = cosine_similarity(tfidf_matrix[movie_idx], tfidf_matrix).flatten()

    group_indices = filtered["original_index"].unique()
    sim_scores_masked = np.zeros_like(sim_scores)
    sim_scores_masked[group_indices] = sim_scores[group_indices]

    sim_scores_masked += np.random.normal(0, 0.005, size=sim_scores.shape)
    sim_scores_masked = np.clip(sim_scores_masked, 0, 1)

    recommended_indices = sim_scores_masked.argsort()[::-1]
    recommended_indices = recommended_indices[recommended_indices != movie_idx]

    top_ids = movies.loc[recommended_indices, "original_index"].values
    recommended = movies[
        movies["original_index"].isin(top_ids) &
        (movies["major"] == major) &
        (movies["cohort"] == cohort) &
        (~movies["title"].str.contains(title, case=False, na=False))
    ].copy()

    recommended["confidence"] = recommended["original_index"].apply(lambda idx: sim_scores_masked[idx])

    top5 = recommended[["title", "genres", "rating_average", "confidence"]] \
        .sort_values(by="confidence", ascending=False).head(5)

    top5["genres"] = top5["genres"].apply(lambda g: ", ".join(eval(g)) if isinstance(g, str) and g.startswith("[") else g)

    return jsonify(top5.to_dict(orient="records"))

@app.route("/feedback", methods=["POST"])
def feedback():
    try:
        data = request.get_json()

        # Extract feedback details
        major = data.get("major")
        cohort = data.get("cohort")
        favorite_movie = data.get("favoriteMovie")
        feedback_type = data.get("feedbackType")  # "like" or "dislike"
        recommendations = data.get("recommendations", [])

        if not all([major, cohort, favorite_movie, feedback_type]):
            return jsonify({"message": "Missing feedback data"}), 400

        # Save feedback to CSV
        feedback_file = r"cineversity\data\user_feedback.csv"
        file_exists = os.path.isfile(feedback_file)
        with open(feedback_file, mode="a", newline="") as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["major", "cohort", "favorite_movie", "feedback_type", "recommendations"])
            writer.writerow([major, cohort, favorite_movie, feedback_type, recommendations])

        print(f"Received Feedback: {data}")
        return jsonify({"message": "Feedback received and saved successfully!"}), 200

    except Exception as e:
        print(f"Error processing feedback: {e}")
        return jsonify({"message": "Error processing feedback"}), 500

if __name__ == "__main__":
    app.run(debug=True)
