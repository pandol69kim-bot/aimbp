#!/usr/bin/env python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def list_all_tracks():
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    async with engine.begin() as conn:
        print("=== 모든 작곡 목록 ===\n")
        result = await conn.execute(text('''
            SELECT id, title, status, created_at
            FROM tracks
            ORDER BY created_at DESC
            LIMIT 30
        '''))

        for idx, row in enumerate(result, 1):
            track_id, title, status, created_at = row
            print(f"{idx}. [{status}] {title}")
            print(f"   ID: {track_id}")
            print(f"   Created: {created_at}\n")

if __name__ == '__main__':
    asyncio.run(list_all_tracks())
