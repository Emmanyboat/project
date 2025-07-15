from supabase import create_client, Client
from app.core.config import settings
import asyncio

# Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
supabase_admin: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

async def init_db():
    """Initialize database connection and run any setup"""
    try:
        # Test connection
        response = supabase.table('users').select("count", count="exact").execute()
        print(f"✅ Database connected successfully")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

async def get_db():
    """Dependency to get database client"""
    return supabase