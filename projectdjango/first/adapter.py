from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        user = sociallogin.user
        
        # 1. Match/Link existing User account by email
        if not sociallogin.is_existing and 'email' in sociallogin.account.extra_data:
            email = sociallogin.account.extra_data.get('email').lower()
            try:
                user = User.objects.get(email=email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass

        # 2. Pull first_name / last_name from the Google payload and fill them out
        if user and user.pk:
            extra_data = sociallogin.account.extra_data
            first_name = extra_data.get('given_name', '')
            last_name = extra_data.get('family_name', '')
            
            updated = False
            if first_name and not user.first_name:
                user.first_name = first_name
                updated = True
            if last_name and not user.last_name:
                user.last_name = last_name
                updated = True
                
            if updated:
                user.save()
