from django import forms
from .models import Books, Students

ROLE_CHOICES=[
    ("admin","Admin"),
    ("liberarian","Liberarian"),
    ("student","Student"),
]

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, widget=forms.TextInput(attrs={"placeholder":"username"}))
    email = forms.EmailField(required=False, widget=forms.EmailInput(attrs={"placeholder":"Email"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder":"Password"}))
    role = forms.ChoiceField(choices=ROLE_CHOICES)

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ["title", "author", "isbn", "price", "quantity", "about"]

class StudentForm(forms.ModelForm):
    class Meta:
        model = Students
        fields = ["name", "email", "phone", "address"]

class IssueBookForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Students.objects.all())
    book = forms.ModelChoiceField(queryset=Books.objects.all())
    issue_date = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))