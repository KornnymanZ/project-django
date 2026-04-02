from .models import Post, Notification

def notify_team_of_new_post(post_id):
    try:
        post = Post.objects.get(id=post_id)
        team = post.team
        author = post.author
        
        for member in team.groupmembers.all():
            if member != author:
                Notification.objects.create(
                    recipient=member,
                    message=f"{author.name} created a new post in {team.name}: '{post.title}'",
                    link=f"/team/{team.id}/#post-{post.id}"
                )
    except Post.DoesNotExist:
        pass

def send_due_date_reminder(post_id):
    try:
        post = Post.objects.get(id=post_id)
        team = post.team
        
        for member in team.groupmembers.all():
            Notification.objects.create(
                recipient=member,
                message=f"Reminder: Action required on '{post.title}' before it's due!",
                link=f"/team/{team.id}/#post-{post.id}"
            )
    except Post.DoesNotExist:
        pass
