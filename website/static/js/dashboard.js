// Handle post filter change
document.getElementById('post-filter').addEventListener('change', function () {
    const filter = this.value;
    window.location.href = `/dashboard?filter=${filter}`;
});

document.addEventListener("DOMContentLoaded", function () {
    // Select all like and dislike buttons
    const likeButtons = document.querySelectorAll(".like-button");
    const dislikeButtons = document.querySelectorAll(".dislike-button");

    likeButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const postId = this.dataset.postId; // Retrieve the post ID from button dataset

            // Send request to server to like post
            fetch(`/like/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // Updating like and dislike_counters dynamically
                        document.getElementById(
                            `like-count-${postId}`
                        ).textContent = data.like_count;
                        document.getElementById(
                            `dislike-count-${postId}`
                        ).textContent = data.dislike_counter;
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    });

    dislikeButtons.forEach((button) => {
        button.addEventListener("click", function () {
            const postId = this.dataset.postId;

            //Send post request to dislike
            fetch(`/dislike/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // Updating like and dislike_counters dynamically
                        document.getElementById(
                            `like-count-${postId}`
                        ).textContent = data.like_count;
                        document.getElementById(
                            `dislike-count-${postId}`
                        ).textContent = data.dislike_counter;
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    });

    // Handle comment form submission
    const commentForms = document.querySelectorAll(".comment-form");
    commentForms.forEach((form) => {
        form.addEventListener("submit", function (event) {
            event.preventDefault();

            const postId = this.dataset.postId;
            const contentInput = this.querySelector('input[name="content"]');
            const content = contentInput.value.trim();

            if (!content) {
                alert("Comment cannot be empty.");
                return;
            }

            // Send comment to the server
            fetch(`/comment/${postId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ content: content }),
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.error) {
                        alert(data.error);
                    } else {
                        // Update the comment list dynamically
                        const comment_list = document.getElementById(
                            `comment-list-${postId}`
                        );
                        comment_list.innerHTML = ""; // Clear existing comments

                        data.comments.forEach(
                            ({
                                user,
                                content,
                                created_at,
                                id,
                                is_owner,
                                is_post_owner,
                            }) => {
                                const comment_items = document.createElement(
                                    "li"
                                );
                                comment_items.className =
                                    "list-group-item d-flex justify-content-between align-items-center";

                                // Create comment content
                                const commentContent = `
                                <div>
                                    <b>${user}:</b> ${content}
                                    <small class="text-muted d-block">${created_at}</small>
                                </div>
                                ${
                                    is_owner || is_post_owner
                                        ? `<button class="btn btn-danger btn-sm delete-comment-button" data-comment-id="${id}" data-post-id="${postId}">Delete</button>`
                                        : ""
                                }
                            `;
                                comment_items.innerHTML = commentContent;
                                comment_list.appendChild(comment_items);
                            }
                        );

                        contentInput.value = ""; // Clear the input field
                        binding_delete_comment_button(); // Rebind delete functionality to new buttons, such as new comments
                    }
                })
                .catch((error) => console.error("Error:", error));
        });
    });

    // Bind delete functionality to delete buttons, to make sure that the server removes the commits from the database
    // Reference: https://stackoverflow.com/questions/73574757/how-to-make-useable-delete-button-to-delete-comments, Adapted create a delete button that works when the page refreshs out
    const binding_delete_comment_button = () => {
        const delete_comment_button = document.querySelectorAll(
            ".delete-comment-button"
        );

        delete_comment_button.forEach((button) => {
            button.addEventListener("click", function () {
                const commentId = this.dataset.commentId;
                const postId = this.dataset.postId;

                if (!confirm("Are you sure you want to delete this comment?")) {
                    return; // Exit if the user cancels the confirmation message
                }

                // Send delete request to the server
                fetch(`/delete_comment/${commentId}`, {
                    method: "DELETE",
                    headers: {
                        "Content-Type": "application/json",
                    },
                })
                    .then((response) => response.json())
                    .then((data) => {
                        if (data.error) {
                            alert(data.error);
                        } else {
                            // Remove the comment from the sever/DOM
                            const comment_list = document.getElementById(
                                `comment-list-${postId}`
                            );
                            const comment_items = button.closest("li");
                            comment_list.removeChild(comment_items); // Remove the comment from the comments list
                        }
                    })
                    .catch((error) => console.error("Error:", error));
            });
        });
    };

    // Initial binding of delete buttons- allowing users to delete when the page loads in
    binding_delete_comment_button();
});
