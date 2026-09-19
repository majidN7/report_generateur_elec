from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BureauCentralBase(BaseModel):
    numero_bureau_central: str = Field(..., min_length=1, max_length=50)
    commune: str = Field(..., min_length=1, max_length=255)
    president_bureau_central: str = Field(..., min_length=1, max_length=255)
    president_cin: str | None = Field(None, max_length=50)
    adresse_bureau_central: str | None = Field(None, max_length=500)
    vice_president_bureau_central: str | None = Field(None, max_length=255)
    vice_president_cin: str | None = Field(None, max_length=50)
    membre_central_1: str | None = Field(None, max_length=255)
    membre_central_1_cin: str | None = Field(None, max_length=50)
    membre_central_2: str | None = Field(None, max_length=255)
    membre_central_2_cin: str | None = Field(None, max_length=50)
    membre_central_3: str | None = Field(None, max_length=255)
    membre_central_3_cin: str | None = Field(None, max_length=50)
    suppleant_central_1: str | None = Field(None, max_length=255)
    suppleant_central_1_cin: str | None = Field(None, max_length=50)
    suppleant_central_2: str | None = Field(None, max_length=255)
    suppleant_central_2_cin: str | None = Field(None, max_length=50)
    suppleant_central_3: str | None = Field(None, max_length=255)
    suppleant_central_3_cin: str | None = Field(None, max_length=50)
    # Le numéro de décision reste un texte fixe du modèle officiel :
    # volontairement absent de ce schéma (voir bureau_vote.py).
    date_signature: str | None = Field(None, max_length=100)


class BureauCentralCreate(BureauCentralBase):
    pass


class BureauCentralUpdate(BaseModel):
    numero_bureau_central: str | None = Field(None, min_length=1, max_length=50)
    commune: str | None = Field(None, min_length=1, max_length=255)
    president_bureau_central: str | None = Field(None, min_length=1, max_length=255)
    president_cin: str | None = Field(None, max_length=50)
    adresse_bureau_central: str | None = Field(None, max_length=500)
    vice_president_bureau_central: str | None = Field(None, max_length=255)
    vice_president_cin: str | None = Field(None, max_length=50)
    membre_central_1: str | None = Field(None, max_length=255)
    membre_central_1_cin: str | None = Field(None, max_length=50)
    membre_central_2: str | None = Field(None, max_length=255)
    membre_central_2_cin: str | None = Field(None, max_length=50)
    membre_central_3: str | None = Field(None, max_length=255)
    membre_central_3_cin: str | None = Field(None, max_length=50)
    suppleant_central_1: str | None = Field(None, max_length=255)
    suppleant_central_1_cin: str | None = Field(None, max_length=50)
    suppleant_central_2: str | None = Field(None, max_length=255)
    suppleant_central_2_cin: str | None = Field(None, max_length=50)
    suppleant_central_3: str | None = Field(None, max_length=255)
    suppleant_central_3_cin: str | None = Field(None, max_length=50)
    date_signature: str | None = Field(None, max_length=100)


class BureauCentralOut(BureauCentralBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BureauCentralPage(BaseModel):
    items: list[BureauCentralOut]
    total: int
    page: int
    page_size: int
