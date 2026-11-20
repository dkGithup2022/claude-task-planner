"""Alembic 과 테스트가 Base.metadata 를 완성하기 위해 import 하는 레지스트리.

add-entity-specs 스킬이 도메인 Entity 모듈을 한 줄씩 append 한다.
예: from .article.article_entity import ArticleEntity  # noqa: F401
"""

from .memory.memory_entity import MemoryEntity  # noqa: F401
from .memory.memory_persona_entity import MemoryPersonaEntity  # noqa: F401
from .memory.memory_source_entity import MemorySourceEntity  # noqa: F401
from .persona.persona_entity import PersonaEntity  # noqa: F401
from .plan.plan_entity import PlanEntity  # noqa: F401
from .plan.plan_persona_entity import PlanPersonaEntity  # noqa: F401
from .plan_edge.plan_edge_entity import PlanEdgeEntity  # noqa: F401
from .plan_node.plan_node_entity import PlanNodeEntity  # noqa: F401
from .plan_node.plan_node_persona_entity import PlanNodePersonaEntity  # noqa: F401
