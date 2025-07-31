# JAK Company Multi-Agents API V2

## 🚀 Vue d'ensemble

La **V2** de l'API Multi-Agents JAK Company est une version entièrement refactorisée et optimisée du système d'orchestration d'agents spécialisés. Cette version apporte des améliorations significatives en termes de performance, maintenabilité et logique décisionnelle.

## 📋 Fonctionnalités principales

### ✨ Nouvelles fonctionnalités V2

- **Orchestration multi-agents optimisée** : Détection intelligente et routage spécialisé
- **Détection de contexte conversationnel** : Compréhension des suites de conversation
- **Gestion de mémoire avancée** : Store de mémoire optimisé avec TTL et nettoyage automatique
- **Validation de séquences de blocs** : Vérification de la cohérence des transitions
- **Escalade intelligente** : Gestion automatique des cas critiques
- **Profils utilisateurs** : Détection automatique des types d'utilisateurs
- **Contexte de paiement** : Gestion spécialisée des questions de financement
- **Nettoyage automatique des sessions** : Maintenance automatique de la mémoire

### 🔧 Améliorations techniques

- **Architecture modulaire** : Séparation claire des responsabilités
- **Cache optimisé** : Utilisation de `lru_cache` et `TTLCache`
- **Gestion d'erreurs robuste** : Middleware et handlers d'exception
- **API RESTful complète** : Endpoints documentés avec Pydantic
- **Tests automatisés** : Suite de tests complète avec validation
- **Logging structuré** : Traçabilité complète des opérations

## 🏗️ Architecture

### Structure des fichiers

```
├── bloc_config_v2.py          # Configuration des blocs et logique décisionnelle
├── detection_engine_v2.py     # Moteur de détection optimisé
├── memory_store_v2.py         # Store de mémoire avancé
├── orchestrator_v2.py         # Orchestrateur principal
├── api_v2.py                  # API FastAPI V2
├── test_v2.py                 # Suite de tests
└── README_V2.md              # Documentation
```

### Composants principaux

#### 1. Configuration des blocs (`bloc_config_v2.py`)

- **BlocType** : Enumération des types de blocs
- **BLOC_KEYWORDS** : Mots-clés par bloc avec descriptions
- **PRIORITY_RULES** : Règles de priorité (CRITICAL, HIGH, MEDIUM, LOW)
- **PROFILE_BLOC_MAPPING** : Mapping profils → blocs
- **DECISION_LOGIC** : Logique décisionnelle complète

#### 2. Moteur de détection (`detection_engine_v2.py`)

- **DetectionEngineV2** : Détection intelligente des intentions
- **ProfileType** : Types de profils utilisateurs
- **FinancingType** : Types de financement
- **Détection contextuelle** : Compréhension des suites de conversation
- **Validation de séquences** : Vérification de la cohérence

#### 3. Store de mémoire (`memory_store_v2.py`)

- **OptimizedMemoryStoreV2** : Gestion avancée des sessions
- **TTLCache** : Cache avec expiration automatique
- **Export/Import** : Sauvegarde et restauration des sessions
- **Statistiques** : Métriques détaillées d'utilisation
- **Nettoyage automatique** : Maintenance de la mémoire

#### 4. Orchestrateur (`orchestrator_v2.py`)

- **MultiAgentOrchestratorV2** : Orchestration principale
- **OrchestrationResult** : Résultats structurés
- **Mapping bloc → agent** : Routage spécialisé
- **Contexte de réponse** : Données enrichies pour les agents

#### 5. API FastAPI (`api_v2.py`)

- **Endpoints RESTful** : API complète et documentée
- **Modèles Pydantic** : Validation des données
- **Compatibilité V1** : Endpoint `/optimize_rag` pour rétrocompatibilité
- **Gestion d'erreurs** : Middleware et handlers globaux
- **Documentation automatique** : Swagger/ReDoc

## 🎯 Logique décisionnelle V2

### Règles de priorité

1. **CRITICAL** : Comportements agressifs, aspects légaux, CPF bloqué, OPCO
2. **HIGH** : Suivi paiement, questions CPF, devenir ambassadeur, contact humain
3. **MEDIUM** : Découverte affiliation, processus ambassadeur, formations
4. **LOW** : Général, entreprise/professionnel

### Profils utilisateurs

- **Ambassador** : Programme d'affiliation et processus
- **Learner/Influencer** : Formations et apprentissage
- **Prospect** : Devis et qualification commerciale

### Types d'agents

- **GENERAL** : Accueil et orientation générale
- **AMBASSADOR** : Programme ambassadeur et affiliation
- **LEARNER** : Catalogue formations et inscription
- **PROSPECT** : Qualification prospects et devis
- **PAYMENT** : Suivi paiements et factures
- **CPF_BLOCKED** : Déblocage dossiers CPF/OPCO
- **QUALITY** : Contrôle qualité et escalades

## 🚀 Installation et utilisation

### Prérequis

```bash
pip install fastapi uvicorn cachetools pydantic
```

### Variables d'environnement

```bash
export OPENAI_API_KEY="your_openai_api_key"
export DEBUG="false"  # Pour le mode développement
```

### Lancement de l'API

```bash
# Lancement direct
python api_v2.py

# Ou avec uvicorn
uvicorn api_v2:app --host 0.0.0.0 --port 8000 --reload
```

### Tests

