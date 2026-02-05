from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, F
from django.utils import timezone

from .models import Books, Students, BookAssignment
from .form import LoginForm, BookForm, StudentForm, IssueBookForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("book_list")
    
    form = LoginForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        username= form.cleaned_data["username"]
        password= form.cleaned_data["password"]

        user= authenticate(request, username=username, password=password)
        if user:
            login(request,user)
            return redirect("book_list")
        else:
            form.add_error(None, "Invalid username")
    return render(request,"login.html",{"form":form})

def logout_view(request):
    logout(request)
    return redirect("login")

# book list
@login_required(login_url="login")
def book_list(request):
    q = request.GET.get("q", "")
    books = Books.objects.all().order_by("id")
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q))

    paginator = Paginator(books, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "book_list.html", {"page_obj": page_obj, "q": q})

# book add
@login_required(login_url="login")
def book_add(request):
    form = BookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        book = form.save(commit=False)
        book.created_by = request.user
        book.save()
        return redirect("book_list")
    return render(request, "book_add.html", {"form": form})

# Student list
@login_required(login_url="login")
def student_list(request):
    students = Students.objects.all().order_by("-id")
    return render(request, "student_list.html", {"students": students})

# Student add
@login_required(login_url="login")
def student_add(request):
    form = StudentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        s = form.save(commit=False)
        s.created_by = request.user
        s.save()
        return redirect("student_list")
    return render(request, "student_add.html", {"form": form})

# Assigned books
@login_required(login_url="login")
def issue_book(request):
    form = IssueBookForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        student = form.cleaned_data["student"]
        book = form.cleaned_data["book"]
        issue_date = form.cleaned_data["issue_date"] or timezone.localdate()

        active = BookAssignment.objects.filter(student=student, status=BookAssignment.STATUS_ISSUED).first()
        if active:
            form.add_error(None, f"Student already has an issued book: {active.book.title}. Return it first.")
            return render(request, "issue_book.html", {"form": form})

        if book.quantity <= 0:
            form.add_error(None, "Book out of stock")
            return render(request, "issue_book.html", {"form": form})

        # decrease stock
        Books.objects.filter(id=book.id).update(quantity=F("quantity") - 1)

        assignment = BookAssignment.objects.create(
            student=student,
            book=book,
            issue_date=issue_date,
            assigned_by=request.user,
            status=BookAssignment.STATUS_ISSUED,
        )

        return redirect("assigned_books")

    return render(request, "issue_book.html", {"form": form})

# Assign list
@login_required(login_url="login")
def assigned_books(request):
    data = BookAssignment.objects.select_related("book", "student").all().order_by("id")
    return render(request, "assigned_books.html", {"assignments": data})

# Total assigned book
@login_required(login_url="login")
def return_book(request, assignment_id):
    assignment = get_object_or_404(BookAssignment, id=assignment_id)

    if assignment.status == BookAssignment.STATUS_RETURNED:
        return redirect("assigned_books")

    assignment.status = BookAssignment.STATUS_RETURNED
    assignment.return_date = timezone.localdate()
    assignment.save()

    Books.objects.filter(id=assignment.book_id).update(quantity=F("quantity") + 1)

    return redirect("assigned_books")