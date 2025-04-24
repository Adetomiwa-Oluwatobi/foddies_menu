from django.db import models
from django.utils.functional import cached_property
from django.contrib.auth.models import User


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('online', 'Online'),
        ('pos', 'POS'),
        ('transfer', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('requesting', 'Requesting'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    ]

    table_number = models.IntegerField()
    item = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='pos')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='requesting')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Table {self.table_number}: {self.item} - ₦{self.price} ({self.status})"



class Payment(models.Model):
    orders = models.ManyToManyField(Order, related_name='payments')  # Link payment to multiple orders
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount for all items
    payment_reference = models.CharField(max_length=255, unique=True)
    payment_status = models.CharField(
        max_length=20, 
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], 
        default='pending'
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment - ₦{self.amount} ({self.payment_status})"


class MenuItem(models.Model):
    image =models.ImageField(upload_to='img/', null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.name




class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    hire_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.department or 'Unassigned'}"

class ProgressRecord(models.Model):
    PERFORMANCE_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('needs_improvement', 'Needs Improvement'),
    ]

    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='progress_records')
    evaluation_date = models.DateField()
    performance_rating = models.CharField(max_length=20, choices=PERFORMANCE_CHOICES)
    tasks_completed = models.IntegerField(default=0)
    comments = models.TextField(blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.evaluation_date}"

class AssignmentHistory(models.Model):
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='assignment_history')
    previous_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    previous_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='previous_assignments')
    new_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    new_role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name='new_assignments')
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-change_date']

    def __str__(self):
        return f"{self.staff.user.get_full_name()} - {self.change_date.date()}"