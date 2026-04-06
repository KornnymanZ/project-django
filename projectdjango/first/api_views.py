from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from .models import Team, Post, Comment, AppUser
from .serializers import TeamSerializer, PostSerializer, CommentSerializer

User = get_user_model()

class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    
    #API endpoint listing all Teams a User is in.
    
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'app_profile'):
            return user.app_profile.teams.all()
        return Team.objects.none()

class PostViewSet(viewsets.ModelViewSet):
    
    #API endpoint streaming Posts inside Teams the User belongs to.
   
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'app_profile'):
            teams = user.app_profile.teams.all()
            return Post.objects.filter(team__in=teams)
        return Post.objects.none()

    def perform_create(self, serializer):
        # Link the post to the author
        serializer.save(author=self.request.user.app_profile)


class CommentViewSet(viewsets.ModelViewSet):
    
    #API endpoint managing real-time Comment.
    
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'app_profile'):
            teams = user.app_profile.teams.all()
            return Comment.objects.filter(post__team__in=teams)
        return Comment.objects.none()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.app_profile)

class GoogleLoginView(APIView):
    
    #API Endpoint for google login via mobile token
    
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('id_token')
        if not token:
            return Response({'error': 'id_token required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify the mobile device token authenticity
        response = requests.get(f'https://oauth2.googleapis.com/tokeninfo?id_token={token}')
        if response.status_code != 200:
            return Response({'error': 'Invalid Google token'}, status=status.HTTP_400_BAD_REQUEST)
            
        user_info = response.json()
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        if not email:
            return Response({'error': 'No email provided by Google'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Retrieve or dynamically map the legacy AppUser schema
        user, created = User.objects.get_or_create(email=email, defaults={'username': email})
        app_user, app_created = AppUser.objects.get_or_create(
            user=user, 
            defaults={'email': email, 'name': name}
        )
        
        # Bypass password systems by providing a standard Token Payload
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
