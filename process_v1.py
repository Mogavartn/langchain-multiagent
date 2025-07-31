import os
import logging
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import re
from dataclasses import dataclass
import traceback
from functools import lru_cache
from cachetools import TTLCache
import time
from collections import defaultdict
from enum import Enum

# Configuration optimisée du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="JAK Company Multi-Agents API", version="10.0-Multi-Agents-Fixed")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vérification de la clé OpenAI
openai_key = os.getenv("OPENAI_API_KEY")
if not openai_key:
    logger.warning("OpenAI API Key not found - some features may not work")
else:
    os.environ["OPENAI_API_KEY"] = openai_key
    logger.info("OpenAI API Key configured")

# ============================================================================
# ENUMS ET CONSTANTES MULTI-AGENTS
# ============================================================================

class AgentType(Enum):
    """Types d'agents spécialisés"""
    GENERAL = "general"
    AMBASSADOR = "ambassador"
    LEARNER = "learner"
    PROSPECT = "prospect"
    PAYMENT = "payment"
    CPF_BLOCKED = "cpf_blocked"
    QUALITY = "quality"

class IntentType(Enum):
    """Types d'intentions détectées par bloc"""
    # Blocs Généraux
    BLOC_GENERAL = "BLOC GENERAL"
    BLOC_G = "BLOC G"
    
    # Blocs Ambassadeur
    BLOC_B1 = "BLOC B.1"
    BLOC_B2 = "BLOC B.2"
    BLOC_D1 = "BLOC D.1"
    BLOC_D2 = "BLOC D.2"
    BLOC_E = "BLOC E"
    
    # Blocs Apprenant/Formation
    BLOC_K = "BLOC K"
    BLOC_M = "BLOC M"
    
    # Blocs Prospect
    BLOC_H = "BLOC H"
    BLOC_I1 = "BLOC I1"
    BLOC_I2 = "BLOC I2"
    
    # Blocs Paiement
    BLOC_A = "BLOC A"
    BLOC_F = "BLOC F"
    BLOC_J = "BLOC J"
    BLOC_L = "BLOC L"
    
    # Blocs CPF/OPCO
    BLOC_C = "BLOC C"
    BLOC_F1 = "BLOC F1"
    BLOC_F2 = "BLOC F2"
    BLOC_F3 = "BLOC F3"
    BLOC_51 = "BLOC 5.1"
    BLOC_52 = "BLOC 5.2"
    BLOC_53 = "BLOC 5.3"
    BLOC_54 = "BLOC 5.4"
    
    # Blocs Qualité
    BLOC_AGRO = "BLOC AGRO"
    BLOC_LEGAL = "BLOC LEGAL"
    BLOC_61 = "BLOC 6.1"
    BLOC_62 = "BLOC 6.2"
    
    FALLBACK = "FALLBACK"

class FinancingType(Enum):
    """Types de financement"""
    DIRECT = "direct"
    OPCO = "opco"
    CPF = "cpf"
    UNKNOWN = "unknown"

# ============================================================================
# MAPPING BLOCS -> AGENTS
# ============================================================================

