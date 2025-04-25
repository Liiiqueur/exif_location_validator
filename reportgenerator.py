import os
import logging
from datetime import datetime
import matplotlib.pyplot as plt
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from jinja2 import Template
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    """분석 보고서 생성을 담당하는 클래스"""
    
    def __init__(self, output_dir: str = "reports"):
        """
        초기화 메서드
        
        Args:
            output_dir: 보고서 저장 디렉토리
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"ReportGenerator 초기화 완료 (출력 디렉토리: {output_dir})")
    
    def generate_pdf_report(self, analysis_results: List[Dict[str, Any]], 
                           output_file: str = None) -> str:
        """
        PDF 형식의 분석 보고서 생성
        
        Args:
            analysis_results: 분석 결과 목록
            output_file: 출력 파일 경로
            
        Returns:
            str: 생성된 PDF 파일 경로
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"exif_report_{timestamp}.pdf")
        
        try:
            # PDF 캔버스 생성
            c = canvas.Canvas(output_file, pagesize=A4)
            width, height = A4
            
            # 제목
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "EXIF 메타데이터 분석 보고서")
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            c.drawString(50, height - 85, f"분석 파일 수: {len(analysis_results)}")
            
            # 각 이미지 분석 결과 추가
            y_position = height - 120
            
            for i, result in enumerate(analysis_results):
                if y_position < 100:  # 페이지 넘김
                    c.showPage()
                    y_position = height - 50
                
                exif_data = result.get('exif_data', {})
                location_result = result.get('location_result', {})
                time_result = result.get('time_result', {})
                
                # 파일 정보
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, f"이미지 {i+1}: {exif_data.get('file_name', '알 수 없음')}")
                y_position -= 20
                
                # 카메라 정보
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y_position, "카메라 정보:")
                y_position -= 15
                
                c.setFont("Helvetica", 9)
                camera_info = exif_data.get('camera', {})
                for key, value in camera_info.items():
                    c.drawString(60, y_position, f"{key}: {value}")
                    y_position -= 12
                
                # GPS 정보
                y_position -= 5
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y_position, "위치 정보:")
                y_position -= 15
                
                c.setFont("Helvetica", 9)
                gps_info = exif_data.get('gps', {})
                if 'coordinates' in gps_info:
                    c.drawString(60, y_position, f"좌표: {gps_info['coordinates']}")
                    y_position -= 12
                    
                    if 'address' in location_result and 'full_address' in location_result['address']:
                        address = location_result['address']['full_address']
                        # 긴 주소 처리
                        if len(address) > 60:
                            parts = [address[i:i+60] for i in range(0, len(address), 60)]
                            for part in parts:
                                c.drawString(60, y_position, part)
                                y_position -= 12
                        else:
                            c.drawString(60, y_position, f"주소: {address}")
                            y_position -= 12
                
                # 시간 정보
                y_position -= 5
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y_position, "시간 정보:")

                y_position -= 15
                
                c.setFont("Helvetica", 9)
                if time_result.get('has_time_data', False):
                    if time_result.get('datetime_original'):
                        c.drawString(60, y_position, f"촬영 시간: {time_result['datetime_original']}")
                        y_position -= 12
                    if time_result.get('gps_datetime'):
                        c.drawString(60, y_position, f"GPS 시간: {time_result['gps_datetime']}")
                        y_position -= 12
                    if time_result.get('local_timezone'):
                        c.drawString(60, y_position, f"시간대: {time_result['local_timezone']}")
                        y_position -= 12
                else:
                    c.drawString(60, y_position, "시간 정보 없음")
                    y_position -= 12
                
                # 검증 결과
                y_position -= 5
                c.setFont("Helvetica-Bold", 10)
                c.drawString(50, y_position, "검증 결과:")
                y_position -= 15
                
                c.setFont("Helvetica", 9)
                # 위치 검증 결과
                if location_result.get('has_gps_data', False):
                    valid_text = "유효함" if location_result.get('location_valid', False) else "유효하지 않음"
                    c.drawString(60, y_position, f"GPS 데이터: {valid_text}")
                    y_position -= 12
                    
                    if location_result.get('distance_from_reference') is not None:
                        distance = location_result['distance_from_reference']
                        within = "예" if location_result.get('within_threshold', False) else "아니오"
                        c.drawString(60, y_position, f"기준점과의 거리: {distance:.2f}km (허용 범위 내: {within})")
                        y_position -= 12
                else:
                    c.drawString(60, y_position, "GPS 데이터 없음")
                    y_position -= 12
                
                # 시간 검증 결과
                if time_result.get('has_time_data', False):
                    consistent = "일관성 있음" if time_result.get('consistent', False) else "불일치 있음"
                    c.drawString(60, y_position, f"시간 정보: {consistent}")
                    y_position -= 12
                    
                    # 시간 차이 표시
                    if time_result.get('time_differences'):
                        for diff_key, diff_value in time_result['time_differences'].items():
                            if diff_value > 60:  # 1분 이상 차이날 경우만 표시
                                c.drawString(60, y_position, f"{diff_key} 차이: {diff_value/60:.1f}분")
                                y_position -= 12
                
                # 특이사항
                if time_result.get('notes'):
                    y_position -= 5
                    c.setFont("Helvetica-Bold", 10)
                    c.drawString(50, y_position, "특이사항:")
                    y_position -= 15
                    
                    c.setFont("Helvetica", 9)
                    for note in time_result.get('notes', [])[:3]:  # 최대 3개 노트만 표시
                        c.drawString(60, y_position, f"- {note}")
                        y_position -= 12
                
                # 구분선
                y_position -= 10
                c.setLineWidth(0.5)
                c.line(50, y_position, width - 50, y_position)
                y_position -= 20
            
            # PDF 저장
            c.save()
            logger.info(f"PDF 보고서 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"PDF 보고서 생성 중 오류: {e}")
            return ""
    
    def generate_html_report(self, analysis_results: List[Dict[str, Any]], 
                            map_path: str = None, output_file: str = None) -> str:
        """
        HTML 형식의 분석 보고서 생성
        
        Args:
            analysis_results: 분석 결과 목록
            map_path: 생성된 지도 HTML 파일 경로
            output_file: 출력 파일 경로
            
        Returns:
            str: 생성된 HTML 파일 경로
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"exif_report_{timestamp}.html")
            
        try:
            # HTML 템플릿
            html_template = """
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>EXIF 메타데이터 분석 보고서</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }
                    .container { max-width: 1200px; margin: 0 auto; }
                    h1, h2, h3 { color: #2c3e50; }
                    .header { margin-bottom: 30px; border-bottom: 1px solid #eee; padding-bottom: 20px; }
                    .summary { background-color: #f9f9f9; padding: 15px; border-radius: 5px; margin-bottom: 30px; }
                    .image-card { margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; padding: 20px; }
                    .image-header { display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
                    .image-body { display: flex; flex-wrap: wrap; }
                    .image-section { margin-bottom: 20px; flex: 1; min-width: 300px; }
                    .data-table { width: 100%; border-collapse: collapse; }
                    .data-table td, .data-table th { border: 1px solid #ddd; padding: 8px; }
                    .data-table th { background-color: #f2f2f2; text-align: left; }
                    .map-container { margin: 30px 0; height: 500px; }
                    .map-container iframe { width: 100%; height: 100%; border: none; }
                    .validation-result { padding: 10px; border-radius: 5px; margin-top: 10px; }
                    .valid { background-color: #d4edda; color: #155724; }
                    .invalid { background-color: #f8d7da; color: #721c24; }
                    .warning { background-color: #fff3cd; color: #856404; }
                    .notes { background-color: #e2e3e5; color: #383d41; padding: 10px; border-radius: 5px; margin-top: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>EXIF 메타데이터 분석 보고서</h1>
                        <p>생성일시: {{ current_datetime }}</p>
                    </div>
                    
                    <div class="summary">
                        <h2>요약</h2>
                        <p>분석된 이미지 수: {{ total_images }}</p>
                        <p>GPS 데이터 포함 이미지: {{ gps_images }}</p>
                        <p>시간 데이터 포함 이미지: {{ time_images }}</p>
                        <p>위치 검증 통과율: {{ location_valid_rate }}%</p>
                        <p>시간 정보 일관성 통과율: {{ time_valid_rate }}%</p>
                    </div>
                    
                    {% if map_path %}
                    <div class="map-container">
                        <h2>촬영 위치 지도</h2>
                        <iframe src="{{ map_path }}"></iframe>
                    </div>
                    {% endif %}
                    
                    <h2>이미지 분석 결과</h2>
                    
                    {% for result in results %}
                    <div class="image-card">
                        <div class="image-header">
                            <h3>{{ result.exif_data.file_name }}</h3>
                        </div>
                        
                        <div class="image-body">
                            <div class="image-section">
                                <h4>카메라 정보</h4>
                                <table class="data-table">
                                    <tr>
                                        <th>속성</th>
                                        <th>값</th>
                                    </tr>
                                    {% for key, value in result.exif_data.camera.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>{{ value }}</td>
                                    </tr>
                                    {% endfor %}
                                    {% for key, value in result.exif_data.image.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>{{ value }}</td>
                                    </tr>
                                    {% endfor %}
                                </table>
                            </div>
                            
                            <div class="image-section">
                                <h4>위치 정보</h4>
                                {% if result.location_result.has_gps_data %}
                                <table class="data-table">
                                    <tr>
                                        <th>속성</th>
                                        <th>값</th>
                                    </tr>
                                    <tr>
                                        <td>좌표</td>
                                        <td>{{ result.exif_data.gps.coordinates[0] }}, {{ result.exif_data.gps.coordinates[1] }}</td>
                                    </tr>
                                    {% if result.location_result.address %}
                                    <tr>
                                        <td>주소</td>
                                        <td>{{ result.location_result.address.full_address }}</td>
                                    </tr>
                                    {% endif %}
                                    {% if result.location_result.distance_from_reference is not none %}
                                    <tr>
                                        <td>기준점과의 거리</td>
                                        <td>{{ "%.2f"|format(result.location_result.distance_from_reference) }} km</td>
                                    </tr>
                                    {% endif %}
                                </table>
                                
                                <div class="validation-result {% if result.location_result.location_valid %}valid{% else %}invalid{% endif %}">
                                    위치 데이터 검증: 
                                    {% if result.location_result.location_valid %}
                                        유효함
                                    {% else %}
                                        유효하지 않음
                                    {% endif %}
                                </div>
                                
                                {% if result.location_result.within_threshold is not none %}
                                <div class="validation-result {% if result.location_result.within_threshold %}valid{% else %}warning{% endif %}">
                                    허용 범위 내 위치: 
                                    {% if result.location_result.within_threshold %}
                                        예
                                    {% else %}
                                        아니오
                                    {% endif %}
                                </div>
                                {% endif %}
                                
                                {% else %}
                                <p>GPS 데이터 없음</p>
                                {% endif %}
                            </div>
                            
                            <div class="image-section">
                                <h4>시간 정보</h4>
                                {% if result.time_result.has_time_data %}
                                <table class="data-table">
                                    <tr>
                                        <th>속성</th>
                                        <th>값</th>
                                    </tr>
                                    {% if result.time_result.datetime_original %}
                                    <tr>
                                        <td>촬영 시간</td>
                                        <td>{{ result.time_result.datetime_original }}</td>
                                    </tr>
                                    {% endif %}
                                    {% if result.time_result.datetime_digitized %}
                                    <tr>
                                        <td>기록 시간</td>
                                        <td>{{ result.time_result.datetime_digitized }}</td>
                                    </tr>
                                    {% endif %}
                                    {% if result.time_result.gps_datetime %}
                                    <tr>
                                        <td>GPS 시간</td>
                                        <td>{{ result.time_result.gps_datetime }}</td>
                                    </tr>
                                    {% endif %}
                                    {% if result.time_result.local_timezone %}
                                    <tr>
                                        <td>현지 시간대</td>
                                        <td>{{ result.time_result.local_timezone }}</td>
                                    </tr>
                                    {% endif %}
                                </table>
                                
                                <div class="validation-result {% if result.time_result.consistent %}valid{% else %}warning{% endif %}">
                                    시간 정보 일관성: 
                                    {% if result.time_result.consistent %}
                                        일관성 있음
                                    {% else %}
                                        불일치 있음
                                    {% endif %}
                                </div>
                                
                                {% if result.time_result.time_differences %}
                                <h5>시간 차이</h5>
                                <table class="data-table">
                                    <tr>
                                        <th>비교 항목</th>
                                        <th>차이 (초)</th>
                                    </tr>
                                    {% for key, value in result.time_result.time_differences.items() %}
                                    <tr>
                                        <td>{{ key }}</td>
                                        <td>{{ value }}</td>
                                    </tr>
                                    {% endfor %}
                                </table>
                                {% endif %}
                                
                                {% else %}
                                <p>시간 데이터 없음</p>
                                {% endif %}
                            </div>
                        </div>
                        
                        {% if result.time_result.notes %}
                        <div class="notes">
                            <h4>특이사항</h4>
                            <ul>
                                {% for note in result.time_result.notes %}
                                <li>{{ note }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            </body>
            </html>
            """
            
            # Jinja2 사용하여 HTML 생성
            template = Template(html_template)
            
            # 요약 통계 계산
            total_images = len(analysis_results)
            gps_images = sum(1 for r in analysis_results if r.get('location_result', {}).get('has_gps_data', False))
            time_images = sum(1 for r in analysis_results if r.get('time_result', {}).get('has_time_data', False))
            
            location_valid = sum(1 for r in analysis_results 
                              if r.get('location_result', {}).get('location_valid', False))
            time_valid = sum(1 for r in analysis_results 
                          if r.get('time_result', {}).get('consistent', False))
            
            location_valid_rate = int((location_valid / gps_images * 100) if gps_images > 0 else 0)
            time_valid_rate = int((time_valid / time_images * 100) if time_images > 0 else 0)
            
            # 상대 경로로 지도 경로 변환
            map_rel_path = os.path.relpath(map_path, self.output_dir) if map_path else None
            
            # HTML 렌더링
            html_content = template.render(
                current_datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_images=total_images,
                gps_images=gps_images,
                time_images=time_images,
                location_valid_rate=location_valid_rate,
                time_valid_rate=time_valid_rate,
                map_path=map_rel_path,
                results=analysis_results
            )
            
            # HTML 파일 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"HTML 보고서 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"HTML 보고서 생성 중 오류: {e}")
            return ""
    
    def generate_data_visualization(self, analysis_results: List[Dict[str, Any]], 
                                   output_file: str = None) -> str:
        """
        분석 데이터 시각화 생성
        
        Args:
            analysis_results: 분석 결과 목록
            output_file: 출력 파일 경로
            
        Returns:
            str: 생성된 이미지 파일 경로
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(self.output_dir, f"exif_visualization_{timestamp}.png")
        
        try:
            # 분석 데이터 추출
            file_names = []
            has_gps = []
            has_time = []
            location_valid = []
            time_consistent = []
            
            for result in analysis_results:
                exif_data = result.get('exif_data', {})
                location_result = result.get('location_result', {})
                time_result = result.get('time_result', {})
                
                file_names.append(os.path.basename(exif_data.get('file_path', 'unknown')))
                has_gps.append(1 if location_result.get('has_gps_data', False) else 0)
                has_time.append(1 if time_result.get('has_time_data', False) else 0)
                location_valid.append(1 if location_result.get('location_valid', False) else 0)
                time_consistent.append(1 if time_result.get('consistent', False) else 0)
            
            # 인덱스 생성
            indices = list(range(len(file_names)))
            
            # 그래프 생성
            plt.figure(figsize=(12, 8))
            
            # 이미지별 데이터 유무 막대 그래프
            plt.subplot(2, 1, 1)
            bar_width = 0.35
            plt.bar(indices, has_gps, bar_width, label='GPS 데이터')
            plt.bar([i + bar_width for i in indices], has_time, bar_width, label='시간 데이터')
            plt.xlabel('이미지')
            plt.ylabel('데이터 유무')
            plt.title('이미지별 메타데이터 유무')
            plt.xticks([i + bar_width/2 for i in indices], file_names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            # 검증 결과 그래프
            plt.subplot(2, 1, 2)
            bar_width = 0.35
            plt.bar(indices, location_valid, bar_width, label='위치 유효')
            plt.bar([i + bar_width for i in indices], time_consistent, bar_width, label='시간 일관성')
            plt.xlabel('이미지')
            plt.ylabel('검증 결과')
            plt.title('이미지별 검증 결과')
            plt.xticks([i + bar_width/2 for i in indices], file_names, rotation=45, ha='right')
            plt.legend()
            plt.tight_layout()
            
            # 이미지 저장
            plt.savefig(output_file)
            plt.close()
            
            logger.info(f"데이터 시각화 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"데이터 시각화 생성 중 오류: {e}")
            return ""