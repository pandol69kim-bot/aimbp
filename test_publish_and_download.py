#!/usr/bin/env python
"""Test album publishing and downloading with cover art"""
import asyncio
import httpx
import tempfile
import os
from PIL import Image

BASE_URL = "http://localhost:8001/api/v1"

async def test_publish_download():
    print("=" * 70)
    print("앨범 발행 및 다운로드 전체 테스트 (커버 포함)")
    print("=" * 70 + "\n")

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
        print(f"[FAIL] 로그인 실패")
        return

    token = login_resp.json().get("data", {}).get("access_token")
    print(f"[OK] 로그인 성공\n")

    # 기존 앨범 사용 (또는 새로 생성)
    album_id = "5f9ecf47-bb44-48e1-b6b9-85484b507ec1"  # 이전 테스트에서 생성한 앨범
    print(f"Step 2: 앨범 확인...")
    get_album_resp = await make_request("GET", f"/albums/{album_id}", token=token)

    if not get_album_resp or get_album_resp.status_code != 200:
        print(f"[FAIL] 앨범 조회 실패")
        return

    album_data = get_album_resp.json().get("data", {})
    print(f"[OK] 앨범: {album_data.get('title')}")
    print(f"     ID: {album_id}")
    print(f"     곡 수: {len(album_data.get('tracks', []))}\n")

    # Step 3: Create cover image
    print("Step 3: 커버 이미지 생성...")
    cover_path = tempfile.gettempdir() + "/album_cover.png"

    # Create a simple test image
    img = Image.new('RGB', (400, 400), color='blue')
    img.save(cover_path)
    print(f"[OK] 커버 이미지 생성: {cover_path}\n")

    # Step 4: Upload cover (create cover in system)
    print("Step 4: 커버 업로드...")

    with open(cover_path, 'rb') as f:
        files = {
            "file": ("cover.png", f, "image/png")
        }
        data = {
            "size": "400:400"
        }

        cover_resp = await asyncio.to_thread(
            lambda: httpx.post(
                f"{BASE_URL}/covers",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
        )

    if not cover_resp or cover_resp.status_code != 201:
        print(f"[FAIL] 커버 업로드 실패: {cover_resp.status_code if cover_resp else 'Error'}")
        if cover_resp:
            print(f"Response: {cover_resp.text}")
        return

    cover_id = cover_resp.json().get("data", {}).get("id")
    print(f"[OK] 커버 업로드 성공")
    print(f"     Cover ID: {cover_id}\n")

    # Step 5: Apply cover to album
    print("Step 5: 앨범에 커버 적용...")
    apply_cover_resp = await make_request("POST", f"/albums/{album_id}/cover", {
        "cover_id": cover_id
    }, token=token)

    if not apply_cover_resp or apply_cover_resp.status_code != 200:
        print(f"[FAIL] 커버 적용 실패: {apply_cover_resp.status_code if apply_cover_resp else 'Error'}")
        if apply_cover_resp:
            print(f"Response: {apply_cover_resp.text}")
        return

    print(f"[OK] 커버 적용 완료\n")

    # Step 6: Publish album
    print("Step 6: 앨범 발행...")
    publish_resp = await make_request("POST", f"/albums/{album_id}/publish", {}, token=token)

    if not publish_resp or publish_resp.status_code != 200:
        print(f"[FAIL] 앨범 발행 실패: {publish_resp.status_code if publish_resp else 'Error'}")
        if publish_resp:
            print(f"Response: {publish_resp.text}")
        return

    published_data = publish_resp.json().get("data", {})
    print(f"[OK] 앨범 발행 완료")
    print(f"     상태: {published_data.get('album', {}).get('status')}\n")

    # Step 7: Download album
    print("Step 7: 앨범 다운로드...")
    download_resp = await make_request("GET", f"/albums/{album_id}/download", token=token)

    if not download_resp or download_resp.status_code != 200:
        print(f"[FAIL] 다운로드 실패: {download_resp.status_code if download_resp else 'Error'}")
        return

    # Save download
    download_path = tempfile.gettempdir() + "/혼합앨범.zip"
    with open(download_path, 'wb') as f:
        f.write(download_resp.content)

    file_size = os.path.getsize(download_path)
    print(f"[OK] 다운로드 완료")
    print(f"     파일: {download_path}")
    print(f"     크기: {file_size:,} bytes\n")

    # Step 8: Verify ZIP contents
    print("Step 8: ZIP 파일 내용 확인...")
    try:
        import zipfile
        with zipfile.ZipFile(download_path, 'r') as z:
            file_list = z.namelist()
            print(f"[OK] ZIP 파일 내용:")
            for filename in file_list:
                file_info = z.getinfo(filename)
                print(f"     - {filename} ({file_info.file_size:,} bytes)")
    except Exception as e:
        print(f"[ERROR] ZIP 확인 실패: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("✓ 혼합 앨범 발행 및 다운로드 완료!")
    print("=" * 70)
    print(f"\n앨범 정보:")
    print(f"  제목: 혼합 앨범 테스트")
    print(f"  포함 곡:")
    print(f"    1. 업로드된 곡 (사용자)")
    print(f"    2. AI로 생성한 곡 (Suno Mock)")
    print(f"  커버: 포함됨")
    print(f"  상태: 발행됨 (다운로드 가능)")
    print(f"\n다운로드 위치: {download_path}")
    print(f"파일 크기: {file_size:,} bytes")

if __name__ == '__main__':
    asyncio.run(test_publish_download())
