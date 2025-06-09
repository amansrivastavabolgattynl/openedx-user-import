from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class BulkUploadJob(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    file_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_users = models.IntegerField(default=0)
    successful_users = models.IntegerField(default=0)
    failed_users = models.IntegerField(default=0)
    error_log = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Bulk Upload Job {self.id} - {self.status}"

class UploadedUser(models.Model):
    job = models.ForeignKey(BulkUploadJob, on_delete=models.CASCADE, related_name='uploaded_users')
    username = models.CharField(max_length=150)
    email = models.EmailField()
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_successful = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    created_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    def __str__(self):
        return f"{self.username} - {'Success' if self.is_successful else 'Failed'}"