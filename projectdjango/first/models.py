from django.db import models
from django.conf import settings
from cloudinary_storage.storage import RawMediaCloudinaryStorage

# Create your models here.
class AppUser(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank = True, null = True, related_name='app_profile')
    name = models.CharField(max_length=70)
    email = models.EmailField(unique=True)
    sid = models.CharField(max_length=50, unique=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', storage=RawMediaCloudinaryStorage(), null=True, blank=True)
    
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email

    @property
    def unread_notifications(self):
        return self.notifications.filter(is_read=False)
    
class Team(models.Model):
    name = models.CharField('Team Name', max_length=100)
    groupmembers = models.ManyToManyField(AppUser, related_name='teams')

    def __str__(self):
        return self.name

class Post(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.name}"

class PostAttachment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='team_posts/', storage=RawMediaCloudinaryStorage())

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)

    @property
    def download_url(self):
        """Forces the Cloudinary file to be downloaded by adding an attachment flag."""
        url = self.file.url
        if 'upload/' in url:
            return url.replace('upload/', 'upload/fl_attachment/')
        return url

    def __str__(self):
        return self.filename

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.name} on {self.post.title}"

class CommentAttachment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='team_comments/', storage=RawMediaCloudinaryStorage())

    @property
    def filename(self):
        import os
        return os.path.basename(self.file.name)

    @property
    def download_url(self):
        #Force cloudinary to download the file
        url = self.file.url
        if 'upload/' in url:
            return url.replace('upload/', 'upload/fl_attachment/')
        return url

    def __str__(self):
        return self.filename

class Notification(models.Model):
    recipient = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    link = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.recipient.name}: {self.message}"