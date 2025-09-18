import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging


class JarvisMemory:
    """
    JARVIS Memory System - SQLite-based persistent memory for conversations, tasks, and reminders
    """

    def __init__(self, db_path: str = "jarvis_memory.db"):
        """Initialize the memory system with SQLite database"""
        self.db_path = Path(db_path)
        self.logger = logging.getLogger(__name__)
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Conversations table - stores all chat history
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS conversations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user_message TEXT NOT NULL,
                        ai_response TEXT NOT NULL,
                        session_id TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Tasks table - stores tasks and reminders
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        description TEXT,
                        due_date TEXT,
                        priority TEXT DEFAULT 'medium',
                        status TEXT DEFAULT 'pending',
                        reminder_time TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP
                    )
                ''')

                # Context table - stores important context and facts
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS context (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        key TEXT UNIQUE NOT NULL,
                        value TEXT NOT NULL,
                        category TEXT DEFAULT 'general',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Sessions table - tracks conversation sessions
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id TEXT UNIQUE NOT NULL,
                        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        end_time TIMESTAMP,
                        message_count INTEGER DEFAULT 0
                    )
                ''')

                conn.commit()
                self.logger.info("Database initialized successfully")

        except Exception as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    # === CONVERSATION MEMORY ===

    def save_conversation(self, user_message: str, ai_response: str, session_id: str = None) -> bool:
        """Save a conversation exchange to memory"""
        try:
            timestamp = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO conversations (timestamp, user_message, ai_response, session_id)
                    VALUES (?, ?, ?, ?)
                ''', (timestamp, user_message, ai_response, session_id))

                # Update session message count
                if session_id:
                    cursor.execute('''
                        UPDATE sessions SET message_count = message_count + 1 
                        WHERE session_id = ?
                    ''', (session_id,))

                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error saving conversation: {e}")
            return False

    def get_recent_conversations(self, limit: int = 10, session_id: str = None) -> List[Dict]:
        """Retrieve recent conversations"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if session_id:
                    cursor.execute('''
                        SELECT timestamp, user_message, ai_response 
                        FROM conversations 
                        WHERE session_id = ?
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (session_id, limit))
                else:
                    cursor.execute('''
                        SELECT timestamp, user_message, ai_response 
                        FROM conversations 
                        ORDER BY timestamp DESC LIMIT ?
                    ''', (limit,))

                rows = cursor.fetchall()
                return [
                    {
                        'timestamp': row[0],
                        'user_message': row[1],
                        'ai_response': row[2]
                    }
                    # Reverse to get chronological order
                    for row in reversed(rows)
                ]

        except Exception as e:
            self.logger.error(f"Error retrieving conversations: {e}")
            return []

    def search_conversations(self, query: str, limit: int = 5) -> List[Dict]:
        """Search through conversation history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT timestamp, user_message, ai_response 
                    FROM conversations 
                    WHERE user_message LIKE ? OR ai_response LIKE ?
                    ORDER BY timestamp DESC LIMIT ?
                ''', (f'%{query}%', f'%{query}%', limit))

                rows = cursor.fetchall()
                return [
                    {
                        'timestamp': row[0],
                        'user_message': row[1],
                        'ai_response': row[2]
                    }
                    for row in rows
                ]

        except Exception as e:
            self.logger.error(f"Error searching conversations: {e}")
            return []

    # === TASK MANAGEMENT ===

    def add_task(self, title: str, description: str = "", due_date: str = None,
                 priority: str = "medium", reminder_time: str = None) -> bool:
        """Add a new task or reminder"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO tasks (title, description, due_date, priority, reminder_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (title, description, due_date, priority, reminder_time))
                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error adding task: {e}")
            return False

    def get_pending_tasks(self) -> List[Dict]:
        """Get all pending tasks"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, due_date, priority, reminder_time, created_at
                    FROM tasks 
                    WHERE status = 'pending'
                    ORDER BY 
                        CASE priority 
                            WHEN 'high' THEN 1 
                            WHEN 'medium' THEN 2 
                            WHEN 'low' THEN 3 
                        END,
                        due_date ASC
                ''')

                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'due_date': row[3],
                        'priority': row[4],
                        'reminder_time': row[5],
                        'created_at': row[6]
                    }
                    for row in rows
                ]

        except Exception as e:
            self.logger.error(f"Error retrieving tasks: {e}")
            return []

    def complete_task(self, task_id: int) -> bool:
        """Mark a task as completed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (task_id,))
                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            return False

    def get_due_reminders(self) -> List[Dict]:
        """Get tasks that need reminders (due today or overdue)"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, description, due_date, priority
                    FROM tasks 
                    WHERE status = 'pending' 
                    AND (due_date <= ? OR reminder_time <= ?)
                    ORDER BY due_date ASC
                ''', (today, datetime.now().isoformat()))

                rows = cursor.fetchall()
                return [
                    {
                        'id': row[0],
                        'title': row[1],
                        'description': row[2],
                        'due_date': row[3],
                        'priority': row[4]
                    }
                    for row in rows
                ]

        except Exception as e:
            self.logger.error(f"Error retrieving reminders: {e}")
            return []

    # === CONTEXT MANAGEMENT ===

    def store_context(self, key: str, value: str, category: str = "general") -> bool:
        """Store important context or facts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO context (key, value, category, updated_at)
                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value, category))
                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error storing context: {e}")
            return False

    def get_context(self, key: str) -> Optional[str]:
        """Retrieve stored context"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'SELECT value FROM context WHERE key = ?', (key,))
                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            self.logger.error(f"Error retrieving context: {e}")
            return None

    def get_all_context(self, category: str = None) -> Dict[str, str]:
        """Get all stored context, optionally filtered by category"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                if category:
                    cursor.execute(
                        'SELECT key, value FROM context WHERE category = ?', (category,))
                else:
                    cursor.execute('SELECT key, value FROM context')

                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}

        except Exception as e:
            self.logger.error(f"Error retrieving all context: {e}")
            return {}

    # === SESSION MANAGEMENT ===

    def start_session(self, session_id: str) -> bool:
        """Start a new conversation session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions (session_id, start_time, message_count)
                    VALUES (?, CURRENT_TIMESTAMP, 0)
                ''', (session_id,))
                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error starting session: {e}")
            return False

    def end_session(self, session_id: str) -> bool:
        """End a conversation session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE sessions SET end_time = CURRENT_TIMESTAMP WHERE session_id = ?
                ''', (session_id,))
                conn.commit()
                return True

        except Exception as e:
            self.logger.error(f"Error ending session: {e}")
            return False

    # === UTILITY METHODS ===

    def get_memory_stats(self) -> Dict:
        """Get memory system statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Count conversations
                cursor.execute('SELECT COUNT(*) FROM conversations')
                conversation_count = cursor.fetchone()[0]

                # Count tasks
                cursor.execute(
                    'SELECT COUNT(*) FROM tasks WHERE status = "pending"')
                pending_tasks = cursor.fetchone()[0]

                cursor.execute(
                    'SELECT COUNT(*) FROM tasks WHERE status = "completed"')
                completed_tasks = cursor.fetchone()[0]

                # Count context items
                cursor.execute('SELECT COUNT(*) FROM context')
                context_count = cursor.fetchone()[0]

                return {
                    'conversations': conversation_count,
                    'pending_tasks': pending_tasks,
                    'completed_tasks': completed_tasks,
                    'context_items': context_count
                }

        except Exception as e:
            self.logger.error(f"Error getting memory stats: {e}")
            return {}

    def cleanup_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean up old conversation data (keep tasks and context)"""
        try:
            cutoff_date = (datetime.now() -
                           timedelta(days=days_to_keep)).isoformat()

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM conversations WHERE timestamp < ?
                ''', (cutoff_date,))

                deleted_count = cursor.rowcount
                conn.commit()

                self.logger.info(
                    f"Cleaned up {deleted_count} old conversations")
                return True

        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
            return False
