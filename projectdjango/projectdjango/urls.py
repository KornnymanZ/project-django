from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from first.api_views import TeamViewSet, PostViewSet, CommentViewSet, GoogleLoginView

# Configure Mobile Router
router = routers.DefaultRouter()
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('first.urls')),
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Secure Mobile Endpoints
    path('api/', include(router.urls)),
    path('api/auth/google/', GoogleLoginView.as_view(), name='api_google_login'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
