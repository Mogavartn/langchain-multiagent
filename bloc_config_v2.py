# Configuration des blocs V2 - JAK Company
from enum import Enum

class BlocType(Enum):
    """Types de blocs selon la logique décisionnelle V2"""
    
    # Blocs Généraux
    GENERAL = "BLOC GENERAL"
    G = "BLOC G"
    
    # Blocs Ambassadeur
    B1 = "BLOC B1"  # Découverte programme affiliation
    B2 = "BLOC B2"  # L'affiliation c'est quoi
    D1 = "BLOC D1"  # Devenir ambassadeur
    D2 = "BLOC D2"  # C'est quoi un ambassadeur
    E = "BLOC E"    # Processus ambassadeur
    
    # Blocs Apprenant/Formation
    K = "BLOC K"    # Formations disponibles
    M = "BLOC M"    # Après choix formation
    
    # Blocs Prospect
    H = "BLOC H"    # Comprendre les offres
    I1 = "BLOC I1"  # Entreprise/Professionnel
    I2 = "BLOC I2"  # Ambassadeur vendeur
    
    # Blocs Paiement
    A = "BLOC A"    # Suivi paiement
    F = "BLOC F"    # Paiement formation
    J = "BLOC J"    # Paiement direct
    L = "BLOC L"    # Délai dépassé
    
    # Blocs CPF/OPCO
    C = "BLOC C"    # Question CPF
    F1 = "BLOC F1"  # CPF bloqué
    F2 = "BLOC F2"  # CPF dossier bloqué
    F3 = "BLOC F3"  # OPCO
    BLOC_51 = "BLOC 51"  # CPF dossier bloqué (admin)
    BLOC_52 = "BLOC 52"  # Relance après escalade
    BLOC_53 = "BLOC 53"  # Seuils fiscaux
    BLOC_54 = "BLOC 54"  # Sans réseaux sociaux
    
    # Blocs Qualité
    AGRO = "BLOC AGRO"  # Comportement agressif
    LEGAL = "BLOC LEGAL"  # Aspects légaux
    BLOC_61 = "BLOC 61"  # Escalade admin
    BLOC_62 = "BLOC 62"  # Escalade commercial

# Mapping profils -> blocs
PROFILE_BLOC_MAPPING = {
    "ambassador": {
        "primary_blocs": [
            BlocType.A,   # Suivi dossier/paiement
            BlocType.B1,  # Découverte programme affiliation
            BlocType.B2,  # L'affiliation c'est quoi
            BlocType.D1,  # Devenir ambassadeur
            BlocType.D2,  # C'est quoi un ambassadeur
            BlocType.E    # Processus ambassadeur
        ],
        "fallback_bloc": BlocType.GENERAL
    },
    "learner_influencer": {
        "primary_blocs": [
            BlocType.A,   # Suivi paiement
            BlocType.K,   # Promo ponctuelle
            BlocType.M    # Après choix formation
        ],
        "fallback_bloc": BlocType.GENERAL
    },
    "prospect": {
        "primary_blocs": [
            BlocType.H,   # Comprendre les offres
            BlocType.C,   # Question CPF
            BlocType.G    # Parler à un humain
        ],
        "fallback_bloc": BlocType.GENERAL
    }
}

