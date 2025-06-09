from django.urls import path
from . import views

app_name = 'bulk_user_upload'

urlpatterns = [
    path('admin/bulk-user-upload/', views.upload_users, name='upload_users'),
    path('admin/bulk-user-upload/jobs/', views.job_list, name='job_list'),
    path('admin/bulk-user-upload/jobs/<int:job_id>/', views.job_detail, name='job_detail'),
    path('admin/bulk-user-upload/jobs/<int:job_id>/status/', views.job_status, name='job_status'),
]