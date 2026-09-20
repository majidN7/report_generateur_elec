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
4. **Compléter le CIN** : chaque personne (président, vice-président, 3
   membres, 3 suppléants) doit avoir son numéro de carte d'identité
   nationale (CIN) pour que l'arrêté — ordinaire ou central — puisse être
   généré ; ça se saisit via *Modifier*. Un badge *Complet* / *À compléter*
   indique le statut sur les deux tableaux. (Seul le président du bureau
   central de rattachement — رئيس المكتب المركزي — reste éditable sur la
   fiche du bureau de vote, à titre informatif ; رقم المكتب المركزي et
   عنوان المكتب المركزي ont été retirés de l'application, l'arrêté
   ordinaire ne les mentionnant plus du tout.)
5. **Générer les arrêtés** :
   - Depuis une ligne du tableau : boutons *Word* / *PDF* pour un
     téléchargement unitaire (désactivés tant qu'il manque le CIN d'une
     personne).
   - *Générer tout (Word)* / *Générer tout (PDF)* : télécharge une archive
     ZIP contenant l'arrêté de chaque bureau complet (les bureaux incomplets
     sont ignorés et comptabilisés).
   - Le numéro de décision ("قرار عاملي رقم .........../2026") reste
     volontairement figé dans le document généré : ni l'API ni l'interface
     ne permettent de le renseigner (voir la décision de conception
     dédiée).

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

- **Deux modèles de documents, mis à jour le 19/09/2026 puis via BV.docx /
  BVC.docx, puis BV_2.docx / BVC_2.docx (20/09/2026)** : le fichier Word
  officiel fourni contient deux arrêtés types (bureaux de vote ordinaires
  et bureaux de vote centraux). Les modèles `docxtpl` actuels
  (`backend/app/templates_word/bureau_ordinaire.docx` et
  `bureau_central.docx`) proviennent de `BV_2.docx`/`BVC_2.docx`, la
  dernière version officielle — une révision de mise en forme/libellés de
  `BV.docx`/`BVC.docx` (retrait du "؛" superflu après le CIN de chaque
  membre/suppléant, ponctuation des "الفصل..." resserrée, un paragraphe vide
  ajouté avant la ligne de signature) qui garde exactement les mêmes champs
  dynamiques et le même en-tête statique ; seul le mapping des placeholders
  a été régénéré depuis ce nouveau fichier. Le fichier officiel précédent
  avait lui-même introduit deux changements par rapport aux versions plus
  anciennes :
  - chaque personne (président, vice-président, 3 membres, 3 suppléants)
    porte la mention "الحامل لبطاقة التعريف الوطنية رقم ..." (numéro de
    CIN) ; le 3ᵉ membre/suppléant est désigné "كاتب" / "نائب الكاتب" (clerc)
    — conservé en base sous les noms de colonnes `membre_3`/`suppleant_3`
    pour ne pas perturber les données déjà importées, seul le libellé
    affiché a changé ;
  - **l'arrêté ordinaire (BV) ne mentionne plus le bureau central de
    rattachement du tout** (la phrase "والتابع للمكتب المركزي رقم..." a
    disparu du modèle officiel) — voir la décision dédiée ci-dessous.
  Les pointillés du modèle ont été remplacés par des variables Jinja
  (`{{ president }}`, `{{ president_cin }}`, etc.), en conservant la mise en
  forme, l'en-tête et le logo institutionnel d'origine, **à l'exception
  explicite du numéro de décision** (voir ci-dessous). Le paragraphe
  introductif du Wali ("إن والي جهة...") reste également un texte fixe,
  identique au modèle officiel : ni la date du scrutin ni l'identité du Wali
  ne sont des champs dynamiques, ce point n'étant pas marqué comme tel dans
  le modèle fourni.
- **Normalisation d'un artefact de saisie dans `BVC_2.docx`** : le
  paragraphe "نائب لرئيس..." du bureau central contenait, dans le fichier
  officiel fourni, un caractère "…" isolé juste avant le blanc du nom (un
  reliquat de saisie visiblement non intentionnel — l'équivalent côté
  `BV_2.docx` n'a pas cette anomalie). Le script de génération du template
  (`build_bv2_bvc2.py`, script ponctuel non versionné) fusionne les
  séquences de points/points de suspension séparées par de simples espaces
  en un seul blanc avant d'y substituer un placeholder Jinja, ce qui évite
  de reproduire ce "…" orphelin dans le document généré ; tout le reste du
  texte (visas, articles, ponctuation) est repris tel quel.
- **Cachet officiel préservé sur la ligne de signature du BVC** : dans
  `BVC_2.docx`, l'image du cachet/sceau est ancrée dans le *même* run que
  le texte "الداخلة، في: ......." (contrairement à `BV_2.docx`, où elle
  occupe un paragraphe vide séparé, juste après la ligne de date). Une
  première régénération du template a reconstruit ce paragraphe sans tenir
  compte de l'image, la supprimant par erreur du document généré (le PDF du
  bureau central s'arrêtait juste après la date, sans cachet, contrairement
  au bureau ordinaire). Le script de génération du template a été corrigé
  pour repérer tout run contenant un `<w:drawing>`/`<w:pict>` et le laisser
  intact à sa position d'origine, en ne reconstruisant que les runs de
  texte autour de lui. Vérifié par rendu PDF réel (le cachet apparaît de
  nouveau sous la ligne de signature du bureau central, comme celle du
  bureau ordinaire).
