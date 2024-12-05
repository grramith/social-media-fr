document.addEventListener('DOMContentLoaded', function () {
    // Handle like button click
    document.querySelector('.like-button').addEventListener('click', function () {
        const postId = this.dataset.postId;

        // Request to post a like
        fetch(`/like/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Update the like and dislike counts dynamically
                document.getElementById(`like-count-${postId}`).textContent = data.like_count;
                document.getElementById(`dislike-count-${postId}`).textContent = data.dislike_count;
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Handle dislike button click
    document.querySelector('.dislike-button').addEventListener('click', function () {
        const postId = this.dataset.postId;

        fetch(`/dislike/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Update the like and dislike counts dynamically
                document.getElementById(`like-count-${postId}`).textContent = data.like_count;
                document.getElementById(`dislike-count-${postId}`).textContent = data.dislike_count;
            }
        })
        .catch(error => console.error('Error:', error));
    });

    // Handle adding comments dynamically
    document.querySelector('.comment-form').addEventListener('submit', function (event) {
        event.preventDefault(); // Prevent default form submission
        const postId = this.dataset.postId;
        const content = this.querySelector('input[name="content"]').value; // Get entered comment content

        fetch(`/comment/${postId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                // Dynamically adding the new comment to the comment list
                const commentList = document.getElementById(`comment-list-${postId}`);
                const newComment = document.createElement('li');
                newComment.className = 'list-group-item';
                newComment.innerHTML = `
                    <b>${data.user}:</b> ${data.content}
                    <small class="text-muted d-block">${data.created_at}</small>
                `;
                commentList.appendChild(newComment); // Append the new comment to the list
                this.querySelector('input[name="content"]').value = ''; // Clear input
            }
        })
        .catch(error => console.error('Error:', error));
    });
});