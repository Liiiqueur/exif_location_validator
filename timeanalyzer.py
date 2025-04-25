import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TimeAnalyzer:
    """시간 정보 분석 및 검증을 담당하는 클래스"""
    
    def __init__(self):
        """초기화 메서드"""
        self.timezone_cache = {}
        logger.info("TimeAnalyzer 초기화 완료")
    
    def parse_exif_datetime(self, datetime_str: str) -> Optional[datetime]:
        """
        EXIF 날짜/시간 문자열을 datetime 객체로 변환
        
        Args:
            datetime_str: EXIF 날짜/시간 문자열 (YYYY:MM:DD HH:MM:SS 형식)
            
        Returns:
            Optional[datetime]: 변환된 datetime 객체 또는 None
        """
        try:
            return datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
        except Exception as e:
            logger.error(f"날짜/시간 파싱 오류: {e}")
            return None
    
    def get_timezone_for_location(self, latitude: float, longitude: float) -> Optional[str]:
        """
        위치 기반 시간대 정보 조회
        
        Args:
            latitude: 위도
            longitude: 경도
            
        Returns:
            Optional[str]: 시간대 식별자 또는 None
        """
        # 캐시 확인
        cache_key = f"{latitude:.4f},{longitude:.4f}"
        if cache_key in self.timezone_cache:
            return self.timezone_cache[cache_key]
            
        try:
            from timezonefinder import TimezoneFinder
            tf = TimezoneFinder()
            timezone_str = tf.timezone_at(lat=latitude, lng=longitude)
            
            if timezone_str:
                self.timezone_cache[cache_key] = timezone_str
                return timezone_str
            else:
                logger.warning(f"시간대 정보를 찾을 수 없음: ({latitude}, {longitude})")
                return None
                
        except ImportError:
            logger.warning("timezonefinder 라이브러리가 설치되지 않았습니다.")
            return None
        except Exception as e:
            logger.error(f"시간대 정보 조회 중 오류: {e}")
            return None
    
    def analyze_time_consistency(self, exif_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        EXIF 데이터의 시간 정보 일관성 분석
        
        Args:
            exif_data: 분석할 EXIF 데이터
            
        Returns:
            Dict: 분석 결과
        """
        result = {
            'has_time_data': False,
            'datetime_original': None,
            'datetime_digitized': None,
            'gps_datetime': None,
            'local_timezone': None,
            'time_differences': {},
            'consistent': False,
            'notes': []
        }
        
        # 시간 데이터 추출
        dt_keys = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
        time_data = {}
        
        for key in dt_keys:
            if 'datetime' in exif_data and key in exif_data['datetime']:
                dt_str = exif_data['datetime'][key]
                dt_obj = self.parse_exif_datetime(dt_str)
                if dt_obj:
                    time_data[key] = dt_obj
        
        # GPS 시간 추출
        if 'gps' in exif_data and 'datetime' in exif_data['gps']:
            try:
                gps_dt_str = exif_data['gps']['datetime']
                # GPS 날짜 형식은 'YYYY:MM:DD' 또는 'YYYY-MM-DD'일 수 있음
                gps_dt_str = gps_dt_str.replace('-', ':')
                gps_dt_obj = datetime.strptime(gps_dt_str, '%Y:%m:%d %H:%M:%S')
                time_data['GPS'] = gps_dt_obj
            except Exception as e:
                logger.warning(f"GPS 시간 파싱 오류: {e}")
        
        if not time_data:
            result['notes'].append("시간 데이터가 없습니다.")
            return result
        
        result['has_time_data'] = True
        
        # 시간 데이터 결과에 할당
        if 'DateTimeOriginal' in time_data:
            result['datetime_original'] = time_data['DateTimeOriginal'].strftime('%Y-%m-%d %H:%M:%S')
        if 'DateTimeDigitized' in time_data:
            result['datetime_digitized'] = time_data['DateTimeDigitized'].strftime('%Y-%m-%d %H:%M:%S')
        if 'GPS' in time_data:
            result['gps_datetime'] = time_data['GPS'].strftime('%Y-%m-%d %H:%M:%S')
        
        # 지역 시간대 정보 추가
        if 'gps' in exif_data and 'coordinates' in exif_data['gps']:
            coords = exif_data['gps']['coordinates']
            timezone_str = self.get_timezone_for_location(coords[0], coords[1])
            if timezone_str:
                result['local_timezone'] = timezone_str
                result['notes'].append(f"현지 시간대: {timezone_str}")
        
        # 시간 차이 계산
        if len(time_data) >= 2:
            time_keys = list(time_data.keys())
            for i in range(len(time_keys)):
                for j in range(i+1, len(time_keys)):
                    key_i, key_j = time_keys[i], time_keys[j]
                    diff = abs((time_data[key_i] - time_data[key_j]).total_seconds())
                    result['time_differences'][f"{key_i}_{key_j}"] = diff
                    
                    # 1시간(3600초) 이상 차이나면 특이사항 기록
                    if diff > 3600:
                        result['notes'].append(f"{key_i}와 {key_j} 시간이 크게 다릅니다: {diff/3600:.2f}시간")
        
        # 일관성 판단 (모든 시간 차이가 5분(300초) 이내면 일관성 있음)
        result['consistent'] = all(diff <= 300 for diff in result['time_differences'].values())
        
        if result['consistent']:
            result['notes'].append("모든 시간 정보가 일관성이 있습니다.")
        else:
            result['notes'].append("시간 정보에 불일치가 있습니다.")
        
        return result