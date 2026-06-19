#!/usr/bin/env python
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def complete_track_by_id(track_id: str):
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    # Step 1: Find the track
    async with engine.begin() as conn:
        result = await conn.execute(text(f'''
            SELECT id, title, status, task_id
            FROM tracks
            WHERE id = '{track_id}'
        '''))
        row = result.fetchone()
        if not row:
            print(f"Track ID {track_id}를 찾을 수 없습니다.")
            return

        track_id, title, status, task_id = row
        print(f"찾은 곡:")
        print(f"  ID: {track_id}")
        print(f"  Title: {title}")
        print(f"  Status: {status}")
        print(f"  Task ID: {task_id}")

    # Step 2: Update the track
    if status == "completed":
        print(f"\n이미 완료된 곡입니다.")
        return

    mock_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    async with engine.begin() as conn:
        print("\n곡 상태를 'completed'로 변경 중...")
        await conn.execute(text(f'''
            UPDATE tracks
            SET status = 'completed',
                file_url = '{mock_url}',
                duration = 180.0
            WHERE id = '{track_id}'
        '''))

    # Step 3: Verify the update
    async with engine.begin() as conn:
        result = await conn.execute(text(f'''
            SELECT id, title, status, file_url
            FROM tracks
            WHERE id = '{track_id}'
        '''))
        row = result.fetchone()
        print(f"\n완료 처리 완료:")
        print(f"  Title: {row[1]}")
        print(f"  Status: {row[2]}")
        print(f"  File URL: {row[3]}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("사용법: python complete_track_by_id.py <track_id>")
        sys.exit(1)

    track_id = sys.argv[1]
    asyncio.run(complete_track_by_id(track_id))
