from rest_framework import serializers
from .models import *


# user profile serializer.
class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.CharField(source='user.email')

    class Meta:
        model = UserProfile
        fields = ['username', 'email',
                  'first_name', 'last_name', 'profile_status', 'profile_photo']


# to display user profile data.
class UserGETPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ['media', 'description', 'date_posted', 'sum_likes']


# to update user profile data.
class UserPOSTPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPost
        fields = ['media', 'description']


# post comments serializer.
class PostCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserComment
        fields = ['comment_owner', 'comment']


# display the user's friend network.
class UserFriendsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendNetwork
        fields = ['friend_username']
