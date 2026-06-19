#!/usr/bin/env python
"""Test MP3 file upload functionality"""
import asyncio
import httpx

async def test_upload():
    print("=== MP3 Upload Test ===\n")

    # Step 1: Login
    print("1. Logging in...")
    login_resp = await asyncio.to_thread(
        lambda: httpx.post(
            "http://localhost:8001/api/v1/auth/login",
            json={"email": "polling@test.com", "password": "password123"},
            timeout=30
        )
    )

    if login_resp.status_code != 200:
        print(f"Login failed: {login_resp.status_code}")
        return

    token = login_resp.json().get("data", {}).get("access_token")
    print(f"[OK] Logged in. Token: {token[:20]}...\n")

    # Step 2: Create MP3 test file
    print("2. Creating test MP3 file...")
    import tempfile
    test_mp3_path = tempfile.gettempdir() + "/test_track.mp3"

    # Create a minimal MP3 file (ID3 header + dummy data)
    with open(test_mp3_path, 'wb') as f:
        # ID3 header
        f.write(b'ID3\x03\x00\x00\x00\x00\x10\x00')
        # Dummy MP3 frames
        f.write(b'\xff\xfb' + b'\x00' * 1000)

    print(f"[OK] Test file created: {test_mp3_path}\n")

    # Step 3: Upload MP3
    print("3. Uploading MP3 file...")
    headers = {"Authorization": f"Bearer {token}"}

    with open(test_mp3_path, 'rb') as f:
        files = {"file": ("test_track.mp3", f, "audio/mpeg")}
        data = {
            "title": "Test Track from Upload",
            "artist": "Test Artist",
            "genre": "Test Genre"
        }

        upload_resp = await asyncio.to_thread(
            lambda: httpx.post(
                "http://localhost:8001/api/v1/music/upload",
                files=files,
                data=data,
                headers=headers,
                timeout=30
            )
        )

    if upload_resp.status_code != 201:
        print(f"Upload failed: {upload_resp.status_code}")
        print(upload_resp.text)
        return

    track_data = upload_resp.json().get("data", {})
    track_id = track_data.get("id")

    print(f"[OK] Upload successful!")
    print(f"  Track ID: {track_id}")
    print(f"  Title: {track_data.get('title')}")
    print(f"  Artist: {track_data.get('artist_name')}")
    print(f"  Status: {track_data.get('status')}")
    print(f"  File URL: {track_data.get('file_url')[:50]}...\n")

    # Step 4: Add to album
    print("4. Creating album...")
    album_resp = await asyncio.to_thread(
        lambda: httpx.post(
            "http://localhost:8001/api/v1/albums",
            json={
                "title": "Test Album with Uploaded Track",
                "description": "This album contains both uploaded MP3 and AI-generated tracks"
            },
            headers=headers,
            timeout=30
        )
    )

    if album_resp.status_code != 201:
        print(f"Album creation failed: {album_resp.status_code}")
        return

    album_data = album_resp.json().get("data", {})
    album_id = album_data.get("id")
    print(f"[OK] Album created: {album_id}\n")

    # Step 5: Add track to album
    print("5. Adding uploaded track to album...")
    add_track_resp = await asyncio.to_thread(
        lambda: httpx.post(
            f"http://localhost:8001/api/v1/albums/{album_id}/tracks",
            json={
                "track_id": track_id,
                "order": 1
            },
            headers=headers,
            timeout=30
        )
    )

    if add_track_resp.status_code != 201:
        print(f"Failed to add track: {add_track_resp.status_code}")
        print(add_track_resp.text)
        return

    print(f"[OK] Track added to album!\n")

    # Step 6: Summary
    print("6. Summary:")
    print(f"  - Album ID: {album_id}")
    print(f"  - Track ID: {track_id}")
    print(f"  - Track Title: {track_data.get('title')}")
    print(f"  - Artist: {track_data.get('artist_name')}")
    print(f"  - Source: Uploaded MP3 file")
    print(f"\n[SUCCESS] MP3 upload test completed!")
    print(f"\nNext steps:")
    print(f"1. Add AI-generated tracks to the same album")
    print(f"2. Set cover art for the album")
    print(f"3. Publish the album")
    print(f"4. Download the album (will include both uploaded and AI-generated tracks)")

if __name__ == '__main__':
    asyncio.run(test_upload())