BLOC_TO_AGENT_MAPPING = {
    # Agent Général
    IntentType.BLOC_GENERAL: AgentType.GENERAL,
    IntentType.BLOC_G: AgentType.GENERAL,
    
    # Agent Ambassadeur
    IntentType.BLOC_B1: AgentType.AMBASSADOR,
    IntentType.BLOC_B2: AgentType.AMBASSADOR,
    IntentType.BLOC_D1: AgentType.AMBASSADOR,
    IntentType.BLOC_D2: AgentType.AMBASSADOR,
    IntentType.BLOC_E: AgentType.AMBASSADOR,
    
    # Agent Apprenant/Formation
    IntentType.BLOC_K: AgentType.LEARNER,
    IntentType.BLOC_M: AgentType.LEARNER,
    
    # Agent Prospect
    IntentType.BLOC_H: AgentType.PROSPECT,
    IntentType.BLOC_I1: AgentType.PROSPECT,
    IntentType.BLOC_I2: AgentType.PROSPECT,
    
    # Agent Paiement
    IntentType.BLOC_A: AgentType.PAYMENT,
    IntentType.BLOC_F: AgentType.PAYMENT,
    IntentType.BLOC_J: AgentType.PAYMENT,
    IntentType.BLOC_L: AgentType.PAYMENT,
    
    # Agent CPF Bloqué
    IntentType.BLOC_C: AgentType.CPF_BLOCKED,
    IntentType.BLOC_F1: AgentType.CPF_BLOCKED,
    IntentType.BLOC_F2: AgentType.CPF_BLOCKED,
    IntentType.BLOC_F3: AgentType.CPF_BLOCKED,
    IntentType.BLOC_51: AgentType.CPF_BLOCKED,
    IntentType.BLOC_52: AgentType.CPF_BLOCKED,
    IntentType.BLOC_53: AgentType.CPF_BLOCKED,
    IntentType.BLOC_54: AgentType.CPF_BLOCKED,
    
    # Agent Qualité
    IntentType.BLOC_AGRO: AgentType.QUALITY,
    IntentType.BLOC_LEGAL: AgentType.QUALITY,
    IntentType.BLOC_61: AgentType.QUALITY,
    IntentType.BLOC_62: AgentType.QUALITY,
}

# ============================================================================
# STORE DE MÉMOIRE MULTI-AGENTS
# ============================================================================

class OptimizedMemoryStoreV8:
    """Store de mémoire optimisé - Version 8 Multi-Agents"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self._store = TTLCache(maxsize=max_size, ttl=ttl_seconds)
        self._access_count = defaultdict(int)
        self._bloc_history = defaultdict(list)
        self._conversation_context = defaultdict(dict)
        self._last_response = defaultdict(str)
        self._agent_history = defaultdict(list)  # NOUVEAU : Historique des agents utilisés
    
    def get(self, key: str) -> List[Dict]:
        self._access_count[key] += 1
        return self._store.get(key, [])
    
    def set(self, key: str, value: List[Dict]):
        if len(value) > 10:
            value = value[-10:]
        self._store[key] = value
    
    def add_message(self, session_id: str, message: str, role: str = "user"):
        messages = self.get(session_id)
        messages.append({"role": role, "content": message, "timestamp": time.time()})
        self.set(session_id, messages)
    
    def add_bloc_presented(self, session_id: str, bloc_id: str):
        if session_id not in self._bloc_history:
            self._bloc_history[session_id] = []
        self._bloc_history[session_id].append(bloc_id)
        if len(self._bloc_history[session_id]) > 5:
            self._bloc_history[session_id] = self._bloc_history[session_id][-5:]
    
    def add_agent_used(self, session_id: str, agent_type: AgentType):
        """NOUVEAU : Enregistre l'agent utilisé"""
        if session_id not in self._agent_history:
            self._agent_history[session_id] = []
        self._agent_history[session_id].append({
            "agent": agent_type.value,
            "timestamp": time.time()
        })
        if len(self._agent_history[session_id]) > 10:
            self._agent_history[session_id] = self._agent_history[session_id][-10:]
    
    def get_last_agent(self, session_id: str) -> Optional[AgentType]:
        """NOUVEAU : Récupère le dernier agent utilisé"""
        history = self._agent_history.get(session_id, [])
        if history:
            last_agent_value = history[-1]["agent"]
            try:
                return AgentType(last_agent_value)
            except ValueError:
                return None
        return None
    
    def has_bloc_been_presented(self, session_id: str, bloc_id: str) -> bool:
        return bloc_id in self._bloc_history.get(session_id, [])
    
    def get_last_bloc(self, session_id: str) -> Optional[str]:
        history = self._bloc_history.get(session_id, [])
        return history[-1] if history else None
    
    def get_last_n_blocs(self, session_id: str, n: int = 3) -> List[str]:
        """Récupère les n derniers blocs présentés"""
        history = self._bloc_history.get(session_id, [])
        return history[-n:] if len(history) >= n else history
    
    def set_conversation_context(self, session_id: str, context_key: str, value: Any):
        self._conversation_context[session_id][context_key] = value
    
    def get_conversation_context(self, session_id: str, context_key: str, default: Any = None) -> Any:
        return self._conversation_context[session_id].get(context_key, default)
    
    def set_payment_context(self, session_id: str, financing_type: str, time_info: Dict, total_days: int):
        """Sauvegarde le contexte de paiement pour une session"""
        payment_context = {
            "financing_type": financing_type,
            "time_info": time_info,
            "total_days": total_days,
            "timestamp": time.time()
        }
        self.set_conversation_context(session_id, "payment_context", payment_context)
    
    def get_payment_context(self, session_id: str) -> Optional[Dict]:
        """Récupère le contexte de paiement pour une session"""
        return self.get_conversation_context(session_id, "payment_context", None)
    
    def clear(self, session_id: str):
        if session_id in self._store:
            del self._store[session_id]
        if session_id in self._bloc_history:
            del self._bloc_history[session_id]
        if session_id in self._conversation_context:
            del self._conversation_context[session_id]
        if session_id in self._last_response:
            del self._last_response[session_id]
        if session_id in self._agent_history:
            del self._agent_history[session_id]
    
    def get_stats(self) -> Dict:
        return {
            "total_sessions": len(self._store),
            "total_bloc_history": len(self._bloc_history),
            "total_agent_history": len(self._agent_history),
            "total_contexts": len(self._conversation_context),
            "most_accessed": max(self._access_count.items(), key=lambda x: x[1]) if self._access_count else None
        }

