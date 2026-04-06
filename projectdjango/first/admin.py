from django.contrib import admin
from .models import AppUser, Team, Post, Comment, PostAttachment, CommentAttachment, Notification

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'team', 'created_at', 'due_date')
    list_filter = ('team', 'created_at')
    search_fields = ('title', 'body')

admin.site.register(AppUser)
admin.site.register(Team)
admin.site.register(Comment)
admin.site.register(PostAttachment)
admin.site.register(CommentAttachment)
admin.site.register(Notification)