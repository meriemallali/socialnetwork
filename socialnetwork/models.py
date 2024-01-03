from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
from datetime import datetime
import uuid


# User Profile model
# To store user's data.
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    userid = models.IntegerField()
    profile_status = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile/', default='blankprofile.jpg')

    def __str__(self):
        return self.user.username


# to store the posted data
class UserPost(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=100)
    media = models.ImageField(upload_to='posts/', null=True)
    description = models.TextField()
    date_posted = models.DateTimeField(default=datetime.now)
    sum_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.username


# To store the comment and comment owner for each post.
class UserComment(models.Model):
    post = models.ForeignKey(UserPost, on_delete=models.CASCADE)
    comment_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    comment = models.TextField()


# To store the likes in each post. referencing by the post id.
class PostLike(models.Model):
    username = models.CharField(max_length=100)
    postid = models.CharField(max_length=500)

    def __str__(self):
        return self.username


# to store the user's friend list
class FriendNetwork(models.Model):
    current_user_id = models.IntegerField()
    user_friend_id = models.IntegerField()
    username = models.CharField(max_length=100, null=True)
    friend_username = models.CharField(max_length=100, null=True)


# to store chat messages.
class Chat(models.Model):
    message_owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    chat_message = models.TextField(null=True, blank=True)
    sent_to = models.CharField(max_length=100, null=True)
    chat_name = models.CharField(null=True, blank=True, max_length=50)
    sent_date = models.DateTimeField(default=datetime.now)
