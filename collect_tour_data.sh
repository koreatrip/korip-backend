#!/bin/bash

echo "전국 투어 API 데이터 수집 시작!"

echo "1단계: 주요 관광지역"
python manage.py sync_tour_api --area-code 1 --limit 200 --collect-all   # 서울
python manage.py sync_tour_api --area-code 39 --limit 150 --collect-all  # 제주
python manage.py sync_tour_api --area-code 6 --limit 120 --collect-all   # 부산
python manage.py sync_tour_api --area-code 31 --limit 100 --collect-all  # 경기
python manage.py sync_tour_api --area-code 32 --limit 80 --collect-all   # 강원
python manage.py sync_tour_api --area-code 2 --limit 50 --collect-all    # 인천

echo "2단계: 나머지 지역"  
python manage.py sync_tour_api --area-code 35 --limit 60 --collect-all   # 경북
python manage.py sync_tour_api --area-code 38 --limit 50 --collect-all   # 전남
python manage.py sync_tour_api --area-code 34 --limit 40 --collect-all   # 충남
python manage.py sync_tour_api --area-code 36 --limit 40 --collect-all   # 경남
python manage.py sync_tour_api --area-code 37 --limit 35 --collect-all   # 전북
python manage.py sync_tour_api --area-code 33 --limit 30 --collect-all   # 충북
python manage.py sync_tour_api --area-code 3 --limit 15 --collect-all    # 대전
python manage.py sync_tour_api --area-code 4 --limit 10 --collect-all    # 대구
python manage.py sync_tour_api --area-code 5 --limit 10 --collect-all    # 광주
python manage.py sync_tour_api --area-code 7 --limit 10 --collect-all    # 울산
python manage.py sync_tour_api --area-code 8 --limit 5 --collect-all     # 세종

echo "전국 투어 데이터 수집 완료! (총 1000개)"
