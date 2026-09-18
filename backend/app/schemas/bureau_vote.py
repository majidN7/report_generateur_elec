from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class BureauVoteBase(BaseModel):
    numero_bureau: str = Field(..., min_length=1, max_length=50)
    commune: str = Field(..., min_length=1, max_length=255)
    adresse_bureau: str = Field(..., min_length=1, max_length=500)
    president: str = Field(..., min_length=1, max_length=255)
    vice_president: str = Field(..., min_length=1, max_length=255)

    numero_bureau_central: str = Field(..., min_length=1, max_length=50)
    president_bureau_central: str = Field(..., min_length=1, max_length=255)
    adresse_bureau_central: str | None = Field(None, max_length=500)

    membre_1: str = Field(..., min_length=1, max_length=255)
    membre_2: str = Field(..., min_length=1, max_length=255)
    membre_3: str = Field(..., min_length=1, max_length=255)
    suppleant_1: str = Field(..., min_length=1, max_length=255)
    suppleant_2: str = Field(..., min_length=1, max_length=255)
    suppleant_3: str = Field(..., min_length=1, max_length=255)

    numero_decision: str | None = Field(None, max_length=50)
    date_signature: str | None = Field(None, max_length=100)


class BureauVoteCreate(BureauVoteBase):
    pass


class BureauVoteUpdate(BaseModel):
    numero_bureau: str | None = Field(None, min_length=1, max_length=50)
    commune: str | None = Field(None, min_length=1, max_length=255)
    adresse_bureau: str | None = Field(None, min_length=1, max_length=500)
    president: str | None = Field(None, min_length=1, max_length=255)
    vice_president: str | None = Field(None, min_length=1, max_length=255)
    numero_bureau_central: str | None = Field(None, min_length=1, max_length=50)
    president_bureau_central: str | None = Field(None, min_length=1, max_length=255)
    adresse_bureau_central: str | None = Field(None, max_length=500)
    membre_1: str | None = Field(None, min_length=1, max_length=255)
    membre_2: str | None = Field(None, min_length=1, max_length=255)
    membre_3: str | None = Field(None, min_length=1, max_length=255)
    suppleant_1: str | None = Field(None, min_length=1, max_length=255)
    suppleant_2: str | None = Field(None, min_length=1, max_length=255)
    suppleant_3: str | None = Field(None, min_length=1, max_length=255)
    numero_decision: str | None = Field(None, max_length=50)
    date_signature: str | None = Field(None, max_length=100)


class BureauVoteOut(BureauVoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BureauVotePage(BaseModel):
    items: list[BureauVoteOut]
    total: int
    page: int
    page_size: int
