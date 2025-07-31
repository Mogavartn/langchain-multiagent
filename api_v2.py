"""
API FastAPI V2 optimisée - JAK Company
Version nettoyée et optimisée pour la logique décisionnelle V2
"""

import os
import time
import logging
import traceback
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from orchestrator_v2 import MultiAgentOrchestratorV2, OrchestrationResult
from bloc_config_v2 import BlocType
from detection_engine_v2 import ProfileType, FinancingType

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modèles Pydantic
class OrchestrationRequest(BaseModel):
    """Modèle de requête d'orchestration"""
    message: str = Field(..., min_length=1, max_length=1000, description="Message de l'utilisateur")
    session_id: str = Field(default="default_session", description="ID de session")
    user_id: Optional[str] = Field(None, description="ID utilisateur")
    platform: Optional[str] = Field("whatsapp", description="Plateforme (whatsapp, web, etc.)")

class OrchestrationResponse(BaseModel):
    """Modèle de réponse d'orchestration"""
    status: str = Field(..., description="Statut de la réponse")
    bloc_id: str = Field(..., description="ID du bloc détecté")
    agent_type: str = Field(..., description="Type d'agent sélectionné")
    should_escalate: bool = Field(..., description="Si une escalade est nécessaire")
    escalation_type: Optional[str] = Field(None, description="Type d'escalade")
    priority_level: str = Field(..., description="Niveau de priorité")
    profile: str = Field(..., description="Profil détecté")
    financing_type: str = Field(..., description="Type de financement")
    processing_time: float = Field(..., description="Temps de traitement")
    session_id: str = Field(..., description="ID de session")
    context_data: Dict[str, Any] = Field(default_factory=dict, description="Données de contexte")

class HealthResponse(BaseModel):
    """Modèle de réponse de santé"""
    status: str
    version: str
    timestamp: float
    checks: Dict[str, str]
    stats: Dict[str, Any]

class SessionDataResponse(BaseModel):
    """Modèle de réponse de données de session"""
    session_id: str
    data: Dict[str, Any]
    exported_at: float

