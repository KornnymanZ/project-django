from rest_framework import serializers
from .models import AppUser, Team, Post, PostAttachment, Comment, CommentAttachment, Notification

class AppUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUser
        fields = ['id', 'name', 'email', 'profile_picture']

class TeamSerializer(serializers.ModelSerializer):
    groupmembers = AppUserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Team
        fields = ['id', 'name', 'groupmembers']

class PostAttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.ReadOnlyField()
    download_url = serializers.ReadOnlyField()

    class Meta:
        model = PostAttachment
        fields = ['id', 'file', 'filename', 'download_url']

class CommentAttachmentSerializer(serializers.ModelSerializer):
    filename = serializers.ReadOnlyField()
    download_url = serializers.ReadOnlyField()

    class Meta:
        model = CommentAttachment
        fields = ['id', 'file', 'filename', 'download_url']

class CommentSerializer(serializers.ModelSerializer):
    author = AppUserSerializer(read_only=True)
    attachments = CommentAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'body', 'created_at', 'attachments']
        read_only_fields = ['post', 'author', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    author = AppUserSerializer(read_only=True)
    attachments = PostAttachmentSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'team', 'author', 'title', 'body', 'created_at', 'due_date', 'attachments', 'comments']
        read_only_fields = ['team', 'author', 'created_at']
