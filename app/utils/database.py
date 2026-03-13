from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import get_settings

settings = get_settings()


class Database:
    """Async MongoDB connection manager."""

    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    @classmethod
    async def connect(cls) -> None:
        """Establish a connection to MongoDB."""
        cls.client = AsyncIOMotorClient(settings.mongodb_uri)
        cls.db = cls.client[settings.database_name]
        # Verify connection
        await cls.client.admin.command("ping")
        print(f"✅ Connected to MongoDB: {settings.database_name}")

    @classmethod
    async def disconnect(cls) -> None:
        """Close the MongoDB connection."""
        if cls.client:
            cls.client.close()
            print("🔌 MongoDB connection closed.")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Return the active database instance."""
        if cls.db is None:
            raise RuntimeError("Database not initialized. Call Database.connect() first.")
        return cls.db
