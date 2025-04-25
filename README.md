![EXIF Validator](https://img.shields.io/badge/EXIF-Validator-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 📸 EXIF 위치 검사기

이 프로젝트는 사진 파일에 포함된 EXIF 정보를 한눈에 확인하고, GPS 위치 검증 및 시각화, 그리고 PDF/HTML 보고서를 자동으로 생성해줍니다. 당신의 사진 관리, 감사, 디지털 포렌식 업무를 더욱 **간편**하고 **강력**하게 만들어 줍니다.

### 💡 주요 기능

- 📂 **파일/폴더 선택**: 단일 이미지 또는 디렉토리 일괄 처리
- 🔍 **EXIF 정보 파싱**: 카메라 정보, 이미지 속성, GPS, 촬영 시간 등
- 🌐 **GPS 검증 & 지도 시각화**: 기준점 설정 후 거리 필터링, 지도 HTML 파일 생성
- 📝 **맞춤형 보고서**: PDF & HTML 형식으로 결과 요약 보고서 생성
- 🚀 **간편 UI**: Tkinter 기반 직관적인 GUI

### 🛠️ 설치 방법
```bash
# 저장소 클론
git clone https://github.com/YourUsername/exif-location-validator.git
cd exif-location-validator

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\\Scripts\\activate   # Windows

# 의존성 설치
pip install -r requirements.txt
```

### 🚀 사용 예시
```bash
python main.py
```
1. ‘파일 선택’ 또는 ‘폴더 선택’ 클릭
2. 기준 위치(위도,경도) 입력 (예: `37.5665,126.9780`)
3. 허용 거리(km) 설정 후 ‘분석 실행’
4. 결과 탭에서 EXIF → 지도 → 보고서 확인!

### 📄 라이선스
© 2025 Liiiqueur. 본 프로젝트의 모든 권리는 Liiiqueur에게 있습니다.

---

## 📸 EXIF Location Validator

This project helps you extract and visualize EXIF data from your photos, validate GPS locations, and generate detailed PDF/HTML reports. Perfect for photographers, data auditors, and digital forensics analysts.

### 💡 Key Features

- 📂 **File/Directory Selection**: Process single images or entire folders
- 🔍 **EXIF Parsing**: Retrieve camera info, image attributes, GPS coordinates, capture timestamps
- 🌐 **GPS Validation & Mapping**: Set reference point, filter by distance, generate interactive HTML maps
- 📝 **Custom Reports**: Generate summary reports in PDF & HTML formats
- 🚀 **Intuitive UI**: Built with Tkinter for easy navigation

### 🛠️ Installation
```bash
# Clone the repo
git clone https://github.com/YourUsername/exif-location-validator.git
cd exif-location-validator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\\Scripts\\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 🚀 Usage
```bash
python main.py
```
1. Click **Select File** or **Select Directory**
2. Enter reference location (latitude, longitude), e.g.: `37.5665,126.9780`
3. Set max distance (km) and click **Run Analysis**
4. Explore results in **Image Info**, **Map**, and **Report** tabs!

### 📄 License
© 2025 Liiiqueur. All rights reserved.
