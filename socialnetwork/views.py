from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import auth
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .forms import *
from .models import *
from itertools import chain


# url : 'signup'
# description : for users to create new account.
def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirmedpassword = request.POST['confirmedpassword']
        # comparing the passwords, if match then check if user exists by email or username.
        # if not, register the new user and create its profile.
        if password == confirmedpassword:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email already exists')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username already taken, try with different one.')
                return redirect('signup')
            else:
                new_user = User.objects.create_user(username=username, email=email, password=password)
                new_user.save()

                # log user in
                logged_user = auth.authenticate(username=username, password=password)
                auth.login(request, logged_user)

                # create the profile for the new user
                new_userProfile = UserProfile.objects.create(user=User.objects.get(username=username),
                                                             userid=User.objects.get(username=username).id)
                new_userProfile.save()
                return redirect('login')
        else:
            messages.info(request, 'Passwords do not match. Re-enter password.')
            return redirect('signup')
    else:
        return render(
            request, 'signup.html')


# url : 'login'
# description: only registered users can sign in.
def signin_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        registered_user = authenticate(username=username, password=password)
        if registered_user:
            if registered_user.is_active:
                login(request, registered_user)
                return redirect('/')
            else:
                messages.info(request, 'Your account has been disabled.')
        else:
            messages.info(request, 'Invalid login details.')

    else:
        return render(request, 'login.html')

    return render(request, 'login.html')


# url: 'logout'
# description: only log in user can log out.
@login_required(login_url='login')
def logout_user(request):
    auth.logout(request)
    return redirect('login')


# url: 'sharepost'
# description: only logged-in user can upload a post. (status and images)
#              uploaded post will be accessible via the feed page and the post's owner profile.
@login_required(login_url='login')
def load_post(request):
    if request.method == 'POST':
        username = request.user.username
        media = request.FILES.get('media')
        description = request.POST['description']
        post_info = UserPost.objects.create(username=username, media=media, description=description)
        post_info.save()
        return redirect('/')
    return redirect('/')


# url: 'comment_post/<str:username>/<uuid:_id>/'
# description: logged-in user can comment on friends posts.
@login_required(login_url='login')
def comment_post(request, username, _id):
    if request.method == 'POST':
        comment_content = request.POST['comment']
        post = UserPost.objects.get(id=_id)
        owner = request.user
        comment = UserComment.objects.create(post=post, comment_owner=owner, comment=comment_content)
        comment.save()

    return redirect('/')


# url : 'likepost'
# description: logged-in user can like posts shared within the user's network.
@login_required(login_url='login')
def heart_post(request):
    username = request.user.username
    postid = request.GET.get('postid')

    current_post = UserPost.objects.get(id=postid)
    extract_hearts = PostLike.objects.filter(postid=postid, username=username).first()

    if extract_hearts is None:
        updated_heart = PostLike.objects.create(postid=postid, username=username)
        updated_heart.save()
        # increase the sum likes by one in user posts.
        current_post.sum_likes = current_post.sum_likes + 1
        current_post.save()
        return redirect('/')
    else:
        extract_hearts.delete()
        current_post.sum_likes = current_post.sum_likes - 1
        current_post.save()
        return redirect('/')


# url : 'search'
# description: logged-in user can search for other users.
@login_required(login_url='login')
def search_username(request):
    if request.method == 'POST':
        # get the input 'username' and then filter data.
        username = request.POST['username']
        search_object = User.objects.filter(username__icontains=username)

        searched_profiles = []
        searched_profiles_list = []

        for users in search_object:
            searched_profiles.append(users.id)

        for id in searched_profiles:
            profiles = UserProfile.objects.filter(userid=id)
            searched_profiles_list.append(profiles)

        searched_profiles_list = list(chain(*searched_profiles_list))
        print(searched_profiles_list)
        data = {
            'username': username,
            'search_result': searched_profiles_list
        }

    return render(request, 'searchresult.html', data)