# Règles prioritaires
PRIORITY_RULES = {
    "CRITICAL": [
        BlocType.AGRO,   # Comportement agressif - Priorité absolue
        BlocType.LEGAL,  # Aspects légaux - Priorité absolue
        BlocType.F1,     # CPF bloqué - Priorité absolue
        BlocType.F3      # OPCO - Priorité absolue
    ],
    "HIGH": [
        BlocType.A,      # Suivi paiement
        BlocType.C,      # Question CPF
        BlocType.D1,     # Devenir ambassadeur
        BlocType.D2,     # C'est quoi un ambassadeur
        BlocType.G,      # Parler à un humain
        BlocType.H,      # Comprendre les offres
        BlocType.K       # Formations disponibles
    ],
    "MEDIUM": [
        BlocType.B1,     # Découverte programme affiliation
        BlocType.B2,     # L'affiliation c'est quoi
        BlocType.E,      # Processus ambassadeur
        BlocType.F,      # Paiement formation
        BlocType.J,      # Paiement direct
        BlocType.L,      # Délai dépassé
        BlocType.M       # Après choix formation
    ],
    "LOW": [
        BlocType.GENERAL,  # Général
        BlocType.G,        # Général
        BlocType.I1,       # Entreprise/Professionnel
        BlocType.I2        # Ambassadeur vendeur
    ]
}

