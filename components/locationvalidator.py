import os
import logging
import folium
from geopy.geocoders import Nominatim
from typing import Dict, Any, List, Tuple, Optional

logger = logging.getLogger(__name__)

class LocationValidator:
    """위치 정보 검증 및 시각화를 담당하는 클래스"""
    
    def __init__(self, user_agent: str = "ExifAnalyzer/1.0"):
        """
        초기화 메서드
        
        Args:
            user_agent: 지오코딩 요청 시 사용할 User-Agent
        """
        self.geolocator = Nominatim(user_agent=user_agent)
        logger.info("LocationValidator 초기화 완료")
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """
        좌표를 주소로 변환
        
        Args:
            latitude: 위도
            longitude: 경도
            
        Returns:
            Dict: 변환된 주소 정보
        """
        try:
            location = self.geolocator.reverse((latitude, longitude), language='ko')
            
            if location:
                address_data = {
                    'full_address': location.address,
                    'raw': location.raw
                }
                
                # raw 데이터에서 유용한 정보 추출
                address_components = {}
                if 'address' in location.raw:
                    addr = location.raw['address']
                    for key, value in addr.items():
                        address_components[key] = value
                
                address_data['components'] = address_components
                logger.info(f"역지오코딩 성공: ({latitude}, {longitude}) -> {location.address}")
                return address_data
            else:
                logger.warning(f"역지오코딩 결과 없음: ({latitude}, {longitude})")
                return {'error': 'No results found'}
                
        except Exception as e:
            logger.error(f"역지오코딩 중 오류 발생: {e}")
            return {'error': str(e)}
    
    def create_map(self, coordinates_list: List[Tuple[float, float]], 
                   labels: List[str] = None, output_path: str = 'map.html') -> str:
        """
        좌표 목록으로 지도 생성
        
        Args:
            coordinates_list: (위도, 경도) 튜플의 리스트
            labels: 각 좌표에 대한 레이블 리스트
            output_path: 저장할 HTML 파일 경로
            
        Returns:
            str: 생성된 지도 HTML 파일 경로
        """
        if not coordinates_list:
            logger.warning("지도 생성을 위한 좌표가 없습니다.")
            return ""
        
        try:
            # 중심점 계산 (모든 좌표의 평균)
            center_lat = sum(coord[0] for coord in coordinates_list) / len(coordinates_list)
            center_lon = sum(coord[1] for coord in coordinates_list) / len(coordinates_list)
            
            # 지도 생성
            map_obj = folium.Map(location=[center_lat, center_lon], zoom_start=13)
            
            # 마커 추가
            for i, coords in enumerate(coordinates_list):
                label = labels[i] if labels and i < len(labels) else f"Point {i+1}"
                popup_text = f"{label}<br>위도: {coords[0]}<br>경도: {coords[1]}"
                folium.Marker(
                    location=coords,
                    popup=popup_text,
                    tooltip=label
                ).add_to(map_obj)
            
            # 모든 점을 연결하는 선 추가 (시간순서대로 연결)
            folium.PolyLine(
                coordinates_list,
                color='blue',
                weight=2,
                opacity=0.7
            ).add_to(map_obj)
            
            # 지도 저장
            map_obj.save(output_path)
            logger.info(f"지도 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"지도 생성 중 오류 발생: {e}")
            return ""
    
    def validate_location(self, exif_data: Dict[str, Any], 
                          reference_location: Optional[Tuple[float, float]] = None, 
                          max_distance: float = 1.0) -> Dict[str, Any]:
        """
        EXIF 데이터의 위치 정보 검증
        
        Args:
            exif_data: 검증할 EXIF 데이터
            reference_location: 기준 위치 (위도, 경도)
            max_distance: 허용 최대 거리 (km)
            
        Returns:
            Dict: 검증 결과
        """
        validation_result = {
            'has_gps_data': False,
            'location_valid': False,
            'address': None,
            'distance_from_reference': None,
            'within_threshold': None
        }
        
        # GPS 데이터 확인
        if 'gps' not in exif_data or 'coordinates' not in exif_data['gps']:
            logger.warning(f"GPS 데이터 없음: {exif_data.get('file_path', 'unknown')}")
            return validation_result
        
        validation_result['has_gps_data'] = True
        coords = exif_data['gps']['coordinates']
        
        # 좌표 유효성 검사 (범위 확인)
        if not (-90 <= coords[0] <= 90 and -180 <= coords[1] <= 180):
            logger.warning(f"유효하지 않은 좌표: {coords}")
            return validation_result
        
        validation_result['location_valid'] = True
        
        # 주소 정보 추가
        address_info = self.reverse_geocode(coords[0], coords[1])
        validation_result['address'] = address_info
        
        # 기준 위치와 비교
        if reference_location:
            try:
                distance = self._calculate_distance(coords, reference_location)
                validation_result['distance_from_reference'] = distance
                validation_result['within_threshold'] = distance <= max_distance
                validation_result['reference_location'] = reference_location
                logger.info(f"거리 계산: {distance:.2f}km (기준치: {max_distance}km)")
            except Exception as e:
                logger.error(f"거리 계산 중 오류: {e}")
        
        return validation_result
    
    def _calculate_distance(self, point1: Tuple[float, float], 
                           point2: Tuple[float, float]) -> float:
        """
        두 지점 간의 거리 계산 (Haversine 공식 사용)
        
        Args:
            point1: 첫 번째 지점 (위도, 경도)
            point2: 두 번째 지점 (위도, 경도)
            
        Returns:
            float: 거리 (km)
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 지구 반경 (km)
        R = 6371.0
        
        lat1, lon1 = radians(point1[0]), radians(point1[1])
        lat2, lon2 = radians(point2[0]), radians(point2[1])
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        distance = R * c
        return distance