# helper function to get the friends list.
def func_friends_list(current_user):
    friends_list = []
    friends = FriendNetwork.objects.filter(current_user_id=current_user)
    friends_reversed = FriendNetwork.objects.filter(user_friend_id=current_user)
    user_friends = FriendNetwork.objects.filter(current_user_id=current_user).first()
    user_friends_reversed = FriendNetwork.objects.filter(user_friend_id=current_user).first()

    if user_friends is None or user_friends_reversed is not None or user_friends is not None or user_friends_reversed is None:
        reversed_list = friends_reversed.values_list('username', flat=True)
        friends_list.extend(reversed_list)
        _list = friends.values_list('friend_username', flat=True)
        friends_list.extend(_list)

    return friends_list


# url: ''
# description: the home page of the application, contain list of the
#              logged-in user friends posts.
@login_required(login_url='login')
def feed(request):
    user_info = UserProfile.objects.get(user=request.user)
    posts_list = UserPost.objects.all()
    comments_in_each_post = {}
    posts_data = {}
    # retrieve each post with its comments and its profile owner.
    for post in posts_list:
        comments_list = UserComment.objects.filter(post=post)
        user_profile = User.objects.get(username=post.username)
        post_profile = UserProfile.objects.filter(user=user_profile)
        comments_in_each_post[post] = comments_list
        posts_data[post] = {
            'comments': comments_list,
            'profile': post_profile.first()
        }

    current_user = request.user.id
    friends_list = func_friends_list(current_user)
    friends_profiles = []
    # retrieve friends profiles.
    for friend in friends_list:
        user_friend = User.objects.get(username=friend)
        friend_profile = UserProfile.objects.filter(user=user_friend)
        friends_profiles.append(friend_profile)

    feed_data = {
        'profile': user_info,
        'posts_data': posts_data,
        'friends_list': friends_list,
        'friends_profiles': friends_profiles,
    }
    return render(request, 'home.html', feed_data)


# url : 'profile/<int:id>/<slug:username>/'
# description: to show the logged-in user its profile
@login_required(login_url='login')
def profile(request, id, username):
    if request.method == "GET":
        user_entity = User.objects.get(username=username, id=id)
        profiledata = UserProfile.objects.get(user=user_entity)
        posts = UserPost.objects.filter(username=username)
        posts_data = {}
        for post in posts:
            comments_list = UserComment.objects.filter(post=post)
            user_profile = User.objects.get(username=post.username)
            post_profile = UserProfile.objects.filter(user=user_profile)
            posts_data[post] = {
                'comments': comments_list,
                'profile': post_profile.first()
            }
        posts_length = len(posts)
        current_user = request.user.id
        current_profile = UserProfile.objects.get(user=current_user)
        friends_list = func_friends_list(current_user)
        friends_count = len(friends_list)

        profile_data = {
            'profiledata': profiledata,
            'profile': current_profile,
            'posts_length': posts_length,
            'friends_list': friends_list,
            'friends_count': friends_count,
            'posts': posts,
            'posts_data': posts_data,
        }
    return render(request, 'profile.html', profile_data)


# helper function to check if the friendship relation exist.
def check_friendship(current_user_id, user_friend_id):
    existing_friendship = FriendNetwork.objects.filter(current_user_id=current_user_id,
                                                       user_friend_id=user_friend_id).first()
    existing_friendship_reversed = FriendNetwork.objects.filter(current_user_id=user_friend_id,
                                                                user_friend_id=current_user_id).first()
    return existing_friendship is None or existing_friendship_reversed is None


# url: 'addfriend'
# description: 	users can add other users as friends.
@login_required(login_url='login')
def add_friend(request):
    if request.method == 'POST':
        username = request.POST['username']
        friend_username = request.POST['friend_username']
        current_user_id = request.POST['userid']
        user_friend_id = request.POST['user_friend_id']

        if check_friendship(current_user_id, user_friend_id):
            friendship = FriendNetwork.objects.create(current_user_id=current_user_id, user_friend_id=user_friend_id,
                                                      username=username, friend_username=friend_username)
            friendship.save()
            return redirect(f'profile/{user_friend_id}/{friend_username}')
    else:
        return redirect('/')


