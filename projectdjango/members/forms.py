from django import forms
from django.contrib.auth.models import User

class EmailUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}), label="Confirm Password")

    class Meta:
        model = User
        fields = ['email']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")
            
        # Ensure email is unique across the User model
        email = cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            self.add_error('email', "A user with that email already exists.")

        return cleaned_data

    def save(self, commit=True):
        from allauth.account.models import EmailAddress
        user = super().save(commit=False)
        # Use email for the underlying username mapping naturally 
        user.username = self.cleaned_data["email"]
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            # Intercept and securely inject the Allauth registry!
            EmailAddress.objects.create(user=user, email=user.email, primary=True, verified=True)
        return user
