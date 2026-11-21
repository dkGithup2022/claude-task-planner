from functools import cache
from threading import Lock

from kiwipiepy import Kiwi

from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer

# 남기는 품사: 일반·고유 명사, 영문, 한자, 동사·형용사 어간.
# 의존 명사(것, 수), 숫자, 조사, 어미, 부호는 뺀다
KEPT_TAGS = frozenset({"NNG", "NNP", "SL", "SH", "VV", "VA"})


class KiwiTextTokenizer(TextTokenizer):
    """kiwipiepy 로 한국어 형태소를 나눈다.

    처음 만들 때 모델을 읽느라 1 초 남짓 걸려 앱에 하나만 둔다.
    """

    def __init__(self) -> None:
        self._kiwi = _shared_kiwi()

    def tokens(self, text: str) -> tuple[str, ...]:
        # 품사를 거른 뒤 영문은 소문자로. 불규칙 활용 표시(VV-I 등)는 앞의 품사로 본다
        if not text.strip():
            return ()
        with _KIWI_LOCK:
            morphemes = self._kiwi.tokenize(text)
        return tuple(
            _normalized(morpheme.form, morpheme.tag)
            for morpheme in morphemes
            if morpheme.tag.split("-")[0] in KEPT_TAGS
        )


def _normalized(form: str, tag: str) -> str:
    return form.lower() if tag == "SL" else form


_KIWI_LOCK = Lock()  # 요청 스레드 여럿이 같은 Kiwi 를 쓰므로 한 번에 하나씩 나눈다


@cache
def _shared_kiwi() -> Kiwi:
    """프로세스에 하나. 앱(컨테이너)을 여러 번 만들어도 모델을 한 번만 읽는다."""
    return Kiwi()
