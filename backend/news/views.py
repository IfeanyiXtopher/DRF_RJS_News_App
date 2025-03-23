from rest_framework.response import Response
from rest_framework import permissions, status, filters
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from news.models import *
from news.serializers import *
from django.middleware.csrf import get_token
from django.http import JsonResponse


def csrf_token_view(request):
    return JsonResponse({"csrfToken": get_token(request)})

@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    if request.method == 'POST':
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomPagination(PageNumberPagination):
    page_size = 3  # Number of news items per page
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def news_post_list(request):
    queryset = NewsPost.objects.order_by('-date_created')

    search_query = request.GET.get('search', None)
    if search_query:
        queryset = queryset.filter(tags__icontains=search_query)

    # Apply pagination
    paginator = CustomPagination()
    paginated_queryset = paginator.paginate_queryset(queryset, request)

    serializer = NewsPostSerializer(paginated_queryset, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'DELETE'])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def news_post_detail(request, slug):
    print(f"Authenticated User: {request.user}")  # Debugging
    print(f"Is Authenticated: {request.user.is_authenticated}")  # Debugging
    
    news_post = get_object_or_404(NewsPost, slug=slug)

    if request.method == 'GET':
        serializer = NewsPostSerializer(news_post)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_403_FORBIDDEN)
        
        news_post.delete()
        return Response({'message': 'News post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)



@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def news_post_featured(request):
    queryset = NewsPost.objects.filter(featured=True)
    serializer = NewsPostSerializer(queryset, many=True)
    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def news_post_category(request):
    category = request.data.get('category', None)
    if category:
        queryset = NewsPost.objects.filter(category__iexact=category).order_by('-date_created')
        # Apply pagination
        paginator = CustomPagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = NewsPostSerializer(paginated_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)
    return Response({'error': 'Category not provided'}, status=status.HTTP_400_BAD_REQUEST)

    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_news(request, pk):
    try:
        liked = request.data.get('liked')
        if liked is None:
            return Response({"detail": "Missing 'liked' parameter"}, status=status.HTTP_400_BAD_REQUEST)

        like, created = Like.objects.get_or_create(user=request.user, news_id=pk)
        
        if not created and like.liked == liked:
            like.delete()
            return Response({"detail": "Like/Dislike removed."}, status=status.HTTP_204_NO_CONTENT)
        
        like.liked = liked
        like.save()
        return Response(LikeSerializer(like).data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_reaction(request, pk):
    user = request.user
    try:
        like = Like.objects.get(user=user, news_id=pk)
        return Response({"reaction": like.liked}, status=status.HTTP_200_OK)
    except Like.DoesNotExist:
        return Response({"reaction": None}, status=status.HTTP_200_OK)



@api_view(['GET'])
def get_reactions(request, pk):
    likes = Like.objects.filter(news_id=pk, liked=True).count()
    dislikes = Like.objects.filter(news_id=pk, liked=False).count()
    return Response({"likes": likes, "dislikes": dislikes}, status=status.HTTP_200_OK) 


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def track_view(request, pk):
    try:
        news = NewsPost.objects.get(pk=pk)
    except NewsPost.DoesNotExist:
        return Response({"error": "News article not found."}, status=status.HTTP_404_NOT_FOUND)

    # Get the user (if authenticated) or IP address (if anonymous)
    user = request.user if request.user.is_authenticated else None
    ip_address = request.META.get('REMOTE_ADDR')

    # Check if the view already exists
    if View.objects.filter(news=news, user=user, ip_address=ip_address).exists():
        return Response({"message": "View already tracked."}, status=status.HTTP_200_OK)

    # Create a new view
    View.objects.create(news=news, user=user, ip_address=ip_address)
    return Response({"message": "View tracked successfully."}, status=status.HTTP_201_CREATED)