```bash
# Exécuter tous les tests
python test_v2.py

# Tests de performance inclus
```

## 📡 API Endpoints

### Endpoints principaux

- `POST /orchestrate` : Orchestration principale V2
- `POST /optimize_rag` : Compatibilité avec l'ancien système
- `GET /health` : Vérification de santé
- `GET /stats` : Statistiques d'orchestration
- `GET /agents` : Liste des agents disponibles
- `GET /blocs` : Liste des blocs disponibles

### Gestion des sessions

- `POST /sessions/{session_id}/clear` : Nettoyer une session
- `GET /sessions/{session_id}/data` : Exporter les données d'une session
- `POST /sessions/{session_id}/import` : Importer des données de session
- `POST /cleanup` : Nettoyage manuel des sessions

### Documentation API

- **Swagger UI** : `http://localhost:8000/docs`
- **ReDoc** : `http://localhost:8000/redoc`

## 🔄 Migration depuis V1

### Changements principaux

1. **Nouvelle architecture** : Séparation modulaire des composants
2. **API restructurée** : Endpoints plus clairs et documentés
3. **Logique optimisée** : Détection et routage améliorés
4. **Gestion mémoire** : Store optimisé avec nettoyage automatique

### Compatibilité

- L'endpoint `/optimize_rag` maintient la compatibilité avec V1
- Format de réponse compatible avec l'ancien système n8n
- Migration progressive possible

### Exemple de migration

```python
# V1 (ancien)
response = await client.post("/optimize_rag", json={
    "message": "Je n'ai pas été payé",
    "session_id": "user123"
})

# V2 (nouveau)
response = await client.post("/orchestrate", json={
    "message": "Je n'ai pas été payé",
    "session_id": "user123",
    "platform": "whatsapp"
})
```

## 📊 Monitoring et métriques

### Statistiques disponibles

- **Sessions actives** : Nombre de sessions en cours
- **Messages traités** : Volume de messages
- **Performance** : Temps de traitement moyen
- **Utilisation mémoire** : Métriques de stockage
- **Taux d'escalade** : Fréquence des escalades

### Logs structurés

```python
# Exemple de log
2024-01-15 10:30:45 - orchestrator_v2 - INFO - Orchestration terminée pour session user123: BLOC A -> payment
```

## 🧪 Tests et validation

### Suite de tests

- **Tests unitaires** : Validation des composants individuels
- **Tests d'intégration** : Scénarios complets
- **Tests de performance** : Mesures de performance
- **Tests de compatibilité** : Validation V1 → V2

### Exécution des tests

```bash
python test_v2.py
```

### Métriques de test

- **Taux de réussite** : Objectif > 95%
- **Performance** : < 100ms par message
- **Couverture** : Tous les composants testés

## 🔧 Configuration avancée

### Paramètres du store de mémoire

```python
memory_store = OptimizedMemoryStoreV2(
    max_sessions=1000,        # Nombre max de sessions
    session_ttl=3600,         # Durée de vie (secondes)
    message_history_limit=50  # Limite messages par session
)
```

### Paramètres de détection

```python
# Personnalisation des mots-clés
BLOC_KEYWORDS[BlocType.A]["keywords"].extend([
    "nouveau_mot_cle",
    "autre_terme"
])
```

### Paramètres d'escalade

```python
# Seuils d'escalade
escalation_rules = {
    "payment_delay_threshold": 90,  # jours
    "aggressive_behavior": "immediate_escalation",
    "legal_issues": "immediate_escalation"
}
```

## 🚨 Gestion des erreurs

### Types d'erreurs

- **Validation** : Messages invalides (400)
- **Session** : Sessions non trouvées (404)
- **Système** : Erreurs internes (500)
- **Orchestration** : Erreurs de traitement (500)

### Gestion automatique

- **Middleware** : Nettoyage automatique des sessions
- **Handlers** : Gestion globale des exceptions
- **Logging** : Traçabilité complète des erreurs
- **Fallback** : Retour au bloc général en cas d'erreur

## 📈 Performance

### Optimisations

- **Cache LRU** : Mise en cache des détections fréquentes
- **TTL Cache** : Expiration automatique des sessions
- **Async/await** : Traitement asynchrone
- **Optimisation mémoire** : Limites et nettoyage automatique

### Métriques cibles

- **Temps de réponse** : < 100ms
- **Mémoire** : < 100MB pour 1000 sessions
- **Throughput** : > 100 messages/seconde
- **Disponibilité** : > 99.9%

## 🔮 Évolutions futures

### Roadmap V2.1

- **Intégration Supabase** : Connexion directe à la base de données
- **Machine Learning** : Amélioration de la détection d'intention
- **Analytics** : Tableaux de bord avancés
- **Multi-langues** : Support international

### Roadmap V2.2

- **Microservices** : Architecture distribuée
- **Kubernetes** : Orchestration containerisée
- **Monitoring** : Métriques temps réel
- **A/B Testing** : Tests de nouvelles logiques

## 📞 Support

### Documentation

- **API Docs** : `/docs` et `/redoc`
- **Code source** : Commentaires détaillés
- **Tests** : Exemples d'utilisation

### Contact

Pour toute question ou support technique, consultez la documentation ou les logs de l'application.

---

**Version** : 2.0.0  
**Dernière mise à jour** : Janvier 2024  
**Statut** : Production Ready ✅