"""
Orchestrateur V2 simplifié - JAK Company
Version sans dépendances externes pour validation rapide
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from dataclasses import dataclass

from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES, PROFILE_BLOC_MAPPING, DECISION_LOGIC

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProfileType(Enum):
    """Types de profils utilisateurs"""
    AMBASSADOR = "ambassador"
    LEARNER_INFLUENCER = "learner_influencer"
    PROSPECT = "prospect"
    UNKNOWN = "unknown"

class FinancingType(Enum):
    """Types de financement"""
    DIRECT = "direct"
    OPCO = "opco"
    CPF = "cpf"
    UNKNOWN = "unknown"

class AgentType(Enum):
    """Types d'agents spécialisés V2"""
    GENERAL = "general"
    AMBASSADOR = "ambassador"
    LEARNER = "learner"
    PROSPECT = "prospect"
    PAYMENT = "payment"
    CPF_BLOCKED = "cpf_blocked"
    QUALITY = "quality"

@dataclass
class OrchestrationResult:
    """Résultat de l'orchestration"""
    bloc_type: BlocType
    agent_type: AgentType
    bloc_id: str
    should_escalate: bool
    escalation_type: Optional[str] = None
    priority_level: str = "MEDIUM"
    profile: str = "unknown"
    financing_type: str = "unknown"
    context_data: Dict[str, Any] = None
    processing_time: float = 0.0
    
    def __post_init__(self):
        if self.context_data is None:
            self.context_data = {}

class SimpleDetectionEngine:
    """Moteur de détection simplifié sans cache"""
    
    def __init__(self):
        self._init_keyword_cache()
        self._init_priority_order()
    
    def _init_keyword_cache(self):
        """Initialise le cache des mots-clés pour optimisation"""
        self._keyword_cache = {}
        for bloc_type, config in BLOC_KEYWORDS.items():
            self._keyword_cache[bloc_type] = set(config["keywords"])
    
    def _init_priority_order(self):
        """Initialise l'ordre de priorité des blocs"""
        self._priority_order = []
        for priority_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            self._priority_order.extend(PRIORITY_RULES[priority_level])
    
    def detect_profile(self, message: str) -> ProfileType:
        """Détecte le profil de l'utilisateur"""
        message_lower = message.lower()
        
        # Détection ambassadeur
        ambassador_indicators = DECISION_LOGIC["profile_detection"]["ambassador_indicators"]
        if any(indicator in message_lower for indicator in ambassador_indicators):
            return ProfileType.AMBASSADOR
        
        # Détection apprenant/influenceur
        learner_indicators = DECISION_LOGIC["profile_detection"]["learner_indicators"]
        if any(indicator in message_lower for indicator in learner_indicators):
            return ProfileType.LEARNER_INFLUENCER
        
        # Détection prospect
        prospect_indicators = DECISION_LOGIC["profile_detection"]["prospect_indicators"]
        if any(indicator in message_lower for indicator in prospect_indicators):
            return ProfileType.PROSPECT
        
        return ProfileType.UNKNOWN
    
    def detect_financing_type(self, message: str) -> FinancingType:
        """Détecte le type de financement"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["cpf", "compte personnel formation"]):
            return FinancingType.CPF
        elif any(word in message_lower for word in ["opco", "opérateur compétences"]):
            return FinancingType.OPCO
        elif any(word in message_lower for word in ["direct", "immédiat", "maintenant"]):
            return FinancingType.DIRECT
        
        return FinancingType.UNKNOWN
    
    def detect_aggressive_behavior(self, message: str) -> bool:
        """Détecte les comportements agressifs"""
        message_lower = message.lower()
        aggressive_keywords = BLOC_KEYWORDS[BlocType.AGRO]["keywords"]
        return any(keyword in message_lower for keyword in aggressive_keywords)
    
    def detect_primary_bloc(self, message: str, session_context: Dict[str, Any] = None) -> BlocType:
        """Détecte le bloc principal selon la logique V2"""
        message_lower = message.lower()
        
        # 1. Vérification priorité absolue - Comportement agressif
        if self.detect_aggressive_behavior(message):
            logger.info("Comportement agressif détecté - BLOC AGRO")
            return BlocType.AGRO
        
        # 2. Vérification par ordre de priorité
        for bloc_type in self._priority_order:
            if bloc_type in self._keyword_cache:
                if self._has_keywords(message_lower, self._keyword_cache[bloc_type]):
                    logger.info(f"Bloc détecté: {bloc_type.value}")
                    return bloc_type
        
        # 3. Fallback vers le bloc général
        logger.info("Aucun bloc spécifique détecté - BLOC GENERAL")
        return BlocType.GENERAL
    
    def _has_keywords(self, message_lower: str, keyword_set: set) -> bool:
        """Vérifie si le message contient les mots-clés d'un bloc"""
        return any(keyword in message_lower for keyword in keyword_set)
    
    def should_escalate(self, bloc_type: BlocType, context: Dict[str, Any]) -> bool:
        """Détermine si une escalade est nécessaire"""
        escalation_rules = DECISION_LOGIC["escalation_rules"]
        
        # Escalade immédiate pour comportements critiques
        if bloc_type in [BlocType.AGRO, BlocType.LEGAL, BlocType.F1, BlocType.F3]:
            return True
        
        # Escalade pour blocs d'escalade spécifiques
        if bloc_type in [BlocType.BLOC_61, BlocType.BLOC_62]:
            return True
        
        return False
    
    def get_escalation_type(self, bloc_type: BlocType) -> str:
        """Détermine le type d'escalade"""
        if bloc_type == BlocType.BLOC_61:
            return "admin"
        elif bloc_type == BlocType.BLOC_62:
            return "commercial"
        elif bloc_type == BlocType.AGRO:
            return "quality"
        elif bloc_type in [BlocType.F1, BlocType.F3]:
            return "cpf_specialist"
        else:
            return "general"
    
    def create_response_context(self, bloc_type: BlocType, message: str, session_context: Dict[str, Any]) -> Dict[str, Any]:
        """Crée le contexte de réponse pour le bloc détecté"""
        context = {
            "bloc_type": bloc_type,
            "bloc_id": bloc_type.value,
            "message": message,
            "should_escalate": self.should_escalate(bloc_type, session_context),
            "priority_level": self._get_priority_level(bloc_type),
            "profile": self.detect_profile(message).value,
            "financing_type": self.detect_financing_type(message).value
        }
        
        # Ajouter le type d'escalade si nécessaire
        if context["should_escalate"]:
            context["escalation_type"] = self.get_escalation_type(bloc_type)
        
        return context
    
    def _get_priority_level(self, bloc_type: BlocType) -> str:
        """Retourne le niveau de priorité d'un bloc"""
        for level, blocs in PRIORITY_RULES.items():
            if bloc_type in blocs:
                return level
        return "LOW"