- **Cachet identique et repositionné (20/09/2026) sur les deux modèles** :
  un nouvel envoi de `BVC.docx` a amélioré la taille et le positionnement
  du cachet (agrandi, décalé, passé devant le texte plutôt que derrière).
  Ce cachet exact (même image, même taille, même position) a été reporté
  sur `bureau_ordinaire.docx` également, pour que les deux documents
  affichent un cachet identique. Techniquement : l'image et l'élément
  `<w:drawing>` (avec ses attributs `wp:extent`/`wp:positionH`/
  `wp:positionV`/`behindDoc`) sont copiés tels quels du bureau central vers
  le bureau ordinaire — seule la relation `r:embed` est réécrite pour
  pointer vers l'image nouvellement ajoutée au paquet `.docx` cible
  (`document.part.get_or_add_image`), sans toucher à la taille ni à la
  position d'origine. Vérifié par rendu PDF réel sur les deux documents :
  le cachet ne chevauche aucun texte et reste entièrement dans le cadre de
  la page.
- **En-tête "قرار عاملي رقم .........../2026" strictement statique** : ce
  numéro de décision n'est **ni lu, ni injecté, ni exposé** nulle part dans
  l'application — sur demande explicite, il doit rester intact et non
  renseignable depuis l'interface. Concrètement : le paragraphe n'a aucun
  placeholder Jinja dans les deux modèles (les pointillés restent du texte
  brut) ; le champ `numero_decision` a été retiré des schémas Pydantic
  (`BureauVoteBase`/`Update`, `BureauCentralBase`/`Update`) et du contexte
  de rendu (`word_merge.py`), donc toute valeur envoyée via l'API est
  silencieusement ignorée (elle n'apparaît jamais dans la réponse) ; le
  champ a aussi été retiré des deux formulaires React. La colonne
  `numero_decision` reste présente en base (nullable, inerte) uniquement
  par prudence vis-à-vis d'éventuelles valeurs déjà enregistrées — elle
  n'est plus lue ni écrite par aucun chemin de code.
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
- **Rattachement au bureau central : ni importé, ni requis pour générer le
  BV** : le fichier `Base_Fusion_Bureaux_Vote__BV.xlsx` (format 2026) sépare
  les bureaux ordinaires et les bureaux centraux en deux feuilles
  indépendantes, et la feuille des bureaux ordinaires ne fournit plus رقم
  المكتب المركزي / رئيس المكتب المركزي du tout — un changement que le
  modèle `BV.docx` a confirmé et rendu définitif en supprimant purement et
  simplement la phrase "والتابع للمكتب المركزي رقم..." de l'arrêté
  ordinaire. En conséquence :
  - `numero_bureau_central`, `president_bureau_central` et
    `adresse_bureau_central` sont nullable sur `BureauVote` (migration
    `d5fbabc5576b`) et **ne conditionnent plus la génération de l'arrêté
    ordinaire** (retirés de `REQUIRED_VOTE_FIELDS` dans `word_merge.py`,
    seul le CIN de chaque personne reste requis) ;
  - l'import des bureaux de vote ne lit plus jamais ces colonnes — y
    compris pour l'ancien format à une seule feuille, qui les contient
    pourtant toujours : si présentes, elles sont ignorées, et l'import ne
    crée plus de fiches "bureau central" à partir de la feuille des
    bureaux de vote (`bureaux_centraux_created` reste à 0 pour cet import) ;
  - seul `president_bureau_central` (رئيس المكتب المركزي) reste éditable
    manuellement sur la fiche du bureau de vote, à titre purement
    informatif : `numero_bureau_central` et `adresse_bureau_central` ont
    été retirés des schémas Pydantic et de l'interface (voir le point
    suivant), n'apparaissant de toute façon plus dans le document généré.
  Les bureaux centraux s'importent désormais exclusivement via leur propre
  feuille/fichier dédié.
- **`numero_bureau_central` / `adresse_bureau_central` retirés de la fiche
  bureau de vote** : ces deux champs ne conditionnant déjà plus rien (voir
  ci-dessus) et ne figurant dans aucun des deux templates Word officiels,
  ils ont été retirés du formulaire, de la fiche détail et du schéma API
  (`BureauVoteBase`/`BureauVoteUpdate`) du bureau de vote — un payload qui
  les envoie encore est silencieusement ignoré, comme pour
  `numero_decision`. Les colonnes restent en base (nullables, inutilisées)
  pour ne pas perdre de données déjà importées. `president_bureau_central`
  n'est pas concerné et reste disponible. *(Ces deux champs, sous le même
  nom, existent aussi sur `BureauCentral` où ils décrivent le bureau
  central lui-même : cette décision ne les concerne pas.)*
- **Date de signature** : absente du fichier Excel, elle est éditable par
  enregistrement ; à défaut, l'application utilise la date du jour (au
  format arabe marocain, ex. "18 شتنبر 2026").
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
