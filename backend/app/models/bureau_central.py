from datetime import datetime, timezone

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BureauCentral(Base):
    """Un bureau de vote central. Importé exclusivement via sa propre
    feuille/fichier dédié (voir excel_import_central.py) — l'import des
    bureaux de vote (excel_import.py) ne crée plus de fiche à partir de
    ses colonnes. Les champs autres que le numéro/commune/président sont
    nullable et à compléter manuellement si l'import ne les fournit pas,
    requis pour générer l'arrêté (voir word_merge.py).
    """

    __tablename__ = "bureaux_centraux"
    __table_args__ = (
        UniqueConstraint("commune", "numero_bureau_central", name="uq_central_commune_numero"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    numero_bureau_central: Mapped[str] = mapped_column(String(50), index=True)
    commune: Mapped[str] = mapped_column(String(255), index=True)
    president_bureau_central: Mapped[str] = mapped_column(String(255))
    president_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    adresse_bureau_central: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vice_president_bureau_central: Mapped[str | None] = mapped_column(String(255), nullable=True)
    vice_president_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # membre_central_3 / suppleant_central_3 correspondent au rôle "كاتب"
    # (clerc/secrétaire) dans le modèle Word du 19/09/2026.
    membre_central_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    membre_central_1_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    membre_central_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    membre_central_2_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    membre_central_3: Mapped[str | None] = mapped_column(String(255), nullable=True)
    membre_central_3_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_central_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_1_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_central_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_2_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)
    suppleant_central_3: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_3_cin: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # numero_decision : colonne conservée pour compatibilité mais inutilisée,
    # voir la remarque équivalente dans bureau_vote.py.
    numero_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_signature: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
