import asyncio
import os
import asyncpg

NEON_DB_URL = os.getenv("NEON_DATABASE_URL")

async def main():
    conn = await asyncpg.connect(NEON_DB_URL)
    tables = await conn.fetch(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
        ORDER BY table_name;
        """
    )
    result = []
    for tbl in tables:
        t = tbl['table_name']
        columns = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name=$1 AND table_schema='public'
            ORDER BY ordinal_position;
            """, t
        )
        result.append({'table': t, 'columns': [dict(c) for c in columns]})
    await conn.close()
    for entry in result:
        print(f"\nTable: {entry['table']}")
        for col in entry['columns']:
            print(f"  - {col['column_name']:<22} {col['data_type']:<16} Nullable: {col['is_nullable']:<4} Default: {col['column_default']}")

if __name__ == "__main__":
    asyncio.run(table_info())