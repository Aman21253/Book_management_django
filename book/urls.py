from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("", views.book_list, name="book_list"),
    path("books/add/", views.book_add, name="book_add"),

    path("students/", views.student_list, name="student_list"),
    path("students/add/", views.student_add, name="student_add"),

    path("issue/", views.issue_book, name="issue_book"),
    path("assigned/", views.assigned_books, name="assigned_books"),
    path("return/<int:assignment_id>/", views.return_book, name="return_book"),
]