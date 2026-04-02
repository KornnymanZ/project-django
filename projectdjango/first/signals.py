from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth.models import Group
from .models import AppUser

@receiver(user_signed_up)
def link_to_app_user(sender, request, user, **kwargs):
    # 1. Look for a pre-registered AppUser with this email
    email = user.email
    app_profile = AppUser.objects.filter(email=email, user__isnull=True).first()

    if app_profile:
        # 2. Link the new Social Auth User to the existing AppUser
        app_profile.user = user
        app_profile.email = email
        app_profile.save()
    else:
        # Optional: If they aren't pre-registered, you could log them out 
        # or delete the user if you want strict "Invite Only"
        pass

@receiver(user_logged_in)
def set_user_group(sender, request, user, **kwargs):
    print(f"DEBUG: Login signal fired for {user.email}")
    email = user.email.lower() if user.email else ""

    # Ensure the AppUser is linked to this user if it exists and isn't linked
    if hasattr(user, 'app_profile') and user.app_profile is not None:
        app_profile = user.app_profile
        # If it's linked but missing a name, fill it in!
        if not app_profile.name and (user.first_name or user.last_name):
            app_profile.name = f"{user.first_name} {user.last_name}".strip()
            app_profile.save()
    elif email:
        app_profile = AppUser.objects.filter(email=email, user__isnull=True).first()
        if app_profile:
            app_profile.user = user
            if not app_profile.name and (user.first_name or user.last_name):
                app_profile.name = f"{user.first_name} {user.last_name}".strip()
            app_profile.save()
            print(f"DEBUG: Auto-linked pre-made User to AppUser for {email}")

    # Check if they already have a group to avoid redundant database hits
    if not user.groups.exists() and email:
        
        # Logic: Adjust this list for your Advisors
        advisors = ['advisor@gmail.com', 'admin@gmail.com']
        
        if email in advisors:
            group_name = "Advisor"
        else:
            group_name = "Student"
            
        group, _ = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

@receiver(social_account_added)
def assign_group_to_new_social_user(request, sociallogin, **kwargs):
    user = sociallogin.user
    email = user.email.lower()

    # Define your logic
    advisors = ['advisor@gmail.com', 'student@gmail.com'] # Test with yours
    
    if email in advisors:
        group_name = "Advisor"
    else:
        group_name = "Student"

    group, created = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)
    
    # Save the user just in case, though adding to groups usually saves the M2M relation automatically
    user.save()
    print(f"DONE: {user.email} added to {group_name} group.")