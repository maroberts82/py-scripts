from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field

class Person(BaseModel):
    
    # Allows you to serialize and validate by field name or alias
    model_config = ConfigDict(populate_by_name=True) 
    
    # lambda allows an inner functions, an outside function could also be used
    id_: str = Field(alias="id", default_factory=lambda: str(uuid4()))
    first_name: str
    last_name: str
    age: int = 0