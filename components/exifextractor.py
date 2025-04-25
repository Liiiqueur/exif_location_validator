import os
import logging
from PIL import Image
import exifread
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ExifExtractor:
    """EXIF 데이터 추출 및 처리를 담당하는 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        self.supported_formats = ['.jpg', '.jpeg', '.tiff', '.tif', '.png', '.heic']
        logger.info("ExifExtractor 초기화 완료")
    
    def is_supported_format(self, file_path: str) -> bool:
        """
        지원되는 이미지 형식인지 확인
        
        Args:
            file_path: 확인할 파일 경로
            
        Returns:
            bool: 지원되는 형식이면 True, 아니면 False
        """
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_formats
    
    def extract_exif(self, file_path: str) -> Dict[str, Any]:
        """
        이미지 파일에서 EXIF 데이터를 추출
        
        Args:
            file_path: EXIF 데이터를 추출할 이미지 파일 경로
            
        Returns:
            Dict: 추출된 EXIF 데이터
        """
        if not os.path.exists(file_path):
            logger.error(f"파일이 존재하지 않습니다: {file_path}")
            return {}
            
        if not self.is_supported_format(file_path):
            logger.warning(f"지원되지 않는 이미지 형식: {file_path}")
            return {}
        
        try:
            # exifread를 사용한 EXIF 추출
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=True)
            
            # Pillow를 사용한 추가 이미지 정보 추출
            img = Image.open(file_path)
            img_info = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
            }
            
            # 추출한 EXIF 데이터 전처리
            exif_data = self._process_exif_tags(tags)
            exif_data['image_info'] = img_info
            exif_data['file_path'] = file_path
            exif_data['file_name'] = os.path.basename(file_path)
            
            logger.info(f"EXIF 데이터 추출 성공: {file_path}")
            return exif_data
            
        except Exception as e:
            logger.error(f"EXIF 추출 중 오류 발생: {e}")
            return {}
    
    def _process_exif_tags(self, tags: Dict) -> Dict[str, Any]:
        """
        EXIF 태그를 처리하여 사용하기 쉬운 형태로 변환
        
        Args:
            tags: exifread로 추출한 원시 EXIF 태그
            
        Returns:
            Dict: 처리된 EXIF 데이터
        """
        processed_data = {
            'camera': {},
            'image': {},
            'gps': {},
            'datetime': {},
            'other': {}
        }
        
        # 카메라 정보 추출
        camera_tags = ['Image Make', 'Image Model', 'EXIF LensModel', 'EXIF LensMake']
        for tag in camera_tags:
            if tag in tags:
                key = tag.split(' ')[-1]
                processed_data['camera'][key] = str(tags[tag])
        
        # 이미지 정보 추출
        image_tags = ['EXIF ExifImageWidth', 'EXIF ExifImageLength', 'Image Orientation',
                       'EXIF FocalLength', 'EXIF FNumber', 'EXIF ISOSpeedRatings',
                       'EXIF ExposureTime', 'EXIF ExposureProgram']
        for tag in image_tags:
            if tag in tags:
                key = tag.split(' ')[-1]
                processed_data['image'][key] = str(tags[tag])
        
        # GPS 정보 추출 및 처리
        processed_data['gps'] = self._extract_gps_info(tags)
        
        # 날짜/시간 정보 추출
        datetime_tags = ['Image DateTime', 'EXIF DateTimeOriginal', 'EXIF DateTimeDigitized']
        for tag in datetime_tags:
            if tag in tags:
                key = tag.split(' ')[-1]
                processed_data['datetime'][key] = str(tags[tag])
        
        # 기타 관심 EXIF 태그 처리
        for tag in tags:
            if tag not in camera_tags + image_tags + datetime_tags and not tag.startswith('GPS'):
                if 'Image' in tag or 'EXIF' in tag:
                    key = tag.split(' ', 1)[1] if ' ' in tag else tag
                    processed_data['other'][key] = str(tags[tag])
        
        return processed_data
    
    def _extract_gps_info(self, tags: Dict) -> Dict[str, Any]:
        """
        EXIF 태그에서 GPS 정보를 추출하고 처리
        
        Args:
            tags: exifread로 추출한 원시 EXIF 태그
            
        Returns:
            Dict: 처리된 GPS 정보
        """
        gps_info = {}
        
        # GPS 좌표 추출
        if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
            try:
                lat = self._convert_to_degrees(tags['GPS GPSLatitude'].values)
                lon = self._convert_to_degrees(tags['GPS GPSLongitude'].values)
                
                # 남위/서경인 경우 음수값으로 변환
                if 'GPS GPSLatitudeRef' in tags and tags['GPS GPSLatitudeRef'].values == 'S':
                    lat = -lat
                if 'GPS GPSLongitudeRef' in tags and tags['GPS GPSLongitudeRef'].values == 'W':
                    lon = -lon
                
                gps_info['latitude'] = lat
                gps_info['longitude'] = lon
                gps_info['coordinates'] = (lat, lon)
            except Exception as e:
                logger.error(f"GPS 좌표 변환 중 오류: {e}")
        
        # GPS 고도 추출
        if 'GPS GPSAltitude' in tags:
            try:
                altitude = float(tags['GPS GPSAltitude'].values[0].num) / float(tags['GPS GPSAltitude'].values[0].den)
                # 고도 참조값이 1이면 해수면 아래
                if 'GPS GPSAltitudeRef' in tags and tags['GPS GPSAltitudeRef'].values[0] == 1:
                    altitude = -altitude
                gps_info['altitude'] = altitude
            except Exception as e:
                logger.error(f"고도 변환 중 오류: {e}")
        
        # GPS 날짜/시간 추출
        if 'GPS GPSDateStamp' in tags and 'GPS GPSTimeStamp' in tags:
            try:
                date_str = str(tags['GPS GPSDateStamp'].values)
                time_values = tags['GPS GPSTimeStamp'].values
                hour = int(time_values[0].num) / int(time_values[0].den)
                minute = int(time_values[1].num) / int(time_values[1].den)
                second = int(time_values[2].num) / int(time_values[2].den)
                time_str = f"{int(hour):02d}:{int(minute):02d}:{int(second):02d}"
                gps_info['datetime'] = f"{date_str} {time_str}"
            except Exception as e:
                logger.error(f"GPS 시간 변환 중 오류: {e}")
        
        return gps_info
    
    def _convert_to_degrees(self, value) -> float:
        """
        GPS 좌표를 도 단위로 변환
        
        Args:
            value: exifread에서 추출한 GPS 좌표 값
            
        Returns:
            float: 도 단위로 변환된 GPS 좌표
        """
        degrees = float(value[0].num) / float(value[0].den)
        minutes = float(value[1].num) / float(value[1].den)
        seconds = float(value[2].num) / float(value[2].den)
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)