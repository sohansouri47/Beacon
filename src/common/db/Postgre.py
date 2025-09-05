import psycopg
import json
import os
from typing import List, Dict, Optional


# class ConversationHistoryManager:
#     def __init__(self, database_url: str = None):
#         self.database_url = database_url or os.getenv("DATABASE_URL")
#         self._create_table()

#     def _create_table(self):
#         """Create conversationss table"""
#         with psycopg.connect(self.database_url) as conn:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     """
#                     CREATE TABLE IF NOT EXISTS conversationss (
#                         username VARCHAR(255) NOT NULL,
#                         conversation_id VARCHAR(255) NOT NULL,
#                         conversation TEXT NOT NULL,
#                         updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#                         PRIMARY KEY (conversation_id)
#                     );
#                 """
#                 )

#     def store(self, username: str, conversation_id: str, conversation):
#         """Store/update conversation"""
#         with psycopg.connect(self.database_url) as conn:
#             with conn.cursor() as cur:
#                 # Check if conversation exists
#                 cur.execute(
#                     "SELECT conversation FROM conversationss WHERE conversation_id = %s",
#                     (conversation_id,),
#                 )
#                 result = cur.fetchone()

#                 if result:
#                     # Append to existing conversation
#                     existing_data = result[0]
#                     if isinstance(existing_data, list):
#                         existing_data.append(conversation)
#                     else:
#                         existing_data = [existing_data, conversation]

#                     cur.execute(
#                         """
#                         UPDATE conversationss
#                         SET conversation = %s, updated_at = CURRENT_TIMESTAMP
#                         WHERE conversation_id = %s
#                     """,
#                         (json.dumps(existing_data), conversation_id),
#                     )
#                 else:
#                     # New conversation
#                     cur.execute(
#                         """
#                         INSERT INTO conversationss (username, conversation_id, conversation)
#                         VALUES (%s, %s, %s)
#                     """,
#                         (username, conversation_id, json.dumps([conversation])),
#                     )

#     def fetch(self, conversation_id: str) -> Optional[Dict]:
#         """Fetch conversation by ID"""
#         with psycopg.connect(self.database_url) as conn:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     """
#                     SELECT username, conversation_id, conversation
#                     FROM conversationss
#                     WHERE conversation_id = %s
#                 """,
#                     (conversation_id,),
#                 )

#                 result = cur.fetchone()
#                 if result:
#                     return {
#                         "username": result[0],
#                         "conversation_id": result[1],
#                         "conversation": result[2],
#                     }
#                 return None

#     def fetch_last_n(self, conversation_id: str, n: int = 10) -> List[Dict]:
#         """Fetch last n interactions from a conversation"""
#         with psycopg.connect(self.database_url) as conn:
#             with conn.cursor() as cur:
#                 cur.execute(
#                     """
#                     SELECT conversation
#                     FROM conversationss
#                     WHERE conversation_id = %s
#                 """,
#                     (conversation_id,),
#                 )

#                 result = cur.fetchone()
#                 if result and result[0]:
#                     all_interactions = result[0]
#                     return (
#                         all_interactions[-n:]
#                         if len(all_interactions) > n
#                         else all_interactions
#                     )
#                 return []

import psycopg
import psycopg.rows
import json
import os
from typing import List, Dict, Optional


class ConversationHistoryManager:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv("DATABASE_URL")

    async def _create_table(self):
        """Create conversationss table"""
        async with await psycopg.AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS conversationss (
                        username VARCHAR(255) NOT NULL,
                        conversation_id VARCHAR(255) NOT NULL,
                        conversation JSONB NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (conversation_id)
                    );
                """
                )
            await conn.commit()

    async def store(self, username: str, conversation_id: str, conversation):
        """Store/update conversation"""
        async with await psycopg.AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    "SELECT conversation FROM conversationss WHERE conversation_id = %s",
                    (conversation_id,),
                )
                result = await cur.fetchone()

                if result:
                    # Append to existing conversation
                    existing_data = result[0]
                    if isinstance(existing_data, list):
                        existing_data.append(conversation)
                    else:
                        existing_data = [existing_data, conversation]

                    await cur.execute(
                        """
                        UPDATE conversationss 
                        SET conversation = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE conversation_id = %s
                    """,
                        (json.dumps(existing_data), conversation_id),
                    )
                else:
                    await cur.execute(
                        """
                        INSERT INTO conversationss (username, conversation_id, conversation)
                        VALUES (%s, %s, %s)
                    """,
                        (username, conversation_id, json.dumps([conversation])),
                    )
            await conn.commit()

    async def fetch(self, conversation_id: str) -> Optional[Dict]:
        """Fetch conversation by ID"""
        async with await psycopg.AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                await cur.execute(
                    """
                    SELECT username, conversation_id, conversation 
                    FROM conversationss 
                    WHERE conversation_id = %s
                """,
                    (conversation_id,),
                )
                result = await cur.fetchone()
                return result

    # async def fetch_last_n(self, conversation_id: str, n: int = 10) -> List[Dict]:
    #     """Fetch last n interactions from a conversation"""
    #     async with await psycopg.AsyncConnection.connect(self.database_url) as conn:
    #         async with conn.cursor() as cur:
    #             await cur.execute(
    #                 """
    #                 SELECT conversation
    #                 FROM conversationss
    #                 WHERE conversation_id = %s
    #             """,
    #                 (conversation_id,),
    #             )
    #             result = await cur.fetchone()

    #             if result and result[0]:
    #                 all_interactions = result[0]
    #                 return (
    #                     all_interactions[-n:]
    #                     if len(all_interactions) > n
    #                     else all_interactions
    #                 )
    #             return []
    async def fetch_last_n(self, conversation_id: str, n: int = 10) -> List[Dict]:
        """Fetch last n interactions from a conversation"""
        async with await psycopg.AsyncConnection.connect(self.database_url) as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT conversation
                    FROM conversationss 
                    WHERE conversation_id = %s
                    """,
                    (conversation_id,),
                )
                result = await cur.fetchone()

                if not result or not result[0]:
                    return []

                raw_data = result[0]

                # recursive JSON decode until it's a list/dict
                def safe_load(data):
                    while isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except Exception:
                            break
                    return data

                all_interactions = safe_load(raw_data)

                if not isinstance(all_interactions, list):
                    return []

                return all_interactions[-n:]
