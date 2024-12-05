from . import db
import bcrypt

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))  # Storing hashed passwords

    # Setup hashed password
    def set_password(self, input_password):
        """Hash raw pasword and store it"""
        self.password = bcrypt.hashpw(
            input_password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    # Checking if the passwords match even if it is hashed
    def check_password(self, input_password):
        """Checks if raw password is equal to the hashed password."""
        return bcrypt.checkpw(
            input_password.encode("utf-8"), self.password.encode("utf-8")
        )

    # Many-to-many relationships for likes and dislikes between users and posts.
    posts = db.relationship("Post", backref="user", lazy=True)
    liked_posts = db.relationship("Post", secondary="like", back_populates="liked_by")
    disliked_posts = db.relationship(
        "Post", secondary="dislike", back_populates="disliked_by"
    )

    # Many-to-many relationship for followers and following between users.
    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin="Follows.followed_id == User.id",
        secondaryjoin="Follows.follower_id == User.id",
        backref="following",
    )

# Many-to-many relationship where a user can follow another user.
class Follows(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    followed_id = db.Column(db.Integer, db.ForeignKey("user.id"))

# Post model
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())  # Timestamping (time of post created)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    liked_by = db.relationship("User", secondary="like", back_populates="liked_posts") #A many-to-many relationship tracking users who liked the post through "like" association table.
    disliked_by = db.relationship(
        "User", secondary="dislike", back_populates="disliked_posts" #A many-to-many relationship tracking users who disliked the post through "dislike" association table.
    )
    comments = db.relationship("Comment", backref="post", lazy=True) # A one-to-many relationship for comments associated with the post.


# Association table for tracking users who liked posts.
like_table = db.Table(
    "like",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)

# Association table for tracking users who disliked posts.
dislike_table = db.Table(
    "dislike",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id"), primary_key=True),
)

# Comment model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))  # Foreign key to Post
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # Foreign key to User
    user = db.relationship("User", backref=db.backref("comments", lazy=True))
