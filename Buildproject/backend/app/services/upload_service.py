"""
Service for handling file uploads.
Provides validation, storage, and management of uploaded images.
"""

from typing import Optional, Tuple
import os
import logging
from pathlib import Path
import hashlib
from datetime import datetime

from app.core.config import settings
from app.utils.time import utc_now

logger = logging.getLogger(__name__)


class UploadService:
    """Service for handling file uploads."""
    
    def __init__(self):
        """Initialize upload service and ensure upload directory exists."""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.max_size_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        self.allowed_types = set(settings.ALLOWED_IMAGE_TYPES.split(','))
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Upload service initialized. Directory: {self.upload_dir}")
    
    def validate_file(
        self,
        file_content: bytes,
        content_type: str,
        filename: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file.
        
        Args:
            file_content: File content as bytes
            content_type: MIME type of the file
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        if len(file_content) > self.max_size_bytes:
            max_mb = self.max_size_bytes / (1024 * 1024)
            return False, f"File size exceeds maximum of {max_mb}MB"
        
        # Check content type
        if content_type not in self.allowed_types:
            return False, f"File type {content_type} not allowed. Allowed types: {', '.join(self.allowed_types)}"
        
        # Check if file is empty
        if len(file_content) == 0:
            return False, "File is empty"
        
        return True, None
    
    def generate_filename(
        self,
        original_filename: str,
        report_id: str
    ) -> str:
        """
        Generate a unique filename for the uploaded file.
        
        Args:
            original_filename: Original filename from upload
            report_id: Report UUID
            
        Returns:
            Generated filename
        """
        # Get file extension
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = '.jpg'  # Default extension
        
        # Generate timestamp
        timestamp = utc_now().strftime('%Y%m%d_%H%M%S')
        
        # Create filename: report_{report_id}_{timestamp}{ext}
        filename = f"report_{report_id}_{timestamp}{ext}"
        
        return filename
    
    def save_file(
        self,
        file_content: bytes,
        filename: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Save file to upload directory.
        
        Args:
            file_content: File content as bytes
            filename: Filename to save as
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            file_path = self.upload_dir / filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            logger.info(f"File saved successfully: {file_path}")
            
            # Return relative path for storage in database
            relative_path = f"{settings.UPLOAD_DIR}/{filename}"
            return True, relative_path, None
            
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return False, None, str(e)
    
    def upload_image(
        self,
        file_content: bytes,
        content_type: str,
        original_filename: str,
        report_id: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Complete image upload workflow: validate, generate filename, and save.
        
        Args:
            file_content: File content as bytes
            content_type: MIME type
            original_filename: Original filename
            report_id: Report UUID
            
        Returns:
            Tuple of (success, file_url, error_message)
        """
        # Validate file
        is_valid, error = self.validate_file(file_content, content_type, original_filename)
        if not is_valid:
            return False, None, error
        
        # Generate unique filename
        filename = self.generate_filename(original_filename, report_id)
        
        # Save file
        success, file_path, error = self.save_file(file_content, filename)
        
        if success:
            # For Phase 3, return local path
            # In later phases, this could return a CDN URL
            return True, file_path, None
        else:
            return False, None, error
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file from the upload directory.
        
        Args:
            file_path: Relative file path
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Extract filename from path
            filename = Path(file_path).name
            full_path = self.upload_dir / filename
            
            if full_path.exists():
                full_path.unlink()
                logger.info(f"File deleted: {full_path}")
                return True
            else:
                logger.warning(f"File not found: {full_path}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete file: {e}")
            return False
    
    def get_file_info(self, file_path: str) -> Optional[dict]:
        """
        Get information about an uploaded file.
        
        Args:
            file_path: Relative file path
            
        Returns:
            Dictionary with file info or None if not found
        """
        try:
            filename = Path(file_path).name
            full_path = self.upload_dir / filename
            
            if not full_path.exists():
                return None
            
            stat = full_path.stat()
            
            return {
                "filename": filename,
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get file info: {e}")
            return None


# Global instance
upload_service = UploadService()

# Made with Bob