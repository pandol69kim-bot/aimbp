# AIMBP Alembic 마이그레이션 도우미
# 사용법:
#   .\migrate.ps1 new "설명"   # 새 마이그레이션 생성
#   .\migrate.ps1 up           # 최신으로 업그레이드
#   .\migrate.ps1 history      # 마이그레이션 이력 보기
#   .\migrate.ps1 current      # 현재 버전 확인

param(
    [Parameter(Position=0)] [string]$Action = "up",
    [Parameter(Position=1)] [string]$Message = ""
)

$CONTAINER = "aimbp-backend"

function Check-Container {
    $status = docker inspect --format "{{.State.Running}}" $CONTAINER 2>$null
    if ($status -ne "true") {
        Write-Host "[ERROR] $CONTAINER 컨테이너가 실행 중이지 않습니다. docker-compose up -d 먼저 실행하세요." -ForegroundColor Red
        exit 1
    }
}

switch ($Action) {
    "new" {
        if (-not $Message) {
            Write-Host "[ERROR] 마이그레이션 설명을 입력하세요. 예: .\migrate.ps1 new '컬럼 추가'" -ForegroundColor Red
            exit 1
        }
        Check-Container
        Write-Host "[INFO] 마이그레이션 생성 중: $Message" -ForegroundColor Cyan
        docker exec $CONTAINER bash -c "cd /app && alembic revision --autogenerate -m '$Message'"

        # 생성된 파일을 호스트로 복사
        $files = docker exec $CONTAINER bash -c "ls /app/alembic/versions/*.py 2>/dev/null | grep -v __pycache__"
        foreach ($file in $files -split "`n") {
            $filename = Split-Path $file -Leaf
            $hostPath = "backend\alembic\versions\$filename"
            if (-not (Test-Path $hostPath)) {
                docker cp "${CONTAINER}:$file" $hostPath
                Write-Host "[OK] 마이그레이션 파일 복사: $hostPath" -ForegroundColor Green
            }
        }
    }
    "up" {
        Check-Container
        Write-Host "[INFO] 마이그레이션 실행 중..." -ForegroundColor Cyan
        docker exec $CONTAINER bash -c "cd /app && alembic upgrade head"
    }
    "history" {
        Check-Container
        docker exec $CONTAINER bash -c "cd /app && alembic history --verbose"
    }
    "current" {
        Check-Container
        docker exec $CONTAINER bash -c "cd /app && alembic current"
    }
    default {
        Write-Host "사용법:" -ForegroundColor Yellow
        Write-Host "  .\migrate.ps1 new '설명'   # 새 마이그레이션 생성"
        Write-Host "  .\migrate.ps1 up           # 최신으로 업그레이드 (기본값)"
        Write-Host "  .\migrate.ps1 history      # 마이그레이션 이력"
        Write-Host "  .\migrate.ps1 current      # 현재 버전"
    }
}
