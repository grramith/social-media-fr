// Handle dropdown filter change
document
    .getElementById("filter-content")
    .addEventListener("change", function () {
        const value = this.value;
        const postsSection = document.getElementById("posts-section");
        const commentsSection = document.getElementById("comments-section");

        // Toggle posts and comments sections based on filter choice
        if (value === "posts") {
            postsSection.style.display = "block";
            commentsSection.style.display = "none";
        } else if (value === "comments") {
            postsSection.style.display = "none";
            commentsSection.style.display = "block";
        }
    });

// Handle post deletion using delagation method
document.addEventListener("click", function (event) {
    if (event.target.classList.contains("delete-post-button")) {
        const postId = event.target.dataset.postId;

        if (confirm("Are you sure you want to delete this post?")) {
            fetch(`/delete_post/${postId}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        event.target.closest(".card").remove();
                    } else {
                        alert(data.error || "Failed to delete post.");
                    }
                })
                .catch((error) => console.error("Error:", error));
        }
    }

    // Checking whether the clicked button is a comment delete button
    if (event.target.classList.contains("delete-comment-button")) {
        const commentId = event.target.dataset.commentId;

        if (confirm("Are you sure you want to delete this comment?")) {
            // Delete request being sent
            fetch(`/delete_comment/${commentId}`, {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.success) {
                        event.target.closest(".card").remove(); // Remove the comment's card from the server
                    } else {
                        alert(data.error || "Failed to delete comment.");
                    }
                })
                .catch((error) => console.error("Error:", error));
        }
    }
});
