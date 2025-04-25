import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, ttk

class ExifAnalyzerGUI:
    """EXIF 메타데이터 분석 도구 GUI 클래스"""
    ICON_PATH = os.path.join(os.path.dirname(__file__), '../icon/GC_3rd_smartsicurity.ico')

    def __init__(self, root, analyzer):
        """
        초기화 메서드
        
        Args:
            root: tkinter 루트 윈도우
            analyzer: ExifAnalyzer 인스턴스
        """
        self.root = root
        self.analyzer = analyzer
        self.reference_location = None
        self.analysis_results = []

         # 창 아이콘 설정
        if os.path.exists(self.ICON_PATH):
            try:
                self.root.iconbitmap(self.ICON_PATH)
            except Exception as e:
                print(f"아이콘 로드 실패 (iconbitmap): {e}")
        
        self.root.title("EXIF Location Validator")
        self.root.geometry("900x700")
        
        self._create_widgets()
    
    def _create_widgets(self):
        """GUI 위젯 생성"""
        # 상단 프레임 (입력부)
        input_frame = ttk.LabelFrame(self.root, text="입력")
        input_frame.pack(fill="x", expand="no", padx=10, pady=5)
        
        # 이미지 선택
        ttk.Label(input_frame, text="이미지 선택:").grid(column=0, row=0, padx=5, pady=5, sticky="w")
        self.path_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.path_var, width=50).grid(column=1, row=0, padx=5, pady=5)
        ttk.Button(input_frame, text="파일 선택", command=self._select_file).grid(column=2, row=0, padx=5, pady=5)
        ttk.Button(input_frame, text="폴더 선택", command=self._select_directory).grid(column=3, row=0, padx=5, pady=5)
        
        # 기준 위치 입력
        ttk.Label(input_frame, text="기준 위치 (위도,경도):").grid(column=0, row=1, padx=5, pady=5, sticky="w")
        self.ref_location_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.ref_location_var, width=30).grid(column=1, row=1, padx=5, pady=5, sticky="w")
        ttk.Label(input_frame, text="(예: 37.5665,126.9780)").grid(column=2, row=1, padx=5, pady=5, sticky="w")
        
        # 허용 거리 입력
        ttk.Label(input_frame, text="허용 거리 (km):").grid(column=0, row=2, padx=5, pady=5, sticky="w")
        self.max_distance_var = tk.StringVar(value="1.0")
        ttk.Entry(input_frame, textvariable=self.max_distance_var, width=10).grid(column=1, row=2, padx=5, pady=5, sticky="w")
        
        # 실행 버튼
        ttk.Button(input_frame, text="분석 실행", command=self._run_analysis).grid(column=0, row=3, columnspan=4, padx=5, pady=10)
        
        # 탭 컨테이너 (결과 표시)
        self.tab_control = ttk.Notebook(self.root)
        self.tab_control.pack(fill="both", expand=True, padx=10, pady=10)
        
        # --- 첫 번째 탭: 이미지 정보 ---
        self.tab_image = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_image, text="이미지 정보")
        
        list_frame = ttk.LabelFrame(self.tab_image, text="이미지 목록")
        list_frame.pack(fill="both", expand=False, padx=5, pady=5)
        self.image_listbox = tk.Listbox(list_frame, height=5)
        self.image_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.image_listbox.bind('<<ListboxSelect>>', self._select_image_from_list)
        
        details_frame = ttk.LabelFrame(self.tab_image, text="상세 정보")
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        details_notebook = ttk.Notebook(details_frame)
        details_notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 기본 정보 탭
        basic_tab = ttk.Frame(details_notebook)
        details_notebook.add(basic_tab, text="기본 정보")
        self.basic_text = tk.Text(basic_tab, wrap="word", height=10)
        self.basic_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # GPS 정보 탭
        gps_tab = ttk.Frame(details_notebook)
        details_notebook.add(gps_tab, text="GPS 정보")
        self.gps_text = tk.Text(gps_tab, wrap="word", height=10)
        self.gps_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 시간 정보 탭
        time_tab = ttk.Frame(details_notebook)
        details_notebook.add(time_tab, text="시간 정보")
        self.time_text = tk.Text(time_tab, wrap="word", height=10)
        self.time_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- 두 번째 탭: 지도 표시 ---
        self.tab_map = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_map, text="지도")
        map_frame = ttk.LabelFrame(self.tab_map, text="촬영 위치 지도")
        map_frame.pack(fill="both", expand=True, padx=5, pady=5)
        self.map_label = ttk.Label(map_frame, text="지도가 생성되면 여기에 표시됩니다.")
        self.map_label.pack(fill="both", expand=True, padx=5, pady=5)
        self.map_button = ttk.Button(map_frame, text="브라우저에서 지도 열기", command=self._open_map_in_browser)
        self.map_button.pack(pady=10)
        self.map_button.state(['disabled'])
        
        # --- 세 번째 탭: 보고서 ---
        self.tab_report = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_report, text="보고서")
        report_frame = ttk.LabelFrame(self.tab_report, text="보고서 생성")
        report_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 보고서 형식 선택
        report_options_frame = ttk.Frame(report_frame)
        report_options_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(report_options_frame, text="보고서 형식:").grid(column=0, row=0, padx=5, pady=5)
        self.report_format_var = tk.StringVar(value="all")
        ttk.Radiobutton(report_options_frame, text="PDF", value="pdf", variable=self.report_format_var).grid(column=1, row=0, padx=5, pady=5)
        ttk.Radiobutton(report_options_frame, text="HTML", value="html", variable=self.report_format_var).grid(column=2, row=0, padx=5, pady=5)
        ttk.Radiobutton(report_options_frame, text="모두", value="all", variable=self.report_format_var).grid(column=3, row=0, padx=5, pady=5)
        
        # ▶ 보고서 생성 버튼 (pack 사용)
        ttk.Button(report_frame, text="보고서 생성", command=self._generate_reports).pack(fill="x", padx=5, pady=10)
        
        # 결과 표시 영역
        self.report_text = tk.Text(report_frame, wrap="word", height=10)
        self.report_text.pack(fill="both", expand=True, padx=5, pady=5)
        
          # 보고서 열기 버튼들
        button_frame = ttk.Frame(report_frame)
        button_frame.pack(fill="x", padx=5, pady=5)
        self.pdf_button = ttk.Button(button_frame, text="PDF 보고서 열기", command=lambda: self._open_report('pdf'))
        self.pdf_button.grid(column=0, row=0, padx=5, pady=5)
        self.pdf_button.state(['disabled'])
        self.html_button = ttk.Button(button_frame, text="HTML 보고서 열기", command=lambda: self._open_report('html'))
        self.html_button.grid(column=1, row=0, padx=5, pady=5)
        self.html_button.state(['disabled'])
        self.vis_button = ttk.Button(button_frame, text="시각화 결과 열기", command=lambda: self._open_report('visualization'))
        self.vis_button.grid(column=2, row=0, padx=5, pady=5)
        self.vis_button.state(['disabled'])
        
        # 상태 바
        self.status_var = tk.StringVar(value="준비")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        
        # 보고서 경로 저장용
        self.report_paths = {}
    
    def _select_file(self):
        """파일 선택 다이얼로그"""
        file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[
                ("이미지 파일", "*.jpg *.jpeg *.tiff *.tif *.png *.heic"),
                ("JPEG 파일", "*.jpg *.jpeg"),
                ("TIFF 파일", "*.tiff *.tif"),
                ("PNG 파일", "*.png"),
                ("HEIC 파일", "*.heic"),
                ("모든 파일", "*.*")
            ]
        )
        if file_path:
            self.path_var.set(file_path)
    
    def _select_directory(self):
        """디렉토리 선택 다이얼로그"""
        dir_path = filedialog.askdirectory(title="이미지 디렉토리 선택")
        if dir_path:
            self.path_var.set(dir_path)
    
    def _parse_reference_location(self):
        """기준 위치 문자열 파싱"""
        try:
            loc_str = self.ref_location_var.get().strip()
            if not loc_str:
                return None
                
            parts = loc_str.split(',')
            if len(parts) != 2:
                return None
                
            lat = float(parts[0].strip())
            lon = float(parts[1].strip())
            
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
            else:
                return None
        except ValueError:
            return None
    
    def _run_analysis(self):
        """분석 실행"""
        path = self.path_var.get()
        if not path:
            self.status_var.set("오류: 이미지 파일 또는 디렉토리를 선택하세요.")
            return
        
        # 기준 위치 파싱
        self.reference_location = self._parse_reference_location()
        if self.ref_location_var.get() and not self.reference_location:
            self.status_var.set("오류: 유효한 기준 위치 형식이 아닙니다. (예: 37.5665,126.9780)")
            return
        
        # 허용 거리 파싱
        try:
            max_distance = float(self.max_distance_var.get())
            if max_distance <= 0:
                raise ValueError("허용 거리는 양수여야 합니다.")
        except ValueError:
            self.status_var.set("오류: 유효한 허용 거리 값이 아닙니다.")
            return
        
        self.status_var.set("분석 중...")
        self.root.update()
        
        # 이미지 분석 수행
        try:
            if os.path.isdir(path):
                self.analysis_results = self.analyzer.analyze_directory(
                    path, self.reference_location, max_distance)
            else:
                result = self.analyzer.analyze_image(
                    path, self.reference_location, max_distance)
                if 'error' not in result:
                    self.analysis_results = [result]
                else:
                    self.analysis_results = []
            
            # 결과 표시
            self._update_image_list()
            self._generate_map()
            
            if self.analysis_results:
                self.status_var.set(f"분석 완료: {len(self.analysis_results)}개의 이미지")
            else:
                self.status_var.set("분석 완료: 유효한 EXIF 데이터가 없습니다.")
                
        except Exception as e:
            self.status_var.set(f"오류 발생: {str(e)}")
    
    def _update_image_list(self):
        """이미지 목록 업데이트"""
        self.image_listbox.delete(0, tk.END)
        
        for i, result in enumerate(self.analysis_results):
            exif_data = result.get('exif_data', {})
            file_name = exif_data.get('file_name', f"이미지 {i+1}")
            self.image_listbox.insert(tk.END, file_name)
        
        if self.analysis_results:
            self.image_listbox.select_set(0)
            self._select_image_from_list(None)
    
    def _select_image_from_list(self, event):
        """이미지 목록에서 선택 시 처리"""
        if not self.analysis_results:
            return
            
        try:
            selected_index = self.image_listbox.curselection()[0]
            self._display_image_details(selected_index)
        except IndexError:
            pass
    
    def _display_image_details(self, index):
        """선택된 이미지의 상세 정보 표시"""
        if not 0 <= index < len(self.analysis_results):
            return
            
        result = self.analysis_results[index]
        exif_data = result.get('exif_data', {})
        location_result = result.get('location_result', {})
        time_result = result.get('time_result', {})
        
        # 기본 정보 표시
        self.basic_text.delete(1.0, tk.END)
        self.basic_text.insert(tk.END, f"파일명: {exif_data.get('file_name', '알 수 없음')}\n")
        self.basic_text.insert(tk.END, f"파일 경로: {exif_data.get('file_path', '알 수 없음')}\n\n")
        
        # 이미지 정보
        self.basic_text.insert(tk.END, "이미지 정보:\n")
        if 'image_info' in exif_data:
            img_info = exif_data['image_info']
            self.basic_text.insert(tk.END, f"형식: {img_info.get('format', '알 수 없음')}\n")
            self.basic_text.insert(tk.END, f"모드: {img_info.get('mode', '알 수 없음')}\n")
            self.basic_text.insert(tk.END, f"크기: {img_info.get('size', '알 수 없음')}\n")
        
        # 카메라 정보
        self.basic_text.insert(tk.END, "\n카메라 정보:\n")
        camera_info = exif_data.get('camera', {})
        if camera_info:
            for key, value in camera_info.items():
                self.basic_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.basic_text.insert(tk.END, "카메라 정보 없음\n")
        
        # 이미지 촬영 정보
        self.basic_text.insert(tk.END, "\n촬영 정보:\n")
        image_info = exif_data.get('image', {})
        if image_info:
            for key, value in image_info.items():
                self.basic_text.insert(tk.END, f"{key}: {value}\n")
        else:
            self.basic_text.insert(tk.END, "촬영 정보 없음\n")
        
        # GPS 정보 표시
        self.gps_text.delete(1.0, tk.END)
        if location_result.get('has_gps_data', False):
            gps_info = exif_data.get('gps', {})
            if 'coordinates' in gps_info:
                coords = gps_info['coordinates']
                self.gps_text.insert(tk.END, f"위도: {coords[0]}\n")
                self.gps_text.insert(tk.END, f"경도: {coords[1]}\n")
            
            if 'altitude' in gps_info:
                self.gps_text.insert(tk.END, f"고도: {gps_info['altitude']}m\n")
            
            if 'datetime' in gps_info:
                self.gps_text.insert(tk.END, f"GPS 시간: {gps_info['datetime']}\n")
            
            self.gps_text.insert(tk.END, "\n")
            
            # 주소 정보
            if 'address' in location_result and 'full_address' in location_result['address']:
                self.gps_text.insert(tk.END, f"주소: {location_result['address']['full_address']}\n\n")
            
            # 기준점과의 거리
            if location_result.get('distance_from_reference') is not None:
                distance = location_result['distance_from_reference']
                within = "예" if location_result.get('within_threshold', False) else "아니오"
                self.gps_text.insert(tk.END, f"기준점과의 거리: {distance:.2f}km\n")
                self.gps_text.insert(tk.END, f"허용 범위 내: {within}\n")
            
            # 검증 결과
            valid_text = "유효함" if location_result.get('location_valid', False) else "유효하지 않음"
            self.gps_text.insert(tk.END, f"\n위치 검증 결과: {valid_text}")
        else:
            self.gps_text.insert(tk.END, "GPS 데이터 없음")
        
        # 시간 정보 표시
        self.time_text.delete(1.0, tk.END)
        if time_result.get('has_time_data', False):
            if time_result.get('datetime_original'):
                self.time_text.insert(tk.END, f"촬영 시간: {time_result['datetime_original']}\n")
                
            if time_result.get('datetime_digitized'):
                self.time_text.insert(tk.END, f"기록 시간: {time_result['datetime_digitized']}\n")
                
            if time_result.get('gps_datetime'):
                self.time_text.insert(tk.END, f"GPS 시간: {time_result['gps_datetime']}\n")
                
            if time_result.get('local_timezone'):
                self.time_text.insert(tk.END, f"현지 시간대: {time_result['local_timezone']}\n")
                
            self.time_text.insert(tk.END, "\n")
            
            # 시간 차이
            if time_result.get('time_differences'):
                self.time_text.insert(tk.END, "시간 차이:\n")
                for key, value in time_result['time_differences'].items():
                    self.time_text.insert(tk.END, f"{key}: {value:.1f}초 ({value/60:.1f}분)\n")
                
            self.time_text.insert(tk.END, "\n")
            
            # 시간 일관성
            consistent = "일관성 있음" if time_result.get('consistent', False) else "불일치 있음"
            self.time_text.insert(tk.END, f"시간 일관성: {consistent}\n\n")
            
            # 특이사항
            if time_result.get('notes'):
                self.time_text.insert(tk.END, "특이사항:\n")
                for note in time_result.get('notes', []):
                    self.time_text.insert(tk.END, f"- {note}\n")
        else:
            self.time_text.insert(tk.END, "시간 데이터 없음")
    
    def _generate_map(self):
        """지도 생성"""
        if not self.analysis_results:
            return
            
        coordinates_list = []
        labels = []
        
        for result in self.analysis_results:
            exif_data = result.get('exif_data', {})
            if 'gps' in exif_data and 'coordinates' in exif_data['gps']:
                coordinates_list.append(exif_data['gps']['coordinates'])
                labels.append(exif_data.get('file_name', 'unknown'))
        
        if coordinates_list:
            map_path = self.analyzer.location_validator.create_map(
                coordinates_list, labels, 
                os.path.join(self.analyzer.output_dir, 'location_map.html')
            )
            
            if map_path:
                self.report_paths['map'] = map_path
                self.map_label.config(text=f"지도가 생성되었습니다: {map_path}")
                self.map_button.state(['!disabled'])
            else:
                self.map_label.config(text="지도 생성에 실패했습니다.")
                self.map_button.state(['disabled'])
        else:
            self.map_label.config(text="GPS 데이터가 없어 지도를 생성할 수 없습니다.")
            self.map_button.state(['disabled'])
    
    def _open_map_in_browser(self):
        """브라우저에서 지도 열기"""
        if 'map' in self.report_paths and os.path.exists(self.report_paths['map']):
            webbrowser.open(f"file://{os.path.abspath(self.report_paths['map'])}")
        else:
            self.status_var.set("오류: 지도 파일을 찾을 수 없습니다.")
    
    def _generate_reports(self):
        """보고서 생성"""
        if not self.analysis_results:
            self.status_var.set("오류: 보고서를 생성할 데이터가 없습니다.")
            return
            
        self.status_var.set("보고서 생성 중...")
        self.root.update()
        
        try:
            # 기존 보고서 결과 초기화
            self.report_text.delete(1.0, tk.END)
            self.pdf_button.state(['disabled'])
            self.html_button.state(['disabled'])
            self.vis_button.state(['disabled'])
            
            # 보고서 생성
            output_format = self.report_format_var.get()
            self.analyzer.results = self.analysis_results
            report_paths = self.analyzer.generate_reports(output_format)
            
            if report_paths:
                self.report_paths.update(report_paths)
                
                # 결과 표시
                self.report_text.insert(tk.END, "보고서가 생성되었습니다:\n\n")
                
                for report_type, path in report_paths.items():
                    self.report_text.insert(tk.END, f"{report_type}: {path}\n")
                    
                    # 버튼 활성화
                    if report_type == 'pdf':
                        self.pdf_button.state(['!disabled'])
                    elif report_type == 'html':
                        self.html_button.state(['!disabled'])
                    elif report_type == 'visualization':
                        self.vis_button.state(['!disabled'])
                
                self.status_var.set("보고서 생성 완료")
            else:
                self.report_text.insert(tk.END, "보고서 생성에 실패했습니다.")
                self.status_var.set("오류: 보고서 생성 실패")
                
        except Exception as e:
            self.status_var.set(f"오류 발생: {str(e)}")
            self.report_text.insert(tk.END, f"보고서 생성 중 오류 발생: {str(e)}")
    
    def _open_report(self, report_type):
        """특정 타입의 보고서 열기"""
        if report_type in self.report_paths and os.path.exists(self.report_paths[report_type]):
            webbrowser.open(f"file://{os.path.abspath(self.report_paths[report_type])}")
        else:
            self.status_var.set(f"오류: {report_type} 보고서 파일을 찾을 수 없습니다.")