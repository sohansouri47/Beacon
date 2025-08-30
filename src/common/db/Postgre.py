import psycopg
import json
import os
from typing import List, Dict, Optional


class ConversationHistoryManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")
        self._create_table()

    def _create_table(self):
        """Create conversations table"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversations (
                        username VARCHAR(255) NOT NULL,
                        conversation_id VARCHAR(255) NOT NULL,
                        conversation JSONB NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (conversation_id)
                    );
                """
                )

    def store(
        self,
        username: str,
        conversation_id: str,
        user_msg: str,
        agent_name: str,
        agent_response: str,
    ):
        """Store/update conversation"""
        new_interaction = {
            "user": user_msg,
            "agent": agent_response,
            "agent_name": agent_name,
        }

        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                # Check if conversation exists
                cur.execute(
                    "SELECT conversation FROM conversations WHERE conversation_id = %s",
                    (conversation_id,),
                )
                result = cur.fetchone()

                if result:
                    # Append to existing conversation
                    existing_data = result[0]
                    if isinstance(existing_data, list):
                        existing_data.append(new_interaction)
                    else:
                        existing_data = [existing_data, new_interaction]

                    cur.execute(
                        """
                        UPDATE conversations 
                        SET conversation = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE conversation_id = %s
                    """,
                        (json.dumps(existing_data), conversation_id),
                    )
                else:
                    # New conversation
                    cur.execute(
                        """
                        INSERT INTO conversations (username, conversation_id, conversation)
                        VALUES (%s, %s, %s)
                    """,
                        (username, conversation_id, json.dumps([new_interaction])),
                    )

    def fetch(self, conversation_id: str) -> Optional[Dict]:
        """Fetch conversation by ID"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT username, conversation_id, conversation 
                    FROM conversations 
                    WHERE conversation_id = %s
                """,
                    (conversation_id,),
                )

                result = cur.fetchone()
                if result:
                    return {
                        "username": result[0],
                        "conversation_id": result[1],
                        "conversation": result[2],
                    }
                return None

    def fetch_last_n(self, conversation_id: str, n: int = 10) -> List[Dict]:
        """Fetch last n interactions from a conversation"""
        with psycopg.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT conversation
                    FROM conversations 
                    WHERE conversation_id = %s
                """,
                    (conversation_id,),
                )

                result = cur.fetchone()
                if result and result[0]:
                    all_interactions = result[0]
                    return (
                        all_interactions[-n:]
                        if len(all_interactions) > n
                        else all_interactions
                    )
                return []
