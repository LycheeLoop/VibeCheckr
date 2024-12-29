document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("search-form");
    const button = document.getElementById("search-button");
    const spinner = button.querySelector(".spinner-border");
    const resultsSection = document.getElementById("results-section");
    let isSubmitting = false;

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        if (isSubmitting) return;
        isSubmitting = true;

        spinner.classList.remove("d-none");
        button.setAttribute("disabled", "true");

        const formData = new FormData(form);

        fetch(form.action, {
            method: "POST",
            body: formData,
            headers: { "X-Requested-With": "XMLHttpRequest" }
        })
        .then(response => response.text())
        .then(data => {
            resultsSection.innerHTML = data;

            // Scroll to the results section
            setTimeout(() => {
                resultsSection.scrollIntoView({ behavior: "smooth" });
            }, 300);

            // Initialize the robotic animation
            const roboticAnimationContainer = document.getElementById("robotic-animation");
            if (roboticAnimationContainer) {
                var animation = lottie.loadAnimation({
                    container: roboticAnimationContainer,  // Element where the animation is displayed
                    renderer: 'svg',                      // Use SVG rendering for scalability
                    loop: true,                           // Loop the animation
                    autoplay: true,                       // Automatically start the animation
                    path: '/static/assets/img/robot.json' // Path to your animation JSON file
                });

                console.log("Robotic animation initialized successfully.");
            } else {
                console.error("Robotic animation container not found.");
            }

            // Extract youtube_url for sentiment analysis
            const youtubeUrlElement = document.querySelector("[data-youtube-url]");
            if (youtubeUrlElement) {
                const youtubeUrl = youtubeUrlElement.dataset.youtubeUrl;

                // Fetch sentiment analysis for YouTube
                fetch("/analyze_sentiment", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"  // URL-encoded format
                    },
                    body: `youtube_url=${encodeURIComponent(youtubeUrl)}`  // Pass youtube_url in the body
                })
                .then(response => response.json())
                .then(sentimentData => {
                    if (sentimentData.summary) {
                        const sentimentSection = document.getElementById("sentiment-summary");
                        const summaryText = sentimentData.summary;
                        let i = 0;

                        // Clear placeholder and start typing effect
                        sentimentSection.innerHTML = "";

                        function typeText() {
                            if (i < summaryText.length) {
                                sentimentSection.innerHTML += summaryText.charAt(i);
                                i++;
                                setTimeout(typeText, 50); // Adjust speed as needed
                            }
                        }

                        typeText();
                    } else {
                        console.error("Error:", sentimentData.error);
                    }
                })
                .catch(error => console.error("Error fetching sentiment analysis:", error));
            } else {
                console.error("Error: youtube_url not found for sentiment analysis.");
            }

            // Extract reddit_url for sentiment analysis
            const redditUrlElement = document.querySelector("[data-reddit-url]");
            if (redditUrlElement) {
                const redditUrl = redditUrlElement.dataset.redditUrl;
                console.log(`Reddit URL for sentiment analysis: ${redditUrl}`); // Debugging

                // Fetch sentiment analysis for Reddit
                fetch("/analyze_reddit_sentiment", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded"  // URL-encoded format
                    },
                    body: `reddit_url=${encodeURIComponent(redditUrl)}`  // Pass reddit_url in the body
                })
                .then(response => response.json())
                .then(sentimentData => {
                    if (sentimentData.summary) {
                        console.log("Reddit Sentiment Summary Received: ", sentimentData.summary); // Debugging
                        const sentimentSection = document.getElementById("sentiment-summary");
                        const summaryText = sentimentData.summary;
                        let i = 0;

                        // Clear placeholder and start typing effect
                        sentimentSection.innerHTML = "";

                        function typeText() {
                            if (i < summaryText.length) {
                                sentimentSection.innerHTML += summaryText.charAt(i);
                                i++;
                                setTimeout(typeText, 50); // Adjust speed as needed
                            }
                        }

                        typeText();
                    } else {
                        console.error("Error:", sentimentData.error);
                    }
                })
                .catch(error => console.error("Error fetching sentiment analysis:", error));
            } else {
                console.error("Error: reddit_url not found for sentiment analysis.");
            }

            spinner.classList.add("d-none");
            button.removeAttribute("disabled");
            isSubmitting = false;
        })
        .catch(error => {
            console.error("Error:", error);
            spinner.classList.add("d-none");
            button.removeAttribute("disabled");
            isSubmitting = false;
        });
    });
});
