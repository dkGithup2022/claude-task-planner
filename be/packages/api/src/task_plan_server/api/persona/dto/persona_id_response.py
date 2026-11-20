from pydantic import BaseModel, Field


class PersonaIdResponse(BaseModel):
    persona_id: int = Field(description="페르소나 id", examples=[2])
