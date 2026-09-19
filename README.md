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
3. **Compléter les bureaux centraux** : l'import du fichier principal crée
   automatiquement une fiche par bureau central référencé (numéro +
   président seulement). Il existe deux façons de la compléter :
   - manuellement, via *Modifier* dans l'onglet *Bureaux centraux* ;
   - en important un **fichier Excel dédié aux bureaux centraux** (bouton
     *Importer Excel* de l'onglet *Bureaux centraux*), qui alimente en une
     fois le vice-président, les 3 membres, les 3 suppléants et l'adresse
     pour tous les bureaux centraux du fichier (voir colonnes attendues
     ci-dessous). Cet import fonctionne aussi de façon autonome : un bureau
     central qui n'existe pas encore est créé directement à partir de ce
     fichier, sans dépendre d'un import préalable des bureaux de vote.
   Un badge *À compléter* / *Complet* indique si l'arrêté peut être généré.
4. **Compléter le CIN de chaque personne** : depuis le modèle Word du
   19/09/2026, chaque personne (président, vice-président, 3 membres, 3
   suppléants) doit avoir son numéro de carte d'identité nationale (CIN)
   pour que l'arrêté — ordinaire ou central — puisse être généré. C'est une
   donnée absente du fichier Excel actuel : elle se saisit via *Modifier*
   (ou un futur import Excel étendu, voir plus bas). Un badge *Complet* /
   *CIN manquant(s)* indique le statut sur les deux tableaux.
5. **Générer les arrêtés** :
   - Depuis une ligne du tableau : boutons *Word* / *PDF* pour un
     téléchargement unitaire (désactivés tant que le CIN de chaque personne
     n'est pas renseigné).
   - *Générer tout (Word)* / *Générer tout (PDF)* : télécharge une archive
     ZIP contenant l'arrêté de chaque bureau complet (les bureaux dont un
     CIN manque sont ignorés et comptabilisés).

## Import dédié des bureaux centraux

En plus de la création automatique de fiches "bureau central" lors de
l'import principal, l'onglet *Bureaux centraux* propose son propre bouton
*Importer Excel* (`POST /api/bureaux-centraux/import`) pour un fichier
dédié à ces bureaux. Colonnes attendues dans la feuille de données
(idéalement nommée `Bureaux_Centraux`) :

| Colonne (obligatoire)         | Champ                            |
|--------------------------------|-----------------------------------|
| الجماعة                        | Commune                           |
| رقم المكتب المركزي             | Numéro du bureau central          |
| رئيس المكتب المركزي            | Président                         |

| Colonne (optionnelle)                | Champ                        |
|----------------------------------------|-------------------------------|
| عنوان المكتب المركزي                  | Adresse                       |
| نائب رئيس المكتب المركزي              | Vice-président                |
| العضو الأول / الثاني / كاتب           | Membres 1, 2 et 3 (clerc)     |
| نائب العضو الأول / الثاني / نائب الكاتب | Suppléants 1, 2 et 3        |
| رقم البطاقة الوطنية - الرئيس / نائب الرئيس / العضو الأول / العضو الثاني / كاتب / نائب العضو الأول / نائب العضو الثاني / نائب الكاتب | CIN de chaque personne (8 colonnes) |

Le rapprochement se fait par (commune, numéro de bureau central) : une
fiche existante (même auto-créée en stub) est complétée/mise à jour, une
fiche absente est créée directement — cet import ne dépend donc pas d'un
import préalable des bureaux de vote. Une cellule optionnelle laissée vide
ne réinitialise pas une valeur déjà enregistrée. **Si vos en-têtes réels
diffèrent** de ce tableau, ajustez `COLUMN_MAP` dans
`backend/app/services/excel_import_central.py` (aucune migration requise,
ce sont des colonnes déjà présentes dans le modèle `BureauCentral`).

## Décisions de conception importantes

- **Deux modèles de documents, mis à jour le 19/09/2026** : le fichier Word
  officiel fourni contient deux arrêtés types (bureaux de vote ordinaires et
  bureaux de vote centraux). La version actuelle des deux modèles
  `docxtpl` (`backend/app/templates_word/bureau_ordinaire.docx` et
  `bureau_central.docx`) est générée depuis le modèle officiel daté du
  19/09/2026, qui a introduit deux changements structurels par rapport à la
  version précédente :
  - chaque personne (président, vice-président, 3 membres, 3 suppléants)
    porte désormais la mention "الحامل لبطاقة التعريف الوطنية رقم ..."
    (numéro de CIN) ;
  - le 3ᵉ membre/suppléant est désormais désigné "كاتب" / "نائب الكاتب"
    (clerc) plutôt qu'un "3ᵉ membre" générique — conservé en base sous les
    noms de colonnes `membre_3`/`suppleant_3` pour ne pas perturber les
    données déjà importées, seul le libellé affiché a changé.
  Les pointillés du modèle ont été remplacés par des variables Jinja
  (`{{ president }}`, `{{ president_cin }}`, etc.), en conservant la mise en
  forme, l'en-tête et le logo institutionnel d'origine. Le paragraphe
  introductif du Wali ("إن والي جهة...") reste un texte fixe, identique au
  modèle officiel : ni la date du scrutin ni l'identité du Wali ne sont
  actuellement des champs dynamiques, ce point n'étant pas marqué comme tel
  dans le modèle fourni.
- **CIN obligatoire avant génération, pas à la création** : le numéro de
  CIN de chaque personne est une donnée entièrement nouvelle, absente du
  fichier Excel principal actuel et des bureaux déjà importés. Il est donc
  stocké en base comme optionnel (comme l'adresse ou le vice-président des
  bureaux centraux), mais requis pour générer un arrêté — ordinaire ou
  central : les boutons Word/PDF sont désactivés et la génération en masse
  ignore silencieusement (en le comptabilisant) tout bureau où un CIN
  manque, avec un message d'erreur listant précisément les champs
  manquants.
- **Bureaux centraux = fiches à compléter (ou import dédié)** : le fichier
  Excel principal ne contient, pour chaque bureau central, que son numéro et
  le nom de son président (ces informations apparaissent répétées sur
  chaque ligne des bureaux ordinaires qui lui sont rattachés). Il ne fournit
  ni son vice-président, ni ses membres/suppléants, ni son adresse propre.
  Plutôt que d'inventer ces données, l'application crée automatiquement une
  fiche "bureau central" (dédupliquée par commune + numéro) lors de l'import
  principal et bloque la génération de son arrêté tant que ces champs n'ont
  pas été renseignés — manuellement, ou via l'import Excel dédié décrit
  ci-dessus — avec un message d'erreur explicite listant les champs
  manquants.
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
| POST    | `/api/bureaux-centraux/import`     | Import dédié du fichier Excel des bureaux centraux |

Documentation interactive complète (Swagger) disponible sur `/docs` une fois
le backend démarré.

## Tests

```bash
cd backend
pytest
```

Les tests couvrent l'import Excel principal et l'import dédié des bureaux
centraux (succès, doublons, upsert, validation), le CRUD des bureaux et la
génération de documents (Word, PDF si LibreOffice est disponible, ZIP en
masse, validation des champs obligatoires des bureaux centraux).

**Migration de base de données** : l'import dédié des bureaux centraux
réutilise intégralement les colonnes déjà présentes sur `BureauCentral`
(ajoutées dès la première version) ; aucune nouvelle migration Alembic
n'était nécessaire pour cette fonctionnalité.
