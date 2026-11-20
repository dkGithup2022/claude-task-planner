# tpm-trial mock 데이터

`/Users/dankim/orca/workspaces/productivility/tpm-trial/mock/` 를 2026-11-20 에 복사했다. 서버 응답과 같은 모양이다.

- `personas.json`: 페르소나 2개
- `memories.json`: 지식 7개 (시각 필드 없음)
- `plans/11.json`: 계획 11, 노드 10개, 간선 29개
- `ids.json`: mock 이 마지막으로 준 번호 (계획 11, 노드 56, 간선 108)

서버 DB 에 넣기: `uv run python scripts/import_mock_data.py` (be/ 에서. DB 가 비어 있어야 한다)
