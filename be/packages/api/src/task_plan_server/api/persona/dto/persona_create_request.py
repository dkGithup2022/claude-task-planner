from pydantic import BaseModel, Field


class PersonaCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255, description="이름. 같은 이름은 둘 수 없다")
    description: str = Field(description="설명. 빈 값도 된다")
