document.getElementById('follow-form').addEventListener('submit', function (e) {
    e.preventDefault();
    fetch(this.action, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.following) {
                // Updating the button to show "Unfollow" and change its style to indicate the current status
                document.getElementById('follow-button').textContent = 'Unfollow';
                document.getElementById('follow-button').classList.remove('btn-primary');
                document.getElementById('follow-button').classList.add('btn-danger');
            } else {
                // Updating the button to show "Follow" and go back to default
                document.getElementById('follow-button').textContent = 'Follow';
                document.getElementById('follow-button').classList.remove('btn-danger');
                document.getElementById('follow-button').classList.add('btn-primary');
            }
            // Update followers count dynamically
            document.getElementById('followers-count').textContent = data.followers_count;
        })
        .catch(error => console.error('Error:', error));
});