# Instance globale du store de mémoire
memory_store = OptimizedMemoryStoreV8()

# ============================================================================
# MOTEUR DE DÉTECTION SUPABASE
# ============================================================================

class SupabaseDrivenDetectionEngineV8:
    """Moteur de détection basé sur les blocs Supabase - Version 8 Multi-Agents"""
    
    def __init__(self):
        # Cette classe contient les méthodes utilitaires de détection
        pass
    
    @lru_cache(maxsize=50)
    def detect_financing_type(self, message_lower: str) -> FinancingType:
        """Détecte le type de financement"""
        if any(word in message_lower for word in ["cpf", "compte personnel formation"]):
            return FinancingType.CPF
        elif any(word in message_lower for word in ["opco", "opérateur compétences"]):
            return FinancingType.OPCO
        elif any(word in message_lower for word in ["direct", "immédiat", "maintenant"]):
            return FinancingType.DIRECT
        return FinancingType.UNKNOWN
    
    @lru_cache(maxsize=50)
    def extract_time_info(self, message_lower: str) -> Dict:
        """Extrait les informations temporelles"""
        time_patterns = {
            "jours": r"(\d+)\s*jour",
            "semaines": r"(\d+)\s*semaine",
            "mois": r"(\d+)\s*mois",
            "années": r"(\d+)\s*année"
        }
        
        time_info = {}
        for unit, pattern in time_patterns.items():
            match = re.search(pattern, message_lower)
            if match:
                time_info[unit] = int(match.group(1))
        
        return time_info
    
    def convert_to_days(self, time_info: Dict) -> int:
        """Convertit les informations temporelles en jours"""
        total_days = 0
        if "jours" in time_info:
            total_days += time_info["jours"]
        if "semaines" in time_info:
            total_days += time_info["semaines"] * 7
        if "mois" in time_info:
            total_days += time_info["mois"] * 30
        if "années" in time_info:
            total_days += time_info["années"] * 365
        return total_days
    
    def detect_formation_interest(self, message_lower: str, session_id: str) -> bool:
        """Détecte si l'utilisateur exprime un intérêt pour une formation spécifique"""
        interest_indicators = [
            "intéressé par", "je choisis", "je veux", "m'intéresse", 
            "ça m'intéresse", "je prends", "je sélectionne", "je souhaite",
            "je voudrais"
        ]
    
        formation_keywords = [
            "comptabilité", "marketing", "langues", "web", "3d", "vente", 
            "développement", "bureautique", "informatique", "écologie", "bilan",
            "anglais", "français", "espagnol", "allemand", "italien"
        ]
    
        has_interest = any(indicator in message_lower for indicator in interest_indicators)
        has_formation = any(keyword in message_lower for keyword in formation_keywords)
    
        # Vérifier si l'utilisateur a récemment vu les formations
        last_blocs = memory_store.get_last_n_blocs(session_id, 3)
        formations_recently_shown = any("BLOC K" in bloc for bloc in last_blocs)
    
        return has_interest and has_formation and formations_recently_shown

    def detect_aggressive_behavior(self, message_lower: str) -> bool:
        """Détecte les comportements agressifs"""
        aggressive_indicators = [
            "nuls", "nul", "merde", "putain", "con", "connard", "salop", "salope",
            "dégage", "va te faire", "ta gueule", "ferme ta gueule", "imbécile",
            "idiot", "stupide", "incompétent", "inutile"
        ]
        
        return any(indicator in message_lower for indicator in aggressive_indicators)

