from flask import render_template, request, redirect, session, flash, jsonify
from website.models import db, User, Post, Comment, Follows
from functools import wraps
from website import app  # Import the app object directly

# Restricts access model to prevent users not logged in from accessing the rest of the websites
# Reference: https://blog.miguelgrinberg.com/post/the-ultimate-guide-to-python-decorators-part-iii-decorators-with-arguments, Adapted the methodology on how to make sure to setup a login required to access the websites by only being logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash("You need to be logged in to access this page.", "danger")
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        input_password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Validate passwords
        if input_password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template('register.html')

        # Check if the email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already registered.", "danger")
            return render_template('register.html')

        # Create new user and hash password section
        new_user = User(name=name, email=email)
        new_user.set_password(input_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')  # Getting form data
        password = request.form.get('password')

        # Check if email already exits
        user = User.query.filter_by(email=email).first()

        # Validatation of email and password
        if user and user.check_password(password):
            session['email'] = user.email
            flash('Successfully logged in!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid email or password. Please try again.', 'danger')
            return render_template('login.html') 

    return render_template('login.html') 

@app.route('/profile')
@login_required
def profile():
    if 'email' not in session:
        return redirect('/login')

    user = User.query.filter_by(email=session['email']).first()
    return render_template('profile.html', user=user)


@app.route('/logout')
@login_required
def logout():
    session.pop('email', None)
    flash('You have successfully logged out.', 'success')
    return redirect('/login')


@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    user = User.query.filter_by(email=session['email']).first()

    # Get form data
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']

    # Validation of current password
    if not user.check_password(current_password):
        flash('Current password is incorrect.', 'danger')
        return redirect('/profile')

    # Validate new password after confirmation
    if new_password != confirm_password:
        flash('New password and confirmation do not match.', 'danger')
        return redirect('/profile')

    # Checking if the new password is the same as the old password
    if user.check_password(new_password):
        flash('New password cannot be the same as the current password.', 'danger')
        return redirect('/profile')

    # Update the datbase with the new password
    user.set_password(new_password)
    db.session.commit()

    flash('Password updated successfully!', 'success')
    return redirect('/profile')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if 'email' not in session:
        return redirect('/login')

    current_user = User.query.filter_by(email=session['email']).first()

    # Handle new post submission
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            new_post = Post(content=content, user_id=current_user.id)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/dashboard')

    # Get filter from specified paramenters
    filter_option = request.args.get('filter', 'all') 

    if filter_option == 'following':
        # Fetching posts by users the current user is following
        posts = Post.query.join(Follows, Follows.followed_id == Post.user_id) \
                          .filter(Follows.follower_id == current_user.id) \
                          .order_by(Post.created_at.desc()).all()
    else:
        # Fetch all posts
        posts = Post.query.order_by(Post.created_at.desc()).all()

    return render_template('dashboard.html', user=current_user, posts=posts, filter=filter_option)
pass

@app.route('/like/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized like'}), 401

    user = User.query.filter_by(email=session['email']).first()
    post = Post.query.get_or_404(post_id)

    # Click like
    if user in post.liked_by:
        post.liked_by.remove(user)  # Like removal if like exists
    else:
        post.liked_by.append(user)  # Add like
        # Ensure doesn't clash with dislike
        if user in post.disliked_by:
            post.disliked_by.remove(user)

    db.session.commit()

    # Returning updated like and dislike counts
    like_count = len(post.liked_by)
    dislike_count = len(post.disliked_by)
    return jsonify({'like_count': like_count, 'dislike_count': dislike_count})
pass