class SimpleMemoryStore:
    """Store de mémoire simplifié sans cachetools"""
    
    def __init__(self):
        self._sessions = {}
        self._message_history = {}
        self._bloc_history = {}
        self._agent_history = {}
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """Récupère le contexte de session"""
        return {
            "session_id": session_id,
            "last_bloc": self._bloc_history.get(session_id, [None])[-1] if session_id in self._bloc_history else None,
            "recent_blocs": self._bloc_history.get(session_id, [])[-5:],
            "last_agent": self._agent_history.get(session_id, [None])[-1] if session_id in self._agent_history else None,
            "recent_agents": self._agent_history.get(session_id, [])[-3:],
            "message_count": len(self._message_history.get(session_id, [])),
            "context_data": {}
        }
    
    def add_message(self, session_id: str, message: str, role: str = "user"):
        """Ajoute un message à l'historique"""
        if session_id not in self._message_history:
            self._message_history[session_id] = []
        self._message_history[session_id].append({
            "role": role,
            "content": message,
            "timestamp": time.time()
        })
    
    def add_bloc_presented(self, session_id: str, bloc_id: str):
        """Enregistre un bloc présenté"""
        if session_id not in self._bloc_history:
            self._bloc_history[session_id] = []
        self._bloc_history[session_id].append(bloc_id)
        if len(self._bloc_history[session_id]) > 5:
            self._bloc_history[session_id] = self._bloc_history[session_id][-5:]
    
    def add_agent_used(self, session_id: str, agent_type: str):
        """Enregistre l'agent utilisé"""
        if session_id not in self._agent_history:
            self._agent_history[session_id] = []
        self._agent_history[session_id].append(agent_type)
        if len(self._agent_history[session_id]) > 10:
            self._agent_history[session_id] = self._agent_history[session_id][-10:]

