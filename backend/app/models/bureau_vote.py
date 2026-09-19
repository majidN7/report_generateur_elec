from datetime import datetime, timezone

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BureauVote(Base):
    """Un bureau de vote ordinaire (une ligne du fichier Excel importé)."""

    __tablename__ = "bureaux_vote"
    __table_args__ = (UniqueConstraint("commune", "numero_bureau", name="uq_bureau_commune_numero"),)

    id: Mapped[int] = mapped_column(primary_key=True)

    numero_bureau: Mapped[str] = mapped_column(String(50), index=True)
    commune: Mapped[str] = mapped_column(String(255), index=True)
    adresse_bureau: Mapped[str] = mapped_column(String(500))
    president: Mapped[str] = mapped_column(String(255))
    president_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    vice_president: Mapped[str] = mapped_column(String(255))
    vice_president_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Nullable : l'import des bureaux de vote (excel_import.py) ne lit plus
    # رقم المكتب المركزي / رئيس المكتب المركزي, quel que soit le format
    # (même l'ancien format à une seule feuille, qui contient pourtant ces
    # colonnes). Le rattachement se saisit à la main. Optionnel au stockage,
    # mais requis pour générer l'arrêté (voir word_merge.py), comme le CIN.
    numero_bureau_central: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)
    president_bureau_central: Mapped[str | None] = mapped_column(String(255), nullable=True)
    adresse_bureau_central: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # membre_3 / suppleant_3 correspondent au rôle "كاتب" (clerc/secrétaire)
    # dans le modèle Word du 19/09/2026, conservés sous ce nom de colonne pour
    # ne pas casser les données déjà importées.
    membre_1: Mapped[str] = mapped_column(String(255))
    membre_1_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    membre_2: Mapped[str] = mapped_column(String(255))
    membre_2_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    membre_3: Mapped[str] = mapped_column(String(255))
    membre_3_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_1: Mapped[str] = mapped_column(String(255))
    suppleant_1_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_2: Mapped[str] = mapped_column(String(255))
    suppleant_2_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_3: Mapped[str] = mapped_column(String(255))
    suppleant_3_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)

    numero_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_signature: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
