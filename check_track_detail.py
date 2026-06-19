#!/usr/bin/env python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_track():
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    async with engine.begin() as conn:
        print("=== 아파트 풍경22 & 이별의슬픔 상세 정보 ===\n")

        # 두 곡 모두 조회
        result = await conn.execute(text('''
            SELECT id, title, status, file_url, task_id, error_message, created_at
            FROM tracks
            WHERE task_id IN ('dc3db218473deadc2db2d189b9999392', '2be3fbda21a6fd0bd357f29711d4b49b')
            ORDER BY created_at DESC
        '''))

        for row in result:
            track_id, title, status, file_url, task_id, error_msg, created_at = row
            print(f"곡: {title}")
            print(f"  Track ID: {track_id}")
            print(f"  Task ID: {task_id}")
            print(f"  Status: {status}")
            print(f"  File URL: {file_url}")
            print(f"  Error: {error_msg}")
            print(f"  Created: {created_at}")
            print()

if __name__ == '__main__':
    asyncio.run(check_track())
