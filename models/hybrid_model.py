import pandas as pd
import numpy as np
from math import sqrt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error

class HybridRecommender:
    def __init__(self, movies_path):
        self.movies = pd.read_csv(movies_path)
        self._validate_data()
        self._prepare_data()
        self.rmse, self.mape = self._train_rating_predictor()

    def _validate_data(self):
        required_columns = ['title', 'genres', 'id', 'rating_average', 'rating_count']
        missing_cols = [col for col in required_columns if col not in self.movies.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    def _prepare_data(self):
        self.movies['overview'] = self.movies['overview'].fillna('')
        self.movies['content'] = (
            self.movies['title'] + " " + self.movies['genres'] + " " + self.movies['overview']
        )
        
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.movies['content'])

    def _train_rating_predictor(self):
        self.movies['log_rating_count'] = np.log1p(self.movies['rating_count']) 
        features = self.movies[['log_rating_count']]
        target = self.movies['rating_average']
        X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train, y_train)
        y_pred = self.model.predict(X_test)
        
        rmse = sqrt(mean_squared_error(y_test, y_pred))
        mask = y_test > 0.1  # Ignore values ≤ 0.1 to avoid division problems
        mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100 if mask.sum() > 0 else float('inf')
        
        print(f"Model trained! RMSE: {rmse:.4f}, MAPE: {mape:.2f}%")
        return rmse, mape

    def _interpret_accuracy(self):
        """Provide a qualitative interpretation of RMSE and MAPE values."""
        if self.rmse < 0.1:
            rmse_level = "High Accuracy (Low Error)"
        elif self.rmse < 0.3:
            rmse_level = "Moderate Accuracy"
        else:
            rmse_level = "Low Accuracy (High Error)"

        if self.mape < 10:
            mape_level = "Very High Accuracy"
        elif self.mape < 20:
            mape_level = "High Accuracy"
        elif self.mape < 30:
            mape_level = "Moderate Accuracy"
        else:
            mape_level = "Low Accuracy"

        return rmse_level, mape_level

    def _content_based_recommendations(self, favorite_movie_ids):
        indices = [self.movies[self.movies['id'] == mid].index[0] for mid in favorite_movie_ids]
        cosine_similarities = cosine_similarity(self.tfidf_matrix[indices], self.tfidf_matrix)
        sim_scores = cosine_similarities.mean(axis=0)

        # Normalize predicted ratings to be between 0 and 1
        predicted_ratings = self.model.predict(self.movies[['log_rating_count']])
        normalized_ratings = (predicted_ratings - predicted_ratings.min()) / (predicted_ratings.max() - predicted_ratings.min())

        # Combine similarity and predicted rating
        weighted_scores = sim_scores * 0.7 + normalized_ratings * 0.3

        recommended_indices = weighted_scores.argsort()[::-1]
        recommended_movies = self.movies.iloc[recommended_indices]
        recommended_movies = recommended_movies[~recommended_movies['id'].isin(favorite_movie_ids)]

        # Calculate confidence score (higher means more confidence in recommendation)
        confidence_scores = weighted_scores[recommended_indices][:5]
        recommended_movies = recommended_movies[['id', 'title', 'rating_average']].head(5)
        recommended_movies['Confidence'] = confidence_scores[:5]  # Assign confidence scores
        
        return recommended_movies

    def recommend(self, favorite_movie_titles):
        favorite_movie_ids = []
        for title in favorite_movie_titles:
            matched_movies = self.movies[self.movies['title'].str.contains(title, case=False, na=False)]
            if not matched_movies.empty:
                favorite_movie_ids.append(matched_movies.iloc[0]['id'])
        
        if not favorite_movie_ids:
            print("No valid movies found in your favorites.")
            return []
        
        recommendations = self._content_based_recommendations(favorite_movie_ids)
        rmse_level, mape_level = self._interpret_accuracy()

        print("\nRecommended Movies (with Confidence Scores):")
        for idx, movie in recommendations.iterrows():
            print(f"{idx + 1}. {movie['title']} (Predicted Rating: {movie['rating_average']:.2f}, Confidence: {movie['Confidence']:.2f})")
        
        print("\nModel Accuracy Levels:")
        print(f"- RMSE: {self.rmse:.4f} ({rmse_level})")
        print(f"- MAPE: {self.mape:.2f}% ({mape_level})")

        return recommendations

# Usage example
movies_path = 'Datasetkeren.csv'
recommender = HybridRecommender(movies_path)
user_favorites = ["Inception", "The Dark Knight", "Avatar", "The Avengers", "Deapool"]
recommender.recommend(user_favorites)
