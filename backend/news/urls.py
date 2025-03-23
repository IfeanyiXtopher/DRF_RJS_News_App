from django.urls import path
from .views import *

urlpatterns = [
    path('', news_post_list, name='news-list'),
    path('featured/', news_post_featured, name='news-featured'),
    path('category/', news_post_category, name='news-category'),
    path('csrf-token/', csrf_token_view, name='csrf-token'),
    path('<slug:slug>/', news_post_detail, name='news-detail'),
    path('<int:pk>/track-view/', track_view, name='track_view'),
    path('<int:pk>/like/', like_news, name='like-news'),

    path('<int:pk>/reactions/', get_reactions, name='get-reactions'),
    path('<int:pk>/user_reaction/', get_user_reaction, name='get-user-reaction'),

]