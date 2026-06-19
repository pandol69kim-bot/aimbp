#!/usr/bin/env python
"""
Suno API 테스트: 실제로 작곡 생성 요청이 작동하는지 확인
"""
import asyncio
import httpx
import json

SUNO_API_BASE = "https://api.sunoapi.org"
SUNO_API_KEY = "1d8cd1287aa8ca2307422184c0043636"
CALLBACK_URL = "https://resample-scribe-busybody.ngrok-free.dev/api/v1/music/webhook/suno"

async def test_generate():
    print("=== Suno API 생성 테스트 ===\n")

    payload = {
        "prompt": "Sad breakup song, emotional, indie",
        "model": "V4",
        "customMode": False,
        "instrumental": False,
        "callBackUrl": CALLBACK_URL,
    }

    print(f"API Base: {SUNO_API_BASE}")
    print(f"Callback URL: {CALLBACK_URL}")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                f"{SUNO_API_BASE}/api/v1/generate",
                headers={"Authorization": f"Bearer {SUNO_API_KEY}"},
                json=payload,
            )

            print(f"응답 상태코드: {resp.status_code}\n")

            data = resp.json()
            print("응답 데이터:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            if data.get("code") == 200:
                task_id = data.get("data", {}).get("taskId")
                print(f"\n✓ 생성 요청 성공!")
                print(f"Task ID: {task_id}")
                print(f"\nWebhook 콜백 대기 중...")
            else:
                print(f"\n✗ API 오류: {data.get('msg')}")

        except httpx.HTTPStatusError as e:
            print(f"✗ HTTP 오류: {e.response.status_code}")
            print(f"응답: {e.response.text}")
        except Exception as e:
            print(f"✗ 오류: {e}")

if __name__ == '__main__':
    asyncio.run(test_generate())
