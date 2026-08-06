import asyncio
import json
import logging
from dotenv import load_dotenv

# Load env variables before importing modules that need them
load_dotenv()

from app.core.redis_client import redis_manager
from app.core.database import db_manager
from app.core.llm import llm
from langchain_core.messages import SystemMessage



logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BackgroundWorker")


async def generate_ticket_summary(session_id: str, ticket_id: str):
    """Fetch ticket from MongoDB, summarize using embedded state, and update ticket."""
    logger.info(f"Processing ticket {ticket_id} for session {session_id}...")

    # 1. Load the ticket from MongoDB
    ticket = await db_manager.get_ticket(ticket_id)
    if not ticket or "state" not in ticket:
        logger.error(f"Cannot find ticket {ticket_id} or state in MongoDB.")
        return

    state = ticket["state"]

    # 2. Extract context
    name = state.get("name", "Unknown Customer")
    email = state.get("email", "Unknown Email")
    phone = state.get("phone", "Unknown Phone")
    orders = state.get("orders", [])

    # In MongoDB, messages are saved as dicts via messages_to_dict
    messages_dicts = state.get("messages", [])
    chat_history = ""
    for m in messages_dicts:
        m_type = m.get("type", "")
        if m_type in ("human", "ai"):
            chat_history += (
                f"{m_type.upper()}: {m.get('data', {}).get('content', '')}\n"
            )

    order_context = json.dumps(orders, indent=2)

    # 3. Generate Summary using LLM
    prompt = f"""
    You are a background summarization agent for a customer support team.
    A user has requested human escalation and a ticket was generated.
    
    USER DETAILS:
    Name: {name}
    Email: {email}
    Phone: {phone}
    
    USER'S ORDERS:
    {order_context}
    
    CHAT HISTORY:
    {chat_history}
    
    TASK:
    Write a concise, professional summary for the human agent.
    Include the user's issue, the specific order they are asking about (if any), and the actions the AI took before escalation.
    Output ONLY the summary, no pleasantries.
    """

    logger.info("Calling LLM for summarization...")
    response = await llm.ainvoke([SystemMessage(content=prompt)])
    summary = response.content

    # 4. Update the MongoDB ticket
    await db_manager.update_ticket_summary(ticket_id, summary)
    logger.info(f"Ticket {ticket_id} successfully updated with AI summary.")


async def listen_for_events():
    """Subscribe to Redis and listen for ticket_events."""
    await db_manager.init_db()
    
    logger.info("Background worker is starting...")

    while True:
        try:
            await redis_manager.connect()
            # ping_interval=60 prevents idle connections from being closed by Render/Redis
            pubsub = redis_manager.client.pubsub(ping_interval=60)
            await pubsub.subscribe("ticket_events")

            logger.info("Background worker is listening for events...")

            async for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    session_id = data.get("session_id")
                    ticket_id = data.get("ticket_id")

                    if session_id and ticket_id:
                        # Run summarization asynchronously
                        asyncio.create_task(generate_ticket_summary(session_id, ticket_id))
        except Exception as e:
            logger.error(f"Error in Redis listener: {e}. Reconnecting in 5 seconds...")
            await asyncio.sleep(5)


if __name__ == "__main__":
    try:
        asyncio.run(listen_for_events())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
