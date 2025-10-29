document.addEventListener("DOMContentLoaded", function() {
    const csrftoken = document.getElementById("csrf-token").value;
    const likeButton = document.getElementById("like-button");
    if (likeButton) {
        likeButton.addEventListener("click", function() {
            const postId = likeButton.dataset.postId;
            fetch(`/like_toggle/${postId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    likeButton.innerText = "❤️";
                } else {
                    likeButton.innerText = "🤍";
                }
                document.getElementById("like-count").innerText = data.like_count;
            })
            .catch(error => {
                console.error("Error:", error);
            });
    
    })
}});