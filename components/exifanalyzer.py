import os
import logging
from typing import Dict, Any, List, Tuple, Optional
from components.exifextractor import ExifExtractor
from components.locationvalidator import LocationValidator
from components.timeanalyzer import TimeAnalyzer
from components.reportgenerator import ReportGenerator

logger = logging.getLogger(__name__)

class ExifAnalyzer:
    """EXIF 메타데이터 분석 및 위치 검증을 통합적으로 수행하는 클래스"""
    
    def __init__(self, output_dir: str = "output"):
        """
        초기화 메서드
        
        Args:
            output_dir: 결과물 저장 디렉토리
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 각 모듈 초기화
        self.extractor = ExifExtractor()
        self.location_validator = LocationValidator()
        self.time_analyzer = TimeAnalyzer()
        self.report_generator = ReportGenerator(output_dir)
        
        self.results = []
        logger.info(f"ExifAnalyzer 초기화 완료 (출력 디렉토리: {output_dir})")
    
    def analyze_image(self, image_path: str, reference_location: Tuple[float, float] = None,
                     max_distance: float = 1.0) -> Dict[str, Any]:
        """
        단일 이미지 분석
        
        Args:
            image_path: 분석할 이미지 경로
            reference_location: 기준 위치 (위도, 경도)
            max_distance: 허용 최대 거리 (km)
            
        Returns:
            Dict: 분석 결과
        """
        try:
            logger.info(f"이미지 분석 시작: {image_path}")
            
            # EXIF 데이터 추출
            exif_data = self.extractor.extract_exif(image_path)
            if not exif_data:
                logger.warning(f"EXIF 데이터를 추출할 수 없음: {image_path}")
                return {'error': 'EXIF 데이터 없음'}
            
            # 위치 검증
            location_result = self.location_validator.validate_location(
                exif_data, reference_location, max_distance)
            
            # 시간 정보 분석
            time_result = self.time_analyzer.analyze_time_consistency(exif_data)
            
            # 분석 결과 취합
            result = {
                'exif_data': exif_data,
                'location_result': location_result,
                'time_result': time_result
            }
            
            logger.info(f"이미지 분석 완료: {image_path}")
            return result
            
        except Exception as e:
            logger.error(f"이미지 분석 중 오류 발생: {e}")
            return {'error': str(e)}
    
    def analyze_directory(self, directory_path: str, reference_location: Tuple[float, float] = None,
                         max_distance: float = 1.0) -> List[Dict[str, Any]]:
        """
        디렉토리 내 모든 이미지 분석
        
        Args:
            directory_path: 분석할 이미지 디렉토리 경로
            reference_location: 기준 위치 (위도, 경도)
            max_distance: 허용 최대 거리 (km)
            
        Returns:
            List[Dict]: 분석 결과 목록
        """
        results = []
        
        try:
            if not os.path.isdir(directory_path):
                logger.error(f"유효한 디렉토리가 아님: {directory_path}")
                return results
            
            image_files = []
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path) and self.extractor.is_supported_format(file_path):
                    image_files.append(file_path)
            
            logger.info(f"{len(image_files)}개의 이미지 파일 발견: {directory_path}")
            
            # 각 이미지 분석
            for image_path in image_files:
                result = self.analyze_image(image_path, reference_location, max_distance)
                if 'error' not in result:
                    results.append(result)
            
            self.results = results
            return results
            
        except Exception as e:
            logger.error(f"디렉토리 분석 중 오류 발생: {e}")
            return results
    
    def generate_reports(self, output_format: str = 'all') -> Dict[str, str]:
        """
        분석 결과 보고서 생성
        
        Args:
            output_format: 출력 형식 ('pdf', 'html', 'all')
            
        Returns:
            Dict: 생성된 보고서 파일 경로
        """
        if not self.results:
            logger.warning("생성할 보고서 데이터가 없습니다.")
            return {}
        
        reports = {}
        
        try:
            # 지도 생성
            coordinates_list = []
            labels = []
            
            for result in self.results:
                exif_data = result.get('exif_data', {})
                if 'gps' in exif_data and 'coordinates' in exif_data['gps']:
                    coordinates_list.append(exif_data['gps']['coordinates'])
                    labels.append(exif_data.get('file_name', 'unknown'))
            
            map_path = None
            if coordinates_list:
                map_path = self.location_validator.create_map(
                    coordinates_list, labels, 
                    os.path.join(self.output_dir, 'location_map.html')
                )
                reports['map'] = map_path
            
            # 시각화 생성
            vis_path = self.report_generator.generate_data_visualization(
                self.results, os.path.join(self.output_dir, 'visualization.png'))
            reports['visualization'] = vis_path
            
            # PDF 보고서
            if output_format in ['pdf', 'all']:
                pdf_path = self.report_generator.generate_pdf_report(
                    self.results, os.path.join(self.output_dir, 'exif_report.pdf'))
                reports['pdf'] = pdf_path
            
            # HTML 보고서
            if output_format in ['html', 'all']:
                html_path = self.report_generator.generate_html_report(
                    self.results, map_path, 
                    os.path.join(self.output_dir, 'exif_report.html'))
                reports['html'] = html_path
            
            logger.info(f"보고서 생성 완료: {', '.join(reports.keys())}")
            return reports
            
        except Exception as e:
            logger.error(f"보고서 생성 중 오류 발생: {e}")
            return reports