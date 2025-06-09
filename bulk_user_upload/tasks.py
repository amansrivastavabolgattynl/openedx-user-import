from celery import shared_task
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
import pandas as pd
import io
import logging
from .models import BulkUploadJob, UploadedUser

logger = logging.getLogger(__name__)

@shared_task
def process_bulk_upload(job_id, csv_content):
    try:
        job = BulkUploadJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()
        
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_content))
        
        successful_count = 0
        failed_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    username = str(row['username']).strip()
                    email = str(row['email']).strip()
                    first_name = str(row['first_name']).strip()
                    last_name = str(row['last_name']).strip()
                    
                    # Check if user already exists
                    if User.objects.filter(username=username).exists():
                        raise Exception(f"Username '{username}' already exists")
                    
                    if User.objects.filter(email=email).exists():
                        raise Exception(f"Email '{email}' already exists")
                    
                    # Create user
                    user = User.objects.create_user(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        password=User.objects.make_random_password()
                    )
                    
                    # Create UploadedUser record
                    UploadedUser.objects.create(
                        job=job,
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                        is_successful=True,
                        created_user=user
                    )
                    
                    successful_count += 1
                    logger.info(f"Successfully created user: {username}")
                    
            except Exception as e:
                error_msg = str(e)
                errors.append(f"Row {index + 2}: {error_msg}")
                
                # Create failed UploadedUser record
                UploadedUser.objects.create(
                    job=job,
                    username=str(row.get('username', '')).strip(),
                    email=str(row.get('email', '')).strip(),
                    first_name=str(row.get('first_name', '')).strip(),
                    last_name=str(row.get('last_name', '')).strip(),
                    is_successful=False,
                    error_message=error_msg
                )
                
                failed_count += 1
                logger.error(f"Failed to create user at row {index + 2}: {error_msg}")
        
        # Update job status
        job.successful_users = successful_count
        job.failed_users = failed_count
        job.error_log = '\n'.join(errors)
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.save()
        
        logger.info(f"Bulk upload job {job_id} completed. Success: {successful_count}, Failed: {failed_count}")
        
    except Exception as e:
        logger.error(f"Bulk upload job {job_id} failed: {str(e)}")
        try:
            job = BulkUploadJob.objects.get(id=job_id)
            job.status = 'failed'
            job.error_log = str(e)
            job.save()
        except:
            pass