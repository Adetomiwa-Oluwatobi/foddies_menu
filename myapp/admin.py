from django.contrib import admin
from .models import *

# Register the Order model
@admin.register(Order)


# Register your models here.


class OrderAdmin(admin.ModelAdmin):
    list_display = ('table_number', 'item', 'price', 'status', 'created_at')  # Display the status
    search_fields = ('table_number', 'item')
    list_filter = ('status', 'table_number', 'created_at')  # Add status to the filters
    actions = ['mark_as_delivered']  # Add a custom action

    # Custom action to mark orders as delivered
    @admin.action(description='Mark selected orders as delivered')
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='delivered')



@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['amount', 'payment_status', 'payment_reference', 'payment_date']
    
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'price', 'category')  # Display all fields in admin
    

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'department', 'created_at']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']