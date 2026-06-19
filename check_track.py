#!/usr/bin/env python
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def check_track():
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    async with engine.begin() as conn:
        # Check users first
        print("=== Users ===")
        result = await conn.execute(text('SELECT id, email, nickname FROM users LIMIT 5'))
        for row in result:
            print(f'  ID: {row[0]}, Email: {row[1]}, Nickname: {row[2]}')

        # Check tracks with title containing "아파트" or "풍경"
        print("\n=== Tracks ===")
        result = await conn.execute(text('''
            SELECT id, user_id, title, status, file_url, error_message, task_id, ai_service, created_at
            FROM tracks
            WHERE title ILIKE '%아파트%' OR title ILIKE '%풍경%'
            ORDER BY created_at DESC
            LIMIT 20
        '''))
        for row in result:
            print(f'\nTrack ID: {row[0]}')
            print(f'  User ID: {row[1]}')
            print(f'  Title: {row[2]}')
            print(f'  Status: {row[3]}')
            print(f'  File URL: {row[4]}')
            print(f'  Error: {row[5]}')
            print(f'  Task ID: {row[6]}')
            print(f'  AI Service: {row[7]}')
            print(f'  Created: {row[8]}')

asyncio.run(check_track())
