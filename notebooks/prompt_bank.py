"""Banque de requêtes — extraite telle quelle du notebook d'Hugo, non modifiée."""
import re, sys, subprocess

def _norm(t):
    return re.sub(r"\s+", " ", str(t)).lower()

def _check_invoice(a):
    date_ok = bool(re.search(r"12[/.\-]0?3[/.\-]2025|2025-03-12", str(a)))
    montant_ok = "1250" in re.sub(r"[\s\u202f\xa0.,]", "", str(a))
    return int(date_ok and montant_ok and "lumen" in _norm(a))

def _check_code(a):
    blocks = re.findall(r"```(?:python|py)?\s*\n(.*?)```", str(a), re.S)
    code = max(blocks, key=len) if blocks else str(a)
    test = ("\n\nres = [{'modele': 'a', 'energie_wh': 1.0, 'tokens': 10},"
            " {'modele': 'b', 'energie_wh': 1.0, 'tokens': 20},"
            " {'modele': 'c', 'energie_wh': 0.1, 'tokens': 0}]\n"
            "assert modele_le_plus_efficient(res) == 'b'\nprint('TEST_OK')\n")
    try:
        r = subprocess.run([sys.executable, "-c", code + test], capture_output=True, text=True,
                           timeout=20, stdin=subprocess.DEVNULL)
        return int(r.returncode == 0 and "TEST_OK" in r.stdout)
    except Exception:
        return 0