# ============================================================================
# ORCHESTRATEUR MULTI-AGENTS
# ============================================================================

class MultiAgentOrchestrator:
    """Orchestrateur qui détermine quel agent utiliser"""
    
    def __init__(self):
        self._init_bloc_keywords()
        self.detection_engine = SupabaseDrivenDetectionEngineV8()
    
    def _init_bloc_keywords(self):
        """Initialise les mots-clés par bloc (logique existante)"""
        self.bloc_keywords = {
            IntentType.BLOC_A: frozenset([
                "paiement", "payé", "payée", "payer", "argent", "facture", "débit", "prélèvement",
                "virement", "chèque", "carte bancaire", "cb", "mastercard", "visa", "pas été payé"
            ]),
            IntentType.BLOC_B1: frozenset([
                "affiliation", "affilié", "affiliée", "programme affiliation", "mail affiliation",
                "email affiliation", "courriel affiliation"
            ]),
            IntentType.BLOC_B2: frozenset([
                "c'est quoi un ambassadeur", "qu'est ce qu'un ambassadeur", "définition ambassadeur",
                "ambassadeur définition", "expliquer ambassadeur"
            ]),
            IntentType.BLOC_C: frozenset([
                "cpf", "compte personnel formation", "formation cpf", "financement cpf",
                "droit formation", "mon compte formation"
            ]),
            IntentType.BLOC_D1: frozenset([
                "devenir ambassadeur", "comment devenir ambassadeur", "postuler ambassadeur",
                "candidature ambassadeur", "rejoindre ambassadeur"
            ]),
            IntentType.BLOC_D2: frozenset([
                "c'est quoi un ambassadeur", "qu'est ce qu'un ambassadeur", "définition ambassadeur"
            ]),
            IntentType.BLOC_E: frozenset([
                "processus ambassadeur", "étapes ambassadeur", "comment ça marche ambassadeur",
                "procédure ambassadeur"
            ]),
            IntentType.BLOC_F: frozenset([
                "paiement formation", "payé formation", "facture formation", "débit formation"
            ]),
            IntentType.BLOC_F1: frozenset([
                "cpf bloqué", "dossier bloqué", "blocage cpf", "problème cpf", "délai cpf"
            ]),
            IntentType.BLOC_F2: frozenset([
                "cpf dossier bloqué", "blocage dossier cpf", "problème dossier cpf"
            ]),
            IntentType.BLOC_F3: frozenset([
                "opco", "opérateur compétences", "délai opco", "blocage opco", "problème opco"
            ]),
            IntentType.BLOC_G: frozenset([
                "parler humain", "contacter humain", "appeler", "téléphoner", "conseiller",
                "assistant", "aide humaine"
            ]),
            IntentType.BLOC_H: frozenset([
                "prospect", "devis", "tarif", "prix", "coût", "formation", "programme",
                "offre", "catalogue"
            ]),
            IntentType.BLOC_I1: frozenset([
                "entreprise", "société", "professionnel", "auto-entrepreneur", "salarié"
            ]),
            IntentType.BLOC_I2: frozenset([
                "ambassadeur vendeur", "vendeur", "commercial", "vente"
            ]),
            IntentType.BLOC_J: frozenset([
                "paiement direct", "paiement immédiat", "payer maintenant"
            ]),
            IntentType.BLOC_K: frozenset([
                "formations disponibles", "catalogue formation", "programmes formation",
                "spécialités", "domaines formation", "c'est quoi vos formations", "quelles sont vos formations"
            ]),
            IntentType.BLOC_L: frozenset([
                "délai dépassé", "retard paiement", "paiement en retard", "délai expiré"
            ]),
            IntentType.BLOC_M: frozenset([
                "après choix", "formation choisie", "inscription", "confirmation", "intéressé par",
                "je voudrais", "je veux", "je choisis", "m'intéresse"
            ]),
            IntentType.BLOC_LEGAL: frozenset([
                "légal", "droit", "juridique", "avocat", "procédure", "recours"
            ]),
            IntentType.BLOC_AGRO: frozenset([
                "agressif", "énervé", "fâché", "colère", "insulte", "grossier", "impoli",
                "nuls", "nul", "merde", "putain", "con", "connard", "salop", "salope"
            ]),
            IntentType.BLOC_GENERAL: frozenset([
                "bonjour", "salut", "hello", "qui êtes-vous", "jak company", "présentation"
            ]),
            IntentType.BLOC_51: frozenset([
                "cpf dossier bloqué", "blocage administratif", "délai administratif"
            ]),
            IntentType.BLOC_52: frozenset([
                "relance", "suivi", "nouvelle", "après escalade"
            ]),
            IntentType.BLOC_53: frozenset([
                "seuils fiscaux", "micro-entreprise", "fiscal", "impôts"
            ]),
            IntentType.BLOC_54: frozenset([
                "sans réseaux sociaux", "pas de réseaux", "pas instagram", "pas snapchat"
            ]),
            IntentType.BLOC_61: frozenset([
                "escalade admin", "administrateur", "responsable", "manager"
            ]),
            IntentType.BLOC_62: frozenset([
                "escalade co", "commercial", "vendeur", "conseiller"
            ])
        }
    
    async def determine_agent(self, message: str, session_id: str) -> Dict[str, Any]:
        """Détermine quel agent utiliser et retourne le contexte"""
        message_lower = message.lower()
        
        # 1. Vérifier d'abord le contexte conversationnel
        follow_up_bloc = self._detect_follow_up_context(message_lower, session_id)
        if follow_up_bloc:
            detected_bloc = follow_up_bloc
            logger.info(f"Contexte conversationnel détecté: {follow_up_bloc.value} pour session {session_id}")
        else:
            # 2. Détection du bloc principal
            detected_bloc = self._detect_primary_bloc(message_lower, session_id)
        
        # 3. Mapping bloc -> agent
        agent_type = BLOC_TO_AGENT_MAPPING.get(detected_bloc, AgentType.GENERAL)
        
        # 4. Création du contexte spécialisé
        context = await self._create_agent_context(detected_bloc, agent_type, message, session_id)
        
        # 5. Enregistrement de l'agent utilisé
        memory_store.add_agent_used(session_id, agent_type)
        
        return context
    
    def _detect_follow_up_context(self, message_lower: str, session_id: str) -> Optional[IntentType]:
        """Détecte les messages de suivi basés sur le contexte conversationnel"""
        
        # Récupérer le contexte récent
        last_bloc = memory_store.get_last_bloc(session_id)
        last_blocs = memory_store.get_last_n_blocs(session_id, 3)
        
        # Détection d'agressivité prioritaire
        if self.detection_engine.detect_aggressive_behavior(message_lower):
            return IntentType.BLOC_AGRO
        
        # Si l'utilisateur a vu les formations et exprime un intérêt
        if self.detection_engine.detect_formation_interest(message_lower, session_id):
            return IntentType.BLOC_M
        
        # Si l'utilisateur vient de voir les ambassadeurs et pose des questions
        if last_bloc in ["BLOC D.1", "BLOC D.2"] and any(word in message_lower for word in ["comment", "quand", "où", "combien"]):
            return IntentType.BLOC_E  # Processus ambassadeur
        
        # Si l'utilisateur vient de voir un problème de paiement et donne plus d'infos
        if last_bloc == "BLOC A" and any(word in message_lower for word in ["depuis", "ça fait", "délai", "attendre"]):
            return IntentType.BLOC_L  # Délai dépassé
        
        # Si l'utilisateur répond à une question de filtrage CPF
        if last_bloc == "BLOC F1" and any(word in message_lower for word in ["oui", "non", "bloqué", "informé"]):
            return IntentType.BLOC_F2  # Suite du processus CPF
        
        # Si l'utilisateur répond à une question de filtrage OPCO
        if last_bloc == "BLOC F3" and any(word in message_lower for word in ["oui", "non", "bloqué", "informé"]):
            return IntentType.BLOC_F2  # Suite du processus OPCO
        
        return None
    
    def _detect_primary_bloc(self, message_lower: str, session_id: str) -> IntentType:
        """Détecte le bloc principal selon la logique Supabase"""
        
        # Priorité absolue pour l'agressivité
        if self.detection_engine.detect_aggressive_behavior(message_lower):
            return IntentType.BLOC_AGRO
        
        # Priorité absolue pour les définitions
        if self._has_keywords(message_lower, self.bloc_keywords[IntentType.BLOC_B2]):
            return IntentType.BLOC_B2
        
        # Priorité pour les problèmes de paiement
        if self._has_keywords(message_lower, self.bloc_keywords[IntentType.BLOC_A]):
            return IntentType.BLOC_A
        
        # Vérification de tous les blocs par ordre de priorité
        priority_order = [
            IntentType.BLOC_F1, IntentType.BLOC_F2, IntentType.BLOC_F3,  # Paiements spéciaux
            IntentType.BLOC_C, IntentType.BLOC_D1, IntentType.BLOC_D2,  # CPF et Ambassadeurs
            IntentType.BLOC_G, IntentType.BLOC_H, IntentType.BLOC_K,    # Contact et Formations
            IntentType.BLOC_LEGAL, IntentType.BLOC_AGRO,                # Légal et Agressivité
            IntentType.BLOC_61, IntentType.BLOC_62,                     # Escalades
            IntentType.BLOC_GENERAL                                      # Général
        ]
        
        for bloc_id in priority_order:
            if bloc_id in self.bloc_keywords and self._has_keywords(message_lower, self.bloc_keywords[bloc_id]):
                return bloc_id
        
        return IntentType.FALLBACK
    
    @lru_cache(maxsize=100)
    def _has_keywords(self, message_lower: str, keyword_set: frozenset) -> bool:
        """Vérifie si le message contient les mots-clés d'un bloc"""
        return any(keyword in message_lower for keyword in keyword_set)
    
    def _should_continue_with_agent(self, message_lower: str, last_agent: AgentType) -> bool:
        """Détermine si on doit continuer avec le même agent"""
        continuation_indicators = ["oui", "non", "ok", "d'accord", "merci", "et", "aussi", "comment"]
        return any(indicator in message_lower for indicator in continuation_indicators)
    
    def _get_continuation_bloc(self, agent_type: AgentType, message_lower: str) -> IntentType:
        """Retourne le bloc de continuation pour un agent"""
        agent_continuation_map = {
            AgentType.AMBASSADOR: IntentType.BLOC_E,  # Processus ambassadeur
            AgentType.LEARNER: IntentType.BLOC_M,     # Formation choisie
            AgentType.PAYMENT: IntentType.BLOC_L,     # Délai dépassé
            AgentType.CPF_BLOCKED: IntentType.BLOC_F2 # Suite CPF
        }
        return agent_continuation_map.get(agent_type, IntentType.BLOC_GENERAL)
    
    async def _create_agent_context(self, bloc_id: IntentType, agent_type: AgentType, message: str, session_id: str) -> Dict[str, Any]:
        """Crée le contexte spécialisé pour chaque agent"""
        
        base_context = {
            "status": "success",
            "session_id": session_id,
            "agent_type": agent_type.value,
            "bloc_id": bloc_id.value,
            "search_query": f"{bloc_id.value.lower()} {message[:50]}",
            "context_needed": [bloc_id.value.lower()],
            "priority_level": "MEDIUM",
            "should_escalade": False,
            "message": message,
            "timestamp": time.time()
        }
        
        # Contexte spécialisé par agent
        if agent_type == AgentType.PAYMENT:
            base_context.update(await self._create_payment_context(message, session_id))
        elif agent_type == AgentType.AMBASSADOR:
            base_context.update(self._create_ambassador_context(bloc_id))
        elif agent_type == AgentType.QUALITY:
            base_context.update(self._create_quality_context(bloc_id))
        elif agent_type == AgentType.CPF_BLOCKED:
            base_context.update(self._create_cpf_context(bloc_id))
        elif agent_type == AgentType.LEARNER:
            base_context.update(self._create_learner_context(bloc_id))
        elif agent_type == AgentType.PROSPECT:
            base_context.update(self._create_prospect_context(bloc_id))
        
        return base_context
    
    async def _create_payment_context(self, message: str, session_id: str) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent paiement"""
        financing_type = self.detection_engine.detect_financing_type(message.lower())
        time_info = self.detection_engine.extract_time_info(message.lower())
        total_days = self.detection_engine.convert_to_days(time_info)
        
        # Sauvegarder le contexte de paiement
        memory_store.set_payment_context(session_id, financing_type.value, time_info, total_days)
        
        return {
            "financing_type": financing_type.value,
            "time_info": time_info,
            "total_days": total_days,
            "priority_level": "CRITICAL" if total_days > 90 else "HIGH" if total_days > 45 else "MEDIUM",
            "should_escalade": total_days > 90,
            "specialized_instructions": f"Gestion paiement {financing_type.value} - Délai: {total_days} jours"
        }
    
    def _create_ambassador_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent ambassadeur"""
        return {
            "priority_level": "HIGH",
            "context_needed": ["ambassadeur", "affiliation", "processus"],
            "specialized_instructions": "Focus sur les 4 étapes pour devenir ambassadeur JAK Company"
        }
    
    def _create_learner_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent apprenant/formation"""
        return {
            "priority_level": "HIGH",
            "context_needed": ["formation", "catalogue", "inscription"],
            "specialized_instructions": "Présentation complète du catalogue de formations JAK Company"
        }
    
    def _create_prospect_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent prospect"""
        return {
            "priority_level": "HIGH",
            "context_needed": ["prospect", "devis", "qualification"],
            "specialized_instructions": "Qualification prospect et orientation commerciale appropriée"
        }
    
    def _create_quality_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent qualité"""
        is_aggressive = bloc_id == IntentType.BLOC_AGRO
        needs_escalation = bloc_id in [IntentType.BLOC_61, IntentType.BLOC_62]
        
        return {
            "priority_level": "CRITICAL" if is_aggressive else "HIGH",
            "should_escalade": needs_escalation,
            "specialized_instructions": "Gestion ferme mais bienveillante" if is_aggressive else "Escalade appropriée vers conseiller humain"
        }
    
    def _create_cpf_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent CPF"""
        return {
            "priority_level": "CRITICAL",
            "context_needed": ["cpf", "blocage", "filtrage", "opco"],
            "specialized_instructions": "Questions de filtrage avant solution complète - Processus de déblocage étape par étape"
        }

