import os
import uuid
import boto3
from pathlib import Path
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from typing import Tuple, Optional
from datetime import datetime


class StorageService:
    def __init__(self, storage_type: str = 'local'):
        self.storage_type = storage_type
        if storage_type == 'local':
            self.upload_folder = os.path.join(os.getcwd(), 'uploads', 'photos')
            Path(self.upload_folder).mkdir(parents=True, exist_ok=True)
        elif storage_type == 'aws_s3':
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket_name = os.getenv('AWS_S3_BUCKET')

    def generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to prevent conflicts"""
        file_extension = os.path.splitext(original_filename)[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}{file_extension}"

    def is_allowed_file(self, filename: str) -> bool:
        """Check if file type is allowed"""
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions

    def upload_file(self, file: FileStorage) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Upload a file to the configured storage
        Returns: (success, file_info, error_message)
        """
        if not file or not file.filename or file.filename == '':
            return False, None, "No file provided"

        if not self.is_allowed_file(file.filename):
            return False, None, "File type not allowed"

        try:
            original_filename = secure_filename(file.filename)
            stored_filename = self.generate_unique_filename(original_filename)
            
            if self.storage_type == 'local':
                return self._upload_local(file, original_filename, stored_filename)
            elif self.storage_type == 'aws_s3':
                return self._upload_s3(file, original_filename, stored_filename)
            else:
                return False, None, f"Unsupported storage type: {self.storage_type}"

        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"

    def _upload_local(self, file: FileStorage, original_filename: str, stored_filename: str) -> Tuple[bool, dict, None]:
        """Upload file to local storage"""
        file_path = os.path.join(self.upload_folder, stored_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        file_info = {
            'filename': original_filename,
            'stored_filename': stored_filename,
            'file_path': f"/uploads/photos/{stored_filename}",  # URL path for frontend
            'file_size': file_size,
            'mime_type': file.mimetype,
            'storage_type': 'local'
        }
        
        return True, file_info, None

    def _upload_s3(self, file: FileStorage, original_filename: str, stored_filename: str) -> Tuple[bool, dict, None]:
        """Upload file to AWS S3"""
        try:
            # Upload to S3
            s3_key = f"photos/{stored_filename}"
            self.s3_client.upload_fileobj(
                file,
                self.bucket_name or '',
                s3_key,
                ExtraArgs={
                    'ContentType': file.mimetype or 'application/octet-stream',
                    'ACL': 'public-read'  # Make files publicly readable
                }
            )
            
            # Generate S3 URL
            s3_url = f"https://{self.bucket_name}.s3.amazonaws.com/{s3_key}"
            
            # Get file size (approximate, since we don't have it directly)
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset position
            
            file_info = {
                'filename': original_filename,
                'stored_filename': stored_filename,
                'file_path': s3_url,
                'file_size': file_size,
                'mime_type': file.mimetype,
                'storage_type': 'aws_s3'
            }
            
            return True, file_info, None

        except Exception as e:
            return False, None, f"S3 upload failed: {str(e)}"

    def delete_file(self, file_path: str, storage_type: str = None) -> bool:
        """Delete a file from storage"""
        storage_type = storage_type or self.storage_type
        
        try:
            if storage_type == 'local':
                # Extract filename from path and delete local file
                filename = os.path.basename(file_path)
                local_path = os.path.join(self.upload_folder, filename)
                if os.path.exists(local_path):
                    os.remove(local_path)
                return True
                
            elif storage_type == 'aws_s3':
                # Extract S3 key from URL and delete from S3
                s3_key = file_path.split('.amazonaws.com/')[-1]
                self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
                return True
                
        except Exception as e:
            print(f"Error deleting file: {str(e)}")
            return False
        
        return False

    def get_file_url(self, file_path: str, storage_type: str = None) -> str:
        """Get the public URL for a file"""
        storage_type = storage_type or self.storage_type
        
        if storage_type == 'local':
            # For local files, return the relative URL path
            return file_path
        elif storage_type == 'aws_s3':
            # For S3 files, return the full URL
            return file_path
        
        return file_path


# Global storage service instance
# Can be configured via environment variables
storage_service = StorageService(
    storage_type=os.getenv('STORAGE_TYPE', 'local')
) 