# Mots-clés par bloc
BLOC_KEYWORDS = {
    BlocType.A: {
        "keywords": [
            "paiement", "payé", "payée", "payer", "argent", "facture", "débit", "prélèvement",
            "virement", "chèque", "carte bancaire", "cb", "mastercard", "visa", "pas été payé"
        ],
        "description": "Suivi paiement et factures"
    },
    BlocType.B1: {
        "keywords": [
            "affiliation", "affilié", "affiliée", "programme affiliation", "mail affiliation",
            "email affiliation", "courriel affiliation"
        ],
        "description": "Découverte programme affiliation"
    },
    BlocType.B2: {
        "keywords": [
            "c'est quoi un ambassadeur", "qu'est ce qu'un ambassadeur", "définition ambassadeur",
            "ambassadeur définition", "expliquer ambassadeur"
        ],
        "description": "L'affiliation c'est quoi"
    },
    BlocType.C: {
        "keywords": [
            "cpf", "compte personnel formation", "formation cpf", "financement cpf",
            "droit formation", "mon compte formation"
        ],
        "description": "Question CPF"
    },
    BlocType.D1: {
        "keywords": [
            "devenir ambassadeur", "comment devenir ambassadeur", "postuler ambassadeur",
            "candidature ambassadeur", "rejoindre ambassadeur"
        ],
        "description": "Devenir ambassadeur"
    },
    BlocType.D2: {
        "keywords": [
            "c'est quoi un ambassadeur", "qu'est ce qu'un ambassadeur", "définition ambassadeur"
        ],
        "description": "C'est quoi un ambassadeur"
    },
    BlocType.E: {
        "keywords": [
            "processus ambassadeur", "étapes ambassadeur", "comment ça marche ambassadeur",
            "procédure ambassadeur"
        ],
        "description": "Processus ambassadeur"
    },
    BlocType.F: {
        "keywords": [
            "paiement formation", "payé formation", "facture formation", "débit formation"
        ],
        "description": "Paiement formation"
    },
    BlocType.F1: {
        "keywords": [
            "cpf bloqué", "dossier bloqué", "blocage cpf", "problème cpf", "délai cpf"
        ],
        "description": "CPF bloqué"
    },
    BlocType.F2: {
        "keywords": [
            "cpf dossier bloqué", "blocage dossier cpf", "problème dossier cpf"
        ],
        "description": "CPF dossier bloqué"
    },
    BlocType.F3: {
        "keywords": [
            "opco", "opérateur compétences", "délai opco", "blocage opco", "problème opco"
        ],
        "description": "OPCO"
    },
    BlocType.G: {
        "keywords": [
            "parler humain", "contacter humain", "appeler", "téléphoner", "conseiller",
            "assistant", "aide humaine"
        ],
        "description": "Parler à un humain"
    },
    BlocType.H: {
        "keywords": [
            "prospect", "devis", "tarif", "prix", "coût", "formation", "programme",
            "offre", "catalogue"
        ],
        "description": "Comprendre les offres"
    },
    BlocType.I1: {
        "keywords": [
            "entreprise", "société", "professionnel", "auto-entrepreneur", "salarié"
        ],
        "description": "Entreprise/Professionnel"
    },
    BlocType.I2: {
        "keywords": [
            "ambassadeur vendeur", "vendeur", "commercial", "vente"
        ],
        "description": "Ambassadeur vendeur"
    },
    BlocType.J: {
        "keywords": [
            "paiement direct", "paiement immédiat", "payer maintenant"
        ],
        "description": "Paiement direct"
    },
    BlocType.K: {
        "keywords": [
            "formations disponibles", "catalogue formation", "programmes formation",
            "spécialités", "domaines formation", "c'est quoi vos formations", "quelles sont vos formations"
        ],
        "description": "Formations disponibles"
    },
    BlocType.L: {
        "keywords": [
            "délai dépassé", "retard paiement", "paiement en retard", "délai expiré"
        ],
        "description": "Délai dépassé"
    },
    BlocType.M: {
        "keywords": [
            "après choix", "formation choisie", "inscription", "confirmation", "intéressé par",
            "je voudrais", "je veux", "je choisis", "m'intéresse"
        ],
        "description": "Après choix formation"
    },
    BlocType.LEGAL: {
        "keywords": [
            "légal", "droit", "juridique", "avocat", "procédure", "recours"
        ],
        "description": "Aspects légaux"
    },
    BlocType.AGRO: {
        "keywords": [
            "agressif", "énervé", "fâché", "colère", "insulte", "grossier", "impoli",
            "nuls", "nul", "merde", "putain", "con", "connard", "salop", "salope",
            "incompétent", "incompétents", "inutile", "nul", "nuls"
        ],
        "description": "Comportement agressif"
    },
    BlocType.GENERAL: {
        "keywords": [
            "bonjour", "salut", "hello", "qui êtes-vous", "jak company", "présentation"
        ],
        "description": "Général"
    },
    BlocType.BLOC_51: {
        "keywords": [
            "cpf dossier bloqué", "blocage administratif", "délai administratif"
        ],
        "description": "CPF dossier bloqué (admin)"
    },
    BlocType.BLOC_52: {
        "keywords": [
            "relance", "suivi", "nouvelle", "après escalade"
        ],
        "description": "Relance après escalade"
    },
    BlocType.BLOC_53: {
        "keywords": [
            "seuils fiscaux", "micro-entreprise", "fiscal", "impôts"
        ],
        "description": "Seuils fiscaux"
    },
    BlocType.BLOC_54: {
        "keywords": [
            "sans réseaux sociaux", "pas de réseaux", "pas instagram", "pas snapchat"
        ],
        "description": "Sans réseaux sociaux"
    },
    BlocType.BLOC_61: {
        "keywords": [
            "escalade admin", "administrateur", "responsable", "manager"
        ],
        "description": "Escalade admin"
    },
    BlocType.BLOC_62: {
        "keywords": [
            "escalade co", "commercial", "vendeur", "conseiller"
        ],
        "description": "Escalade commercial"
    }
}

# Logique décisionnelle
DECISION_LOGIC = {
    "initialization": {
        "default_bloc": BlocType.GENERAL,
        "priority_check": True
    },
    "profile_detection": {
        "ambassador_indicators": [
            "ambassadeur", "affiliation", "commission", "programme affiliation"
        ],
        "learner_indicators": [
            "formation", "apprenant", "étudiant", "cours", "apprentissage"
        ],
        "prospect_indicators": [
            "devis", "tarif", "prix", "coût", "prospect", "nouveau"
        ]
    },
    "escalation_rules": {
        "payment_delay_threshold": 90,  # jours
        "aggressive_behavior": "immediate_escalation",
        "legal_issues": "immediate_escalation",
        "cpf_blocked": "immediate_escalation"
    },
    "continuity_rules": {
        "same_agent_continuation": [
            "oui", "non", "ok", "d'accord", "merci", "et", "aussi", "comment"
        ],
        "context_switch_threshold": 3  # messages
    }
}