# ASTRÉA — DÉPLOIEMENT HD API SUR RENDER (100% GRATUIT)

## CONTEXTE

La librairie utilisée est `human-design-py` (MIT license, publiée mars 2026).
Repo : https://github.com/geodetheseeker/human-design-py
Auteur : geodetheseeker (Projector 2/4 qui voulait vérifier la précision des outils existants)

Coût total : 0 €/mois
L'API tourne sur Render free tier (750h/mois = 1 service always-on).

---

## FICHIERS DU PROJET

```
astraea-hd-api/
├── main.py          ← FastAPI app (wrapper + calculs)
├── chart.py         ← Librairie human-design-py (copie directe)
├── requirements.txt ← Dépendances Python
├── render.yaml      ← Config Render
└── .gitignore
```

---

## ÉTAPE 1 — CRÉER LE REPO GITHUB

1. Va sur github.com → New repository
2. Nom : `astraea-hd-api`
3. Visibilité : **Private** (pour ne pas exposer le code)
4. Ne pas initialiser avec README

Ensuite en terminal :
```bash
cd astraea-hd-api
git init
git add .
git commit -m "Initial commit — Astrea HD API"
git branch -M main
git remote add origin https://github.com/TON_USERNAME/astraea-hd-api.git
git push -u origin main
```

---

## ÉTAPE 2 — DÉPLOYER SUR RENDER

1. Va sur https://render.com → Sign up (gratuit)
2. New → Web Service
3. Connecte ton repo GitHub → sélectionne `astraea-hd-api`
4. Configuration :
   - **Name :** astraea-hd-api
   - **Runtime :** Python 3
   - **Build Command :** `pip install -r requirements.txt`
   - **Start Command :** `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan :** Free
5. Clic Deploy Web Service
6. Attends ~3-5 minutes pour le premier build

Render te donnera une URL du type :
`https://astraea-hd-api.onrender.com`

**Test :** ouvre `https://astraea-hd-api.onrender.com/health`
Tu dois voir : `{"status":"ok","service":"Astraea HD API"}`

---

## ÉTAPE 3 — TESTER L'API

```bash
curl -X POST https://astraea-hd-api.onrender.com/bodygraph \
  -H "Content-Type: application/json" \
  -d '{"date": "1990-03-29", "time": "16:05", "city": "Paris"}'
```

Réponse JSON attendue :
```json
{
  "type": "Generator",
  "strategy": "Respond",
  "authority": "Emotional",
  "profile": "6/2",
  "centers_defined": ["Root", "Sacral", "Solar Plexus", "Spleen"],
  "centers_open": ["Ajna", "Head", "Heart", "Self", "Throat"],
  "channels": [
    {"name": "Concentration", "gates": [9, 52]},
    {"name": "Judgment", "gates": [18, 58]},
    {"name": "Emoting", "gates": [39, 55]}
  ],
  "incarnation_cross": {
    "family": "Left Angle Cross",
    "personality_sun_gate": 17,
    "personality_earth_gate": 18,
    "design_sun_gate": 38,
    "design_earth_gate": 39,
    "label": "Left Angle Cross — Porte 17 / Porte 18 (Personnalité) — Porte 38 / Porte 39 (Design)"
  },
  "active_gates": [1, 2, 7, 9, 13, 15, 17, 18, 38, 39, 41, 49, 51, 52, 54, 55, 58, 61]
}
```

---

## ÉTAPE 4 — GARDER L'API ÉVEILLÉE (Important !)

Render free tier endort le service après 15 minutes d'inactivité.
Le réveil prend ~30-50 secondes et peut faire timeout Make.

**Solution gratuite : UptimeRobot**
1. Crée un compte sur https://uptimerobot.com (gratuit, 50 moniteurs inclus)
2. Add New Monitor
3. Type : HTTP(s)
4. URL : `https://astraea-hd-api.onrender.com/health`
5. Interval : **Every 5 minutes**

