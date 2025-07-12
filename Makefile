
# KORIP 백엔드 개발용 Makefile
# 쉽게 사용할 수 있도록 도커 명령어들을 정리

# Docker Compose 명령어 자동 감지 (docker-compose / docker compose 둘 다 지원)
DC = $(shell command -v docker-compose >/dev/null 2>&1 && echo "docker-compose" || echo "docker compose")

# =============================================================================
# 🚀 초기 설정 (git pull 받은 후 처음 할 일들)
# =============================================================================

# 1. 첫 실행 (프로젝트 전체 설정)
setup:
	@echo "🔧 프로젝트 초기 설정 시작..."
	$(DC) build --no-cache
	$(DC) up -d
	make migrate
	make load-data
	@echo "✅ 초기 설정 완료! 이제 개발할 수 있습니다."

# 2. 도커 컨테이너 빌드 (의존성 변경 시)
build:
	@echo "🏗️  도커 이미지 빌드 중..."
	$(DC) build --no-cache

# 3. 서버 실행
up:
	@echo "🚀 서버 실행 중..."
	$(DC) up -d

# 4. 서버 중지
down:
	@echo "🛑 서버 중지 중..."
	$(DC) down

# =============================================================================
# 📊 데이터베이스 관련
# =============================================================================

# 마이그레이션 생성 및 적용
migrate:
	@echo "🗄️  마이그레이션 실행 중..."
	$(DC) run web python manage.py makemigrations
	$(DC) run web python manage.py migrate

# 마이그레이션만 생성
makemigrations:
	@echo "📝 마이그레이션 파일 생성 중..."
	$(DC) run web python manage.py makemigrations

# 마이그레이션만 적용
migrate-apply:
	@echo "⚡ 마이그레이션 적용 중..."
	$(DC) run web python manage.py migrate

# 기본 카테고리 데이터 로드
load-data:
	@echo "📦 카테고리 데이터 로드 중..."
	$(DC) run web python manage.py load_categories

# 슈퍼유저 생성
superuser:
	@echo "👤 슈퍼유저 생성..."
	$(DC) run web python manage.py createsuperuser

# 데이터베이스 초기화 (주의: 모든 데이터 삭제됨)
reset-db:
	@echo "⚠️  데이터베이스 초기화 중... (모든 데이터 삭제)"
	$(DC) down
	docker volume rm korip_postgres_data 2>/dev/null || true
	$(DC) up -d
	make migrate
	make load-data

# =============================================================================
# 🧪 테스트 관련
# =============================================================================

# 전체 테스트 실행
test:
	@echo "🧪 전체 테스트 실행 중..."
	$(DC) run web python manage.py test

# 특정 앱 테스트 실행 (예: make test-app app=places)
test-app:
	@echo "🧪 $(app) 앱 테스트 실행 중..."
	$(DC) run web python manage.py test $(app).tests

# 특정 테스트 클래스 실행 (예: make test-class class=places.tests.CategoryAPITest)
test-class:
	@echo "🧪 $(class) 테스트 클래스 실행 중..."
	$(DC) run web python manage.py test $(class)

# 테스트 커버리지 확인 (coverage 설치 후 사용)
test-coverage:
	@echo "📊 테스트 커버리지 확인 중..."
	$(DC) run web coverage run --source='.' manage.py test
	$(DC) run web coverage report
	$(DC) run web coverage html

# =============================================================================
# 🛠️  개발 도구
# =============================================================================

# Django 쉘 접속
shell:
	@echo "🐍 Django 쉘 접속..."
	$(DC) run web python manage.py shell

# 컨테이너 내부 bash 접속
bash:
	@echo "💻 컨테이너 bash 접속..."
	$(DC) exec web bash

# 로그 확인
logs:
	@echo "📋 로그 확인 중..."
	$(DC) logs -f web

# PostgreSQL 데이터베이스 접속
db-shell:
	@echo "🗄️  PostgreSQL 접속..."
	$(DC) exec db psql -U korip_user -d korip_db

# 의존성 설치 (pyproject.toml 변경 후)
install:
	@echo "📦 의존성 설치 중..."
	$(DC) run web poetry install
	make build

# =============================================================================
# 🧹 정리 작업
# =============================================================================

# 사용하지 않는 도커 이미지/컨테이너 정리
clean:
	@echo "🧹 도커 정리 중..."
	$(DC) system prune -f || true
	$(DC) volume prune -f || true

# 프로젝트 완전 초기화 (주의: 모든 데이터 및 이미지 삭제)
reset-all:
	@echo "💥 프로젝트 완전 초기화 중..."
	$(DC) down -v --remove-orphans
	@echo "🧹 Docker 리소스 정리 중..."
	$(DC) system prune -a -f || true
	$(DC) volume prune -f || true
	make setup

# 데이터베이스 및 마이그레이션 완전 초기화 (마이그레이션 충돌 해결용)
reset-migrations:
	@echo "🔄 마이그레이션 완전 초기화 중..."
	$(DC) down -v --remove-orphans
	@echo "📝 마이그레이션 파일 삭제 중..."
	find . -path "*/migrations/*.py" -not -name "__init__.py" -delete || true
	$(DC) up -d
	@echo "⏳ 데이터베이스 준비 대기 중..."
	sleep 5
	make migrate
	make load-data
	@echo "✅ 마이그레이션 초기화 완료!"

# =============================================================================
# 📖 도움말
# =============================================================================

# 사용 가능한 명령어 목록 표시
help:
	@echo "🚀 KORIP 백엔드 개발용 Makefile 명령어"
	@echo ""
	@echo "📌 Docker 호환성: docker-compose와 docker compose 모두 지원"
	@echo ""
	@echo "📌 초기 설정:"
	@echo "  make setup           - 프로젝트 초기 설정 (처음 한 번만)"
	@echo "  make build           - 도커 이미지 빌드"
	@echo "  make up              - 서버 실행"
	@echo "  make down            - 서버 중지"
	@echo ""
	@echo "📌 데이터베이스:"
	@echo "  make migrate         - 마이그레이션 생성 및 적용"
	@echo "  make load-data       - 기본 카테고리 데이터 로드"
	@echo "  make superuser       - 슈퍼유저 생성"
	@echo "  make reset-db        - 데이터베이스 초기화"
	@echo ""
	@echo "📌 테스트:"
	@echo "  make test            - 전체 테스트 실행"
	@echo "  make test-app app=앱명 - 특정 앱 테스트"
	@echo ""
	@echo "📌 개발 도구:"
	@echo "  make shell           - Django 쉘 접속"
	@echo "  make bash            - 컨테이너 bash 접속"
	@echo "  make logs            - 로그 확인"
	@echo ""
	@echo "📌 정리 작업:"
	@echo "  make clean           - 도커 이미지/컨테이너 정리"
	@echo "  make clean-docker    - Docker 완전 정리 (볼륨 포함)"
	@echo "  make reset-migrations- 마이그레이션 완전 초기화"
	@echo "  make reset-all       - 프로젝트 완전 초기화"
	@echo ""
	@echo "📌 사용 예시:"
	@echo "  git pull origin develop"
	@echo "  make setup           # 처음 한 번만"
	@echo "  make up              # 서버 실행"
	@echo "  make test            # 테스트 실행"

# 기본 명령어 (make만 입력 시)
.DEFAULT_GOAL := help
