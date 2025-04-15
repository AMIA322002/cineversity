document.addEventListener("DOMContentLoaded", () => {
    const path = window.location.pathname;

    // === UNIVERSAL LOGO HANDLER ===
    const logo = document.querySelector(".logo");

    if (logo) {
        logo.style.cursor = "pointer";
        logo.addEventListener("click", () => {
            window.location.href = "../templates/index.html";
        });
    }

    // === cineversity\templates\index.html ===
    if (path.includes("index.html")) {
        const button = document.querySelector(".get-rec-button");

        button?.addEventListener("click", () => {
            const favoriteMovie = document.querySelector(".movie-input")?.value;
            const major = document.querySelector(".input-major")?.value;
            const cohort = document.querySelector(".input-cohort")?.value;

            if (!favoriteMovie || !major || !cohort) {
                alert("Please fill in all fields.");
                return;
            }

            localStorage.setItem("favoriteMovie", favoriteMovie);
            localStorage.setItem("major", major);
            localStorage.setItem("cohort", cohort);

            window.location.href = "../templates/recommendation.html";
        });
    }

    // === RECOMMENDATION.HTML ===
    if (path.includes("recommendation.html")) {
        const favoriteMovieInput = document.querySelector(".movie-input");
        const majorInput = document.querySelector(".input-major");
        const cohortInput = document.querySelector(".input-cohort");
        const button = document.querySelector(".get-rec-button");
        const recContainer = document.querySelector(".recs");

        const storedMovie = localStorage.getItem("favoriteMovie");
        const storedMajor = localStorage.getItem("major");
        const storedCohort = localStorage.getItem("cohort");

        if (!storedMovie || !storedMajor || !storedCohort) {
            alert("Missing input. Please go back and fill the form.");
            window.location.href = "../templates/index.html";
            return;
        }

        // Prefill inputs
        if (favoriteMovieInput) favoriteMovieInput.value = storedMovie;
        if (majorInput) majorInput.value = storedMajor;
        if (cohortInput) cohortInput.value = storedCohort;

        const fetchRecommendations = (title, major, cohort) => {
            const apiURL = `http://127.0.0.1:5000/recommend?title=${encodeURIComponent(title)}&major=${major}&cohort=${cohort}`;

            fetch(apiURL)
                .then(res => {
                    if (!res.ok) throw new Error("API error");
                    return res.json();
                })
                .then(data => {
                    localStorage.setItem("recommendations", JSON.stringify(data));
                    if (!recContainer) return;

                    recContainer.innerHTML = "";

                    data.forEach(movie => {
                        const card = document.createElement("div");
                        card.className = "movrec";
                        card.innerHTML = `
                            <div class="rectangle"></div>
                            <div class="genres">${movie.genres || "Genres not available"}</div>
                            <div class="title">${movie.title}</div>
                        `;
                        recContainer.appendChild(card);
                    });
                })
                .catch(err => {
                    console.error("Failed to fetch recommendations:", err);
                    alert("Something went wrong. Please try again.");
                });
        };

        // Fetch recommendations once on initial load
        fetchRecommendations(storedMovie, storedMajor, storedCohort);

        // Debounced re-fetch on button click
        let fetchCooldown = false;

        button?.addEventListener("click", () => {
            if (fetchCooldown) return;
            fetchCooldown = true;
            setTimeout(() => fetchCooldown = false, 1500); // 1.5 sec cooldown

            const fav = favoriteMovieInput?.value;
            const major = majorInput?.value;
            const cohort = cohortInput?.value;

            if (!fav || !major || !cohort) {
                alert("Please complete all fields to get recommendations.");
                return;
            }

            localStorage.setItem("favoriteMovie", fav);
            localStorage.setItem("major", major);
            localStorage.setItem("cohort", cohort);

            fetchRecommendations(fav, major, cohort);
        });

        // Feedback buttons
        const likeButton = document.querySelector(".like-button");
        const dislikeButton = document.querySelector(".dislike-button");

        const handleFeedback = (feedbackType) => {
            const feedbackData = {
                major: storedMajor,
                cohort: storedCohort,
                favoriteMovie: storedMovie,
                feedbackType: feedbackType,
                recommendations: JSON.parse(localStorage.getItem("recommendations")) || []
            };

            fetch("http://127.0.0.1:5000/feedback", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(feedbackData)
            })
                .then(res => {
                    if (!res.ok) throw new Error("Failed to send feedback");
                    return res.json();
                })
                .then(data => {
                    console.log("Feedback sent successfully:", data);
                    window.location.href = "../templates/result.html"; // Redirect to result.html
                })
                .catch(err => {
                    console.error("Error sending feedback:", err);
                    alert("Failed to send feedback. Please try again.");
                });
        };

        likeButton?.addEventListener("click", () => handleFeedback("like"));
        dislikeButton?.addEventListener("click", () => handleFeedback("dislike"));
    }

    // === RESULT.HTML ===
    if (path.includes("result.html")) {
        const fav = localStorage.getItem("favoriteMovie");
        const major = localStorage.getItem("major");
        const cohort = localStorage.getItem("cohort");

        const message = document.querySelector(".result-message");
        if (message) {
            message.innerHTML = `
                <h2>Thank you!</h2>
                <p>Your favorite movie: <strong>${fav}</strong></p>
                <p>Your major: <strong>${major.replace(/-/g, " ")}</strong></p>
                <p>Your cohort: <strong>${cohort}</strong></p>
            `;
        }

        localStorage.clear();
    }
});
