#!/usr/bin/env python
"""
Webhook 엔드포인트 테스트: Suno 콜백이 실제로 도착하는지 확인
"""
import asyncio
import httpx
import json

WEBHOOK_URL = "http://localhost:8001/api/v1/music/webhook/suno"

# Suno API 콜백 형식 (문서에서)
SUNO_CALLBACK_PAYLOAD = {
    "code": 200,
    "msg": "success",
    "data": {
        "task_id": "dc3db218473deadc2db2d189b9999392",
        "callbackType": "audio",  # "text" 또는 "audio"
        "data": [
            {
                "id": "abc123",
                "audio_url": "https://example.com/music.mp3",
                "stream_audio_url": "https://example.com/stream.mp3",
                "image_url": "https://example.com/cover.png",
                "title": "Test Song",
                "tags": "indie, sad"
            }
        ]
    }
}

async def test_webhook():
    print("=== Webhook 엔드포인트 테스트 ===\n")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Payload:\n{json.dumps(SUNO_CALLBACK_PAYLOAD, indent=2, ensure_ascii=False)}\n")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            resp = await client.post(
                WEBHOOK_URL,
                json=SUNO_CALLBACK_PAYLOAD,
            )

            print(f"응답 상태코드: {resp.status_code}")
            print(f"응답 본문:")

            try:
                data = resp.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
            except:
                print(resp.text)

            print(f"\n백엔드에 webhook이 도착했는지 확인해보세요.")
            print(f"데이터베이스에서 해당 track의 상태를 조회하세요:")
            print(f"  SELECT status, file_url FROM tracks WHERE task_id = 'dc3db218473deadc2db2d189b9999392'")

        except httpx.ConnectError as e:
            print(f"연결 실패: {e}")
            print(f"\n백엔드 서버가 실행 중인지 확인하세요.")
            print(f"  http://localhost:8001 에 접속해보세요.")
        except Exception as e:
            print(f"오류: {e}")

if __name__ == '__main__':
    asyncio.run(test_webhook())
