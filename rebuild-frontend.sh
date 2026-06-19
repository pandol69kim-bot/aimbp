#!/bin/bash

# 프론트엔드 도커 재빌드 스크립트
# 사용법: bash rebuild-frontend.sh

echo "======================================"
echo "프론트엔드 도커 재빌드"
echo "======================================"

cd "F:\USB Drive\_웹어플\AIMBP"

echo ""
echo "[1/4] 컨테이너 중지..."
docker-compose stop frontend

echo "[2/4] 이미지 재빌드..."
docker-compose up -d --build frontend
sleep 5

echo "[3/4] 컨테이너 상태 확인..."
docker-compose ps frontend

echo ""
echo "[4/4] 로그 확인..."
docker-compose logs --tail=10 frontend

echo ""
echo "======================================"
echo "✅ 재빌드 완료!"
echo "======================================"
echo ""
echo "브라우저에서 다음을 수행하세요:"
echo "1. Ctrl + Shift + Delete (캐시 초기화)"
echo "2. Ctrl + F5 (강제 새로고침)"
echo "3. http://localhost:3001 방문"
