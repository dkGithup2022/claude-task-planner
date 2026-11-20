"""NodeSpec: 노드 정의서 md 를 절로 읽고, 같은 모양으로 되돌린다."""

from task_plan_manager.model.plan.node_spec import NodeSpec

MAKE_PLAN_MD = (
    "### 하는 일\n댓글 테이블을 설계한다.\n\n"
    "### 산출물\n- 형태: 코드 변경\n마이그레이션 1개\n인덱스 (notice_id, created_at)\n\n"
    "### 그 외 설명\n- 외래 키는 걸지 않는다.\n- 타입은 기존 PK 와 맞춘다."
)


def test_should_read_sections_and_write_back_same_md():
    spec = NodeSpec.from_md(MAKE_PLAN_MD)
    assert spec == NodeSpec(
        does="댓글 테이블을 설계한다.",
        output_form="코드 변경",
        output_contents="마이그레이션 1개\n인덱스 (notice_id, created_at)",
        notes="- 외래 키는 걸지 않는다.\n- 타입은 기존 PK 와 맞춘다.",
    )
    assert spec.to_md() == MAKE_PLAN_MD


def test_should_treat_placeholders_as_empty_and_write_them_back():
    md = "### 하는 일\n한다\n\n### 산출물\n- 형태: (정하지 않음)\n\n### 그 외 설명\n(없음)"
    spec = NodeSpec.from_md(md)
    assert (spec.output_form, spec.output_contents, spec.notes) == ("", "", "")
    assert spec.to_md() == md


def test_should_keep_text_without_headers_and_extra_sections():
    assert NodeSpec.from_md("README 를 쓴다").does == "README 를 쓴다"
    spec = NodeSpec.from_md("### 하는 일\n한다\n\n### 산출물\n표 하나\n\n### 참고\n링크")
    assert (spec.output_form, spec.output_contents) == ("", "표 하나")
    assert spec.to_md().endswith("### 그 외 설명\n(없음)\n\n### 참고\n링크")


def test_should_not_lose_text_before_headers_or_repeated_sections():
    spec = NodeSpec.from_md("목표: 빠르게\n\n### 하는 일\n한다\n\n### 참고\nR1\n\n### 참고\nR2")
    assert spec.does == "목표: 빠르게\n\n한다"
    assert spec.extra_md == "### 참고\nR1\n\nR2"
