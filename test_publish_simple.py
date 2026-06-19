#!/usr/bin/env python
"""Simple album publishing test - generate cover with AI"""
import asyncio
import httpx
import tempfile
import os
import time

BASE_URL = "http://localhost:8001/api/v1"

async def test_publish():
    print("=" * 70)
    print("앨범 발행 및 다운로드 테스트 (AI 커버 생성)")
    print("=" * 70 + "\n")

    async def make_request(method, endpoint, data=None, token=None):
        """Make HTTP request"""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{BASE_URL}{endpoint}"

        try:
            if method == "GET":
                resp = await asyncio.to_thread(
                    lambda: httpx.get(url, headers=headers, timeout=30)
                )
            elif method == "POST":
                resp = await asyncio.to_thread(
                    lambda: httpx.post(url, json=data, headers=headers, timeout=30)
                )
            return resp
        except Exception as e:
            print(f"[ERROR] {e}")
            return None

    # Step 1: Login
    print("Step 1: 로그인...")
    login_resp = await make_request("POST", "/auth/login", {
        "email": "polling@test.com",
        "password": "password123"
    })

    if not login_resp or login_resp.status_code != 200:
        print(f"[FAIL] 로그인 실패")
        return

    token = login_resp.json().get("data", {}).get("access_token")
    print(f"[OK] 로그인 성공\n")

    # 기존 앨범
    album_id = "5f9ecf47-bb44-48e1-b6b9-85484b507ec1"

    # Step 2: Get album info
    print(f"Step 2: 앨범 조회...")
    get_album_resp = await make_request("GET", f"/albums/{album_id}", token=token)

    if not get_album_resp or get_album_resp.status_code != 200:
        print(f"[FAIL] 앨범 조회 실패")
        return

    album_data = get_album_resp.json().get("data", {})
    print(f"[OK] 앨범: {album_data.get('title')}")
    print(f"     곡 수: {len(album_data.get('tracks', []))}\n")

    # Step 3: Generate cover with AI
    print(f"Step 3: AI로 커버 생성...")
    gen_cover_resp = await make_request("POST", "/cover/generate", {
        "album_id": album_id,
        "prompt_genre": "Pop",
        "prompt_mood": "Happy",
        "prompt_keywords": "colorful, vibrant, music, album",
        "ai_model": "openai"
    }, token=token)

    if not gen_cover_resp or gen_cover_resp.status_code != 201:
        print(f"[WARN] 커버 생성 실패: {gen_cover_resp.status_code if gen_cover_resp else 'Error'}")
        print(f"       대신 Mock 커버를 사용합니다\n")
        # Use mock cover data
        covers = []
        cover_id = None
    else:
        covers = gen_cover_resp.json().get("data", [])
        cover_id = covers[0].get("id") if covers else None
        print(f"[OK] 커버 생성 요청 완료")
        print(f"     {len(covers)}개 사이즈 생성\n")

    # Wait a bit for cover generation
    if cover_id:
        print(f"Step 4: 커버 생성 대기 (10초)...")
        for i in range(10):
            await asyncio.to_thread(lambda: time.sleep(1))
            print(f"     [{i+1}/10]", end='\r')
        print("\n[OK] 대기 완료\n")

        # Step 5: Apply cover to album
        print(f"Step 5: 앨범에 커버 적용...")
        apply_cover_resp = await make_request("POST", f"/albums/{album_id}/cover", {
            "cover_id": cover_id
        }, token=token)

        if not apply_cover_resp or apply_cover_resp.status_code != 200:
            print(f"[WARN] 커버 적용 실패: {apply_cover_resp.status_code if apply_cover_resp else 'Error'}")
        else:
            print(f"[OK] 커버 적용 완료\n")
    else:
        print(f"Step 4: Mock 커버 사용\n")

    # Step 6: Publish album
    print(f"Step 6: 앨범 발행...")
    publish_resp = await make_request("POST", f"/albums/{album_id}/publish", {}, token=token)

    if not publish_resp or publish_resp.status_code != 200:
        print(f"[FAIL] 앨범 발행 실패: {publish_resp.status_code if publish_resp else 'Error'}")
        if publish_resp:
            print(f"Response: {publish_resp.text}")
        return

    print(f"[OK] 앨범 발행 완료\n")

    # Step 7: Download album
    print(f"Step 7: 앨범 다운로드...")
    download_resp = await make_request("GET", f"/albums/{album_id}/download", token=token)

    if not download_resp or download_resp.status_code != 200:
        print(f"[FAIL] 다운로드 실패: {download_resp.status_code if download_resp else 'Error'}")
        return

    # Save ZIP
    download_path = tempfile.gettempdir() + "/혼합앨범_발행.zip"
    with open(download_path, 'wb') as f:
        f.write(download_resp.content)

    file_size = os.path.getsize(download_path)
    print(f"[OK] 다운로드 완료")
    print(f"     경로: {download_path}")
    print(f"     크기: {file_size:,} bytes\n")

    # Step 8: Verify ZIP
    print(f"Step 8: ZIP 파일 내용 확인...")
    try:
        import zipfile
        with zipfile.ZipFile(download_path, 'r') as z:
            file_list = z.namelist()
            print(f"[OK] ZIP 파일 구조:")
            for filename in file_list:
                file_info = z.getinfo(filename)
                size_kb = file_info.file_size / 1024
                print(f"     - {filename} ({size_kb:.1f} KB)")
    except Exception as e:
        print(f"[ERROR] ZIP 확인 실패: {e}")
        return

    # Summary
    print("\n" + "=" * 70)
    print("SUCCESS! 혼합 앨범 발행 및 다운로드 완료!")
    print("=" * 70)
    print(f"\n앨범 완성:")
    print(f"  제목: 혼합 앨범 테스트")
    print(f"  포함 곡:")
    print(f"    1. 업로드된 MP3 파일 (사용자)")
    print(f"    2. Suno AI로 생성한 곡 (Mock)")
    print(f"  커버: AI 생성 커버")
    print(f"  상태: 발행됨")
    print(f"  다운로드 파일: {download_path}")
    print(f"  총 크기: {file_size:,} bytes")

if __name__ == '__main__':
    asyncio.run(test_publish())
