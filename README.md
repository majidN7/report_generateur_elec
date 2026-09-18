# Gestion des Bureaux de Vote — Élections 2026

Application web complète pour gérer, visualiser et générer automatiquement les
arrêtés officiels de désignation des présidents et membres des bureaux de
vote (ordinaires et centraux), à partir d'un fichier Excel de données et d'un
modèle Word officiel.

## Sommaire

- [Architecture](#architecture)
- [Démarrage rapide avec Docker](#démarrage-rapide-avec-docker)
- [Installation manuelle](#installation-manuelle)
- [Utilisation](#utilisation)
- [Décisions de conception importantes](#décisions-de-conception-importantes)
- [Structure du projet](#structure-du-projet)
- [Tests](#tests)

## Architecture

| Composant   | Technologie                                                     |
|-------------|------------------------------------------------------------------|
| Backend     | Python 3.11, FastAPI, SQLAlchemy 2, Alembic                     |
| Frontend    | React 19, TypeScript, Vite, Tailwind CSS 4, React Router         |
| Base de données | PostgreSQL (production/Docker) ou SQLite (dev rapide sans dépendance) |
| Génération Word | `docxtpl` (Jinja2 + `python-docx`)                           |
| Génération PDF  | LibreOffice headless (`soffice --convert-to pdf`)             |

```
report_generateur_elec/
├── backend/                 # API FastAPI
│   ├── app/
│   │   ├── models/          # Modèles SQLAlchemy (BureauVote, BureauCentral)
│   │   ├── schemas/         # Schémas Pydantic
│   │   ├── routers/         # Endpoints REST
│   │   ├── services/        # Import Excel, fusion Word/PDF
│   │   └── templates_word/  # Modèles docxtpl (générés depuis le .docx fourni)
│   ├── alembic/              # Migrations de base de données
│   ├── tests/                 # Tests pytest
│   └── Dockerfile
├── frontend/                 # Application React
│   ├── src/
│   │   ├── api/               # Client HTTP + types
│   │   ├── components/        # Formulaires, tableau, modales
│   │   └── pages/              # Écrans (Bureaux de vote / Bureaux centraux)
│   └── Dockerfile
└── docker-compose.yml
```

## Démarrage rapide avec Docker

Prérequis : Docker et Docker Compose.

```bash
docker compose up --build
```

- Frontend : http://localhost:8080
- API backend : http://localhost:8000 (documentation interactive sur `/docs`)
- Base de données PostgreSQL : exposée en interne au service `db`

Les migrations de base de données sont appliquées automatiquement au
démarrage du conteneur backend.

## Installation manuelle

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Base SQLite par défaut (aucune configuration requise) :
python -m alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Pour utiliser PostgreSQL au lieu de SQLite, définissez la variable
d'environnement avant de lancer les commandes ci-dessus (voir
`.env.example`) :

```bash
export DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/bureaux_vote
```

**Génération PDF** : nécessite LibreOffice installé sur la machine
(`soffice` doit être dans le `PATH`). Sous Debian/Ubuntu :
`sudo apt-get install libreoffice-writer`. Sans LibreOffice, la génération
Word (.docx) reste pleinement fonctionnelle ; seule l'option "PDF" échouera.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

L'application est disponible sur http://localhost:5173 et proxifie les
appels `/api/*` vers `http://localhost:8000` (voir `vite.config.ts`).

## Utilisation

1. **Importer les données** : depuis l'écran "Bureaux de vote", cliquez sur
   *Importer Excel* et sélectionnez le fichier (feuille `Donnees_Fusion`,
   colonnes : الرئيس, نائب الرئيس, رقم مكتب التصويت, الجماعة, عنوان مكتب
   التصويت, رقم المكتب المركزي, رئيس المكتب المركزي, membres et suppléants).
   Un rapport d'import indique les lignes créées, mises à jour, les doublons
   ignorés et les erreurs de validation.
2. **Gérer les bureaux** : recherchez, filtrez par commune, triez, consultez
   le détail, modifiez ou supprimez un enregistrement, ou ajoutez-en un
   manuellement.
3. **Compléter les bureaux centraux** : l'import crée automatiquement une
   fiche par bureau central référencé (numéro + président). Comme le fichier
   Excel source ne fournit pas le vice-président, les membres, les
   suppléants ni l'adresse propres au bureau central, ces fiches doivent être
   complétées manuellement dans l'onglet *Bureaux centraux* avant de pouvoir
   générer leur arrêté (un badge *À compléter* / *Complet* indique le
   statut).
4. **Générer les arrêtés** :
   - Depuis une ligne du tableau : boutons *Word* / *PDF* pour un
     téléchargement unitaire.
   - *Générer tout (Word)* / *Générer tout (PDF)* : télécharge une archive
     ZIP contenant l'arrêté de chaque bureau (les bureaux centraux
     incomplets sont ignorés et comptabilisés).

## Décisions de conception importantes

- **Deux modèles de documents** : le fichier Word officiel fourni contient
  deux arrêtés types (bureaux de vote ordinaires et bureaux de vote
  centraux). Ils ont été convertis en deux modèles `docxtpl` distincts
  (`backend/app/templates_word/bureau_ordinaire.docx` et
  `bureau_central.docx`) en remplaçant les pointillés du modèle par des
  variables Jinja (`{{ president }}`, `{{ numero_bureau }}`, etc.), tout en
  conservant la mise en forme, l'en-tête et le logo institutionnel d'origine.
- **Bureaux centraux = fiches à compléter** : le fichier Excel fourni ne
  contient, pour chaque bureau central, que son numéro et le nom de son
  président (ces informations apparaissent répétées sur chaque ligne des
  bureaux ordinaires qui lui sont rattachés). Il ne fournit ni son
  vice-président, ni ses membres/suppléants, ni son adresse propre.
  Plutôt que d'inventer ces données, l'application crée automatiquement une
  fiche "bureau central" (dédupliquée par commune + numéro) lors de l'import
  et bloque la génération de son arrêté tant que ces champs n'ont pas été
  renseignés manuellement — avec un message d'erreur explicite listant les
  champs manquants.
- **Adresse du bureau central (arrêté ordinaire)** : la phrase de l'arrêté
  ordinaire mentionne aussi le lieu du bureau central de rattachement. Par
  défaut, l'application réutilise l'adresse du bureau de vote lui-même
  (cas fréquent où le bureau central est colocalisé), mais ce champ est
  éditable indépendamment sur chaque bureau de vote si nécessaire.
- **Numéro de décision / date de signature** : absents du fichier Excel, ils
  sont éditables par enregistrement ; à défaut, l'application utilise
  respectivement l'identifiant interne de l'enregistrement et la date du
  jour (au format arabe marocain, ex. "18 شتنبر 2026").
- **Détection des doublons à l'import** : un bureau est identifié de façon
  unique par le couple (commune, numéro de bureau). Une ligne déjà présente
  en base est mise à jour (upsert) ; une ligne dupliquée *au sein du même
  fichier* est ignorée et comptabilisée dans le rapport d'import.

## Structure du projet

Voir l'arborescence ci-dessus. Les routes API principales :

| Méthode | Route                              | Description                          |
|---------|-------------------------------------|---------------------------------------|
| POST    | `/api/import/excel`                | Importer un fichier Excel             |
| GET     | `/api/bureaux`                     | Liste paginée / recherche / tri       |
| POST    | `/api/bureaux`                     | Créer un bureau de vote               |
| GET/PUT/DELETE | `/api/bureaux/{id}`         | Lire / modifier / supprimer           |
| GET     | `/api/bureaux/{id}/document`       | Télécharger l'arrêté (docx ou pdf)    |
| POST    | `/api/bureaux/generate-batch`      | Télécharger un ZIP de tous les arrêtés|
| GET/POST/PUT/DELETE | `/api/bureaux-centraux*`   | Mêmes opérations pour les bureaux centraux |

Documentation interactive complète (Swagger) disponible sur `/docs` une fois
le backend démarré.

## Tests

```bash
cd backend
pytest
```

Les tests couvrent l'import Excel (succès, doublons, upsert, validation),
le CRUD des bureaux et la génération de documents (Word, PDF si LibreOffice
est disponible, ZIP en masse, validation des champs obligatoires des
bureaux centraux).
