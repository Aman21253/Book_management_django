from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone

from .utils import admin_or_liberarian_required, student_required
from .models import Books, Students, BookAssignment
from .form import (
    LoginForm,
    RegisterForm,
    BookForm,
    StudentForm,
    IssueBookForm
)

# ---------------- AUTH ----------------

def login_view(request):
    if request.user.is_authenticated:
        return redirect("book_list")

    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("book_list")
        else:
            form.add_error(None, "Invalid username or password")

    return render(request, "login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("book_list")

    form = RegisterForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        role = form.cleaned_data["role"]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        group = Group.objects.get(name=role)
        user.groups.add(group)

        login(request, user)
        return redirect("book_list")

    return render(request, "register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")


# ---------------- BOOKS ----------------

@login_required(login_url="login")
def book_list(request):
    if request.user.groups.filter(name="student").exists():
        return redirect("my_issued_books")

    q = request.GET.get("q", "")
    books = Books.objects.all().order_by("id")

    if q:
        books = books.filter(
            Q(title__icontains=q) |
            Q(author__icontains=q) |
            Q(isbn__icontains=q)
        )

    paginator = Paginator(books, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "book_list.html", {
        "page_obj": page_obj,
        "q": q
    })


@login_required(login_url="login")
@admin_or_liberarian_required
def book_add(request):
    form = BookForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        book = form.save(commit=False)
        book.created_by = request.user
        book.save()
        return redirect("book_list")

    return render(request, "book_add.html", {"form": form})


# ---------------- STUDENTS ----------------

@login_required(login_url="login")
@admin_or_liberarian_required
def student_list(request):
    students = Students.objects.all().order_by("-id")
    return render(request, "student_list.html", {"students": students})


@login_required(login_url="login")
@admin_or_liberarian_required
def student_add(request):
    form = StudentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        password = form.cleaned_data["password"]

        with transaction.atomic():
            s = form.save()

            user = User.objects.create_user(
                username=s.email,
                password=password
            )

            # 3) student group assign
            group = Group.objects.get(name="student")
            user.groups.add(group)

        return redirect("student_list")
    return render(request, "student_add.html", {"form": form})

# ---------------- ISSUE / ASSIGN ----------------

@login_required(login_url="login")
@admin_or_liberarian_required
def issue_book(request):
    form = IssueBookForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        student = form.cleaned_data["student"]
        book = form.cleaned_data["book"]
        issue = form.cleaned_data["issue"] or timezone.localdate()

        active = BookAssignment.objects.filter(
            student=student,
            status=BookAssignment.STATUS_ISSUED
        ).first()

        if active:
            form.add_error(
                None,
                f"Student already has book: {active.book.title}"
            )
            return render(request, "issue_book.html", {"form": form})

        if book.quantity <= 0:
            form.add_error(None, "Book out of stock")
            return render(request, "issue_book.html", {"form": form})

        Books.objects.filter(id=book.id).update(
            quantity=F("quantity") - 1
        )

        BookAssignment.objects.create(
            student=student,
            book=book,
            issue=issue,
            assigned_by=request.user,
            status=BookAssignment.STATUS_ISSUED,
        )

        return redirect("assigned_books")

    return render(request, "issue_book.html", {"form": form})


@login_required(login_url="login")
@admin_or_liberarian_required
def assigned_books(request):
    assignments = BookAssignment.objects.select_related(
        "book", "student"
    ).all()

    return render(request, "assigned_books.html", {
        "assignments": assignments
    })


@login_required(login_url="login")
@admin_or_liberarian_required
def return_book(request, assignment_id):
    assignment = get_object_or_404(BookAssignment, id=assignment_id)

    if assignment.status == BookAssignment.STATUS_RETURNED:
        return redirect("assigned_books")

    assignment.status = BookAssignment.STATUS_RETURNED
    assignment.return_date = timezone.localdate()
    assignment.save()

    Books.objects.filter(id=assignment.book_id).update(
        quantity=F("quantity") + 1
    )

    return redirect("assigned_books")


# ---------------- STUDENT VIEW ----------------

@login_required(login_url="login")
@student_required
def my_issued_books(request):
    student = Students.objects.filter(
        email=request.user.email
    ).first()

    assignments = BookAssignment.objects.filter(
        student=student,
        status=BookAssignment.STATUS_ISSUED
    ) if student else BookAssignment.objects.none()

    return render(request, "my_issued_books.html", {
        "assignments": assignments,
        "is_student": True
    })