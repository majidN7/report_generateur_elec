from pydantic import BaseModel


class ImportRowError(BaseModel):
    row: int
    message: str


class ImportReport(BaseModel):
    total_rows: int
    created: int
    updated: int
    skipped_duplicates: int
    errors: list[ImportRowError]
    bureaux_centraux_created: int
