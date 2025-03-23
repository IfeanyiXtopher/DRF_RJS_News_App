from rest_framework import serializers
from .models import NewsPost, Like, User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_superuser'] = user.is_superuser
        # ...

        return token


class NewsPostSerializer(serializers.ModelSerializer):
    views_count = serializers.SerializerMethodField()
    
    likes_count = serializers.SerializerMethodField()
    likes_user_ids = serializers.SerializerMethodField()

    dislikes_count = serializers.SerializerMethodField()
    dislikes_user_ids = serializers.SerializerMethodField()

    class Meta:
        model = NewsPost
        fields = '__all__'

    def get_views_count(self, obj):
        """Returns the total number of views"""
        return obj.views.count()

    def get_likes_count(self, obj):
        """Returns the count of likes"""
        return obj.likes.filter(liked=True).count()

    def get_dislikes_count(self, obj):
        """Returns the count of dislikes"""
        return obj.likes.filter(liked=False).count()

    def get_likes_user_ids(self, obj):
        """Returns a list of user IDs who liked the news"""
        return [like.user.id for like in obj.likes.filter(liked=True)]

    def get_dislikes_user_ids(self, obj):
        """Returns a list of user IDs who disliked the news"""
        return [like.user.id for like in obj.likes.filter(liked=False)]



class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'news', 'liked']