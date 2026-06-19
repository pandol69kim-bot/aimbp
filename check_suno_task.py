#!/usr/bin/env python
import asyncio
import httpx
import sys

SUNO_API_BASE = "https://api.sunoapi.org"
SUNO_API_KEY = "1d8cd1287aa8ca2307422184c0043636"

async def check_suno_task(task_id: str):
    """Suno API에서 직접 task 상태를 조회"""

    print(f"Suno API Task Status 조회")
    print(f"Task ID: {task_id}")
    print(f"API Base: {SUNO_API_BASE}\n")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            # Suno API에서 task 상태 조회
            url = f"{SUNO_API_BASE}/api/v1/query"

            print(f"API 요청: POST {url}")
            print(f"Headers: Authorization: Bearer {SUNO_API_KEY[:20]}...")
            print(f"Payload: {{'task_ids': ['{task_id}']}}\n")

            resp = await client.post(
                url,
                headers={"Authorization": f"Bearer {SUNO_API_KEY}"},
                json={"task_ids": [task_id]},
            )

            print(f"응답 상태코드: {resp.status_code}")
            data = resp.json()

            print(f"\n응답 데이터:")
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if data.get("code") == 200:
                tasks = data.get("data", [])
                if tasks:
                    task = tasks[0]
                    print(f"\n=== Task 상태 요약 ===")
                    print(f"Task ID: {task.get('id')}")
                    print(f"Status: {task.get('status')}")
                    print(f"State: {task.get('state')}")
                    print(f"Title: {task.get('title')}")
                    print(f"Audio URL: {task.get('audio_url')}")
                    print(f"Image URL: {task.get('image_url')}")
                else:
                    print("\n응답에 task 데이터가 없습니다.")
            else:
                print(f"\nAPI 오류: {data.get('msg')}")

        except httpx.HTTPStatusError as e:
            print(f"HTTP 오류 {e.response.status_code}")
            print(f"응답: {e.response.text}")
        except Exception as e:
            print(f"오류: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python check_suno_task.py <task_id>")
        print("\n예제:")
        print("  python check_suno_task.py dc3db218473deadc2db2d189b9999392")
        sys.exit(1)

    task_id = sys.argv[1]
    asyncio.run(check_suno_task(task_id))
