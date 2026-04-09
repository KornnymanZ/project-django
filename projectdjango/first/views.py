import json
import mimetypes
import requests as http_requests
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Team, Post, PostAttachment, Comment, CommentAttachment, Notification
from .forms import PostForm, CommentForm, ProfileUpdateForm
from .tasks import notify_team_of_new_post, send_due_date_reminder

def home(request):
    events = []
    upcoming_posts = []
    
    if request.user.is_authenticated and hasattr(request.user, 'app_profile'):
        app_profile = request.user.app_profile
        now = timezone.now()
        
        
        teams = app_profile.teams.all()
        # Filter all posts from all teams that the user are in with due date
        due_posts = Post.objects.filter(team__in=teams, due_date__isnull=False).order_by('due_date')
        
        
        upcoming_posts = due_posts.filter(due_date__gte=now)
        
        for post in due_posts:
            events.append({
                'title': post.title[:20] + ('...' if len(post.title) > 20 else ''),
                'start': post.due_date.isoformat(),
                'url': reverse('team_detail', args=[post.team.id]) + f'#post-{post.id}',
                'backgroundColor': '#ffc107',
                'borderColor': '#ffc107',
                'textColor': '#000'
            })
            
    return render(request, 'home.html', {
        'events_list': events,
        'upcoming_posts': upcoming_posts
    })

@login_required
def team_page(request):
    teams = []
    requests_made = []
    if hasattr(request.user, 'app_profile') and request.user.app_profile:
        teams = request.user.app_profile.teams.prefetch_related('groupmembers').all()
        requests_made = request.user.app_profile.requests_made.all().order_by('-created_at')
    return render(request, 'team.html', {'teams': teams, 'requests_made': requests_made})

@login_required
def team_detail(request, team_id):
    if not hasattr(request.user, 'app_profile') or not request.user.app_profile:
        return redirect('home')

    app_profile = request.user.app_profile
    team = get_object_or_404(Team, id=team_id)

    if not team.groupmembers.filter(id=app_profile.id).exists():
        return redirect('team')
        
    posts = team.posts.prefetch_related('attachments', 'author', 'comments__author', 'comments__attachments').all()

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.team = team
            post.author = app_profile
            post.save()
            
            files = request.FILES.getlist('attachments')
            for f in files:
                PostAttachment.objects.create(post=post, file=f)
                
            # Send notification
            notify_team_of_new_post(post.id)
            
            # Check for due date and send reminder
            if post.due_date:
                reminder_time = post.due_date - timedelta(days=2)
                if reminder_time > timezone.now():
                    send_due_date_reminder(post.id)
                
            return redirect('team_detail', team_id=team.id)
    else:
        form = PostForm()

    comment_form = CommentForm()

    return render(request, 'team_detail.html', {'team': team, 'posts': posts, 'form': form, 'comment_form': comment_form, 'app_profile': app_profile})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author.user_id != request.user.id:
        return redirect('team_detail', team_id=post.team.id)
        
    if request.method == "POST":
        team_id = post.team.id
        post.delete()
        return redirect('team_detail', team_id=team_id)
        
    return redirect('team_detail', team_id=post.team.id)

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if post.author.user_id != request.user.id:
        return redirect('team_detail', team_id=post.team.id)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            
            files = request.FILES.getlist('attachments')
            for f in files:
                PostAttachment.objects.create(post=post, file=f)
                
            return redirect('team_detail', team_id=post.team.id)
    else:
        form = PostForm(instance=post)
        
    return render(request, 'edit_post.html', {'form': form, 'team_id': post.team.id})

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    app_profile = request.user.app_profile
    
    if not post.team.groupmembers.filter(id=app_profile.id).exists():
        return redirect('team')
        
    if request.method == "POST":
        form = CommentForm(request.POST, request.FILES)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = app_profile
            comment.save()
            
            files = request.FILES.getlist('attachments')
            for f in files:
                CommentAttachment.objects.create(comment=comment, file=f)
                
            from .tasks import notify_author_of_new_comment
            notify_author_of_new_comment(comment.id)
                
    return redirect('team_detail', team_id=post.team.id)

@login_required
def read_notification(request, note_id):
    note = get_object_or_404(Notification, id=note_id, recipient=request.user.app_profile)
    note.is_read = True
    note.save()
    return redirect(note.link)

@login_required
def profile_page(request):
    app_profile = request.user.app_profile
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=app_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=app_profile)
        
    teams = app_profile.teams.prefetch_related('groupmembers').all()
    
    return render(request, 'profile.html', {
        'app_profile': app_profile,
        'form': form,
        'teams': teams
    })

@login_required
def download_post_attachment(request, attachment_id):
    """Proxy download: fetches from Cloudinary server-side to bypass free-tier PDF block."""
    attachment = get_object_or_404(PostAttachment, id=attachment_id)
    return _proxy_download(attachment.file, attachment.filename)

