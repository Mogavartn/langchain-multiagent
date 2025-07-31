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

# Import des composants modulaires V2
from bloc_config_v2 import BlocType, BLOC_KEYWORDS, PRIORITY_RULES, PROFILE_BLOC_MAPPING, DECISION_LOGIC
from detection_engine_v2 import DetectionEngineV2, ProfileType, FinancingType
from memory_store_v2 import OptimizedMemoryStoreV2
from orchestrator_v2 import MultiAgentOrchestratorV2, AgentType, OrchestrationResult

# Configuration optimisée du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(title="JAK Company Multi-Agents API V2", version="2.0-Optimized")

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
# INSTANCES GLOBALES V2
# ============================================================================

# Instance globale du store de mémoire
memory_store = OptimizedMemoryStoreV2()

# Instance globale du moteur de détection
detection_engine = DetectionEngineV2()

# Instance globale de l'orchestrateur
orchestrator = MultiAgentOrchestratorV2()

# ============================================================================
# MAPPING BLOCS -> AGENTS (pour compatibilité)
# ============================================================================

BLOC_TO_AGENT_MAPPING = {
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

# ============================================================================
# ENDPOINTS API V2
# ============================================================================

@app.get("/")
async def root():
    """Endpoint racine avec informations sur l'API Multi-Agents V2"""
    return {
        "message": "JAK Company Multi-Agents API V2",
        "version": "2.0-Optimized",
        "status": "active",
        "architecture": "Multi-Agents Modular V2",
        "agents": [agent.value for agent in AgentType],
        "features": [
            "Agent routing by specialization",
            "Context-aware decision making",
            "Agent continuity tracking",
            "Specialized prompts per domain",
            "Enhanced memory management",
            "Payment context filtering",
            "Aggressive behavior detection",
            "Modular architecture",
            "Optimized performance",
            "Comprehensive testing"
        ],
        "endpoints": {
            "POST /orchestrator": "Determine which agent to use",
            "GET /health": "Health check", 
            "GET /agents": "List available agents",
            "POST /clear_memory/{session_id}": "Clear session memory",
            "GET /memory_status": "Memory store statistics",
            "POST /optimize_rag": "Legacy compatibility endpoint"
        },
        "modular_components": [
            "bloc_config_v2.py",
            "detection_engine_v2.py", 
            "memory_store_v2.py",
            "orchestrator_v2.py"
        ]
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
    """Endpoint principal pour l'orchestration multi-agents V2"""
    start_time = time.time()
    
    try:
        # Récupération des données
        body = await request.json()
        message = body.get("message", "").strip()
        session_id = body.get("session_id", "default_session")
        
        # Validation des entrées
        if not message:
            return {
                "status": "error",
                "message": "Message is required",
                "session_id": session_id,
                "processing_time": round(time.time() - start_time, 3)
            }
        
        if len(message) > 1000:
            return {
                "status": "error", 
                "message": "Message too long (max 1000 characters)",
                "session_id": session_id,
                "processing_time": round(time.time() - start_time, 3)
            }
        
        # Ajout du message à la mémoire
        memory_store.add_message(session_id, message, "user")
        
        # Orchestration avec le composant modulaire
        orchestration_result = await orchestrator.orchestrate(message, session_id)
        
        # Conversion du résultat en format de réponse
        response = {
            "status": "success",
            "session_id": session_id,
            "agent_type": orchestration_result.agent_type.value,
            "bloc_id": orchestration_result.bloc_id,
            "search_query": f"{orchestration_result.bloc_id.lower()} {message[:50]}",
            "context_needed": [orchestration_result.bloc_id.lower()],
            "priority_level": orchestration_result.priority_level,
            "should_escalade": orchestration_result.should_escalate,
            "escalation_type": orchestration_result.escalation_type,
            "profile": orchestration_result.profile,
            "financing_type": orchestration_result.financing_type,
            "message": message,
            "timestamp": time.time(),
            "processing_time": round(time.time() - start_time, 3),
            "context_data": orchestration_result.context_data
        }
        
        logger.info(f"Agent selected for session {session_id}: {orchestration_result.agent_type.value} -> {orchestration_result.bloc_id}")
        
        return response
        
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
    """Vérification de santé de l'API Multi-Agents V2"""
    try:
        memory_stats = memory_store.get_stats()
        orchestrator_stats = orchestrator.get_orchestration_stats()
        
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
            "version": "2.0-Optimized",
            "checks": checks,
            "memory_stats": memory_stats,
            "orchestrator_stats": orchestrator_stats,
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