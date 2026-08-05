from app.core.database import db_manager


class AdminService:
    @staticmethod
    def verify_credentials(username: str, password: str) -> bool:
        # Hardcoded auth for now
        return username == "admin" and password == "password"

    @staticmethod
    async def get_all_tickets() -> list:
        return await db_manager.get_all_tickets()

    @staticmethod
    async def resolve_ticket(ticket_id: str, resolution: str) -> None:
        await db_manager.resolve_ticket(ticket_id, resolution)
