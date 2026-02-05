from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import uuid

# Pass:ABAB@1234

# Book
class Books(models.Model):
    title= models.CharField(max_length=50)
    author= models.CharField(max_length=50)
    isbn = models.CharField(max_length=13, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField( default=0)
    about = models.CharField(max_length=1000, blank=True, default = "-")
    number_of_pages= models.CharField(max_length=5, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    updated_at= models.DateTimeField( auto_now=True )

    class Meta:
        db_table = "book_details"

    def __str__(self):
        return self.title

# Student
class Students(models.Model):
    name= models.CharField(max_length=50)
    email= models.EmailField( max_length=254)
    phone= models.CharField(max_length=10, unique= True)
    address= models.TextField()

    def __str__(self):
        return self.name

# Book assign
class BookAssignment(models.Model):
    STATUS_ISSUED = "issued"
    STATUS_RETURNED= "returned"

    STATUS_CHOISES = [
        (STATUS_ISSUED,"issued"),
        (STATUS_RETURNED,"returned")
    ]

    transaction_id = models.UUIDField(default= uuid.uuid4, editable=False, unique=True)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, related_name="assignement")
    student= models.ForeignKey(Students, on_delete=models.CASCADE, related_name="assignment")
    issue = models.DateField(null=True, blank=False)
    return_date = models.DateField( auto_now=True )
    status= models.CharField(max_length=20 , choices=STATUS_CHOISES, default=STATUS_ISSUED)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "book_assignments"
        ordering = ["issue"]
    
    def __str__(self):
        return f"{self.transaction_id} | {self.book.title} -> {self.student.name} ({self.status})"
