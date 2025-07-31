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

app = FastAPI(title="JAK Company Multi-Agents API", version="10.0-Multi-Agents")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    
    # Blocs Qualité
    BLOC_AGRO = "BLOC AGRO"
    BLOC_LEGAL = "BLOC LEGAL"
    BLOC_61 = "BLOC 6.1"
    BLOC_62 = "BLOC 6.2"
    
    FALLBACK = "FALLBACK"

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
    
    # Agent Qualité
    IntentType.BLOC_AGRO: AgentType.QUALITY,
    IntentType.BLOC_LEGAL: AgentType.QUALITY,
    IntentType.BLOC_61: AgentType.QUALITY,
    IntentType.BLOC_62: AgentType.QUALITY,
}

# ============================================================================
# STORE DE MÉMOIRE (identique)
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
            return AgentType(last_agent_value)
        return None
    
    def has_bloc_been_presented(self, session_id: str, bloc_id: str) -> bool:
        return bloc_id in self._bloc_history.get(session_id, [])
    
    def get_last_bloc(self, session_id: str) -> Optional[str]:
        history = self._bloc_history.get(session_id, [])
        return history[-1] if history else None
    
    def set_conversation_context(self, session_id: str, context_key: str, value: Any):
        self._conversation_context[session_id][context_key] = value
    
    def get_conversation_context(self, session_id: str, context_key: str, default: Any = None) -> Any:
        return self._conversation_context[session_id].get(context_key, default)
    
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
                "affiliation", "affilié", "affiliée", "programme affiliation", "mail affiliation"
            ]),
            IntentType.BLOC_B2: frozenset([
                "c'est quoi un ambassadeur", "qu'est ce qu'un ambassadeur", "définition ambassadeur"
            ]),
            IntentType.BLOC_D1: frozenset([
                "devenir ambassadeur", "comment devenir ambassadeur", "postuler ambassadeur"
            ]),
            IntentType.BLOC_K: frozenset([
                "formations disponibles", "catalogue formation", "programmes formation",
                "spécialités", "domaines formation", "c'est quoi vos formations"
            ]),
            IntentType.BLOC_AGRO: frozenset([
                "agressif", "énervé", "fâché", "colère", "insulte", "grossier", "impoli",
                "nuls", "nul", "merde", "putain", "con", "connard"
            ]),
            # ... autres blocs
        }
    
    async def determine_agent(self, message: str, session_id: str) -> Dict[str, Any]:
        """Détermine quel agent utiliser et retourne le contexte"""
        message_lower = message.lower()
        
        # 1. Détection du bloc principal
        detected_bloc = self._detect_primary_bloc(message_lower, session_id)
        
        # 2. Mapping bloc -> agent
        agent_type = BLOC_TO_AGENT_MAPPING.get(detected_bloc, AgentType.GENERAL)
        
        # 3. Création du contexte spécialisé
        context = await self._create_agent_context(detected_bloc, agent_type, message, session_id)
        
        # 4. Enregistrement de l'agent utilisé
        memory_store.add_agent_used(session_id, agent_type)
        
        return context
    
    def _detect_primary_bloc(self, message_lower: str, session_id: str) -> IntentType:
        """Détecte le bloc principal (logique existante adaptée)"""
        
        # Priorité absolue pour l'agressivité
        if self._has_keywords(message_lower, self.bloc_keywords[IntentType.BLOC_AGRO]):
            return IntentType.BLOC_AGRO
        
        # Priorité pour les définitions
        if self._has_keywords(message_lower, self.bloc_keywords[IntentType.BLOC_B2]):
            return IntentType.BLOC_B2
        
        # Priorité pour les problèmes de paiement
        if self._has_keywords(message_lower, self.bloc_keywords[IntentType.BLOC_A]):
            return IntentType.BLOC_A
        
        # Logique contextuelle basée sur l'historique
        last_agent = memory_store.get_last_agent(session_id)
        if last_agent and self._should_continue_with_agent(message_lower, last_agent):
            return self._get_continuation_bloc(last_agent, message_lower)
        
        # Détection par mots-clés pour les autres blocs
        for bloc_id, keywords in self.bloc_keywords.items():
            if self._has_keywords(message_lower, keywords):
                return bloc_id
        
        return IntentType.FALLBACK
    
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
        
        return base_context
    
    async def _create_payment_context(self, message: str, session_id: str) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent paiement"""
        financing_type = self._detect_financing_type(message.lower())
        time_info = self._extract_time_info(message.lower())
        total_days = self._convert_to_days(time_info)
        
        return {
            "financing_type": financing_type,
            "time_info": time_info,
            "total_days": total_days,
            "priority_level": "HIGH" if total_days > 45 else "MEDIUM",
            "should_escalade": total_days > 90
        }
    
    def _create_ambassador_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent ambassadeur"""
        return {
            "priority_level": "HIGH",
            "context_needed": ["ambassadeur", "affiliation", "processus"],
            "specialized_instructions": "Focus sur les 4 étapes pour devenir ambassadeur"
        }
    
    def _create_quality_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent qualité"""
        is_aggressive = bloc_id == IntentType.BLOC_AGRO
        needs_escalation = bloc_id in [IntentType.BLOC_61, IntentType.BLOC_62]
        
        return {
            "priority_level": "CRITICAL" if is_aggressive else "HIGH",
            "should_escalade": needs_escalation,
            "specialized_instructions": "Gestion ferme mais bienveillante" if is_aggressive else "Escalade appropriée"
        }
    
    def _create_cpf_context(self, bloc_id: IntentType) -> Dict[str, Any]:
        """Contexte spécialisé pour l'agent CPF"""
        return {
            "priority_level": "CRITICAL",
            "context_needed": ["cpf", "blocage", "filtrage"],
            "specialized_instructions": "Questions de filtrage avant solution complète"
        }
    
    def _detect_financing_type(self, message_lower: str):
        """Détecte le type de financement (logique existante)"""
        if any(word in message_lower for word in ["cpf", "compte personnel formation"]):
            return "cpf"
        elif any(word in message_lower for word in ["opco", "opérateur compétences"]):
            return "opco"
        return "unknown"
    
    def _extract_time_info(self, message_lower: str) -> Dict:
        """Extrait les informations temporelles (logique existante)"""
        time_patterns = {
            "jours": r"(\d+)\s*jour",
            "semaines": r"(\d+)\s*semaine", 
            "mois": r"(\d+)\s*mois"
        }
        
        time_info = {}
        for unit, pattern in time_patterns.items():
            match = re.search(pattern, message_lower)
            if match:
                time_info[unit] = int(match.group(1))
        
        return time_info
    
    def _convert_to_days(self, time_info: Dict) -> int:
        """Convertit en jours (logique existante)"""
        total_days = 0
        if "jours" in time_info:
            total_days += time_info["jours"]
        if "semaines" in time_info:
            total_days += time_info["semaines"] * 7
        if "mois" in time_info:
            total_days += time_info["mois"] * 30
        return total_days

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
        "version": "10.0",
        "status": "active",
        "architecture": "Multi-Agents Specialized",
        "agents": [agent.value for agent in AgentType],
        "features": [
            "Agent routing by specialization",
            "Context-aware decision making",
            "Agent continuity tracking",
            "Specialized prompts per domain",
            "Enhanced memory management"
        ],
        "endpoints": {
            "POST /orchestrator": "Determine which agent to use",
            "GET /health": "Health check", 
            "GET /agents": "List available agents",
            "POST /clear_memory/{session_id}": "Clear session memory"
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
        AgentType.GENERAL: "Accueil et orientation générale",
        AgentType.AMBASSADOR: "Programme ambassadeur et affiliation", 
        AgentType.LEARNER: "Formations et apprentissage",
        AgentType.PROSPECT: "Devis et qualification prospects",
        AgentType.PAYMENT: "Suivi des paiements et factures",
        AgentType.CPF_BLOCKED: "Déblocage CPF et OPCO",
        AgentType.QUALITY: "Contrôle qualité et escalades"
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
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": "10.0-Multi-Agents",
            "memory_stats": memory_stats,
            "agents_available": len(AgentType),
            "orchestrator": "operational"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

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
# POINT D'ENTRÉE PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)