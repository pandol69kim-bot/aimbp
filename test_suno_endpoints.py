#!/usr/bin/env python
"""
Suno API의 다양한 엔드포인트 테스트
상태 조회 엔드포인트를 찾기 위함
"""
import asyncio
import httpx
import json

SUNO_API_BASE = "https://api.sunoapi.org"
SUNO_API_KEY = "1d8cd1287aa8ca2307422184c0043636"
TASK_ID = "f8897f47-4399-47d1-924f-cf3a3e0218f8"  # 위에서 생성한 task

async def test_endpoints():
    print("=== Suno API 엔드포인트 테스트 ===\n")

    endpoints = [
        # (HTTP method, URL format, description)
        ("GET", f"{SUNO_API_BASE}/api/v1/query", "query endpoint"),
        ("GET", f"{SUNO_API_BASE}/api/v1/fetch", "fetch endpoint"),
        ("GET", f"{SUNO_API_BASE}/api/v1/status", "status endpoint"),
        ("GET", f"{SUNO_API_BASE}/api/v1/{TASK_ID}", "task id in path"),
        ("POST", f"{SUNO_API_BASE}/api/v1/query", "query POST"),
        ("POST", f"{SUNO_API_BASE}/api/v1/fetch", "fetch POST"),
    ]

    headers = {"Authorization": f"Bearer {SUNO_API_KEY}"}

    async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
        for method, url, desc in endpoints:
            print(f"테스트: {method} {desc}")
            print(f"  URL: {url}")

            try:
                if method == "GET":
                    resp = await client.get(
                        url,
                        headers=headers,
                        params={"task_id": TASK_ID, "task_ids": TASK_ID},
                    )
                else:
                    resp = await client.post(
                        url,
                        headers=headers,
                        json={"task_ids": [TASK_ID], "task_id": TASK_ID},
                    )

                print(f"  Status: {resp.status_code}")

                if resp.status_code < 400:
                    try:
                        data = resp.json()
                        # 첫 500자만 출력
                        text = json.dumps(data, indent=2, ensure_ascii=False)[:500]
                        print(f"  Response: {text}")
                    except:
                        print(f"  Response (text): {resp.text[:200]}")
                else:
                    print(f"  Error: {resp.text[:200]}")

            except Exception as e:
                print(f"  Exception: {e}")

            print()

if __name__ == '__main__':
    asyncio.run(test_endpoints())
