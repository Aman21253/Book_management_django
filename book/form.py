from django import forms
from .models import Books, Students

ROLE_CHOICES=[
    ("admin","Admin"),
    ("liberarian","Liberarian"),
    ("student", "Student"),
]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder":"username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder":"username"}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ["title", "author", "isbn", "price", "quantity", "about"]

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Confirm Password"}))

    class Meta:
        model = Students
        fields = [ "email", "phone" ,"address"]

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password")
        p2 = cleaned.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match")
        return cleaned

class IssueBookForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Students.objects.all())
    book = forms.ModelChoiceField(queryset=Books.objects.all())
    issue = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))