# 프론트엔드 도커 재빌드 스크립트
# 사용법: .\rebuild-frontend.ps1

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "프론트엔드 도커 재빌드" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

$projectRoot = "F:\USB Drive\_웹어플\AIMBP"
Set-Location $projectRoot

Write-Host "`n[1/4] 컨테이너 중지..." -ForegroundColor Yellow
docker-compose stop frontend | Out-Null
Start-Sleep -Seconds 2

Write-Host "[2/4] 이미지 재빌드..." -ForegroundColor Yellow
docker-compose up -d --build frontend | Out-Null
Start-Sleep -Seconds 5

Write-Host "[3/4] 컨테이너 상태 확인..." -ForegroundColor Yellow
$status = docker-compose ps frontend
Write-Host $status

Write-Host "`n[4/4] 로그 확인..." -ForegroundColor Yellow
docker-compose logs --tail=10 frontend

Write-Host "`n======================================" -ForegroundColor Green
Write-Host "✅ 재빌드 완료!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host "`n브라우저에서 다음을 수행하세요:" -ForegroundColor Cyan
Write-Host "1. Ctrl + Shift + Delete (캐시 초기화)" -ForegroundColor White
Write-Host "2. Ctrl + F5 (강제 새로고침)" -ForegroundColor White
Write-Host "3. http://localhost:3001 방문" -ForegroundColor White