Résultat : le service ne dort jamais, temps de réponse toujours < 2 secondes.

---

## ÉTAPE 5 — INTÉGRER DANS MAKE

### Module HTTP Request

- **URL :** `https://astraea-hd-api.onrender.com/bodygraph`
- **Method :** POST
- **Headers :** `Content-Type: application/json`
- **Timeout :** 60 secondes (pour le premier appel si pas de UptimeRobot)
- **Body (Raw JSON) :**
```json
{
  "date": "{{formatDate(1.birthdate; 'YYYY-MM-DD')}}",
  "time": "{{formatDate(1.birthtime; 'HH:mm')}}",
  "city": "{{1.birth_city}}"
}
```

### Variables à extraire (module Parse JSON → Set Variables)

| Variable Make | Chemin JSON |
|---|---|
| `hd_type` | `type` |
| `hd_strategy` | `strategy` |
| `hd_authority` | `authority` |
| `hd_profile` | `profile` |
| `hd_centers_defined` | `centers_defined` (array → join ", ") |
| `hd_centers_open` | `centers_open` (array → join ", ") |
| `hd_channels` | `channels[].name` (map → join ", ") |
| `hd_cross_label` | `incarnation_cross.label` |
| `hd_cross_family` | `incarnation_cross.family` |
| `hd_cross_p_sun` | `incarnation_cross.personality_sun_gate` |
| `hd_cross_p_earth` | `incarnation_cross.personality_earth_gate` |
| `hd_cross_d_sun` | `incarnation_cross.design_sun_gate` |
| `hd_cross_d_earth` | `incarnation_cross.design_earth_gate` |

### Traductions EN → FR (module Make "Set Variables" après Parse JSON)

```
type_fr = switch(hd_type;
  "Generator"; "Générateur";
  "Manifesting Generator"; "Générateur Manifestant";
  "Manifestor"; "Manifesteur";
  "Projector"; "Projecteur";
  "Reflector"; "Réflecteur";
  hd_type)

strategy_fr = switch(hd_strategy;
  "Respond"; "Répondre";
  "Respond and Inform"; "Répondre et Informer";
  "Inform"; "Informer avant d'agir";
  "Wait for Invitation"; "Attendre l'invitation";
  "Wait a Lunar Cycle"; "Attendre un cycle lunaire";
  hd_strategy)

authority_fr = switch(hd_authority;
  "Emotional"; "Emotionnelle";
  "Sacral"; "Sacrale";
  "Splenic"; "Splénique";
  "Ego"; "de l'Ego";
  "Self-Projected"; "Auto-projetée";
  "Mental/Outer"; "Mentale";
  hd_authority)
```

---

## LIMITES CONNUES DE LA LIBRAIRIE

| Fonctionnalité | Statut |
|---|---|
| Type | ✅ Calculé |
| Stratégie | ✅ Dérivée du type |
| Autorité | ✅ Calculée |
| Profil | ✅ Calculé |
| Centres définis/ouverts | ✅ Calculés |
| Canaux définis | ✅ Dérivés des portes |
| Portes actives | ✅ Calculées |
| Croix d'Incarnation (portes) | ✅ Portes calculées |
| Nom exact de la Croix (192 croix) | ⚠️ Non nommé, mais portes disponibles |
| Variables (PHS) | ❌ Non implémenté |
| Bodygraph visuel | ❌ Non implémenté |

Pour le livre Astréa : les prompts Claude API peuvent décrire la Croix d'Incarnation à partir des 4 numéros de portes + la famille (Right/Left Angle Cross). Claude a la connaissance des 192 croix dans ses données d'entraînement.

---

## COÛT FINAL

| Service | Coût |
|---|---|
| GitHub (private repo) | 0 € |
| Render free tier | 0 € |
| UptimeRobot | 0 € |
| human-design-py (MIT) | 0 € |
| **TOTAL** | **0 €/mois** |

---

*Astréa HD API — Avril 2026*
