# Python 3.11 베이스 이미지
FROM python:3.11-slim

# 🗺️ GIS 라이브러리 설치를 위한 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 🗺️ GDAL 환경변수 설정
ENV GDAL_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgdal.so
ENV GEOS_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/libgeos_c.so

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 최신 버전 설치
RUN pip install poetry==1.8.3

# Poetry 설정 (가상환경 생성 안 함)
RUN poetry config virtualenvs.create false

# Poetry 파일들 복사
COPY pyproject.toml poetry.lock* ./

# 의존성 설치 (verbose로 상세 에러 확인)
RUN poetry install --only=main -vvv

# 소스 코드 복사
COPY . .

# 포트 8000 노출
EXPOSE 8000

# 서버 실행 명령어
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
