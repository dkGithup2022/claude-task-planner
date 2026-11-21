from fastembed import TextEmbedding

from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding

# 차원을 확인하려고 만들 때 한 번 벡터로 바꿔 보는 글. 모델을 처음 읽는 시간도 이때 쓴다
DIMENSION_CHECK_TEXT = "준비"


class FastembedTextEmbedder(TextEmbedder):
    """fastembed (ONNX 로 도는 임베딩 모델, torch 없음) 로 글을 벡터로 바꾼다.

    처음 만들 때 모델 파일을 내려받아 FASTEMBED_CACHE_PATH (없으면 임시 폴더 아래) 에 두고 읽는다.
    시간이 걸려 앱에 하나만 둔다. 만들 때 모델이 내는 벡터 길이가 dimension 과 다르면 ValueError.
    """

    def __init__(self, model: str, dimension: int) -> None:
        self._model = model
        self._embedding = TextEmbedding(model)
        _check_dimension(model, dimension, len(self._vector_of(DIMENSION_CHECK_TEXT)))

    @property
    def enabled(self) -> bool:
        return True

    @property
    def model(self) -> str:
        return self._model

    def embed(self, text: str) -> MemoryEmbedding:
        return MemoryEmbedding(self._model, self._vector_of(text))

    def _vector_of(self, text: str) -> tuple[float, ...]:
        vector = next(iter(self._embedding.embed([text])))
        return tuple(float(value) for value in vector)


def _check_dimension(model: str, expected: int, actual: int) -> None:
    """설정한 차원과 모델이 내는 벡터 길이가 같은지. 다르면 서버가 뜨지 않게 에러를 낸다."""
    if actual != expected:
        raise ValueError(
            f"embedding dimension mismatch: model={model}, expected={expected}, actual={actual}"
        )
