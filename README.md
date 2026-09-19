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
- [Formats Excel pris en charge](#formats-excel-pris-en-charge-import-principal)
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
   *Importer Excel*. Deux formats sont acceptés dans le même fichier
   (voir [Formats Excel pris en charge](#formats-excel-pris-en-charge)) :
   l'ancien fichier à une seule feuille, ou le nouveau modèle 2026 à deux
   feuilles séparées (bureaux ordinaires + bureaux centraux, tous deux avec
   CIN) — les deux feuilles sont importées automatiquement en une seule
   opération. Un rapport d'import indique les lignes créées, mises à jour,
   les doublons ignorés et les erreurs de validation.
2. **Gérer les bureaux** : recherchez, filtrez par commune, triez, consultez
   le détail, modifiez ou supprimez un enregistrement, ou ajoutez-en un
   manuellement.
3. **Gérer les bureaux centraux** : ils s'importent exclusivement via leur
   propre feuille/fichier dédié (l'import des bureaux de vote ne les crée
   plus, voir plus bas) :
   - le **fichier Excel dédié aux bureaux centraux** (bouton *Importer
     Excel* de l'onglet *Bureaux centraux*, ou directement via la feuille
     `مكاتب التصويت المركزية` du nouveau format 2026), qui alimente en une
     fois le président, le vice-président, les 3 membres, les 3 suppléants,
     l'adresse et le CIN de chacun ;
   - ou manuellement, via *+ Ajouter un bureau central* / *Modifier* dans
     l'onglet *Bureaux centraux*.
   Un badge *À compléter* / *Complet* indique si l'arrêté peut être généré.
4. **Compléter le CIN et le rattachement au bureau central** : depuis le
   modèle Word du 19/09/2026, chaque personne (président, vice-président, 3
   membres, 3 suppléants) doit avoir son numéro de carte d'identité
   nationale (CIN) pour que l'arrêté — ordinaire ou central — puisse être
   généré. De plus, l'import des bureaux de vote (quel que soit le format)
   ne fournit plus le numéro et le président du bureau central de
   rattachement (رقم المكتب المركزي / رئيس المكتب المركزي) : ces deux
   champs, comme le CIN, se saisissent via *Modifier*. Un badge *Complet* /
   *À compléter* indique le statut sur les deux tableaux.
5. **Générer les arrêtés** :
   - Depuis une ligne du tableau : boutons *Word* / *PDF* pour un
     téléchargement unitaire (désactivés tant qu'il manque le CIN d'une
     personne ou, pour un bureau ordinaire, son rattachement au bureau
     central).
   - *Générer tout (Word)* / *Générer tout (PDF)* : télécharge une archive
     ZIP contenant l'arrêté de chaque bureau complet (les bureaux incomplets
     sont ignorés et comptabilisés).

## Formats Excel pris en charge (import principal)

L'endpoint `POST /api/import/excel` détecte automatiquement le format du
fichier envoyé :

- **Format historique** (une seule feuille, ex. `Donnees_Fusion`) :
  الرئيس, نائب الرئيس, رقم مكتب التصويت, الجماعة, عنوان مكتب التصويت,
  membres/suppléants 1 à 3, plus les 8 colonnes CIN optionnelles (`بطاقة
  التعريف الوطنية <rôle>`).
- **Format 2026** (`Base_Fusion_Bureaux_Vote__BV.xlsx`), reconnu à la
  présence d'une feuille nommée `رؤساء وأعضاء مكاتب التصويت` et/ou `مكاتب
  التصويت المركزية` : chaque feuille est importée dans la table
  correspondante (bureaux de vote / bureaux centraux), toutes deux avec le
  CIN de chaque personne.

**Important** : dans les deux formats, l'import des bureaux de vote ne lit
plus les colonnes رقم المكتب المركزي / رئيس المكتب المركزي, même si elles
sont présentes dans le fichier (cas de l'ancien format) — voir la décision
de conception ci-dessous. Le rattachement à un bureau central se saisit
donc systématiquement à la main, via *Modifier*.

Dans les deux formats, une ligne dupliquée (même commune + même numéro) au
sein du fichier est comptabilisée en doublon ignoré, et une ligne déjà
présente en base est mise à jour (upsert).

## Import dédié des bureaux centraux

Les bureaux centraux s'importent exclusivement via cette voie (l'import des
bureaux de vote ne crée plus de fiche "bureau central", voir la décision de
conception ci-dessous) : soit la feuille `مكاتب التصويت المركزية` du
nouveau format 2026 (traitée automatiquement par l'import principal), soit
le bouton dédié *Importer Excel* de l'onglet *Bureaux centraux*
(`POST /api/bureaux-centraux/import`) pour un fichier à part. Les deux
partagent le même mapping de colonnes (en-têtes exacts du modèle Excel
officiel) :

| Colonne (obligatoire) | Champ                     |
|------------------------|----------------------------|
| رئيس المكتب المركزي   | Président                  |
| رقم المكتب المركزي    | Numéro du bureau central   |
| الجماعة               | Commune                    |

| Colonne (optionnelle)                              | Champ                     |
|------------------------------------------------------|----------------------------|
| بطاقة التعريف الوطنية رئيس المكتب المركزي           | CIN du président           |
| عنوان مكتب التصويت                                  | Adresse                    |
| نائب رئيس المكتب المركزي                            | Vice-président             |
| بطاقة التعريف الوطنية نائب رئيس المكتب المركزي      | CIN du vice-président      |
| العضو الأول / الثاني / الثالث                       | Membres 1, 2 et 3          |
| بطاقة التعريف الوطنية عضو الأول / الثاني / الثالث   | CIN des membres 1, 2 et 3  |
| نائب العضو الأول / الثاني / الثالث                  | Suppléants 1, 2 et 3       |
| بطاقة التعريف الوطنية نائب العضو الأول / الثاني / الثالث | CIN des suppléants 1, 2 et 3 |

Le rapprochement se fait par (commune, numéro de bureau central) : une
fiche existante est complétée/mise à jour, une fiche absente est créée
directement — cet import ne dépend donc pas d'un import préalable des
bureaux de vote. Une cellule optionnelle laissée vide ne réinitialise pas
une valeur déjà enregistrée. **Si vos en-têtes réels diffèrent** de ce
tableau, ajustez `COLUMN_MAP` dans
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
- **Bureaux centraux = import dédié, génération bloquée tant qu'incomplet** :
  les bureaux centraux ne sont plus jamais déduits ou stubés depuis l'import
  des bureaux de vote (voir point suivant) — ils viennent exclusivement de
  leur propre feuille/fichier dédié (voir *Import dédié des bureaux
  centraux* ci-dessus). Tant que le président, le vice-président, les 3
  membres, les 3 suppléants, l'adresse ou un CIN manquent, la génération de
  l'arrêté est bloquée avec un message d'erreur explicite listant les
  champs manquants.
- **Rattachement au bureau central retiré de l'import des bureaux de vote** :
  le fichier `Base_Fusion_Bureaux_Vote__BV.xlsx` (format 2026) sépare les
  bureaux ordinaires et les bureaux centraux en deux feuilles indépendantes,
  et la feuille des bureaux ordinaires ne fournit plus رقم المكتب المركزي /
  رئيس المكتب المركزي du tout. `numero_bureau_central` et
  `president_bureau_central` sont donc devenus nullable sur `BureauVote`
  (migration `d5fbabc5576b`), suivant le même principe que le CIN :
  optionnels au stockage, mais requis pour générer l'arrêté
  (`MissingFieldsError`, 422, message explicite). Suite à cela, l'import des
  bureaux de vote a été simplifié pour ne plus jamais lire ces deux colonnes
  — y compris pour l'ancien format à une seule feuille, qui les contient
  pourtant toujours : si présentes, elles sont désormais ignorées. Ce choix
  uniformise le comportement des deux formats (le rattachement se saisit
  systématiquement à la main, via *Modifier*) et l'import ne crée plus de
  fiches "bureau central" à partir de la feuille des bureaux de vote
  (`bureaux_centraux_created` reste toujours à 0 pour cet import) : les
  bureaux centraux s'importent désormais exclusivement via leur propre
  feuille/fichier dédié.
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
| DELETE  | `/api/bureaux/all`                 | Supprimer tous les bureaux de vote (irréversible) |
| DELETE  | `/api/bureaux-centraux/all`        | Supprimer tous les bureaux centraux (irréversible) |

Le bouton *Supprimer tout* de chaque onglet appelle l'un de ces deux
endpoints après confirmation explicite (le nombre d'enregistrements est
affiché dans la boîte de dialogue) ; les deux tables sont indépendantes,
supprimer les bureaux de vote n'efface pas les bureaux centraux et
inversement.

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
