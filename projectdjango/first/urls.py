
from django.urls import path
from . import views

urlpatterns = [
    
    path('', views.home, name="home"),
    path('team/', views.team_page, name="team"),
    path('team/<int:team_id>/', views.team_detail, name="team_detail"),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('notification/<int:note_id>/', views.read_notification, name='read_notification'),
    path('profile/', views.profile_page, name='profile'),
    path('download/post/<int:attachment_id>/', views.download_post_attachment, name='download_post_attachment'),
    path('download/comment/<int:attachment_id>/', views.download_comment_attachment, name='download_comment_attachment'),
]
 