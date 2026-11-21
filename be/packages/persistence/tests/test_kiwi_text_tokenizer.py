"""KiwiTextTokenizer: 검색에 쓸 품사만 남기고 영문은 소문자로."""

from task_plan_server.persistence.memory.kiwi_text_tokenizer import KiwiTextTokenizer


def test_keeps_nouns_english_and_verb_stems_only() -> None:
    sentence = "문서를 만드는 계획에서는 검토를 마지막 노드로 따로 두지 않는다"
    tokens = KiwiTextTokenizer().tokens(sentence)

    # 보조 용언(VX, 여기서는 "않" 과 kiwi 가 VX 로 본 "만들") 은 남기지 않는다
    assert tokens == ("문서", "계획", "검토", "마지막", "노드", "두")


def test_drops_particles_numbers_and_dependent_nouns_and_lowers_english() -> None:
    tokens = KiwiTextTokenizer().tokens("API 설계에서 정한 것은 3개의 REST 규칙이다")

    assert "api" in tokens and "rest" in tokens and "설계" in tokens
    assert not {"API", "에서", "것", "3", "개"} & set(tokens)


def test_returns_empty_for_blank_text() -> None:
    assert KiwiTextTokenizer().tokens("   ") == ()
