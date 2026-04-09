from django import forms
from .models import Post, Comment, AppUser

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(attrs={'class': 'form-control'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class PostForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        label="Attach Files"
    )

    class Meta:
        model = Post
        fields = ['title', 'body', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Give your post a title...', 'required': 'True'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write what you want to share with the team. Any URLs you include will automatically turn into clickable links!', 'rows': 4, 'required': 'True'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'})
        }

class CommentForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        label="Attach Files"
    )

    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write a comment...', 'rows': 2, 'required': 'True'})
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = AppUser
        fields = ['profile_picture']
        widgets = {
            'profile_picture': forms.ClearableFileInput(attrs={'class': 'form-control', 'id': 'avatarInput'}),
        }

from .models import TeamRequest

class TeamRequestForm(forms.ModelForm):
    attachments = MultipleFileField(required=False, label="Attach Files (Optional)")
    
    class Meta:
        model = TeamRequest
        fields = ['team_name', 'description', 'proposed_members', 'proposed_advisors']
        widgets = {
            'team_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter proposed team name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your team/project'}),
        }

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)
        
        # Filter proposed_members: Only allow AppUsers NOT in any team AND NOT in Advisor group
        # excluding the current_user so they don't select themselves.
        self.fields['proposed_members'].widget.attrs.update({'class': 'form-select'})
        self.fields['proposed_members'].queryset = AppUser.objects.filter(
            teams__isnull=True, 
            user__groups__name__exact='Student'
        ).exclude(id=current_user.id if current_user else None).distinct()
        self.fields['proposed_members'].required = False
        
        # Filter proposed_advisors: Only allow AppUsers IN Advisor group.
        # They can be in multiple teams, so we don't check teams__isnull.
        self.fields['proposed_advisors'].widget.attrs.update({'class': 'form-select'})
        self.fields['proposed_advisors'].queryset = AppUser.objects.filter(
            user__groups__name__exact='Advisor'
        ).distinct()

class TeamResponseForm(forms.ModelForm):
    class Meta:
        model = TeamRequest
        fields = ['advisor_feedback']
        widgets = {
            'advisor_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional feedback for the student...'})
        }
