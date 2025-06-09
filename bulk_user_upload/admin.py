from django.contrib import admin
from .models import BulkUploadJob, UploadedUser

@admin.register(BulkUploadJob)
class BulkUploadJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'created_by', 'status', 'total_users', 'successful_users', 'failed_users', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('file_name', 'created_by__username')
    readonly_fields = ('created_at', 'completed_at')
    
    def has_add_permission(self, request):
        return False

@admin.register(UploadedUser)
class UploadedUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'job', 'is_successful', 'created_user')
    list_filter = ('is_successful', 'job__status')
    search_fields = ('username', 'email')
    
    def has_add_permission(self, request):
        return False