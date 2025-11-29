"""
Database schema initialization script.
Run this to clean and recreate all database tables.
"""
import asyncio
import asyncpg
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.config import settings

async def init_database():
    """Initialize database with schema"""
    
    # Read schema file
    schema_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Connect to database
    conn = await asyncpg.connect(settings.DATABASE_URL)
    
    try:
        print("🗑️  Cleaning existing database...")
        print("📝 Creating new schema...")
        
        # Execute schema
        await conn.execute(schema_sql)
        
        print("✅ Database schema created successfully!")
        print("✅ Default admin account created: admin@fitmates.com / admin123")
        print("✅ Sample client created: john@example.com / client123")
        
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(init_database())
