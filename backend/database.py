import asyncpg
from typing import Optional, Any, List
import logging
import config as config_module

settings = config_module.settings
logger = logging.getLogger(__name__)

class DatabaseError(Exception):
    """Custom exception for database errors"""
    pass

class Database:
    """Database connection manager using asyncpg with error handling"""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool with retry logic"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.pool = await asyncpg.create_pool(
                    settings.DATABASE_URL,
                    min_size=5,
                    max_size=20,
                    command_timeout=60,
                    max_queries=50000,
                    max_inactive_connection_lifetime=300
                )
                logger.info("✅ Database connection pool created successfully")
                
                # Test connection
                async with self.pool.acquire() as conn:
                    await conn.fetchval("SELECT 1")
                logger.info("✅ Database connection verified")
                return
                
            except Exception as e:
                logger.error(f"❌ Error connecting to database (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    import asyncio
                    await asyncio.sleep(retry_delay)
                else:
                    raise DatabaseError(f"Failed to connect to database after {max_retries} attempts") from e
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            try:
                await self.pool.close()
                logger.info("✅ Database connection pool closed")
            except Exception as e:
                logger.error(f"❌ Error closing database pool: {e}")
    
    async def execute(self, query: str, *args) -> str:
        """
        Execute a query that doesn't return results
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Query execution status
            
        Raises:
            DatabaseError: If query execution fails
        """
        if not self.pool:
            raise DatabaseError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except asyncpg.PostgresError as e:
            logger.error(f"Database execute error: {e}\nQuery: {query}")
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during execute: {e}")
            raise DatabaseError(f"Unexpected database error: {str(e)}") from e
    
    async def fetch(self, query: str, *args) -> List[asyncpg.Record]:
        """
        Fetch multiple rows
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            List of database records
            
        Raises:
            DatabaseError: If query execution fails
        """
        if not self.pool:
            raise DatabaseError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetch(query, *args)
        except asyncpg.PostgresError as e:
            logger.error(f"Database fetch error: {e}\nQuery: {query}")
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during fetch: {e}")
            raise DatabaseError(f"Unexpected database error: {str(e)}") from e
    
    async def fetchrow(self, query: str, *args) -> Optional[asyncpg.Record]:
        """
        Fetch a single row
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single database record or None
            
        Raises:
            DatabaseError: If query execution fails
        """
        if not self.pool:
            raise DatabaseError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetchrow(query, *args)
        except asyncpg.PostgresError as e:
            logger.error(f"Database fetchrow error: {e}\nQuery: {query}")
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during fetchrow: {e}")
            raise DatabaseError(f"Unexpected database error: {str(e)}") from e
    
    async def fetchval(self, query: str, *args) -> Any:
        """
        Fetch a single value
        
        Args:
            query: SQL query string
            *args: Query parameters
            
        Returns:
            Single value from query result
            
        Raises:
            DatabaseError: If query execution fails
        """
        if not self.pool:
            raise DatabaseError("Database pool not initialized")
            
        try:
            async with self.pool.acquire() as connection:
                return await connection.fetchval(query, *args)
        except asyncpg.PostgresError as e:
            logger.error(f"Database fetchval error: {e}\nQuery: {query}")
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error during fetchval: {e}")
            raise DatabaseError(f"Unexpected database error: {str(e)}") from e
    
    async def health_check(self) -> bool:
        """
        Check database connectivity
        
        Returns:
            True if database is accessible, False otherwise
        """
        try:
            if not self.pool:
                return False
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Global database instance
db = Database()
