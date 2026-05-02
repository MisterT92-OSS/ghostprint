"""
GhostPrint - Metadata Extractor
Extract metadata from files, documents, and images
"""
import os
from typing import Dict, List, Optional
from pathlib import Path


class MetadataExtractor:
    """Extract metadata from various file types"""
    
    SUPPORTED_TYPES = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.tiff', '.bmp', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'],
        'archive': ['.zip', '.tar', '.gz', '.rar', '.7z'],
    }
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
    
    def extract_image_metadata(self, file_path: str) -> Dict:
        """Extract EXIF data from images"""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            with Image.open(file_path) as img:
                metadata = {
                    'format': img.format,
                    'mode': img.mode,
                    'size': img.size,
                    'exif': {}
                }
                
                # Extract EXIF
                exif_data = img._getexif()
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag = TAGS.get(tag_id, tag_id)
                        metadata['exif'][tag] = value
                
                # Extract GPS if present
                if 'GPSInfo' in metadata['exif']:
                    metadata['gps'] = self._extract_gps(metadata['exif']['GPSInfo'])
                
                return metadata
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_gps(self, gps_info) -> Dict:
        """Extract GPS coordinates from EXIF"""
        try:
            from PIL.ExifTags import GPSTAGS
            
            gps_data = {}
            for key in gps_info.keys():
                decode = GPSTAGS.get(key, key)
                gps_data[decode] = gps_info[key]
            
            # Convert to decimal coordinates
            def convert_to_degrees(value):
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            
            lat = convert_to_degrees(gps_data.get('GPSLatitude'))
            if gps_data.get('GPSLatitudeRef') != 'N':
                lat = -lat
            
            lon = convert_to_degrees(gps_data.get('GPSLongitude'))
            if gps_data.get('GPSLongitudeRef') != 'E':
                lon = -lon
            
            return {
                'latitude': lat,
                'longitude': lon,
                'altitude': gps_data.get('GPSAltitude'),
                'timestamp': gps_data.get('GPSTimeStamp'),
                'map_url': f"https://maps.google.com/?q={lat},{lon}"
            }
        except:
            return {}
    
    def extract_pdf_metadata(self, file_path: str) -> Dict:
        """Extract metadata from PDF"""
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(file_path)
            metadata = reader.metadata
            
            return {
                'title': metadata.title if metadata else None,
                'author': metadata.author if metadata else None,
                'subject': metadata.subject if metadata else None,
                'creator': metadata.creator if metadata else None,
                'producer': metadata.producer if metadata else None,
                'creation_date': metadata.creation_date_raw if metadata else None,
                'modification_date': metadata.modification_date_raw if metadata else None,
                'num_pages': len(reader.pages)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def extract_office_metadata(self, file_path: str) -> Dict:
        """Extract metadata from Office documents"""
        try:
            from docx import Document
            doc = Document(file_path)
            
            core_props = doc.core_properties
            
            return {
                'title': core_props.title,
                'author': core_props.author,
                'subject': core_props.subject,
                'keywords': core_props.keywords,
                'comments': core_props.comments,
                'created': core_props.created.isoformat() if core_props.created else None,
                'modified': core_props.modified.isoformat() if core_props.modified else None,
                'last_modified_by': core_props.last_modified_by,
                'revision': core_props.revision
            }
        except Exception as e:
            return {'error': str(e)}
    
    def extract_file_info(self, file_path: str) -> Dict:
        """Extract basic file info"""
        path = Path(file_path)
        
        stat = os.stat(file_path)
        
        return {
            'filename': path.name,
            'extension': path.suffix,
            'size_bytes': stat.st_size,
            'size_human': self._human_readable_size(stat.st_size),
            'created': stat.st_ctime,
            'modified': stat.st_mtime,
            'accessed': stat.st_atime,
            'absolute_path': str(path.absolute())
        }
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
    
    def analyze(self, file_path: str) -> Dict:
        """Full file analysis"""
        if not os.path.exists(file_path):
            return {'error': 'File not found'}
        
        results = {
            'file_info': self.extract_file_info(file_path)
        }
        
        ext = Path(file_path).suffix.lower()
        
        if ext in self.SUPPORTED_TYPES['image']:
            results['metadata'] = self.extract_image_metadata(file_path)
        elif ext == '.pdf':
            results['metadata'] = self.extract_pdf_metadata(file_path)
        elif ext in ['.docx', '.doc']:
            results['metadata'] = self.extract_office_metadata(file_path)
        else:
            results['metadata'] = {'note': f'File type {ext} not fully supported yet'}
        
        return results