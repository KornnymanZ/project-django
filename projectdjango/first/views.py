import json
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
        
        # Globally extract all teams the user physically belongs to
        teams = app_profile.teams.all()
        # Filter all posts across all valid teams that possess any distinct due_date 
        due_posts = Post.objects.filter(team__in=teams, due_date__isnull=False).order_by('due_date')
        
        # Explicitly array mapping the upcoming components
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
    if hasattr(request.user, 'app_profile') and request.user.app_profile:
        teams = request.user.app_profile.teams.prefetch_related('groupmembers').all()
    return render(request, 'team.html', {'teams': teams})

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
                
            # Fire notification to teammates synchronously (no background worker needed)
            notify_team_of_new_post(post.id)
            
            # Check for due date and spawn negative offset reminder if valid
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
