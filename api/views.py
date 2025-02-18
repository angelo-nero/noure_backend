from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from .models import Category, Discussion, Comment, News, ProgrammingLanguage, CodeSnippet, Code, Tag, Blog
from .serializers import CategorySerializer, DiscussionSerializer, CommentSerializer, UserSerializer, DiscussionCreateSerializer, CommentCreateSerializer, NewsSerializer, ProgrammingLanguageSerializer, CodeSnippetSerializer, CodeSnippetCreateSerializer, TagSerializer, BlogSerializer, BlogCreateSerializer, UserCreateSerializer, GroupSerializer
import logging
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

User = get_user_model()

# Create your views here.

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]  # Only admin users can manage categories
    
    def get_queryset(self):
        # Add ordering to make the list consistent
        return Category.objects.all().order_by('name')

class DiscussionPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class DiscussionViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    pagination_class = DiscussionPagination
    
    def get_queryset(self):
        queryset = Discussion.objects.all().order_by('-created_at')  # Most recent first
        category = self.request.query_params.get('category', None)
        
        logger.debug(f"Category parameter received: {category}")
        
        if category is not None:
            queryset = queryset.filter(category__slug=category)
            logger.debug(f"Filtered queryset count: {queryset.count()}")
            
        return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return DiscussionCreateSerializer
        return DiscussionSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data
        
        return Response({
            'token': str(refresh.access_token),
            'user': user_data
        })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )


class NewsViewSet(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Override to ensure only admin users can create/update/delete
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [AllowAny()]

class ProgrammingLanguageViewSet(viewsets.ModelViewSet):
    queryset = ProgrammingLanguage.objects.all()
    serializer_class = ProgrammingLanguageSerializer
    permission_classes = [IsAdminUser]  # Only admin users can manage languages
    
    def get_queryset(self):
        return ProgrammingLanguage.objects.all().order_by('name')

class CodeSnippetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CodeSnippetSerializer
    queryset = CodeSnippet.objects.all()

    def get_queryset(self):
        sort_by = self.request.query_params.get('sort', 'newest')
        queryset = CodeSnippet.objects.all()\
            .select_related('author')\
            .prefetch_related('codes', 'codes__language', 'likes', 'dislikes')
        
        if sort_by == 'oldest':
            return queryset.order_by('created_at')
        elif sort_by == 'most_liked':
            return sorted(queryset.all(), key=lambda x: (-x.likes_count, -x.created_at.timestamp()))
        else:  # newest
            return queryset.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'create':
            return CodeSnippetCreateSerializer
        return CodeSnippetSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        snippet = self.get_object()
        user = request.user
        
        if user in snippet.dislikes.all():
            snippet.dislikes.remove(user)
        
        if user in snippet.likes.all():
            snippet.likes.remove(user)
            reaction = None
        else:
            snippet.likes.add(user)
            reaction = 'like'
        
        return Response({
            'likes_count': snippet.likes_count,
            'dislikes_count': snippet.dislikes_count,
            'user_reaction': reaction
        })

    @action(detail=True, methods=['POST'])
    def dislike(self, request, pk=None):
        snippet = self.get_object()
        user = request.user
        
        if user in snippet.likes.all():
            snippet.likes.remove(user)
        
        if user in snippet.dislikes.all():
            snippet.dislikes.remove(user)
            reaction = None
        else:
            snippet.dislikes.add(user)
            reaction = 'dislike'
        
        return Response({
            'likes_count': snippet.likes_count,
            'dislikes_count': snippet.dislikes_count,
            'user_reaction': reaction
        })

class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

class BlogViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return BlogCreateSerializer
        return BlogSerializer

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = Blog.objects.all().order_by('-created_at')
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        return queryset.distinct()

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        blog = self.get_object()
        user = request.user
        
        if user in blog.likes.all():
            blog.likes.remove(user)
            liked = False
        else:
            blog.likes.add(user)
            liked = True
        
        return Response({
            'likes_count': blog.likes_count,
            'user_has_liked': liked
        })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def toggle_user_status(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_user(request):
    try:
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response(UserSerializer(user).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Group.objects.all().order_by('name')
