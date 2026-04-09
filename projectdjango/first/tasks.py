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

from .models import Comment, TeamRequest

def notify_author_of_new_comment(comment_id):
    try:
        comment = Comment.objects.get(id=comment_id)
        post = comment.post
        post_author = post.author
        comment_author = comment.author
        
        if post_author != comment_author:
            Notification.objects.create(
                recipient=post_author,
                message=f"[{post.team.name}] {comment_author.name} commented on your post '{post.title}'",
                link=f"/team/{post.team.id}/#post-{post.id}"
            )
    except Comment.DoesNotExist:
        pass

def notify_advisors_of_team_request(request_id):
    try:
        team_request = TeamRequest.objects.get(id=request_id)
        requester = team_request.requested_by
        
        for advisor in team_request.proposed_advisors.all():
            Notification.objects.create(
                recipient=advisor,
                message=f"New team request '{team_request.team_name}' from {requester.name}",
                link='/team/requests/manage/'
            )
    except TeamRequest.DoesNotExist:
        pass

def notify_student_of_request_decision(request_id):
    try:
        team_request = TeamRequest.objects.get(id=request_id)
        requester = team_request.requested_by
        status = team_request.status
        
        Notification.objects.create(
            recipient=requester,
            message=f"Team request '{team_request.team_name}' was {status.lower()}.",
            link='/team/'  # Route back to teams page
        )
    except TeamRequest.DoesNotExist:
        pass
