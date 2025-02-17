from rest_framework import serializers
from .models import Category, Discussion, Comment, News, ProgrammingLanguage, Code, CodeSnippet, Tag, Blog
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.contrib.auth.models import Group

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active')

    def get_role(self, obj):
        if obj.is_superuser:
            return 'admin'
        elif obj.is_staff:
            return 'moderator'
        return 'user'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Convert is_active to isActive for frontend
        if 'is_active' in data:
            data['isActive'] = data.pop('is_active')
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

class DiscussionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['title', 'content', 'category']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['discussion', 'content']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = '__all__'

class DiscussionSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Discussion
        fields = '__all__' 

class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        fields = ['id', 'title', 'body', 'created_at', 'updated_at']

class ProgrammingLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgrammingLanguage
        fields = ['id', 'name', 'slug', 'code']
        read_only_fields = ['id', 'slug']

class CodeSerializer(serializers.ModelSerializer):
    language = ProgrammingLanguageSerializer(read_only=True)
    language_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Code
        fields = ['id', 'language', 'language_id', 'code']

class CodeSnippetSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    codes = CodeSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    dislikes_count = serializers.IntegerField(read_only=True)
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = CodeSnippet
        fields = ['id', 'title', 'description', 'author', 'codes', 'created_at', 
                 'likes_count', 'dislikes_count', 'user_reaction']

    def get_user_reaction(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if user in obj.likes.all():
                return 'like'
            elif user in obj.dislikes.all():
                return 'dislike'
        return None

class CodeSnippetCreateSerializer(serializers.ModelSerializer):
    codes = CodeSerializer(many=True)

    class Meta:
        model = CodeSnippet
        fields = ['title', 'description', 'codes']

    def create(self, validated_data):
        codes_data = validated_data.pop('codes')
        snippet = CodeSnippet.objects.create(**validated_data)
        
        for code_data in codes_data:
            Code.objects.create(snippet=snippet, **code_data)
        
        return snippet

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class BlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    user_has_liked = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Blog
        fields = ['id', 'title', 'content', 'author', 'tags', 'image', 'image_url',
                 'created_at', 'updated_at', 'likes_count', 'user_has_liked']

    def get_user_has_liked(self, obj):
        user = self.context['request'].user
        return user in obj.likes.all() if user.is_authenticated else False

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
        return None

class BlogCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = Blog
        fields = ['title', 'content', 'image', 'tags']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        blog = Blog.objects.create(**validated_data)
        
        for tag_name in tags_data:
            tag, _ = Tag.objects.get_or_create(
                name=tag_name.lower(),
                slug=slugify(tag_name)
            )
            blog.tags.add(tag)
        
        return blog

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['user', 'moderator', 'admin'])

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'is_active')

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.pop('role', 'user')
        
        user = User.objects.create(
            **validated_data,
            is_active=True
        )
        user.set_password(password)
        
        # Set appropriate permissions based on role
        if role == 'admin':
            user.is_superuser = True
            user.is_staff = True
        elif role == 'moderator':
            user.is_staff = True
        
        user.save()
        return user

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']