from datetime import datetime, timezone

from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class BureauCentral(Base):
    """Un bureau de vote central. Les colonnes "membres"/"nom du vice-président"
    n'existent pas dans le fichier Excel source (qui ne fournit que le numéro
    et le président du bureau central rattachés à chaque bureau ordinaire) :
    ces enregistrements sont donc auto-créés (stubs) lors de l'import puis
    complétés manuellement par l'utilisateur avant de pouvoir générer l'arrêté
    du bureau central.
    """

    __tablename__ = "bureaux_centraux"
    __table_args__ = (
        UniqueConstraint("commune", "numero_bureau_central", name="uq_central_commune_numero"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    numero_bureau_central: Mapped[str] = mapped_column(String(50), index=True)
    commune: Mapped[str] = mapped_column(String(255), index=True)
    president_bureau_central: Mapped[str] = mapped_column(String(255))
    adresse_bureau_central: Mapped[str | None] = mapped_column(String(500), nullable=True)
    vice_president_bureau_central: Mapped[str | None] = mapped_column(String(255), nullable=True)

    membre_central_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    membre_central_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    membre_central_3: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_1: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    suppleant_central_3: Mapped[str | None] = mapped_column(String(255), nullable=True)

    numero_decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date_signature: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc)
    )