PROMPT_BANK = [
    # ---------------- Tier 1 : Routine ----------------
    {"id": "T1_01_factuel", "tier": "T1",
     "prompt": "Quelle est la capitale de l'Australie ? Réponds en une phrase.",
     "reference": "Canberra.",
     "check": lambda a: int("canberra" in _norm(a))},
    {"id": "T1_02_extraction", "tier": "T1",
     "prompt": ("Extrais la date, le montant et le fournisseur du texte suivant et réponds uniquement en JSON "
                "avec les clés date, montant, fournisseur : « Facture n°4587 émise le 12/03/2025 par "
                "Société Lumen SAS pour un montant de 1 250,00 € TTC. »"),
     "reference": '{"date": "12/03/2025", "montant": "1250,00 € TTC", "fournisseur": "Société Lumen SAS"}',
     "check": _check_invoice},
    {"id": "T1_03_classification", "tier": "T1",
     "prompt": ("Classe ce message client dans une seule catégorie parmi : Facturation, Technique, Commercial, "
                "Réclamation. Message : « Je n'arrive plus à me connecter à l'application depuis la mise à jour "
                "d'hier. » Réponds uniquement par le nom de la catégorie."),
     "reference": "Technique",
     "check": lambda a: int("technique" in _norm(a) and not any(
         k in _norm(a) for k in ["facturation", "commercial", "réclamation"]))},
    {"id": "T1_04_traduction", "tier": "T1",
     "prompt": "Traduis en anglais : « Le comité de pilotage est reporté à jeudi prochain. »",
     "reference": "The steering committee has been postponed to next Thursday.",
     "check": lambda a: int("steering committee" in _norm(a) and "thursday" in _norm(a))},

    # ---------------- Tier 2 : Analytique ----------------
    {"id": "T2_01_synthese", "tier": "T2",
     "prompt": ("Résume en 3 points clés, pour un comité de direction, le texte suivant : « Depuis 2024, le groupe "
                "a déployé un assistant d'IA générative auprès de 8 000 collaborateurs. L'outil est principalement "
                "utilisé pour la rédaction d'emails, la synthèse de documents et la recherche d'information interne. "
                "Les gains de productivité déclarés atteignent en moyenne 45 minutes par semaine et par utilisateur. "
                "Cependant, la facture de calcul a triplé en un an, et la direction RSE s'inquiète de l'absence "
                "d'indicateurs sur la consommation énergétique et les émissions associées. Le comité doit décider "
                "d'ici la fin du trimestre s'il généralise l'outil aux 20 000 salariés du groupe, et sous quelles "
                "conditions de gouvernance. »"),
     "reference": ("Trois points : (1) adoption : 8 000 utilisateurs, usages rédaction/synthèse/recherche ; "
                   "(2) bénéfices vs risques : 45 min/semaine gagnées mais coûts de calcul x3 et aucun KPI "
                   "environnemental ; (3) décision : généralisation à 20 000 salariés d'ici fin de trimestre, "
                   "conditionnée à une gouvernance."),
     "check": None},
    {"id": "T2_02_email", "tier": "T2",
     "prompt": ("Rédige un email professionnel et concis à un client pour l'informer que la livraison de son tableau "
                "de bord de pilotage IA est décalée de deux semaines en raison d'un problème de qualité des données. "
                "Propose une solution intermédiaire et un point d'étape."),
     "reference": ("Objet explicite ; reconnaissance du retard ; cause (qualité des données) ; nouveau délai de deux "
                   "semaines ; solution intermédiaire concrète ; proposition de point d'étape ; ton professionnel."),
     "check": None},
    {"id": "T2_03_dissertation", "tier": "T2",
     "prompt": ("Rédige une dissertation de 3 paragraphes sur les avantages et inconvénients "
                "de l'open source dans l'intelligence artificielle."),
     "reference": ("Trois paragraphes ; avantages (transparence, collaboration, coûts, innovation, souveraineté) ; "
                   "inconvénients (usages malveillants, sécurité, financement, responsabilité, qualité) ; "
                   "conclusion nuancée."),
     "check": None},
    {"id": "T2_04_comparaison", "tier": "T2",
     "prompt": ("Compare, sous forme de tableau, l'hébergement d'un LLM dans le cloud public et sur une "
                "infrastructure interne (on-premise) pour une banque, selon quatre critères : coût, sécurité, "
                "conformité réglementaire et empreinte carbone. Termine par une recommandation en deux phrases."),
     "reference": ("Tableau à 4 critères ; cloud : coût variable, élasticité, dépendance fournisseur, localisation "
                   "des données ; on-premise : CAPEX, contrôle, conformité facilitée, efficacité énergétique souvent "
                   "moindre ; recommandation argumentée (souvent hybride)."),
     "check": None},

    # ---------------- Tier 3 : Complexe ----------------
    {"id": "T3_01_calcul", "tier": "T3",
     "prompt": ("Une entreprise compte 12 000 salariés. 35 % d'entre eux utilisent un assistant d'IA, à raison de "
                "8 requêtes par jour, 220 jours par an. Chaque requête consomme 0,3 Wh. Calcule la consommation "
                "annuelle totale en MWh en détaillant chaque étape."),
     "reference": "4 200 utilisateurs ; 33 600 requêtes/jour ; 7 392 000 requêtes/an ; 2 217 600 Wh = 2,2176 MWh.",
     "check": lambda a: int(bool(re.search(r"2[.,]2\d*\s*mwh", _norm(a)) or
                                 re.search(r"2\s?217[.,]6\s*kwh", _norm(a))))},
    {"id": "T3_02_logique", "tier": "T3",
     "prompt": ("Trois consultants, Alice, Bruno et Chloé, travaillent chacun sur un projet différent parmi : "
                "Finance, RH et IT. Alice ne travaille pas sur l'IT. Bruno travaille sur la Finance. "
                "Qui travaille sur l'IT ? Raisonne étape par étape puis donne la réponse finale."),
     "reference": "Bruno = Finance ; Alice n'est pas sur l'IT donc Alice = RH ; donc Chloé = IT.",
     "check": lambda a: int(bool(re.search(r"chlo[ée][^.\n]{0,80}\bit\b|\bit\b[^.\n]{0,80}chlo[ée]", _norm(a))))},
    {"id": "T3_03_code", "tier": "T3",
     "prompt": ("Écris une fonction Python nommée modele_le_plus_efficient(resultats) qui prend une liste de "
                "dictionnaires avec les clés 'modele', 'energie_wh' et 'tokens', et renvoie le nom du modèle ayant "
                "le plus faible ratio énergie par token. Ignore les entrées dont tokens vaut 0. "
                "Réponds avec un seul bloc de code Python."),
     "reference": "Filtrer tokens > 0, calculer energie_wh / tokens, renvoyer le 'modele' du minimum.",
     "check": _check_code},
    {"id": "T3_04_architecture", "tier": "T3",
     "prompt": ("Tu es architecte IA dans une grande banque. Propose une architecture de routage de modèles "
                "(petit modèle, modèle moyen, grand modèle) pour un assistant interne. Précise les critères "
                "d'escalade, la gestion de la latence et les indicateurs de suivi environnemental."),
     "reference": ("Classifieur ou règles de complexité en entrée ; SLM par défaut ; escalade sur confiance faible, "
                   "type de tâche ou échec de contrôle ; budgets de latence par tier ; KPI : Wh/requête, gCO2e, "
                   "taux d'escalade, qualité, coût ; gouvernance et journalisation."),
     "check": None},
]