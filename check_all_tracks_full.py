#!/usr/bin/env python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_all():
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    async with engine.begin() as conn:
        print("=== 모든 작곡 (50개 제한) ===\n")

        result = await conn.execute(text('''
            SELECT id, title, status, file_url, task_id, error_message, created_at
            FROM tracks
            ORDER BY created_at DESC
            LIMIT 50
        '''))

        rows = result.fetchall()
        print(f"총 {len(rows)}개의 곡:\n")

        for idx, row in enumerate(rows, 1):
            track_id, title, status, file_url, task_id, error_msg, created_at = row
            print(f"{idx}. [{status}] {title}")
            print(f"   Track ID: {track_id}")
            print(f"   Task ID: {task_id}")
            if file_url:
                print(f"   File: {file_url[:60]}...")
            if error_msg:
                print(f"   Error: {error_msg}")
            print()

if __name__ == '__main__':
    asyncio.run(check_all())
