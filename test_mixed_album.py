#!/usr/bin/env python
"""Test complete mixed album workflow (AI + Upload)"""
import asyncio
import httpx
import tempfile
import os

BASE_URL = "http://localhost:8001/api/v1"

async def test_mixed_album():
    print("=" * 60)
    print("혼합 앨범 생성 전체 테스트 (AI 곡 + 업로드 MP3)")
    print("=" * 60 + "\n")

    async def make_request(method, endpoint, data=None, files=None, token=None):
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
                if files:
                    resp = await asyncio.to_thread(
                        lambda: httpx.post(url, files=files, data=data, headers=headers, timeout=30)
                    )
                else:
                    resp = await asyncio.to_thread(
                        lambda: httpx.post(url, json=data, headers=headers, timeout=30)
                    )
            return resp
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            return None

    # Step 1: Login
    print("Step 1: 로그인...")
    login_resp = await make_request("POST", "/auth/login", {
        "email": "polling@test.com",
        "password": "password123"
    })

    if not login_resp or login_resp.status_code != 200:
        print(f"[FAIL] 로그인 실패: {login_resp.status_code if login_resp else 'Connection error'}")
        if login_resp:
            print(f"Response: {login_resp.text}")
        return

    token = login_resp.json().get("data", {}).get("access_token")
    if not token:
        print("[FAIL] 토큰을 받지 못했습니다")
        return

    print(f"[OK] 로그인 성공\n")

    # Step 2: Create album
    print("Step 2: 앨범 생성...")
    album_resp = await make_request("POST", "/albums", {
        "title": "혼합 앨범 테스트",
        "description": "Suno AI 곡 + 업로드 MP3 혼합"
    }, token=token)

    if not album_resp or album_resp.status_code != 201:
        print(f"[FAIL] 앨범 생성 실패: {album_resp.status_code if album_resp else 'Error'}")
        if album_resp:
            print(f"Response: {album_resp.text}")
        return

    album_id = album_resp.json().get("data", {}).get("id")
    print(f"[OK] 앨범 생성: {album_id}\n")

    # Step 3: Upload MP3 file
    print("Step 3: MP3 파일 업로드...")

    # Create test MP3
    test_mp3 = tempfile.gettempdir() + "/test_upload.mp3"
    with open(test_mp3, 'wb') as f:
        f.write(b'ID3\x03\x00\x00\x00\x00\x10\x00')
        f.write(b'\xff\xfb' + b'\x00' * 2000)

    with open(test_mp3, 'rb') as f:
        files = {
            "file": ("업로드곡.mp3", f, "audio/mpeg")
        }
        data = {
            "title": "업로드된 곡",
            "artist": "테스트 아티스트",
            "genre": "테스트"
        }

        upload_resp = await asyncio.to_thread(
            lambda: httpx.post(
                f"{BASE_URL}/music/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
        )

    if not upload_resp or upload_resp.status_code != 201:
        print(f"[FAIL] 업로드 실패: {upload_resp.status_code if upload_resp else 'Error'}")
        if upload_resp:
            print(f"Response: {upload_resp.text}")
        print(f"[DEBUG] 요청 URL: {BASE_URL}/music/upload")
        print(f"[DEBUG] 파일: {test_mp3}")
        return

    uploaded_track = upload_resp.json().get("data", {})
    uploaded_track_id = uploaded_track.get("id")
    print(f"[OK] MP3 업로드 성공")
    print(f"     Track ID: {uploaded_track_id}")
    print(f"     Title: {uploaded_track.get('title')}")
    print(f"     Artist: {uploaded_track.get('artist_name')}\n")

    # Step 4: Create AI-generated track (using Mock mode)
    print("Step 4: AI 곡 생성 (Mock 모드)...")
    ai_resp = await make_request("POST", "/music/generate", {
        "title": "AI로 생성한 곡",
        "genre": "Pop",
        "mood": "Happy",
        "ai_service": "suno"
    }, token=token)

    if not ai_resp or ai_resp.status_code != 201:
        print(f"[FAIL] AI 곡 생성 실패: {ai_resp.status_code if ai_resp else 'Error'}")
        if ai_resp:
            print(f"Response: {ai_resp.text}")
        # Continue anyway
        ai_track_id = None
    else:
        ai_track = ai_resp.json().get("data", {})
        ai_track_id = ai_track.get("id")
        print(f"[OK] AI 곡 생성 요청")
        print(f"     Track ID: {ai_track_id}")
        print(f"     Title: {ai_track.get('title')}\n")

    # Step 5: Add tracks to album
    print("Step 5: 앨범에 곡 추가...")

    # Add uploaded track
    add1_resp = await make_request("POST", f"/albums/{album_id}/tracks", {
        "track_id": uploaded_track_id,
        "order": 1
    }, token=token)

    if not add1_resp or add1_resp.status_code != 201:
        print(f"[FAIL] 업로드 곡 추가 실패: {add1_resp.status_code if add1_resp else 'Error'}")
        if add1_resp:
            print(f"Response: {add1_resp.text}")
        return

    print(f"[OK] 업로드된 곡 추가 (순서: 1)")

    # Add AI track if available
    if ai_track_id:
        add2_resp = await make_request("POST", f"/albums/{album_id}/tracks", {
            "track_id": ai_track_id,
            "order": 2
        }, token=token)

        if not add2_resp or add2_resp.status_code != 201:
            print(f"[FAIL] AI 곡 추가 실패: {add2_resp.status_code if add2_resp else 'Error'}")
        else:
            print(f"[OK] AI 곡 추가 (순서: 2)\n")
    else:
        print("[SKIP] AI 곡 추가 스킵\n")

    # Step 6: Set cover art
    print("Step 6: 커버 아트 설정...")
    # For now, skip cover (optional for publish)
    print("[SKIP] 커버 아트 생략\n")

    # Step 7: Publish album
    print("Step 7: 앨범 발행...")

    # First, get album to check if we need cover
    get_album_resp = await make_request("GET", f"/albums/{album_id}", token=token)
    album_data = get_album_resp.json().get("data", {}) if get_album_resp else {}

    if not album_data.get("cover_url"):
        print("[WARN] 커버 아트가 없습니다. 커버 추가 후 발행해주세요.")
        return

    publish_resp = await make_request("POST", f"/albums/{album_id}/publish", {}, token=token)

    if not publish_resp or publish_resp.status_code != 200:
        print(f"[FAIL] 앨범 발행 실패: {publish_resp.status_code if publish_resp else 'Error'}")
        if publish_resp:
            print(f"Response: {publish_resp.text}")
        return

    print(f"[OK] 앨범 발행 완료\n")

    # Step 8: Download album
    print("Step 8: 앨범 다운로드...")
    download_resp = await make_request("GET", f"/albums/{album_id}/download", token=token)

    if not download_resp or download_resp.status_code != 200:
        print(f"[FAIL] 다운로드 실패: {download_resp.status_code if download_resp else 'Error'}")
        return

    # Save download
    download_path = f"{tempfile.gettempdir()}/mixed_album.zip"
    with open(download_path, 'wb') as f:
        f.write(download_resp.content)

    print(f"[OK] 다운로드 완료")
    print(f"     경로: {download_path}")
    print(f"     크기: {os.path.getsize(download_path)} bytes\n")

    # Summary
    print("=" * 60)
    print("✓ 혼합 앨범 생성 성공!")
    print("=" * 60)
    print(f"앨범 ID: {album_id}")
    print(f"포함된 곡:")
    print(f"  1. 업로드된 곡 (사용자)")
    if ai_track_id:
        print(f"  2. AI로 생성한 곡 (Suno)")
    print(f"다운로드 파일: {download_path}")

if __name__ == '__main__':
    asyncio.run(test_mixed_album())
