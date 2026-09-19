from pydantic import BaseModel


class BulkDeleteResponse(BaseModel):
    deleted: int