# Initialisation de l'API
app = FastAPI(
    title="JAK Company Multi-Agents API V2",
    description="API optimisée pour l'orchestration multi-agents JAK Company",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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

# Instance globale de l'orchestrateur
orchestrator = MultiAgentOrchestratorV2()

# Tâches en arrière-plan
async def cleanup_old_sessions_task():
    """Tâche de nettoyage des anciennes sessions"""
    try:
        cleared_count = orchestrator.cleanup_old_sessions()
        if cleared_count > 0:
            logger.info(f"Nettoyage automatique: {cleared_count} sessions supprimées")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage automatique: {e}")

# Endpoints
@app.get("/", response_model=Dict[str, Any])
async def root():
    """Endpoint racine avec informations sur l'API V2"""
    return {
        "message": "JAK Company Multi-Agents API V2",
        "version": "2.0.0",
        "status": "active",
        "architecture": "Multi-Agents V2 Optimized",
        "features": [
            "Orchestration multi-agents optimisée",
            "Détection de contexte conversationnel",
            "Gestion de mémoire avancée",
            "Validation de séquences de blocs",
            "Escalade intelligente",
            "Profils utilisateurs",
            "Contexte de paiement",
            "Nettoyage automatique des sessions"
        ],
        "endpoints": {
            "POST /orchestrate": "Orchestration principale V2",
            "POST /optimize_rag": "Compatibilité avec l'ancien système",
            "GET /health": "Vérification de santé",
            "GET /stats": "Statistiques d'orchestration",
            "GET /agents": "Liste des agents disponibles",
            "GET /blocs": "Liste des blocs disponibles",
            "POST /sessions/{session_id}/clear": "Nettoyer une session",
            "GET /sessions/{session_id}/data": "Exporter les données d'une session",
            "POST /sessions/{session_id}/import": "Importer des données de session"
        }
    }

@app.post("/orchestrate", response_model=OrchestrationResponse)
async def orchestrate_message(request: OrchestrationRequest):
    """Endpoint principal d'orchestration V2"""
    start_time = time.time()
    
    try:
        # Validation du message
        is_valid, error_msg = orchestrator.validate_message(request.message)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Orchestration
        result = await orchestrator.orchestrate(request.message, request.session_id)
        
        # Création de la réponse
        response = OrchestrationResponse(
            status="success",
            bloc_id=result.bloc_id,
            agent_type=result.agent_type.value,
            should_escalate=result.should_escalate,
            escalation_type=result.escalation_type,
            priority_level=result.priority_level,
            profile=result.profile,
            financing_type=result.financing_type,
            processing_time=result.processing_time,
            session_id=request.session_id,
            context_data=result.context_data
        )
        
        logger.info(f"Orchestration réussie pour session {request.session_id}: {result.bloc_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'orchestration: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne lors de l'orchestration: {str(e)}"
        )

@app.post("/optimize_rag")
async def optimize_rag_compatibility(request: Request):
    """Endpoint de compatibilité avec l'ancien système"""
    logger.info("Endpoint de compatibilité /optimize_rag appelé")
    
    try:
        body = await request.json()
        message = body.get("message", "").strip()
        session_id = body.get("session_id", "default_session")
        
        if not message:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "message": "Message is required",
                    "session_id": session_id
                }
            )
        
        # Utiliser l'orchestrateur V2
        result = await orchestrator.orchestrate(message, session_id)
        
        # Format de réponse compatible avec l'ancien système
        response = {
            "status": "success",
            "session_id": session_id,
            "agent_type": result.agent_type.value,
            "bloc_id": result.bloc_id,
            "search_query": f"{result.bloc_id.lower()} {message[:50]}",
            "context_needed": [result.bloc_id.lower()],
            "priority_level": result.priority_level,
            "should_escalade": result.should_escalate,
            "message": message,
            "timestamp": time.time(),
            "processing_time": result.processing_time
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Erreur dans l'endpoint de compatibilité: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e),
                "session_id": body.get("session_id", "unknown") if 'body' in locals() else "unknown"
            }
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de santé de l'API V2"""
    try:
        # Récupérer les statistiques
        stats = orchestrator.get_orchestration_stats()
        
        # Vérifications
        checks = {
            "api_status": "healthy",
            "orchestrator": "operational",
            "detection_engine": "ready",
            "memory_store": "ready",
            "openai_key": "configured" if openai_key else "missing"
        }
        
        response = HealthResponse(
            status="healthy",
            version="2.0.0",
            timestamp=time.time(),
            checks=checks,
            stats=stats
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Récupère les statistiques d'orchestration"""
    try:
        stats = orchestrator.get_orchestration_stats()
        return {
            "status": "success",
            "stats": stats,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/agents")
async def list_agents():
    """Liste des agents disponibles"""
    agents = []
    for agent_type in orchestrator.bloc_agent_mapping.values():
        agents.append({
            "type": agent_type.value,
            "name": agent_type.name,
            "specialization": orchestrator.get_agent_specialization(agent_type)
        })
    
    return {
        "status": "success",
        "agents": agents,
        "total_agents": len(agents)
    }

@app.get("/blocs")
async def list_blocs():
    """Liste des blocs disponibles"""
    from bloc_config_v2 import BLOC_KEYWORDS
    
    blocs = []
    for bloc_type, config in BLOC_KEYWORDS.items():
        blocs.append({
            "bloc_id": bloc_type.value,
            "description": config["description"],
            "keywords_count": len(config["keywords"]),
            "agent_type": orchestrator.bloc_agent_mapping.get(bloc_type, "unknown").value
        })
    
    return {
        "status": "success",
        "blocs": blocs,
        "total_blocs": len(blocs)
    }

@app.post("/sessions/{session_id}/clear")
async def clear_session(session_id: str):
    """Nettoie une session spécifique"""
    try:
        success = orchestrator.memory_store.clear_session(session_id)
        if success:
            return {
                "status": "success",
                "message": f"Session {session_id} nettoyée avec succès",
                "session_id": session_id
            }
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} non trouvée")
    except Exception as e:
        logger.error(f"Error clearing session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear session: {str(e)}")

@app.get("/sessions/{session_id}/data", response_model=SessionDataResponse)
async def export_session_data(session_id: str):
    """Exporte les données d'une session"""
    try:
        data = orchestrator.export_session_data(session_id)
        if data:
            return SessionDataResponse(
                session_id=session_id,
                data=data,
                exported_at=time.time()
            )
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} non trouvée")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting session data {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to export session data: {str(e)}")

@app.post("/sessions/{session_id}/import")
async def import_session_data(session_id: str, data: Dict[str, Any]):
    """Importe des données de session"""
    try:
        success = orchestrator.import_session_data(session_id, data)
        if success:
            return {
                "status": "success",
                "message": f"Données importées pour la session {session_id}",
                "session_id": session_id
            }
        else:
            raise HTTPException(status_code=400, detail="Données de session invalides")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing session data {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to import session data: {str(e)}")

@app.post("/cleanup")
async def manual_cleanup(background_tasks: BackgroundTasks):
    """Déclenche un nettoyage manuel des sessions"""
    try:
        background_tasks.add_task(cleanup_old_sessions_task)
        return {
            "status": "success",
            "message": "Nettoyage des sessions déclenché en arrière-plan"
        }
    except Exception as e:
        logger.error(f"Error triggering cleanup: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger cleanup: {str(e)}")

# Middleware pour le nettoyage automatique
@app.middleware("http")
async def auto_cleanup_middleware(request: Request, call_next):
    """Middleware pour le nettoyage automatique des sessions"""
    # Nettoyer les anciennes sessions toutes les 100 requêtes
    if hasattr(auto_cleanup_middleware, 'request_count'):
        auto_cleanup_middleware.request_count += 1
    else:
        auto_cleanup_middleware.request_count = 1
    
    if auto_cleanup_middleware.request_count % 100 == 0:
        try:
            orchestrator.cleanup_old_sessions()
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage automatique: {e}")
    
    response = await call_next(request)
    return response

# Gestionnaire d'erreurs global
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestionnaire d'erreurs global"""
    logger.error(f"Erreur non gérée: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Erreur interne du serveur",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "Internal server error"
        }
    )

# Point d'entrée principal
if __name__ == "__main__":
    uvicorn.run(
        "api_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )