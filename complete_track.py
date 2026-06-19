#!/usr/bin/env python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def complete_track():
    task_id_to_find = "dc3db218473deadc2db2d189b9999392"
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    # Step 1: Find the track
    async with engine.begin() as conn:
        result = await conn.execute(text(f'''
            SELECT id, user_id, title, status, task_id
            FROM tracks
            WHERE task_id = '{task_id_to_find}'
        '''))
        row = result.fetchone()
        if not row:
            print("Track not found!")
            return

        track_id, user_id, title, status, task_id = row
        print(f"Found track:")
        print(f"  ID: {track_id}")
        print(f"  Title: {title}")
        print(f"  Status: {status}")
        print(f"  Task ID: {task_id}")

    # Step 2: Update the track in a separate transaction
    mock_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    async with engine.begin() as conn:
        print("\nUpdating track status to 'completed'...")
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
        print(f"\nUpdate complete:")
        print(f"  Title: {row[1]}")
        print(f"  Status: {row[2]}")
        print(f"  File URL: {row[3]}")

if __name__ == '__main__':
    asyncio.run(complete_track())