# Instance globale de l'orchestrateur
orchestrator = MultiAgentOrchestrator()

# ============================================================================
# ENDPOINTS API MULTI-AGENTS
# ============================================================================

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API Multi-Agents"""
    return {
        "message": "JAK Company Multi-Agents API",
        "version": "10.0-Fixed",
        "status": "active",
        "architecture": "Multi-Agents Specialized",
        "agents": [agent.value for agent in AgentType],
        "features": [
            "Agent routing by specialization",
            "Context-aware decision making",
            "Agent continuity tracking",
            "Specialized prompts per domain",
            "Enhanced memory management",
            "Payment context filtering",
            "Aggressive behavior detection"
        ],
        "endpoints": {
            "POST /orchestrator": "Determine which agent to use",
            "GET /health": "Health check", 
            "GET /agents": "List available agents",
            "POST /clear_memory/{session_id}": "Clear session memory",
            "GET /memory_status": "Memory store statistics"
        }
    }

@app.get("/agents")
async def list_agents():
    """Liste des agents disponibles"""
    return {
        "agents": [
            {
                "type": agent.value,
                "name": agent.name,
                "specialization": _get_agent_specialization(agent)
            }
            for agent in AgentType
        ]
    }

def _get_agent_specialization(agent: AgentType) -> str:
    """Retourne la spécialisation de chaque agent"""
    specializations = {
        AgentType.GENERAL: "Accueil et orientation générale JAK Company",
        AgentType.AMBASSADOR: "Programme ambassadeur et processus d'affiliation", 
        AgentType.LEARNER: "Catalogue formations et processus d'inscription",
        AgentType.PROSPECT: "Qualification prospects et devis commerciaux",
        AgentType.PAYMENT: "Suivi paiements, factures et délais",
        AgentType.CPF_BLOCKED: "Déblocage dossiers CPF et OPCO",
        AgentType.QUALITY: "Contrôle qualité, escalades et gestion conflits"
    }
    return specializations.get(agent, "Spécialisation non définie")

@app.post("/orchestrator")
async def orchestrate_agents(request: Request):
    """Endpoint principal pour l'orchestration multi-agents"""
    start_time = time.time()
    
    try:
        # Récupération des données
        body = await request.json()
        message = body.get("message", "").strip()
        session_id = body.get("session_id", "default_session")
        
        if not message:
            return {
                "status": "error",
                "message": "Message is required",
                "session_id": session_id,
                "processing_time": round(time.time() - start_time, 3)
            }
        
        # Ajout du message à la mémoire
        memory_store.add_message(session_id, message, "user")
        
        # Détermination de l'agent et création du contexte
        agent_context = await orchestrator.determine_agent(message, session_id)
        
        # Ajout du temps de traitement
        agent_context["processing_time"] = round(time.time() - start_time, 3)
        
        logger.info(f"Agent selected for session {session_id}: {agent_context['agent_type']} -> {agent_context['bloc_id']}")
        
        return agent_context
        
    except Exception as e:
        logger.error(f"Error in orchestrator: {e}")
        logger.error(traceback.format_exc())
        return {
            "status": "error",
            "message": str(e),
            "session_id": session_id,
            "processing_time": round(time.time() - start_time, 3)
        }

