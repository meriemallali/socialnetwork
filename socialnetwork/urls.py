from django.urls import path
from . import views

urlpatterns = [
    path('login', views.signin_user, name="login"),
    path('signup', views.register, name="signup"),
    path('logout', views.logout_user, name="logout"),
    path('', views.feed, name="feed"),
    path('sharepost', views.load_post, name="sharepost"),
    path('comment_post/<str:username>/<uuid:_id>/', views.comment_post, name='comment_post'),
    path('likes', views.heart_post, name="likes"),
    path('addfriend', views.add_friend, name="addfriend"),
    path('unfriend', views.unfriend, name="unfriend"),
    path('profile/<int:id>/<slug:username>', views.profile, name="profile"),
    path('search', views.search_username, name="searchresult"),
    path('settings', views.profile_settings, name="settings"),
    # Real time chat urls
    path('chat/<int:id>/<str:username>', views.chat, name='chat'),
    # rest urls
    path('restlinks', views.restLinks, name='restlinks'),
    path('api/userdata', views.UserData.as_view(), name='api_userdata'),
    path('api/userprofile', views.UserProfileView.as_view(), name='api_profile'),
    path('api/userpost', views.UserPostView.as_view(), name='api_post'),
]
