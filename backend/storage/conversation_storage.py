"""
Storage Layer - Persistencia con SQLite
Sistema híbrido como Antigravity: SQLite + Archivos
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class StoredMessage:
    """Mensaje almacenado"""
    id: Optional[int]
    conversation_id: str
    role: str
    content: str
    tool_calls: Optional[str]  # JSON string
    tool_call_id: Optional[str]
    created_at: str


@dataclass
class StoredConversation:
    """Conversación almacenada"""
    id: str
    title: Optional[str]
    created_at: str
    updated_at: str
    message_count: int


class ConversationStorage:
    """
    Gestiona la persistencia de conversaciones
    
    Arquitectura:
    - SQLite: Mensajes, metadata, búsquedas
    - Archivos: Artifacts (task.md, etc.)
    """
    
    def __init__(self, base_dir: str = "~/.agent_data"):
        self.base_dir = Path(base_dir).expanduser()
        self.db_dir = self.base_dir / "conversations"
        self.artifacts_dir = self.base_dir / "artifacts"
        
        # Crear directorios
        self.db_dir.mkdir(parents=True, exist_ok=True)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        
        # Database principal
        self.db_path = self.db_dir / "agent.db"
        self._init_database()
    
    def _init_database(self):
        """Inicializa el schema de la base de datos"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
        
        # Tabla de conversaciones
        conn.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        # Tabla de mensajes
        conn.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                tool_calls TEXT,
                tool_call_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        ''')
        
        # Migración: Agregar tool_call_id si no existe
        try:
            conn.execute("ALTER TABLE messages ADD COLUMN tool_call_id TEXT")
        except sqlite3.OperationalError:
            # Ya existe la columna
            pass
        
        # Índices para búsquedas rápidas
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_conversation 
            ON messages(conversation_id)
        ''')
        
        conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_created 
            ON messages(created_at)
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Obtiene una conexión con configuración adecuada"""
        conn = sqlite3.connect(self.db_path, timeout=10.0)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    
    def create_conversation(self, conversation_id: str, title: Optional[str] = None) -> bool:
        """Crea una nueva conversación"""
        try:
            conn = self._get_connection()
            conn.execute(
                "INSERT INTO conversations (id, title) VALUES (?, ?)",
                (conversation_id, title)
            )
            conn.commit()
            conn.close()
            
            # Crear directorio de artifacts
            artifact_dir = self.artifacts_dir / conversation_id
            artifact_dir.mkdir(exist_ok=True)
            
            return True
        except sqlite3.IntegrityError:
            # Ya existe
            return False
    
    def save_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_call_id: Optional[str] = None
    ) -> int:
        """
        Guarda un mensaje en la conversación
        
        Returns:
            ID del mensaje guardado
        """
        conn = self._get_connection()
        
        # Asegurar que la conversación existe (en la misma transacción)
        try:
            conn.execute(
                "INSERT OR IGNORE INTO conversations (id) VALUES (?)",
                (conversation_id,)
            )
        except:
            pass
        
        # Serializar tool_calls si existen
        tool_calls_json = json.dumps(tool_calls) if tool_calls else None
        
        # Insertar mensaje
        cursor = conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, tool_calls, tool_call_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (conversation_id, role, content, tool_calls_json, tool_call_id)
        )
        
        message_id = cursor.lastrowid
        
        # Actualizar contador y timestamp de conversación
        conn.execute(
            """
            UPDATE conversations 
            SET message_count = message_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (conversation_id,)
        )
        
        conn.commit()
        conn.close()
        
        # Crear directorio de artifacts si no existe
        artifact_dir = self.artifacts_dir / conversation_id
        artifact_dir.mkdir(exist_ok=True)
        
        return message_id
    
    def get_messages(self, conversation_id: str, limit: Optional[int] = None) -> List[StoredMessage]:
        """Obtiene los mensajes de una conversación"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        query = """
            SELECT id, conversation_id, role, content, tool_calls, tool_call_id, created_at
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor = conn.execute(query, (conversation_id,))
        rows = cursor.fetchall()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append(StoredMessage(
                id=row['id'],
                conversation_id=row['conversation_id'],
                role=row['role'],
                content=row['content'],
                tool_calls=row['tool_calls'],
                tool_call_id=row['tool_call_id'],
                created_at=row['created_at']
            ))
        
        return messages
    
    def get_conversation(self, conversation_id: str) -> Optional[StoredConversation]:
        """Obtiene información de una conversación"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            """
            SELECT id, title, created_at, updated_at, message_count
            FROM conversations
            WHERE id = ?
            """,
            (conversation_id,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        return StoredConversation(
            id=row['id'],
            title=row['title'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            message_count=row['message_count']
        )
    
    def list_conversations(self, limit: int = 50) -> List[StoredConversation]:
        """Lista todas las conversaciones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            """
            SELECT id, title, created_at, updated_at, message_count
            FROM conversations
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            StoredConversation(
                id=row['id'],
                title=row['title'],
                created_at=row['created_at'],
                updated_at=row['updated_at'],
                message_count=row['message_count']
            )
            for row in rows
        ]
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Elimina una conversación y sus mensajes"""
        conn = sqlite3.connect(self.db_path)
        
        # Eliminar mensajes
        conn.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
        
        # Eliminar conversación
        conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        
        conn.commit()
        conn.close()
        
        # Eliminar directorio de artifacts
        artifact_dir = self.artifacts_dir / conversation_id
        if artifact_dir.exists():
            import shutil
            shutil.rmtree(artifact_dir)
        
        return True
    
    def save_artifact(self, conversation_id: str, name: str, content: str) -> Path:
        """
        Guarda un artifact (archivo markdown, etc.)
        
        Args:
            conversation_id: ID de la conversación
            name: Nombre del artifact (ej: "task.md")
            content: Contenido del artifact
        
        Returns:
            Path al archivo guardado
        """
        artifact_dir = self.artifacts_dir / conversation_id
        artifact_dir.mkdir(exist_ok=True)
        
        artifact_path = artifact_dir / name
        artifact_path.write_text(content, encoding='utf-8')
        
        return artifact_path
    
    def load_artifact(self, conversation_id: str, name: str) -> Optional[str]:
        """Carga un artifact"""
        artifact_path = self.artifacts_dir / conversation_id / name
        
        if not artifact_path.exists():
            return None
        
        return artifact_path.read_text(encoding='utf-8')
    
    def list_artifacts(self, conversation_id: str) -> List[str]:
        """Lista los artifacts de una conversación"""
        artifact_dir = self.artifacts_dir / conversation_id
        
        if not artifact_dir.exists():
            return []
        
        return [f.name for f in artifact_dir.iterdir() if f.is_file()]
    
    def search_messages(self, query: str, limit: int = 50) -> List[StoredMessage]:
        """Busca mensajes por contenido"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute(
            """
            SELECT id, conversation_id, role, content, tool_calls, created_at
            FROM messages
            WHERE content LIKE ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (f"%{query}%", limit)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            StoredMessage(
                id=row['id'],
                conversation_id=row['conversation_id'],
                role=row['role'],
                content=row['content'],
                tool_calls=row['tool_calls'],
                created_at=row['created_at']
            )
            for row in rows
        ]



    def save_api_key(self, provider: str, api_key: str):
        """Guarda una API key en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO api_keys (provider, api_key, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (provider, api_key))
        conn.commit()
        conn.close()

    def get_api_key(self, provider: str):
        """Obtiene una API key de la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT api_key FROM api_keys WHERE provider = ?", (provider,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None


# Singleton global
_storage_instance: Optional[ConversationStorage] = None





# Singleton del storage
_storage_instance = None


def get_storage():
    """Obtiene la instancia singleton del storage"""
    global _storage_instance
    
    if _storage_instance is None:
        _storage_instance = ConversationStorage()
    
    return _storage_instance
