import os
import sqlite3
import json
import logging
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Database")

# We no longer need SQLite paths
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")


class DatabaseManager:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def init_db(cls):
        """Initialize MongoDB connections. SQLite is removed."""
        if cls.client is None:
            try:
                import certifi

                cls.client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
                cls.db = cls.client.trendly_ai

                # Check connection
                await cls.client.admin.command("ping")
                logger.info("Connected to MongoDB successfully.")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {e}")

    @classmethod
    async def create_ticket(cls, session_id: str, state_dict: dict) -> str:
        """Create a new ticket in MongoDB embedding the full chat state."""
        if cls.db is None:
            await cls.init_db()

        ticket_doc = {
            "session_id": session_id,
            "status": "open",
            "summary": "AI is generating summary...",
            "resolution": None,
            "state": state_dict,  # Embed full chat history/orders here
        }

        result = await cls.db.tickets.insert_one(ticket_doc)
        ticket_id_str = str(result.inserted_id)
        logger.info(f"Created MongoDB ticket {ticket_id_str} for session {session_id}")
        return ticket_id_str

    @classmethod
    async def get_ticket(cls, ticket_id: str) -> dict:
        """Fetch a specific ticket by ID."""
        if cls.db is None:
            await cls.init_db()
        return await cls.db.tickets.find_one({"_id": ObjectId(ticket_id)})

    @classmethod
    async def update_ticket_summary(cls, ticket_id: str, summary: str):
        """Update a ticket's AI-generated summary."""
        if cls.db is None:
            await cls.init_db()
        await cls.db.tickets.update_one(
            {"_id": ObjectId(ticket_id)}, {"$set": {"summary": summary}}
        )
        logger.info(f"Updated summary for ticket {ticket_id}")

    @classmethod
    async def get_all_tickets(cls) -> list:
        """Get all tickets for the Admin Dashboard."""
        if cls.db is None:
            await cls.init_db()
        cursor = cls.db.tickets.find().sort("_id", -1)

        tickets = []
        async for doc in cursor:
            # We don't send the massive 'state' dictionary to the frontend
            tickets.append(
                {
                    "id": str(doc["_id"]),
                    "session_id": doc.get("session_id", ""),
                    "summary": doc.get("summary", ""),
                    "status": doc.get("status", "open"),
                    "resolution": doc.get("resolution", ""),
                }
            )
        return tickets

    @classmethod
    async def resolve_ticket(cls, ticket_id: str, resolution: str):
        """Mark a ticket as resolved."""
        if cls.db is None:
            await cls.init_db()
        await cls.db.tickets.update_one(
            {"_id": ObjectId(ticket_id)},
            {"$set": {"status": "resolved", "resolution": resolution}},
        )


# Global singleton
db_manager = DatabaseManager()
