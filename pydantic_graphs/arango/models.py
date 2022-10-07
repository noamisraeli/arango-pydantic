import uuid
import pydantic


class Document(pydantic.BaseModel):
    key: str = pydantic.Field(description="the key in the collection, must be unique in the collection", default_factory=lambda: str(uuid.uuid4()))

DocumentId = str

class DocumentResponse(pydantic.BaseModel):
    id: DocumentId
    
class Edge(Document):
    source: DocumentId
    destenation: DocumentId