# url: 'unfriend'
# description: 	users can delete other users from the friend network.
@login_required(login_url='login')
def unfriend(request):
    if request.method == 'POST':
        username = request.POST['username']
        friend_username = request.POST['friend_username']
        current_user_id = request.POST['userid']
        user_friend_id = request.POST['user_friend_id']

        # check for friendship.
        friendship = check_friendship(current_user_id, user_friend_id)
        if friendship:
            FriendNetwork.objects.filter(current_user_id=current_user_id, user_friend_id=user_friend_id).delete()
            FriendNetwork.objects.filter(current_user_id=user_friend_id, user_friend_id=current_user_id).delete()
            return redirect(f'profile/{user_friend_id}/{friend_username}')

    else:
        return redirect(f'profile/{request.user.id}/{request.user.username}')


# url: 'settings'
# description: only logged-in users can access and change the account settings.
@login_required(login_url='login')
def profile_settings(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        # if profile photo is not updated, we keep the default blank profile.
        if request.FILES.get('profile_photo') is None:
            firstname = request.POST['first_name']
            lastname = request.POST['last_name']
            status = request.POST['profile_status']
            profile_photo = profile.profile_photo
            profile.first_name = firstname
            profile.last_name = lastname
            profile.profile_status = status
            profile.profile_photo = profile_photo
            profile.save()
        elif request.FILES.get('profile_photo') is not None:
            firstname = request.POST['first_name']
            lastname = request.POST['last_name']
            status = request.POST['profile_status']
            profile_photo = request.FILES.get('profile_photo')
            profile.first_name = firstname
            profile.last_name = lastname
            profile.profile_status = status
            profile.profile_photo = profile_photo
            profile.save()

        return redirect('settings')

    return render(request, 'settings.html', {'profile': profile})


# this is for the real chat
# url : 'chat/<int:id>/<str:username>'
# description : users can chat in realtime with friends
def chat(request, username, id):
    current_profile = UserProfile.objects.get(user=request.user)
    current_user = User.objects.get(username=username)
    current_user_id = request.user.id
    friends_list = func_friends_list(current_user_id)
    friends_profiles = []
    # retrieve user's friends profiles.
    for friend in friends_list:
        user_friend = User.objects.get(username=friend)
        friend_profile = UserProfile.objects.filter(user=user_friend)
        friends_profiles.append(friend_profile)

    # filter chat history
    if request.user.id <= current_user.id:
        chat_name = f'chat_{current_user.id}-{request.user.id}'
    else:
        chat_name = f'chat_{request.user.id}-{current_user.id}'

    # Retrieve chat history
    chat_history = Chat.objects.filter(chat_name=chat_name)

    context = {
        'user': current_user,
        'profile': current_profile,
        'friends_profiles': friends_profiles,
        'messages': chat_history,
    }

    return render(request, 'chat.html', context)


# API views -->

# url : 'restlinks'
# description : render the rest links to the rest interface page.
def restLinks(request):
    # rendering the user's profile, for the navigation bar.
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'restlinks.html', {'profile': profile})


# url : 'api/userdata'
# description : returns the profile information with  the posts and friend list.
class UserData(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.filter(user=request.user)
        user_posts = UserPost.objects.filter(username=request.user.username)
        user_friends = FriendNetwork.objects.filter(username=request.user.username)

        user_profile_serializer = UserProfileSerializer(user_profile, many=True).data
        user_posts_serializer = UserPOSTPostSerializer(user_posts, many=True).data
        user_friends_serializer = UserFriendsSerializer(user_friends, many=True).data
        friends_list = []
        for friend_username in user_friends_serializer:
            username = friend_username['friend_username']
            friends_list.append(username)

        data = {
            'profile': user_profile_serializer,
            'posts': user_posts_serializer,
            'friends list ': friends_list,
        }
        return Response(data)


# url : 'api/userprofile'
# description : returns the logged-in user profile
# and the HTML form for the user to change their profile data.
class UserProfileView(generics.ListCreateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return UserProfile.objects.filter(user=user)


# url : 'api/userpost'
# description : if method is get display all the logged-in user posts,
# if method is post allow the logged-in user to add a new post.
class UserPostView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserGETPostSerializer
        elif self.request.method == 'POST':
            return UserPOSTPostSerializer

    def get(self, request, *args, **kwargs):
        user_posts = UserPost.objects.filter(username=request.user.username)
        user_posts_serializer = UserGETPostSerializer(user_posts, many=True).data
        data = {
            'Posts': user_posts_serializer
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.data
            return Response(data)
        else:
            return Response(serializer.errors)

