from fastapi import HTTPException, UploadFile
import os
import shutil
from datetime import datetime
from typing import Tuple

class FileUploadService:
    """Service class for handling file uploads"""
    
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png"]
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR = "app/static/user_photos"
    
    @classmethod
    def validate_image_file(cls, file: UploadFile) -> None:
        """Validate uploaded image file"""
        # Check file type
        if file.content_type not in cls.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400, 
                detail="Invalid file format. Only jpg, jpeg, png allowed"
            )
        
        # Check file size
        if file.size and file.size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413, 
                detail="File size exceeds maximum limit of 5MB"
            )
    
    @classmethod
    def generate_filename(cls, role: str, user_id: int, original_filename: str) -> str:
        """Generate safe filename for uploaded files"""
        timestamp = int(datetime.now().timestamp())
        file_extension = original_filename.split('.')[-1] if original_filename else 'jpg'
        return f"{role}_{user_id}_{timestamp}.{file_extension}"
    
    @classmethod
    def save_file(cls, file: UploadFile, filename: str) -> Tuple[str, str]:
        """
        Save uploaded file and return file_path and url_path
        Returns: (file_path, url_path)
        """
        # Create upload directory if it doesn't exist
        os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
        
        file_path = os.path.join(cls.UPLOAD_DIR, filename)
        url_path = f"/static/user_photos/{filename}"
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to save file: {str(e)}"
            )
        
        return file_path, url_path
    
    @classmethod
    def upload_profile_photo(cls, file: UploadFile, role: str, user_id: int) -> str:
        """
        Complete profile photo upload process
        Returns: URL path for the uploaded photo
        """
        cls.validate_image_file(file)
        filename = cls.generate_filename(role, user_id, file.filename)
        _, url_path = cls.save_file(file, filename)
        return url_path