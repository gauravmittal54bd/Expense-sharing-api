from django.db import models
import uuid
from django.utils import timezone

class User(models.Model):
    userid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobileNumber = models.CharField(max_length=15)
    balance = models.CharField(max_length=10, null=True, blank=True)
    owe = models.CharField(max_length=10, null=True, blank=True)
    to = models.CharField(max_length=255, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)


    def __str__(self):
        return self.name

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payer_id = models.CharField(max_length=255) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=20)
    share= models.TextField(default='[]')
    participants_ids = models.TextField(default='[]')
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Expense {self.id} - {self.amount}"
