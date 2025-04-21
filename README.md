Cineversity 🎬
Cineversity is a hybrid movie recommendation system developed as a capstone project. It combines collaborative filtering and content-based approaches to provide personalized movie suggestions.

🚀 Features
Hybrid Recommendation Engine: Merges collaborative filtering with content-based filtering for enhanced accuracy.

User-Friendly Interface: Intuitive web interface for seamless user interaction.

Real-Time Suggestions: Provides instant movie recommendations based on user preferences.

Scalable Architecture: Designed to handle a growing user base and expanding movie database.

📁 Project Structure
php
Copy code
cineversity/
├── data/                   # Datasets and preprocessing scripts
├── models/                 # Trained models and training scripts
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates for the web interface
├── application.py          # Main Flask application
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
⚙️ Installation
Clone the Repository:

bash
Copy code
git clone https://github.com/AMIA322002/cineversity.git
cd cineversity
Create a Virtual Environment:

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Run the Application:

bash
Copy code
python application.py
Access the application at http://localhost:5000/.

📊 Dataset
The project utilizes the TMDB 5000 Movie Dataset from Kaggle, which includes metadata on approximately 5000 movies from TMDb. This dataset provides information such as plot, cast, crew, budget, and revenues, making it a valuable resource for building a movie recommendation system.

🤝 Contributing
Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request.

📄 License
This project is licensed under the MIT License.

📬 Contact
For any inquiries or feedback, please contact AMIA322002.
