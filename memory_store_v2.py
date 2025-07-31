"""
Store de mémoire V2 optimisé - JAK Company
Version nettoyée et optimisée pour la gestion des sessions et contextes
"""

import time
import logging
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, deque
from cachetools import TTLCache
from dataclasses import dataclass, asdict
from enum import Enum
from bloc_config_v2 import BlocType

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Statuts de session"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ESCALATED = "escalated"
    COMPLETED = "completed"

@dataclass
class MessageEntry:
    """Entrée de message dans l'historique"""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: float
    bloc_id: Optional[str] = None
    agent_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SessionContext:
    """Contexte de session"""
    session_id: str
    status: SessionStatus
    created_at: float
    last_activity: float
    profile_type: Optional[str] = None
    current_bloc: Optional[str] = None
    recent_blocs: List[str] = None
    message_count: int = 0
    escalation_count: int = 0
    
    def __post_init__(self):
        if self.recent_blocs is None:
            self.recent_blocs = []
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class OptimizedMemoryStoreV2:
    """Store de mémoire V2 optimisé pour JAK Company"""
    
    def __init__(self, max_sessions: int = 1000, session_ttl: int = 3600, message_history_limit: int = 50):
        """
        Initialise le store de mémoire
        
        Args:
            max_sessions: Nombre maximum de sessions en mémoire
            session_ttl: Durée de vie des sessions en secondes
            message_history_limit: Limite du nombre de messages par session
        """
        self._sessions = TTLCache(maxsize=max_sessions, ttl=session_ttl)
        self._message_history = defaultdict(lambda: deque(maxlen=message_history_limit))
        self._bloc_history = defaultdict(lambda: deque(maxlen=10))
        self._agent_history = defaultdict(lambda: deque(maxlen=10))
        self._context_data = defaultdict(dict)
        self._access_stats = defaultdict(int)
        self._session_stats = {
            "total_created": 0,
            "total_cleared": 0,
            "current_active": 0
        }
    
    def get_or_create_session(self, session_id: str) -> SessionContext:
        """Récupère ou crée une session"""
        if session_id not in self._sessions:
            session = SessionContext(
                session_id=session_id,
                status=SessionStatus.ACTIVE,
                created_at=time.time(),
                last_activity=time.time()
            )
            self._sessions[session_id] = session
            self._session_stats["total_created"] += 1
            self._session_stats["current_active"] += 1
            logger.info(f"Session créée: {session_id}")
        else:
            session = self._sessions[session_id]
            session.last_activity = time.time()
        
        self._access_stats[session_id] += 1
        return session
    
    def add_message(self, session_id: str, message: str, role: str = "user", 
                   bloc_id: Optional[str] = None, agent_type: Optional[str] = None) -> None:
        """Ajoute un message à l'historique de la session"""
        session = self.get_or_create_session(session_id)
        
        message_entry = MessageEntry(
            role=role,
            content=message,
            timestamp=time.time(),
            bloc_id=bloc_id,
            agent_type=agent_type
        )
        
        self._message_history[session_id].append(message_entry)
        session.message_count += 1
        
        logger.debug(f"Message ajouté à la session {session_id}: {role} - {message[:50]}...")
    
    def add_bloc_presented(self, session_id: str, bloc_id: str) -> None:
        """Enregistre un bloc présenté"""
        session = self.get_or_create_session(session_id)
        
        self._bloc_history[session_id].append({
            "bloc_id": bloc_id,
            "timestamp": time.time()
        })
        
        session.current_bloc = bloc_id
        session.recent_blocs.append(bloc_id)
        
        # Garder seulement les 5 derniers blocs
        if len(session.recent_blocs) > 5:
            session.recent_blocs = session.recent_blocs[-5:]
        
        logger.debug(f"Bloc présenté à la session {session_id}: {bloc_id}")
    
    def add_agent_used(self, session_id: str, agent_type: str) -> None:
        """Enregistre l'agent utilisé"""
        session = self.get_or_create_session(session_id)
        
        self._agent_history[session_id].append({
            "agent_type": agent_type,
            "timestamp": time.time()
        })
        
        logger.debug(f"Agent utilisé pour la session {session_id}: {agent_type}")
    
    def set_session_profile(self, session_id: str, profile_type: str) -> None:
        """Définit le profil de la session"""
        session = self.get_or_create_session(session_id)
        session.profile_type = profile_type
        logger.debug(f"Profil défini pour la session {session_id}: {profile_type}")
    
    def set_context_data(self, session_id: str, key: str, value: Any) -> None:
        """Définit une donnée de contexte"""
        self._context_data[session_id][key] = value
        logger.debug(f"Contexte défini pour la session {session_id}: {key} = {value}")
    
    def get_context_data(self, session_id: str, key: str, default: Any = None) -> Any:
        """Récupère une donnée de contexte"""
        return self._context_data[session_id].get(key, default)
    
    def set_payment_context(self, session_id: str, financing_type: str, 
                          time_info: Dict[str, int], total_days: int) -> None:
        """Sauvegarde le contexte de paiement"""
        payment_context = {
            "financing_type": financing_type,
            "time_info": time_info,
            "total_days": total_days,
            "timestamp": time.time()
        }
        self.set_context_data(session_id, "payment_context", payment_context)
        logger.debug(f"Contexte de paiement sauvegardé pour la session {session_id}")
    
    def get_payment_context(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Récupère le contexte de paiement"""
        return self.get_context_data(session_id, "payment_context")
    
    def get_messages(self, session_id: str, limit: Optional[int] = None) -> List[MessageEntry]:
        """Récupère les messages d'une session"""
        messages = list(self._message_history[session_id])
        if limit:
            messages = messages[-limit:]
        return messages
    
    def get_last_message(self, session_id: str) -> Optional[MessageEntry]:
        """Récupère le dernier message d'une session"""
        messages = self._message_history[session_id]
        return messages[-1] if messages else None
    
    def get_last_bloc(self, session_id: str) -> Optional[str]:
        """Récupère le dernier bloc présenté"""
        blocs = self._bloc_history[session_id]
        return blocs[-1]["bloc_id"] if blocs else None
    
    def get_last_n_blocs(self, session_id: str, n: int = 3) -> List[str]:
        """Récupère les n derniers blocs présentés"""
        blocs = list(self._bloc_history[session_id])
        bloc_ids = [bloc["bloc_id"] for bloc in blocs[-n:]]
        return bloc_ids
    
    def get_last_agent(self, session_id: str) -> Optional[str]:
        """Récupère le dernier agent utilisé"""
        agents = self._agent_history[session_id]
        return agents[-1]["agent_type"] if agents else None
    
    def get_last_n_agents(self, session_id: str, n: int = 3) -> List[str]:
        """Récupère les n derniers agents utilisés"""
        agents = list(self._agent_history[session_id])
        agent_types = [agent["agent_type"] for agent in agents[-n:]]
        return agent_types
    
    def has_bloc_been_presented(self, session_id: str, bloc_id: str) -> bool:
        """Vérifie si un bloc a déjà été présenté"""
        blocs = self._bloc_history[session_id]
        return any(bloc["bloc_id"] == bloc_id for bloc in blocs)
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Récupère le contexte complet d'une session"""
        session = self.get_or_create_session(session_id)
        
        context = {
            "session": session.to_dict(),
            "last_bloc": self.get_last_bloc(session_id),
            "recent_blocs": self.get_last_n_blocs(session_id, 5),
            "last_agent": self.get_last_agent(session_id),
            "recent_agents": self.get_last_n_agents(session_id, 3),
            "message_count": len(self._message_history[session_id]),
            "context_data": dict(self._context_data[session_id])
        }
        
        return context
    
    def mark_session_escalated(self, session_id: str) -> None:
        """Marque une session comme escaladée"""
        session = self.get_or_create_session(session_id)
        session.status = SessionStatus.ESCALATED
        session.escalation_count += 1
        logger.info(f"Session escaladée: {session_id}")
    
    def mark_session_completed(self, session_id: str) -> None:
        """Marque une session comme terminée"""
        session = self.get_or_create_session(session_id)
        session.status = SessionStatus.COMPLETED
        logger.info(f"Session terminée: {session_id}")
    
    def clear_session(self, session_id: str) -> bool:
        """Nettoie une session spécifique"""
        try:
            # Supprimer de tous les stores
            if session_id in self._sessions:
                del self._sessions[session_id]
                self._session_stats["current_active"] -= 1
            
            if session_id in self._message_history:
                del self._message_history[session_id]
            
            if session_id in self._bloc_history:
                del self._bloc_history[session_id]
            
            if session_id in self._agent_history:
                del self._agent_history[session_id]
            
            if session_id in self._context_data:
                del self._context_data[session_id]
            
            if session_id in self._access_stats:
                del self._access_stats[session_id]
            
            self._session_stats["total_cleared"] += 1
            logger.info(f"Session nettoyée: {session_id}")
            return True
            
        except KeyError:
            logger.warning(f"Session non trouvée pour nettoyage: {session_id}")
            return False
    
    def cleanup_inactive_sessions(self, max_inactive_time: int = 1800) -> int:
        """Nettoie les sessions inactives"""
        current_time = time.time()
        sessions_to_clear = []
        
        for session_id, session in self._sessions.items():
            if current_time - session.last_activity > max_inactive_time:
                sessions_to_clear.append(session_id)
        
        cleared_count = 0
        for session_id in sessions_to_clear:
            if self.clear_session(session_id):
                cleared_count += 1
        
        if cleared_count > 0:
            logger.info(f"Sessions inactives nettoyées: {cleared_count}")
        
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du store"""
        current_time = time.time()
        
        # Calculer les sessions actives récentes
        recent_sessions = sum(
            1 for session in self._sessions.values()
            if current_time - session.last_activity < 300  # 5 minutes
        )
        
        # Trouver la session la plus accédée
        most_accessed = max(self._access_stats.items(), key=lambda x: x[1]) if self._access_stats else None
        
        stats = {
            "total_sessions": len(self._sessions),
            "recent_sessions": recent_sessions,
            "total_messages": sum(len(messages) for messages in self._message_history.values()),
            "total_contexts": len(self._context_data),
            "session_stats": self._session_stats.copy(),
            "most_accessed_session": most_accessed,
            "memory_usage": {
                "sessions": len(self._sessions),
                "message_histories": len(self._message_history),
                "bloc_histories": len(self._bloc_history),
                "agent_histories": len(self._agent_history),
                "context_data": len(self._context_data)
            }
        }
        
        return stats
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Exporte toutes les données d'une session"""
        if session_id not in self._sessions:
            return None
        
        session_data = {
            "session_info": self._sessions[session_id].to_dict(),
            "messages": [msg.to_dict() for msg in self._message_history[session_id]],
            "bloc_history": list(self._bloc_history[session_id]),
            "agent_history": list(self._agent_history[session_id]),
            "context_data": dict(self._context_data[session_id]),
            "access_count": self._access_stats.get(session_id, 0)
        }
        
        return session_data
    
    def import_session_data(self, session_id: str, data: Dict[str, Any]) -> bool:
        """Importe des données de session"""
        try:
            # Créer la session
            session_info = data["session_info"]
            session = SessionContext(**session_info)
            self._sessions[session_id] = session
            
            # Importer les messages
            for msg_data in data.get("messages", []):
                message_entry = MessageEntry(**msg_data)
                self._message_history[session_id].append(message_entry)
            
            # Importer les historiques
            for bloc_data in data.get("bloc_history", []):
                self._bloc_history[session_id].append(bloc_data)
            
            for agent_data in data.get("agent_history", []):
                self._agent_history[session_id].append(agent_data)
            
            # Importer les données de contexte
            self._context_data[session_id].update(data.get("context_data", {}))
            
            # Importer les statistiques d'accès
            if "access_count" in data:
                self._access_stats[session_id] = data["access_count"]
            
            logger.info(f"Données de session importées: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'import des données de session {session_id}: {e}")
            return False