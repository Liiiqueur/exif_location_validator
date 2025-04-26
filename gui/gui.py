import os
import webbrowser
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import io
import math

class ModernUI:
    """모던 UI 스타일을 위한 클래스"""
    # 색상 정의
    COLORS = {
        'background': '#FFFFFF',
        'foreground': '#333333',
        'primary': '#2D7DD2',
        'secondary': '#F5F5F5',
        'accent': '#4CAF50',
        'warning': '#FF5252',
        'border': '#E0E0E0',
        'hover': '#EAEAEA'
    }
    
    # 폰트 정의
    FONTS = {
        'header': ('Helvetica', 14, 'bold'),
        'subheader': ('Helvetica', 12, 'bold'),
        'body': ('Helvetica', 10),
        'small': ('Helvetica', 9),
    }
    
    @staticmethod
    def apply_style(root):
        """스타일 적용"""
        style = ttk.Style()
        
        # 기본 테마 설정
        style.theme_use('clam')
        
        # 글로벌 스타일 설정
        root.configure(bg=ModernUI.COLORS['background'])
        style.configure('TFrame', background=ModernUI.COLORS['background'])
        style.configure('TLabel', background=ModernUI.COLORS['background'], foreground=ModernUI.COLORS['foreground'])
        style.configure('TButton', 
                        background=ModernUI.COLORS['primary'], 
                        foreground='white', 
                        borderwidth=0,
                        focuscolor=ModernUI.COLORS['primary'],
                        font=ModernUI.FONTS['body'])
        
        # 버튼 호버 효과
        style.map('TButton', 
                  background=[('active', ModernUI.COLORS['primary']), ('hover', '#3D8DE2')],
                  foreground=[('active', 'white')])
        
        # 엔트리 필드 스타일
        style.configure('TEntry', 
                       fieldbackground=ModernUI.COLORS['background'],
                       bordercolor=ModernUI.COLORS['border'],
                       lightcolor=ModernUI.COLORS['border'],
                       darkcolor=ModernUI.COLORS['border'],
                       borderwidth=1)
        
        # 노트북(탭) 스타일
        style.configure('TNotebook', 
                       background=ModernUI.COLORS['background'],
                       borderwidth=0)
        style.configure('TNotebook.Tab', 
                       background=ModernUI.COLORS['secondary'],
                       foreground=ModernUI.COLORS['foreground'],
                       padding=[10, 2],
                       borderwidth=0)
        style.map('TNotebook.Tab', 
                 background=[('selected', ModernUI.COLORS['background'])],
                 foreground=[('selected', ModernUI.COLORS['primary'])])
        
        # 레이블 프레임 스타일
        style.configure('TLabelframe', 
                       background=ModernUI.COLORS['background'],
                       bordercolor=ModernUI.COLORS['border'],
                       font=ModernUI.FONTS['subheader'])
        style.configure('TLabelframe.Label', 
                       background=ModernUI.COLORS['background'],
                       foreground=ModernUI.COLORS['primary'],
                       font=ModernUI.FONTS['subheader'])
        
        # 리스트박스 스타일 (tk 위젯이므로 ttk 스타일 직접 적용 불가)
        # 실제 위젯 생성 시 적용
        
        # 추가 스타일 - 액션 버튼
        style.configure('Action.TButton', 
                       background=ModernUI.COLORS['accent'],
                       foreground='white')
        style.map('Action.TButton', 
                 background=[('active', '#5DBF61'), ('hover', '#5DBF61')])
        
        # 추가 스타일 - 경고 버튼
        style.configure('Warning.TButton', 
                       background=ModernUI.COLORS['warning'],
                       foreground='white')
        style.map('Warning.TButton', 
                 background=[('active', '#FF6E6E'), ('hover', '#FF6E6E')])
        
        # 스크롤바 스타일
        style.configure('TScrollbar', 
                       background=ModernUI.COLORS['secondary'],
                       arrowcolor=ModernUI.COLORS['foreground'],
                       borderwidth=0)
        style.map('TScrollbar', 
                 background=[('active', ModernUI.COLORS['border']), 
                            ('hover', ModernUI.COLORS['border'])])
        
        return style

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
        self.image_cache = {}  # 이미지 캐시
        
        # 스타일 적용
        self.style = ModernUI.apply_style(root)
        
        # 창 설정
        self.root.title("EXIF Location Validator")
        self.root.geometry("1000x800")
        
        # 창 아이콘 설정
        if os.path.exists(self.ICON_PATH):
            try:
                self.root.iconbitmap(self.ICON_PATH)
            except Exception as e:
                print(f"아이콘 로드 실패 (iconbitmap): {e}")
        
        # 위젯 생성
        self._create_widgets()
    
    def _create_widgets(self):
        """GUI 위젯 생성"""
        # 메인 컨테이너
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 헤더 섹션
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill="x", padx=0, pady=(0, 20))
        
        header_label = ttk.Label(header_frame, text="EXIF 메타데이터 분석 도구", 
                                font=ModernUI.FONTS['header'])
        header_label.pack(side="left")
        
        # === 입력 섹션 ===
        input_frame = ttk.LabelFrame(main_container, text="분석 설정")
        input_frame.pack(fill="x", padx=0, pady=(0, 20))
        
        # 파일 선택 섹션
        file_frame = ttk.Frame(input_frame)
        file_frame.pack(fill="x", padx=10, pady=15)
        
        ttk.Label(file_frame, text="이미지 선택:", 
                 font=ModernUI.FONTS['body']).grid(row=0, column=0, padx=(0, 10), pady=0, sticky="w")
        
        self.path_var = tk.StringVar()
        path_entry = ttk.Entry(file_frame, textvariable=self.path_var, width=50)
        path_entry.grid(row=0, column=1, padx=(0, 10), pady=0, sticky="ew")
        
        button_frame = ttk.Frame(file_frame)
        button_frame.grid(row=0, column=2, padx=0, pady=0)
        
        file_button = ttk.Button(button_frame, text="파일 선택", command=self._select_file)
        file_button.pack(side="left", padx=(0, 10))
        
        dir_button = ttk.Button(button_frame, text="폴더 선택", command=self._select_directory)
        dir_button.pack(side="left")
        
        file_frame.columnconfigure(1, weight=1)  # 경로 입력 칸이 늘어나도록
        
        # 중앙 설정 프레임
        settings_frame = ttk.Frame(input_frame)
        settings_frame.pack(fill="x", padx=10, pady=(0, 15))
        
        # 기준 위치 설정
        ref_frame = ttk.Frame(settings_frame)
        ref_frame.pack(side="left", padx=(0, 20))
        
        ttk.Label(ref_frame, text="기준 위치 (위도,경도):", 
                 font=ModernUI.FONTS['body']).pack(side="left", padx=(0, 10))
        
        self.ref_location_var = tk.StringVar()
        ttk.Entry(ref_frame, textvariable=self.ref_location_var, width=20).pack(side="left", padx=(0, 10))
        
        ttk.Label(ref_frame, text="예: 37.5665,126.9780", 
                 font=ModernUI.FONTS['small'], foreground="#999999").pack(side="left")
        
        # 허용 거리 설정
        dist_frame = ttk.Frame(settings_frame)
        dist_frame.pack(side="left")
        
        ttk.Label(dist_frame, text="허용 거리 (km):", 
                 font=ModernUI.FONTS['body']).pack(side="left", padx=(0, 10))
        
        self.max_distance_var = tk.StringVar(value="1.0")
        ttk.Entry(dist_frame, textvariable=self.max_distance_var, width=6).pack(side="left")
        
        # 실행 버튼
        action_frame = ttk.Frame(input_frame)
        action_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        analyze_button = ttk.Button(action_frame, text="분석 실행", 
                                   command=self._run_analysis, style='Action.TButton')
        analyze_button.pack(pady=5, ipadx=10, ipady=5)
        
        # === 메인 컨텐츠 영역 ===
        content_frame = ttk.Frame(main_container)
        content_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # 좌측 이미지 목록 패널
        left_panel = ttk.Frame(content_frame)
        left_panel.pack(side="left", fill="y", padx=(0, 15), pady=0)
        
        # 목록 헤더
        ttk.Label(left_panel, text="이미지 목록", 
                 font=ModernUI.FONTS['subheader']).pack(anchor="w", pady=(0, 10))
        
        # 이미지 목록 컨테이너
        list_container = ttk.Frame(left_panel, width=250)
        list_container.pack(fill="both", expand=True)
        
        # 이미지 목록 및 스크롤바
        list_frame = ttk.Frame(list_container)
        list_frame.pack(fill="both", expand=True)
        
        self.image_listbox = tk.Listbox(list_frame, 
                                      bg=ModernUI.COLORS['background'],
                                      fg=ModernUI.COLORS['foreground'],
                                      selectbackground=ModernUI.COLORS['primary'],
                                      selectforeground='white',
                                      font=ModernUI.FONTS['body'],
                                      borderwidth=1,
                                      relief="solid",
                                      highlightthickness=0,
                                      width=30)
        self.image_listbox.pack(side="left", fill="both", expand=True)
        self.image_listbox.bind('<<ListboxSelect>>', self._select_image_from_list)
        
        # 스크롤바 추가
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                                      command=self.image_listbox.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.image_listbox.config(yscrollcommand=list_scrollbar.set)
        
        # 이미지 미리보기 영역
        preview_frame = ttk.LabelFrame(left_panel, text="미리보기", width=250, height=200)
        preview_frame.pack(fill="x", pady=(15, 0))
        preview_frame.pack_propagate(False)  # 크기 고정
        
        self.preview_label = ttk.Label(preview_frame, text="이미지 없음", 
                                     background=ModernUI.COLORS['secondary'])
        self.preview_label.pack(fill="both", expand=True, padx=2, pady=2)
        
        # 우측 상세 정보 패널
        right_panel = ttk.Frame(content_frame)
        right_panel.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        
        # 탭 컨테이너 (결과 표시)
        self.tab_control = ttk.Notebook(right_panel)
        self.tab_control.pack(fill="both", expand=True)
        
        # --- 첫 번째 탭: 이미지 정보 ---
        self.tab_image = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_image, text="이미지 정보")
        
        # 탭 내 스크롤 가능한 프레임
        tab_image_scroll = ttk.Frame(self.tab_image)
        tab_image_scroll.pack(fill="both", expand=True)
        
        # 캔버스와 스크롤바를 통한 스크롤 구현
        canvas = tk.Canvas(tab_image_scroll, bg=ModernUI.COLORS['background'], 
                          highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(tab_image_scroll, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scroll_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        scroll_frame.bind("<Configure>", on_frame_configure)
        
        # 기본 정보 섹션
        basic_info_frame = ttk.LabelFrame(scroll_frame, text="기본 정보")
        basic_info_frame.pack(fill="x", expand=False, padx=10, pady=(10, 5))
        
        self.basic_text = self._create_styled_text(basic_info_frame, height=10)
        self.basic_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # GPS 정보 섹션
        gps_info_frame = ttk.LabelFrame(scroll_frame, text="GPS 정보")
        gps_info_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.gps_text = self._create_styled_text(gps_info_frame, height=10)
        self.gps_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 시간 정보 섹션
        time_info_frame = ttk.LabelFrame(scroll_frame, text="시간 정보")
        time_info_frame.pack(fill="x", expand=False, padx=10, pady=5)
        
        self.time_text = self._create_styled_text(time_info_frame, height=10)
        self.time_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        # --- 두 번째 탭: 지도 ---
        self.tab_map = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_map, text="지도")
        
        map_frame = ttk.LabelFrame(self.tab_map, text="촬영 위치 지도")
        map_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        map_content = ttk.Frame(map_frame)
        map_content.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.map_label = ttk.Label(map_content, text="지도가 생성되면 여기에 표시됩니다.",
                                  font=ModernUI.FONTS['body'],
                                  foreground="#999999")
        self.map_label.pack(fill="both", expand=True)
        
        self.map_button = ttk.Button(map_content, text="브라우저에서 지도 열기", 
                                   command=self._open_map_in_browser)
        self.map_button.pack(pady=10)
        self.map_button.state(['disabled'])
        
        # --- 세 번째 탭: 보고서 ---
        self.tab_report = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_report, text="보고서")
        
        report_frame = ttk.LabelFrame(self.tab_report, text="보고서 생성")
        report_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 보고서 형식 선택
        report_options_frame = ttk.Frame(report_frame)
        report_options_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(report_options_frame, text="보고서 형식:",
                 font=ModernUI.FONTS['body']).pack(side="left", padx=(0, 10))
        
        self.report_format_var = tk.StringVar(value="all")
        
        radio_frame = ttk.Frame(report_options_frame)
        radio_frame.pack(side="left")
        
        ttk.Radiobutton(radio_frame, text="PDF", value="pdf", 
                       variable=self.report_format_var).pack(side="left", padx=(0, 15))
        ttk.Radiobutton(radio_frame, text="HTML", value="html", 
                       variable=self.report_format_var).pack(side="left", padx=(0, 15))
        ttk.Radiobutton(radio_frame, text="모두", value="all", 
                       variable=self.report_format_var).pack(side="left")
        
        # 보고서 생성 버튼
        report_button_frame = ttk.Frame(report_frame)
        report_button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(report_button_frame, text="보고서 생성", 
                  command=self._generate_reports, style="Action.TButton").pack(pady=5, ipadx=10, ipady=5)
        
        # 결과 텍스트 영역
        report_result_frame = ttk.Frame(report_frame)
        report_result_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.report_text = self._create_styled_text(report_result_frame, height=10)
        self.report_text.pack(fill="both", expand=True)
        
        # 보고서 버튼 영역
        report_button_container = ttk.Frame(report_frame)
        report_button_container.pack(fill="x", padx=10, pady=(0, 10))
        
        self.pdf_button = ttk.Button(report_button_container, text="PDF 보고서 열기", 
                                    command=lambda: self._open_report('pdf'))
        self.pdf_button.pack(side="left", padx=(0, 10))
        self.pdf_button.state(['disabled'])
        
        self.html_button = ttk.Button(report_button_container, text="HTML 보고서 열기", 
                                     command=lambda: self._open_report('html'))
        self.html_button.pack(side="left", padx=(0, 10))
        self.html_button.state(['disabled'])
        
        self.vis_button = ttk.Button(report_button_container, text="시각화 결과 열기", 
                                    command=lambda: self._open_report('visualization'))
        self.vis_button.pack(side="left")
        self.vis_button.state(['disabled'])
        
        # 상태 바
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill="x", padx=0, pady=(20, 0))
        
        self.status_var = tk.StringVar(value="준비")
        status_bar = ttk.Label(status_frame, textvariable=self.status_var, 
                              relief="sunken", anchor="w",
                              background=ModernUI.COLORS['secondary'],
                              padding=(10, 5))
        status_bar.pack(fill="x")
        
        # 보고서 경로 저장용
        self.report_paths = {}
    
    def _create_styled_text(self, parent, height=10):
        """스타일이 적용된 텍스트 위젯 생성"""
        text = tk.Text(parent, 
                      height=height,
                      wrap="word",
                      bg=ModernUI.COLORS['background'],
                      fg=ModernUI.COLORS['foreground'],
                      font=ModernUI.FONTS['body'],
                      borderwidth=1,
                      relief="solid",
                      padx=10,
                      pady=10)
        
        # 스크롤바 연결
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=text.yview)
        scrollbar.pack(side="right", fill="y")
        text.configure(yscrollcommand=scrollbar.set)
        
        return text
    
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
            # 파일 선택 시 미리보기 표시
            self._show_image_preview(file_path)
    
    def _select_directory(self):
        """디렉토리 선택 다이얼로그"""
        dir_path = filedialog.askdirectory(title="이미지 디렉토리 선택")
        if dir_path:
            self.path_var.set(dir_path)
            # 미리보기 초기화
            self._clear_image_preview()
    
    def _show_image_preview(self, image_path):
        """이미지 미리보기 표시"""
        try:
            # 이미지 로드 및 리사이즈
            image = Image.open(image_path)
            
            # 미리보기 크기 계산 (비율 유지)
            preview_width = 246  # 프레임 크기에 맞게 조정
            preview_height = 196
            
            # 비율 계산
            img_width, img_height = image.size
            ratio = min(preview_width / img_width, preview_height / img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            # 이미지 리사이즈
            image = image.resize((new_width, new_height), Image.LANCZOS)
            
            # ImageTk 객체 생성
            photo = ImageTk.PhotoImage(image)
            
            # 라벨에 이미지 표시
            self.preview_label.config(image=photo)
            self.preview_label.image = photo  # 참조 유지
            
            # 파일명 추출
            file_name = os.path.basename(image_path)
            self.preview_label.config(text=file_name, compound="bottom")
        except Exception as e:
            print(f"이미지 미리보기 오류: {e}")
            self._clear_image_preview()
    
    def _clear_image_preview(self):
        """이미지 미리보기 초기화"""
        self.preview_label.config(image=None)
        self.preview_label.image = None
        self.preview_label.config(text="이미지 없음")
    
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
            self._show_status("오류: 이미지 파일 또는 디렉토리를 선택하세요.", is_error=True)
            return
        
        # 기준 위치 파싱
        self.reference_location = self._parse_reference_location()
        if self.ref_location_var.get() and not self.reference_location:
            self._show_status("오류: 유효한 기준 위치 형식이 아닙니다. (예: 37.5665,126.9780)", is_error=True)
            return
        
        # 허용 거리 파싱
        try:
            max_distance = float(self.max_distance_var.get())
            if max_distance <= 0:
                raise ValueError("허용 거리는 양수여야 합니다.")
        except ValueError:
            self._show_status("오류: 유효한 허용 거리 값이 아닙니다.", is_error=True)
            return
        
        # 분석 시작
        self._show_status("분석 중...")
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
                self._show_status(f"분석 완료: {len(self.analysis_results)}개의 이미지")
            else:
                self._show_status("분석 완료: 유효한 EXIF 데이터가 없습니다.")
                
        except Exception as e:
            self._show_status(f"오류 발생: {str(e)}", is_error=True)
    
    def _show_status(self, message, is_error=False):
        """상태 메시지 표시"""
        self.status_var.set(message)
        # 에러 메시지는 붉은색으로 표시 (직접 라벨에 적용할 수 없어 별도 강조 없음)
    
    def _update_image_list(self):
        """이미지 목록 업데이트"""
        self.image_listbox.delete(0, tk.END)
        self.image_cache = {}  # 이미지 캐시 초기화
        
        for i, result in enumerate(self.analysis_results):
            exif_data = result.get('exif_data', {})
            file_name = exif_data.get('file_name', f"이미지 {i+1}")
            file_path = exif_data.get('file_path', '')

            # 파일명 표시
            self.image_listbox.insert(tk.END, file_name)
            
            # 이미지 캐시에 경로 저장
            self.image_cache[i] = file_path
        
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
            
            # 이미지 미리보기 업데이트
            if selected_index in self.image_cache:
                file_path = self.image_cache[selected_index]
                if file_path and os.path.exists(file_path):
                    self._show_image_preview(file_path)
                else:
                    self._clear_image_preview()
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
        
        # 텍스트 위젯 스타일 설정
        text_tags = {
            'header': {'font': ModernUI.FONTS['subheader'], 'foreground': ModernUI.COLORS['primary']},
            'subheader': {'font': ModernUI.FONTS['body'], 'foreground': ModernUI.COLORS['primary']},
            'key': {'font': ModernUI.FONTS['body'], 'foreground': '#555555'},
            'value': {'font': ModernUI.FONTS['body'], 'foreground': ModernUI.COLORS['foreground']},
            'valid': {'font': ModernUI.FONTS['body'], 'foreground': ModernUI.COLORS['accent']},
            'invalid': {'font': ModernUI.FONTS['body'], 'foreground': ModernUI.COLORS['warning']},
            'important': {'font': ModernUI.FONTS['subheader'], 'foreground': ModernUI.COLORS['foreground']}
        }
        
        # 기본 정보 표시
        self.basic_text.delete(1.0, tk.END)
        
        # 태그 설정
        for tag, style in text_tags.items():
            self.basic_text.tag_configure(tag, **style)
        
        # 파일 정보
        self.basic_text.insert(tk.END, "파일 정보\n", 'header')
        self.basic_text.insert(tk.END, "파일명: ", 'key')
        self.basic_text.insert(tk.END, f"{exif_data.get('file_name', '알 수 없음')}\n", 'value')
        self.basic_text.insert(tk.END, "파일 경로: ", 'key')
        self.basic_text.insert(tk.END, f"{exif_data.get('file_path', '알 수 없음')}\n\n", 'value')
        
        # 이미지 정보
        self.basic_text.insert(tk.END, "이미지 정보\n", 'subheader')
        if 'image_info' in exif_data:
            img_info = exif_data['image_info']
            for key, value in img_info.items():
                self.basic_text.insert(tk.END, f"{key}: ", 'key')
                self.basic_text.insert(tk.END, f"{value}\n", 'value')
        else:
            self.basic_text.insert(tk.END, "이미지 정보 없음\n", 'value')
        
        # 카메라 정보
        self.basic_text.insert(tk.END, "\n카메라 정보\n", 'subheader')
        camera_info = exif_data.get('camera', {})
        if camera_info:
            for key, value in camera_info.items():
                self.basic_text.insert(tk.END, f"{key}: ", 'key')
                self.basic_text.insert(tk.END, f"{value}\n", 'value')
        else:
            self.basic_text.insert(tk.END, "카메라 정보 없음\n", 'value')
        
        # 이미지 촬영 정보
        self.basic_text.insert(tk.END, "\n촬영 설정\n", 'subheader')
        image_info = exif_data.get('image', {})
        if image_info:
            for key, value in image_info.items():
                self.basic_text.insert(tk.END, f"{key}: ", 'key')
                self.basic_text.insert(tk.END, f"{value}\n", 'value')
        else:
            self.basic_text.insert(tk.END, "촬영 정보 없음\n", 'value')
        
        # GPS 정보 표시
        self.gps_text.delete(1.0, tk.END)
        
        # 태그 설정
        for tag, style in text_tags.items():
            self.gps_text.tag_configure(tag, **style)
        
        if location_result.get('has_gps_data', False):
            self.gps_text.insert(tk.END, "GPS 좌표 정보\n", 'header')
            
            gps_info = exif_data.get('gps', {})
            if 'coordinates' in gps_info:
                coords = gps_info['coordinates']
                self.gps_text.insert(tk.END, "위도: ", 'key')
                self.gps_text.insert(tk.END, f"{coords[0]}\n", 'value')
                self.gps_text.insert(tk.END, "경도: ", 'key')
                self.gps_text.insert(tk.END, f"{coords[1]}\n", 'value')
            
            if 'altitude' in gps_info:
                self.gps_text.insert(tk.END, "고도: ", 'key')
                self.gps_text.insert(tk.END, f"{gps_info['altitude']}m\n", 'value')
            
            if 'datetime' in gps_info:
                self.gps_text.insert(tk.END, "GPS 시간: ", 'key')
                self.gps_text.insert(tk.END, f"{gps_info['datetime']}\n", 'value')
            
            # 주소 정보
            self.gps_text.insert(tk.END, "\n위치 정보\n", 'subheader')
            if 'address' in location_result and 'full_address' in location_result['address']:
                self.gps_text.insert(tk.END, "주소: ", 'key')
                self.gps_text.insert(tk.END, f"{location_result['address']['full_address']}\n", 'value')
            
            # 기준점과의 거리
            self.gps_text.insert(tk.END, "\n기준점 검증\n", 'subheader')
            if location_result.get('distance_from_reference') is not None:
                distance = location_result['distance_from_reference']
                within = location_result.get('within_threshold', False)
                
                self.gps_text.insert(tk.END, "기준점 거리: ", 'key')
                self.gps_text.insert(tk.END, f"{distance:.2f}km\n", 'value')
                
                self.gps_text.insert(tk.END, "허용 범위 내: ", 'key')
                if within:
                    self.gps_text.insert(tk.END, "예 ✓\n", 'valid')
                else:
                    self.gps_text.insert(tk.END, "아니오 ✗\n", 'invalid')
            
            # 검증 결과
            self.gps_text.insert(tk.END, "\n검증 결과: ", 'important')
            if location_result.get('location_valid', False):
                self.gps_text.insert(tk.END, "위치 검증 통과 ✓", 'valid')
            else:
                self.gps_text.insert(tk.END, "위치 검증 실패 ✗", 'invalid')
        else:
            self.gps_text.insert(tk.END, "GPS 데이터 없음", 'value')
        
        # 시간 정보 표시
        self.time_text.delete(1.0, tk.END)
        
        # 태그 설정
        for tag, style in text_tags.items():
            self.time_text.tag_configure(tag, **style)
        
        if time_result.get('has_time_data', False):
            self.time_text.insert(tk.END, "시간 정보\n", 'header')
            
            if time_result.get('datetime_original'):
                self.time_text.insert(tk.END, "촬영 시간: ", 'key')
                self.time_text.insert(tk.END, f"{time_result['datetime_original']}\n", 'value')
                
            if time_result.get('datetime_digitized'):
                self.time_text.insert(tk.END, "기록 시간: ", 'key')
                self.time_text.insert(tk.END, f"{time_result['datetime_digitized']}\n", 'value')
                
            if time_result.get('gps_datetime'):
                self.time_text.insert(tk.END, "GPS 시간: ", 'key')
                self.time_text.insert(tk.END, f"{time_result['gps_datetime']}\n", 'value')
                
            if time_result.get('local_timezone'):
                self.time_text.insert(tk.END, "현지 시간대: ", 'key')
                self.time_text.insert(tk.END, f"{time_result['local_timezone']}\n", 'value')
            
            # 시간 차이
            if time_result.get('time_differences'):
                self.time_text.insert(tk.END, "\n시간 차이\n", 'subheader')
                for key, value in time_result['time_differences'].items():
                    self.time_text.insert(tk.END, f"{key}: ", 'key')
                    self.time_text.insert(tk.END, f"{value:.1f}초 ({value/60:.1f}분)\n", 'value')
            
            # 시간 일관성
            self.time_text.insert(tk.END, "\n검증 결과: ", 'important')
            if time_result.get('consistent', False):
                self.time_text.insert(tk.END, "시간 일관성 확인 ✓", 'valid')
            else:
                self.time_text.insert(tk.END, "시간 불일치 발견 ✗", 'invalid')
            
            # 특이사항
            if time_result.get('notes'):
                self.time_text.insert(tk.END, "\n\n특이사항\n", 'subheader')
                for note in time_result.get('notes', []):
                    self.time_text.insert(tk.END, f"• {note}\n", 'value')
        else:
            self.time_text.insert(tk.END, "시간 데이터 없음", 'value')
    
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
                self.map_label.config(text=f"지도가 생성되었습니다: {os.path.basename(map_path)}",
                                    foreground=ModernUI.COLORS['foreground'])
                self.map_button.state(['!disabled'])
            else:
                self.map_label.config(text="지도 생성에 실패했습니다.",
                                    foreground=ModernUI.COLORS['warning'])
                self.map_button.state(['disabled'])
        else:
            self.map_label.config(text="GPS 데이터가 없어 지도를 생성할 수 없습니다.",
                                foreground="#999999")
            self.map_button.state(['disabled'])
    
    def _open_map_in_browser(self):
        """브라우저에서 지도 열기"""
        if 'map' in self.report_paths and os.path.exists(self.report_paths['map']):
            webbrowser.open(f"file://{os.path.abspath(self.report_paths['map'])}")
        else:
            self._show_status("오류: 지도 파일을 찾을 수 없습니다.", is_error=True)
    
    def _generate_reports(self):
        """보고서 생성"""
        if not self.analysis_results:
            self._show_status("오류: 보고서를 생성할 데이터가 없습니다.", is_error=True)
            return
            
        self._show_status("보고서 생성 중...")
        self.root.update()
        
        try:
            # 기존 보고서 결과 초기화
            self.report_text.delete(1.0, tk.END)
            self.pdf_button.state(['disabled'])
            self.html_button.state(['disabled'])
            self.vis_button.state(['disabled'])
            
            # 스타일 태그 설정
            self.report_text.tag_configure('header', font=ModernUI.FONTS['subheader'], 
                                         foreground=ModernUI.COLORS['primary'])
            self.report_text.tag_configure('path', font=ModernUI.FONTS['body'], 
                                         foreground=ModernUI.COLORS['foreground'])
            
            # 보고서 생성
            output_format = self.report_format_var.get()
            self.analyzer.results = self.analysis_results
            report_paths = self.analyzer.generate_reports(output_format)
            
            if report_paths:
                self.report_paths.update(report_paths)
                
                # 결과 표시
                self.report_text.insert(tk.END, "보고서가 생성되었습니다\n\n", 'header')
                
                for report_type, path in report_paths.items():
                    pretty_type = {
                        'pdf': 'PDF 보고서',
                        'html': 'HTML 보고서',
                        'visualization': '시각화 결과'
                    }.get(report_type, report_type)
                    
                    self.report_text.insert(tk.END, f"{pretty_type}:\n", 'header')
                    self.report_text.insert(tk.END, f"{path}\n\n", 'path')
                    
                    # 버튼 활성화
                    if report_type == 'pdf':
                        self.pdf_button.state(['!disabled'])
                    elif report_type == 'html':
                        self.html_button.state(['!disabled'])
                    elif report_type == 'visualization':
                        self.vis_button.state(['!disabled'])
                
                self._show_status("보고서 생성 완료")
            else:
                self.report_text.insert(tk.END, "보고서 생성에 실패했습니다.")
                self._show_status("오류: 보고서 생성 실패", is_error=True)
                
        except Exception as e:
            self._show_status(f"오류 발생: {str(e)}", is_error=True)
            self.report_text.insert(tk.END, f"보고서 생성 중 오류 발생: {str(e)}")
    
    def _open_report(self, report_type):
        """특정 타입의 보고서 열기"""
        if report_type in self.report_paths and os.path.exists(self.report_paths[report_type]):
            webbrowser.open(f"file://{os.path.abspath(self.report_paths[report_type])}")
        else:
            self._show_status(f"오류: {report_type} 보고서 파일을 찾을 수 없습니다.", is_error=True)