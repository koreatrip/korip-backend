#!/bin/bash

echo "nginx 설정 업데이트 시작..."

# 현재 작업 디렉토리 확인
if [ ! -f "deployment/nginx/korip.conf" ]; then
    echo "ERROR: deployment/nginx/korip.conf 파일이 없습니다!"
    echo "현재 위치: $(pwd)"
    exit 1
fi

# nginx 설정 파일 백업
echo "기존 설정 백업 중..."
sudo cp /etc/nginx/sites-available/korip /etc/nginx/sites-available/korip.backup.$(date +%Y%m%d_%H%M%S)

# 새로운 nginx 설정 파일 복사
echo "새 nginx 설정 파일 복사 중..."
sudo cp deployment/nginx/korip.conf /etc/nginx/sites-available/korip

# 설정 문법 검사
echo "nginx 설정 문법 검사 중..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "SUCCESS: nginx 설정 문법 검사 통과!"

    # nginx 재시작
    echo "nginx 재시작 중..."
    sudo systemctl reload nginx

    if [ $? -eq 0 ]; then
        echo "SUCCESS: nginx 재시작 완료!"

        # 연결 테스트
        echo "연결 테스트 중..."
        echo "korip.me 테스트:"
        curl -I https://korip.me 2>/dev/null | head -1

        echo "api.korip.me 테스트 (HTTP):"
        curl -I http://api.korip.me 2>/dev/null | head -1

        echo ""
        echo "nginx 설정 업데이트 완료!"
        echo "다음 단계:"
        echo "1. api.korip.me SSL 인증서 생성:"
        echo "   sudo certbot --nginx -d api.korip.me"
        echo "2. Django ALLOWED_HOSTS 설정 확인"
        echo "3. CORS 설정 확인"

    else
        echo "ERROR: nginx 재시작 실패!"
        exit 1
    fi
else
    echo "ERROR: nginx 설정 오류 발생!"
    echo "백업 파일로 복구하려면:"
    echo "sudo cp /etc/nginx/sites-available/korip.backup.* /etc/nginx/sites-available/korip"
    exit 1
fi