class MultiAgentOrchestratorV2Simple:
    """Orchestrateur V2 simplifié pour JAK Company"""
    
    def __init__(self):
        self.detection_engine = SimpleDetectionEngine()
        self.memory_store = SimpleMemoryStore()
        self._init_bloc_agent_mapping()
        logger.info("Orchestrateur V2 Simple initialisé")
    
    def _init_bloc_agent_mapping(self):
        """Initialise le mapping bloc -> agent"""
        self.bloc_agent_mapping = {
            # Agent Général
            BlocType.GENERAL: AgentType.GENERAL,
            BlocType.G: AgentType.GENERAL,
            
            # Agent Ambassadeur
            BlocType.B1: AgentType.AMBASSADOR,
            BlocType.B2: AgentType.AMBASSADOR,
            BlocType.D1: AgentType.AMBASSADOR,
            BlocType.D2: AgentType.AMBASSADOR,
            BlocType.E: AgentType.AMBASSADOR,
            
            # Agent Apprenant/Formation
            BlocType.K: AgentType.LEARNER,
            BlocType.M: AgentType.LEARNER,
            
            # Agent Prospect
            BlocType.H: AgentType.PROSPECT,
            BlocType.I1: AgentType.PROSPECT,
            BlocType.I2: AgentType.PROSPECT,
            
            # Agent Paiement
            BlocType.A: AgentType.PAYMENT,
            BlocType.F: AgentType.PAYMENT,
            BlocType.J: AgentType.PAYMENT,
            BlocType.L: AgentType.PAYMENT,
            
            # Agent CPF Bloqué
            BlocType.C: AgentType.CPF_BLOCKED,
            BlocType.F1: AgentType.CPF_BLOCKED,
            BlocType.F2: AgentType.CPF_BLOCKED,
            BlocType.F3: AgentType.CPF_BLOCKED,
            BlocType.BLOC_51: AgentType.CPF_BLOCKED,
            BlocType.BLOC_52: AgentType.CPF_BLOCKED,
            BlocType.BLOC_53: AgentType.CPF_BLOCKED,
            BlocType.BLOC_54: AgentType.CPF_BLOCKED,
            
            # Agent Qualité
            BlocType.AGRO: AgentType.QUALITY,
            BlocType.LEGAL: AgentType.QUALITY,
            BlocType.BLOC_61: AgentType.QUALITY,
            BlocType.BLOC_62: AgentType.QUALITY,
        }
    
    def orchestrate_sync(self, message: str, session_id: str) -> OrchestrationResult:
        """Orchestre le traitement d'un message (version synchrone)"""
        start_time = time.time()
        
        try:
            # 1. Récupérer le contexte de session
            session_context = self.memory_store.get_session_context(session_id)
            
            # 2. Ajouter le message à l'historique
            self.memory_store.add_message(session_id, message, "user")
            
            # 3. Détecter le bloc approprié
            bloc_type = self.detection_engine.detect_primary_bloc(message, session_context)
            
            # 4. Déterminer l'agent
            agent_type = self._determine_agent(bloc_type)
            
            # 5. Créer le contexte de réponse
            response_context = self.detection_engine.create_response_context(
                bloc_type, message, session_context
            )
            
            # 6. Enregistrer les informations
            self._record_orchestration_data(session_id, bloc_type, agent_type, response_context)
            
            # 7. Créer le résultat
            result = OrchestrationResult(
                bloc_type=bloc_type,
                agent_type=agent_type,
                bloc_id=bloc_type.value,
                should_escalate=response_context["should_escalate"],
                escalation_type=response_context.get("escalation_type"),
                priority_level=response_context["priority_level"],
                profile=response_context["profile"],
                financing_type=response_context["financing_type"],
                context_data=response_context,
                processing_time=time.time() - start_time
            )
            
            logger.info(f"Orchestration terminée pour session {session_id}: {bloc_type.value} -> {agent_type.value}")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'orchestration pour session {session_id}: {e}")
            # Retourner un résultat de fallback
            return OrchestrationResult(
                bloc_type=BlocType.GENERAL,
                agent_type=AgentType.GENERAL,
                bloc_id=BlocType.GENERAL.value,
                should_escalate=False,
                priority_level="LOW",
                processing_time=time.time() - start_time
            )
    
    def _determine_agent(self, bloc_type: BlocType) -> AgentType:
        """Détermine l'agent approprié pour un bloc"""
        return self.bloc_agent_mapping.get(bloc_type, AgentType.GENERAL)
    
    def _record_orchestration_data(self, session_id: str, bloc_type: BlocType, 
                                 agent_type: AgentType, context: Dict[str, Any]) -> None:
        """Enregistre les données d'orchestration"""
        
        # Enregistrer le bloc présenté
        self.memory_store.add_bloc_presented(session_id, bloc_type.value)
        
        # Enregistrer l'agent utilisé
        self.memory_store.add_agent_used(session_id, agent_type.value)
    
    def validate_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """Valide un message entrant"""
        if not message or not message.strip():
            return False, "Message vide"
        
        if len(message.strip()) < 2:
            return False, "Message trop court"
        
        if len(message) > 1000:
            return False, "Message trop long"
        
        return True, None
    
    def get_orchestration_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques d'orchestration"""
        stats = {
            "orchestrator_version": "V2-Simple",
            "detection_engine": "SimpleDetectionEngine",
            "memory_store": "SimpleMemoryStore",
            "total_blocs_mapped": len(self.bloc_agent_mapping),
            "total_agents": len(AgentType),
            "memory_stats": {
                "sessions": len(self.memory_store._sessions),
                "message_histories": len(self.memory_store._message_history),
                "bloc_histories": len(self.memory_store._bloc_history),
                "agent_histories": len(self.memory_store._agent_history)
            },
            "bloc_agent_mapping": {
                bloc.value: agent.value 
                for bloc, agent in self.bloc_agent_mapping.items()
            }
        }
        
        return stats