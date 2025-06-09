from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import pandas as pd
import io
from .forms import BulkUserUploadForm
from .models import BulkUploadJob, UploadedUser
from .tasks import process_bulk_upload

@staff_member_required
def upload_users(request):
    if request.method == 'POST':
        form = BulkUserUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            
            # Create upload job
            job = BulkUploadJob.objects.create(
                created_by=request.user,
                file_name=csv_file.name,
                status='pending'
            )
            
            # Read and parse CSV
            content = csv_file.read().decode('utf-8')
            df = pd.read_csv(io.StringIO(content))
            job.total_users = len(df)
            job.save()
            
            # Process upload asynchronously
            process_bulk_upload.delay(job.id, content)
            
            messages.success(request, f'Upload job created successfully. Job ID: {job.id}')
            return redirect('bulk_user_upload:job_detail', job_id=job.id)
    else:
        form = BulkUserUploadForm()
    
    return render(request, 'bulk_user_upload/upload_form.html', {'form': form})

@staff_member_required
def job_list(request):
    jobs = BulkUploadJob.objects.all()
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        jobs = jobs.filter(
            Q(file_name__icontains=search) |
            Q(created_by__username__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bulk_user_upload/job_list.html', {
        'page_obj': page_obj,
        'search': search
    })

@staff_member_required
def job_detail(request, job_id):
    job = get_object_or_404(BulkUploadJob, id=job_id)
    uploaded_users = job.uploaded_users.all()
    
    # Pagination for uploaded users
    paginator = Paginator(uploaded_users, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bulk_user_upload/job_detail.html', {
        'job': job,
        'page_obj': page_obj
    })

@staff_member_required
@require_http_methods(["GET"])
def job_status(request, job_id):
    job = get_object_or_404(BulkUploadJob, id=job_id)
    return JsonResponse({
        'status': job.status,
        'total_users': job.total_users,
        'successful_users': job.successful_users,
        'failed_users': job.failed_users,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None
    })