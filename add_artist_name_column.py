#!/usr/bin/env python
"""Add artist_name column to tracks table"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def migrate():
    engine = create_async_engine('postgresql+asyncpg://aimbp:aimbp1234@localhost:5432/aimbp')

    async with engine.begin() as conn:
        print("Adding artist_name column to tracks table...")

        try:
            # Check if column already exists
            result = await conn.execute(text("""
                SELECT EXISTS(
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'tracks' AND column_name = 'artist_name'
                )
            """))

            exists = result.scalar()

            if exists:
                print("Column artist_name already exists!")
            else:
                # Add column
                await conn.execute(text("""
                    ALTER TABLE tracks ADD COLUMN artist_name VARCHAR(255) NULL
                """))
                await conn.commit()
                print("[OK] Column artist_name added successfully!")

        except Exception as e:
            print(f"Error: {e}")
            await conn.rollback()
            raise

if __name__ == '__main__':
    asyncio.run(migrate())
