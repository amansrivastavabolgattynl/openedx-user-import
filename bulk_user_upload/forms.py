from django import forms
from django.conf import settings
import pandas as pd
import io

class BulkUserUploadForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with user data. Required columns: username, email, first_name, last_name',
        widget=forms.FileInput(attrs={'accept': '.csv'})
    )
    
    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        
        # Check file size
        if file.size > getattr(settings, 'BULK_USER_UPLOAD_MAX_FILE_SIZE', 10 * 1024 * 1024):
            raise forms.ValidationError('File size too large. Maximum size is 10MB.')
        
        # Check file extension
        if not file.name.endswith('.csv'):
            raise forms.ValidationError('File must be a CSV file.')
        
        # Validate CSV content
        try:
            # Read the file content
            file.seek(0)
            content = file.read().decode('utf-8')
            file.seek(0)  # Reset file pointer
            
            # Parse CSV
            df = pd.read_csv(io.StringIO(content))
            
            # Check required columns
            required_columns = ['username', 'email', 'first_name', 'last_name']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise forms.ValidationError(f'Missing required columns: {", ".join(missing_columns)}')
            
            # Check maximum number of users
            max_users = getattr(settings, 'BULK_USER_UPLOAD_MAX_USERS', 1000)
            if len(df) > max_users:
                raise forms.ValidationError(f'Too many users. Maximum allowed: {max_users}')
            
            # Check for empty required fields
            for col in required_columns:
                if df[col].isnull().any():
                    raise forms.ValidationError(f'Column {col} contains empty values.')
            
        except pd.errors.EmptyDataError:
            raise forms.ValidationError('CSV file is empty.')
        except pd.errors.ParserError:
            raise forms.ValidationError('Invalid CSV format.')
        except UnicodeDecodeError:
            raise forms.ValidationError('File encoding error. Please use UTF-8 encoding.')
        
        return file