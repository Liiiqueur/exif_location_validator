# exif_analyzer_project/main.py

import os
import sys
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional, Union

# 필요한 라이브러리 설치 확인 및 임포트
try:
    import exifread
    from PIL import Image
    import piexif
    import folium
    import pytz
    import geopy
    from geopy.geocoders import Nominatim
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    import pandas as pd
    import matplotlib.pyplot as plt
    from jinja2 import Template
    import tkinter as tk
    from tkinter import filedialog, ttk
    import webbrowser
    from timezonefinder import TimezoneFinder
except ImportError as e:
    print(f"필요한 라이브러리를 설치해주세요: {e}")
    print("pip install -r requirements.txt")
    sys.exit(1)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("exif_analyzer.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EXIF_Analyzer")

# ====== 사용자 정의 모듈 ======
from exifanalyzer import ExifAnalyzer
from exifextractor import ExifExtractor
from locationvalidator import LocationValidator
from timeanalyzer import TimeAnalyzer
from reportgenerator import ReportGenerator

# GUI 모듈은 선택적으로 처리
try:
    from gui import ExifAnalyzerGUI
except ImportError:
    ExifAnalyzerGUI = None


def main():
    import argparse

    parser = argparse.ArgumentParser(description='EXIF 메타데이터 분석 및 위치 검증 도구')
    parser.add_argument('--path', type=str, help='분석할 이미지 파일 또는 디렉토리 경로')
    parser.add_argument('--output', type=str, default='output', help='결과물 저장 디렉토리')
    parser.add_argument('--ref-location', type=str, help='기준 위치 (위도,경도 형식)')
    parser.add_argument('--max-distance', type=float, default=1.0, help='허용 최대 거리 (km)')
    parser.add_argument('--report-format', type=str, default='all', choices=['pdf', 'html', 'all'], help='보고서 출력 형식')
    parser.add_argument('--gui', action='store_true', help='GUI 모드로 실행')

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    analyzer = ExifAnalyzer(args.output)

    # GUI 실행 시
    if args.gui:
        if ExifAnalyzerGUI:
            root = tk.Tk()
            app = ExifAnalyzerGUI(root, analyzer)
            root.mainloop()
        else:
            print("GUI 모듈이 없습니다. gui.py를 확인하세요.")
        return

    if not args.path:
        print("오류: 이미지 파일 또는 디렉토리 경로를 지정해야 합니다.")
        return

    reference_location = None
    if args.ref_location:
        try:
            parts = args.ref_location.split(',')
            if len(parts) == 2:
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                reference_location = (lat, lon)
        except ValueError:
            print("오류: 유효한 기준 위치 형식이 아닙니다. (예: 37.5665,126.9780)")
            return

    results = []
    if os.path.isdir(args.path):
        print(f"디렉토리 분석 중: {args.path}")
        results = analyzer.analyze_directory(args.path, reference_location, args.max_distance)
    else:
        print(f"이미지 분석 중: {args.path}")
        result = analyzer.analyze_image(args.path, reference_location, args.max_distance)
        if 'error' not in result:
            results = [result]

    if not results:
        print("분석 결과가 없습니다.")
        return

    print(f"{len(results)}개의 이미지 분석 완료")
    print("보고서 생성 중...")
    report_paths = analyzer.generate_reports(args.report_format)

    if report_paths:
        print("보고서 생성 완료:")
        for report_type, path in report_paths.items():
            print(f"  {report_type}: {path}")
    else:
        print("보고서 생성에 실패했습니다.")


if __name__ == "__main__":
    main()