@app.route('/dislike/<int:post_id>', methods=['POST'])
@login_required
def dislike_post(post_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized dislike'}), 401

    user = User.query.filter_by(email=session['email']).first()
    post = Post.query.get_or_404(post_id)

    # Click dislike
    if user in post.disliked_by:
        post.disliked_by.remove(user)  # Remove the dislike if already disliked
    else:
        post.disliked_by.append(user)  # Add dislike
        # Ensure there is no clash with the like
        if user in post.liked_by:
            post.liked_by.remove(user)

    db.session.commit()

    # Return updated like and dislike counts
    like_count = len(post.liked_by)
    dislike_count = len(post.disliked_by)
    return jsonify({'like_count': like_count, 'dislike_count': dislike_count})
pass

@app.route('/comment/<int:post_id>', methods=['POST'])
@login_required
def comment_post(post_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in to comment on this post.'}), 401

    user = User.query.filter_by(email=session['email']).first()
    post = Post.query.get_or_404(post_id)

    # Get comment content
    content = request.json.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Comment content cannot be left empty to post.'}), 400

    # Add comments to the database, of what is being committed
    new_comment = Comment(content=content, post_id=post.id, user_id=user.id)
    db.session.add(new_comment)
    db.session.commit()

    # Fetching all comments for the post, posting the comment with all the info
    comments = [
        {
            'id': c.id,
            'content': c.content,
            'user': c.user.name,
            'created_at': c.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_owner': c.user_id == user.id,
            'is_post_owner': post.user_id == user.id
        }
        for c in post.comments
    ]

    return jsonify({'comments': comments})
pass


@app.route('/delete_comment/<int:comment_id>', methods=['DELETE'])
@login_required
def delete_comment(comment_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access to delete comment.'}), 401

    user = User.query.filter_by(email=session['email']).first()
    comment = Comment.query.get_or_404(comment_id)

    # Ensuring whether the comment belongs to the user logged in
    if comment.user_id != user.id:
        return jsonify({'error': 'You are not authorized to delete this comment.'}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({'success': True})
pass

@app.route('/search', methods=['GET'])
@login_required
def search():
    if 'email' not in session:
        return redirect('/login')

    query = request.args.get('query', '').strip()

    if not query:
        flash("Search query cannot be empty.", "danger")
        return redirect('/dashboard')

    # Performing search for users, posts, and comments (the search is completely case insensitive)
    users = User.query.filter(User.name.ilike(f"%{query}%")).all()  # Match for users
    posts = Post.query.filter(Post.content.ilike(f"%{query}%")).all()  # Match for posts
    comments = Comment.query.filter(Comment.content.ilike(f"%{query}%")).all()  # Match for comments

    return render_template('search.html', query=query, users=users, posts=posts, comments=comments)
pass


@app.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('user_profile.html', user=user)
pass


@app.route('/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized, cannot follow user'}), 401

    current_user = User.query.filter_by(email=session['email']).first()
    user_to_follow = User.query.get_or_404(user_id)

    if user_to_follow in current_user.following:
        # Unfollow the user
        current_user.following.remove(user_to_follow)
        following = False
    else:
        # Follow the user 
        current_user.following.append(user_to_follow)
        following = True

    db.session.commit()
    return jsonify({'following': following, 'followers_count': len(user_to_follow.followers)})
pass


@app.route('/user/<int:user_id>/followers')
@login_required
def user_followers(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('followers.html', user=user)
pass

@app.route('/user/<int:user_id>/following')
@login_required
def user_following(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('following.html', user=user)
pass

# Injects the currently logged-in user (`current_user`) into all templates if an email exists in the session. 
# Sets `current_user` to `None` for templates when no user is logged in.
@app.context_processor
def inject_current_user():
    if 'email' in session:
        current_user = User.query.filter_by(email=session['email']).first()
        return {'current_user': current_user}
    return {'current_user': None}
pass

@app.route('/post/<int:post_id>')
@login_required
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)
pass

@app.route('/my_posts', methods=['GET'])
@login_required
def my_posts():
    if 'email' not in session:
        return redirect('/login')

    user = User.query.filter_by(email=session['email']).first()

    # Fetch user's posts and comments
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).all()
    user_comments = Comment.query.filter_by(user_id=user.id).order_by(Comment.created_at.desc()).all()

    return render_template(
        'my_posts.html',
        user=user,
        posts=user_posts,
        comments=user_comments
    )
pass

@app.route('/delete_post/<int:post_id>', methods=['DELETE'])
@login_required
def delete_post(post_id):
    if 'email' not in session:
        return jsonify({'error': 'Unauthorized access, cannot delete post.'}), 401

    user = User.query.filter_by(email=session['email']).first()
    post = Post.query.get_or_404(post_id)

    # Ensure the post belongs to the user logged in
    if post.user_id != user.id:
        return jsonify({'error': 'You are not authorized to delete this post.'}), 403

    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})
pass