@login_required
def download_comment_attachment(request, attachment_id):
    """Proxy download: fetches from Cloudinary server-side to bypass free-tier PDF block."""
    attachment = get_object_or_404(CommentAttachment, id=attachment_id)
    return _proxy_download(attachment.file, attachment.filename)

def _proxy_download(file_field, filename):
    """Streams a file from Cloudinary through Django using SDK-signed authentication."""
    import cloudinary.utils
    import os
    
    file_name = file_field.name
    public_id = file_name

    base, ext = os.path.splitext(file_name)
    file_format = ext.lstrip('.')  # e.g., "pdf"
    
    signed_url, _ = cloudinary.utils.cloudinary_url(
        base,
        resource_type="raw",
        sign_url=True,
        type="upload",
        format=file_format
    )
    
    print(f"DEBUG PROXY: Attempting signed URL: {signed_url}")
    
    # Fetch the file using the signed/authenticated URL
    resp = http_requests.get(signed_url, timeout=30)
    
    if resp.status_code != 200:
        #Try download the url
        direct_url = file_field.url
        print(f"DEBUG PROXY: Signed URL failed ({resp.status_code}), trying direct: {direct_url}")
        resp = http_requests.get(direct_url, timeout=30)
        
        if resp.status_code != 200:
            print(f"DEBUG PROXY: Direct URL also failed ({resp.status_code})")
            return HttpResponse("File not available.", status=404)
    
    content_type, _ = mimetypes.guess_type(filename)
    if not content_type:
        content_type = 'application/octet-stream'
    
    response = HttpResponse(resp.content, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

from .models import TeamRequest, TeamRequestAttachment
from .forms import TeamRequestForm, TeamResponseForm

@login_required
def toggle_pin_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    is_author = (post.author.user_id == request.user.id)
    is_advisor = request.user.groups.filter(name='Advisor').exists() or request.user.is_staff
    
    if not (is_author or is_advisor):
        return redirect('team_detail', team_id=post.team.id)

    if request.method == "POST":
        post.is_pinned = not post.is_pinned
        post.save()
        
    return redirect('team_detail', team_id=post.team.id)

@login_required
def create_team_request(request):
    app_profile = getattr(request.user, 'app_profile', None)
    if not app_profile:
        return redirect('home')

    if app_profile.teams.exists() and not request.user.groups.filter(name='Advisor').exists():
        return redirect('team')

    if request.method == "POST":
        form = TeamRequestForm(request.POST, request.FILES, current_user=request.user)
        if form.is_valid():
            team_request = form.save(commit=False)
            team_request.requested_by = app_profile
            team_request.save()
            form.save_m2m()

            files = request.FILES.getlist('attachments')
            for f in files:
                TeamRequestAttachment.objects.create(team_request=team_request, file=f)

            from .tasks import notify_advisors_of_team_request
            notify_advisors_of_team_request(team_request.id)

            return redirect('team')
    else:
        form = TeamRequestForm(current_user=request.user)

    return render(request, 'create_team_request.html', {'form': form})

@login_required
def manage_team_requests(request):
    if not request.user.groups.filter(name='Advisor').exists() and not request.user.is_staff:
        return redirect('home')

    app_profile = getattr(request.user, 'app_profile', None)
    if not app_profile:
        return redirect('home')

    pending_requests = app_profile.advisor_requests.filter(status='Pending').order_by('-created_at')
    
    return render(request, 'manage_team_requests.html', {'requests': pending_requests})

@login_required
def respond_team_request(request, request_id):
    if not request.user.groups.filter(name='Advisor').exists() and not request.user.is_staff:
        return redirect('home')
        
    team_request = get_object_or_404(TeamRequest, id=request_id)
    
    if request.method == "POST":
        form = TeamResponseForm(request.POST, instance=team_request)
        action = request.POST.get('action')
        
        if form.is_valid():
            team_request = form.save(commit=False)
            team_request.responded_by = request.user.app_profile
            
            if action == 'approve':
                team_request.status = 'Approved'
                team_request.save()
                
                new_team = Team.objects.create(name=team_request.team_name)
                
                new_team.groupmembers.add(team_request.requested_by)
                for member in team_request.proposed_members.all():
                    new_team.groupmembers.add(member)
                for advisor in team_request.proposed_advisors.all():
                    new_team.groupmembers.add(advisor)
                    
            elif action == 'reject':
                team_request.status = 'Rejected'
                team_request.save()
                
            from .tasks import notify_student_of_request_decision
            notify_student_of_request_decision(team_request.id)
            
            return redirect('manage_team_requests')
            
    else:
        form = TeamResponseForm(instance=team_request)
        
    return render(request, 'respond_team_request.html', {'team_request': team_request, 'form': form})

