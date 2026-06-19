#!/usr/bin/env python
"""
Polling 방식이 정상 작동하는지 테스트
"""
import asyncio
import httpx
import json
import time

async def test_polling():
    print("=== Polling 방식 작곡 생성 테스트 ===\n")

    # 로그인 (존재하는 계정으로)
    print("1. 로그인 중...")
    login_resp = await asyncio.to_thread(
        lambda: httpx.post(
            "http://localhost:8001/api/v1/auth/login",
            json={"email": "polling@test.com", "password": "password123"},
            timeout=30
        )
    )

    if login_resp.status_code != 200:
        print(f"로그인 실패: {login_resp.status_code}")
        print(login_resp.text)
        return

    login_data = login_resp.json()
    token = login_data.get("data", {}).get("access_token")
    print(f"[OK] 로그인 성공, Token: {token[:20]}...\n")

    # 작곡 생성
    print("2. 작곡 생성 중 (Polling 방식)...")
    generate_payload = {
        "title": "Polling Test Song",
        "genre": "indie",
        "mood": "happy",
        "ai_service": "suno"
    }

    headers = {"Authorization": f"Bearer {token}"}

    gen_resp = await asyncio.to_thread(
        lambda: httpx.post(
            "http://localhost:8001/api/v1/music/generate",
            json=generate_payload,
            headers=headers,
            timeout=30
        )
    )

    if gen_resp.status_code != 201:
        print(f"생성 실패: {gen_resp.status_code}")
        print(gen_resp.text)
        return

    gen_data = gen_resp.json()
    track_data = gen_data.get("data", {})
    track_id = track_data.get("id")
    task_id = track_data.get("task_id")

    print(f"[OK] 작곡 생성 요청 완료")
    print(f"  Track ID: {track_id}")
    print(f"  Task ID: {task_id}")
    print(f"  Initial Status: {track_data.get('status')}\n")

    # 상태 확인 (주기적으로)
    print("3. 상태 모니터링 중...\n")
    start_time = time.time()
    max_wait = 300  # 5분 대기

    for attempt in range(30):  # 30번 시도
        await asyncio.sleep(5)  # 5초 대기

        status_resp = await asyncio.to_thread(
            lambda: httpx.get(
                f"http://localhost:8001/api/v1/music/{track_id}/status",
                headers=headers,
                timeout=30
            )
        )

        if status_resp.status_code == 200:
            status_data = status_resp.json().get("data", {})
            status = status_data.get("status")
            file_url = status_data.get("file_url")

            elapsed = time.time() - start_time
            print(f"[{elapsed:.0f}s] Attempt {attempt+1}: Status = {status}, URL = {file_url[:50] if file_url else 'None'}...")

            if status == "completed":
                print(f"\n[OK] 작곡 생성 완료!")
                print(f"  File URL: {file_url}")
                return

            elif status == "failed":
                error = status_data.get("error_message")
                print(f"\n[FAIL] 작곡 생성 실패: {error}")
                return

        if time.time() - start_time > max_wait:
            print(f"\n⏱ 타임아웃 (5분 초과)")
            return

    print(f"\n⏱ 폴링 제한 도달 (30회 시도)")

if __name__ == '__main__':
    asyncio.run(test_polling())