@app.get("/health")
async def health_check():
    """Vérification de santé de l'API Multi-Agents"""
    try:
        memory_stats = memory_store.get_stats()
        
        checks = {
            "api_status": "healthy",
            "memory_store": "operational",
            "orchestrator": "ready",
            "detection_engine": "ready",
            "openai_key": "configured" if openai_key else "missing"
        }
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "10.0-Multi-Agents-Fixed",
            "checks": checks,
            "memory_stats": memory_stats,
            "agents_available": len(AgentType),
            "blocs_mapped": len(BLOC_TO_AGENT_MAPPING)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/memory_status")
async def memory_status():
    """Retourne les statistiques du store de mémoire"""
    try:
        stats = memory_store.get_stats()
        return {
            "status": "success",
            "memory_stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting memory status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get memory status: {str(e)}")

@app.post("/clear_memory/{session_id}")
async def clear_memory(session_id: str):
    """Nettoie la mémoire d'une session spécifique"""
    try:
        memory_store.clear(session_id)
        return {
            "status": "success",
            "message": f"Memory cleared for session {session_id}",
            "session_id": session_id,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error clearing memory: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear memory: {str(e)}")

# ============================================================================
# ENDPOINT DE COMPATIBILITÉ AVEC L'ANCIEN SYSTÈME
# ============================================================================

@app.post("/optimize_rag")
async def optimize_rag_compatibility(request: Request):
    """Endpoint de compatibilité avec l'ancien système - redirige vers orchestrator"""
    logger.info("Legacy endpoint /optimize_rag called - redirecting to orchestrator")
    return await orchestrate_agents(request)

# ============================================================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)