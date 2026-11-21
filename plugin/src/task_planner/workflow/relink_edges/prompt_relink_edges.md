## 목적
계획의 일부 노드가 생기거나 바뀌었습니다. 바뀐 노드와 그 앞뒤 노드 사이의 간선을 다시 정합니다.
간선 A → B 는 B 가 A 의 산출물을 받아야 시작할 수 있다는 뜻입니다.

## 배경
계획을 실행하는 단위 하나를 노드(node), 노드 사이의 선후행 관계를 간선(edge)으로 나타냅니다.
노드마다 제목, 종류(document / research / code / hitl), 정의서(하는 일, 산출물, 그 외 설명)가 있습니다. hitl 은 사용자가 확인하는 노드입니다.
앞 단계에서 큰 작업을 여러 노드로 분해하거나, 노드를 넣고 빼고 합쳤습니다. 이 프롬프트는 그 뒤의 선후행 관계를 다시 올바르게 정합니다.
아래 판단 기준에 맞는 간선 배열을 돌려줍니다.

## 입력
JSON 하나입니다.
- change: 무엇을 바꿨는지 한 줄
- original_nodes: 이번에 지워지거나 바뀌기 전의 노드. 없으면 []
- changed_nodes: 이번에 생기거나 바뀐 노드. 나눈 경우 나뉜 노드 전부
- neighbor_nodes: 바뀌기 전에 원래 노드의 선행·후행이던 노드 (한 단계만)
- previous_edges: 바뀌기 전, 위 노드들 사이의 간선
- user_edges: 사용자가 직접 잇거나(link) 끊으라고(unlink) 한 간선
- fixed_edges: 그대로 남는 간선. 판단할 때 참고만 하고 다시 정하지 않습니다. 없으면 []

노드 하나의 모양: id, title, kind, does(하는 일), output(산출물의 form 과 contents), notes(그 외 설명)

처음 계획을 만들 때는 모든 노드가 changed_nodes 이고, original_nodes 와 neighbor_nodes 는 비어 있습니다.

## 판단 기준
계획을 수행할 때, 다음 노드를 수행하는 데 이전 노드의 결과가 필요하면 잇습니다.
- 뒤 노드가 앞 노드의 산출물을 실제로 받아 써야 할 때만 잇습니다. 노드의 does 와 output 을 보고 판단합니다.
- 원래 노드로 들어오던 간선은, 분해된 노드 가운데 그 산출물을 받아 써야 하는 노드로 옮깁니다. 원래 노드에서 나가던 간선은 그 산출물을 만드는 노드에서 잇습니다.
- 바뀌지 않은 앞뒤 노드끼리의 간선도 다시 봅니다. 사이에 노드가 들어왔어도, 뒤 노드가 앞 노드의 산출물을 직접 써야 하면 남깁니다.
- 사용자가 정한 간선은 그대로 둡니다. link 는 남기고, unlink 는 다시 잇지 않습니다.
- 간선을 따라가다 처음 노드로 돌아오는 순환을 만들지 않습니다.

예시를 참고합니다.

## 예시 1: 나누기

입력
```json
{
  "change": "39 \"댓글 화면 구현\" 을 41, 42, 43 으로 나눔",
  "original_nodes": [
    {"id": 39, "title": "댓글 화면 구현", "kind": "code",
     "does": "공지 상세 화면에 댓글 목록, 작성, 수정, 삭제 화면을 만들고 댓글 API 와 연결한다.",
     "output": {"form": "코드 변경", "contents": "공지 상세 화면의 댓글 영역 컴포넌트와 API 호출 코드"},
     "notes": "로그인하지 않은 사용자에게는 입력창 대신 로그인 안내를 보인다."}
  ],
  "changed_nodes": [
    {"id": 41, "title": "댓글 영역 와이어프레임", "kind": "document",
     "does": "댓글 목록, 입력창, 수정·삭제 버튼의 배치와 로그인·본인 여부에 따른 표시를 와이어프레임으로 잡는다.",
     "output": {"form": "문서", "contents": "댓글 영역 와이어프레임과 상태별 표시 규칙"},
     "notes": "기존 공지 상세 화면의 배치를 따른다."},
    {"id": 42, "title": "댓글 UI 컴포넌트 구현", "kind": "code",
     "does": "와이어프레임대로 댓글 목록과 입력 컴포넌트를 만든다. 데이터는 아직 가짜 값으로 채운다.",
     "output": {"form": "코드 변경", "contents": "댓글 목록·입력·수정 컴포넌트"},
     "notes": ""},
    {"id": 43, "title": "댓글 UI와 API 연결", "kind": "code",
     "does": "컴포넌트에서 댓글 API 를 불러 목록, 작성, 수정, 삭제가 실제로 동작하게 한다.",
     "output": {"form": "코드 변경", "contents": "API 호출 코드와 오류 처리"},
     "notes": "로그인하지 않은 사용자에게는 입력창 대신 로그인 안내를 보인다."}
  ],
  "neighbor_nodes": [
    {"id": 35, "title": "프론트 공지 상세 화면 구조 파악", "kind": "research",
     "does": "공지 상세 화면의 컴포넌트 구조와 상태 관리 방식을 조사한다.",
     "output": {"form": "조사 노트", "contents": "화면 구조와 댓글 영역을 붙일 위치"},
     "notes": ""},
    {"id": 34, "title": "인증·권한 처리 방식 파악", "kind": "research",
     "does": "로그인 여부, 본인 여부, 관리자 여부를 서버와 화면에서 어떻게 확인하는지 조사한다.",
     "output": {"form": "조사 노트", "contents": "권한 확인 방법과 쓸 함수"},
     "notes": ""},
    {"id": 37, "title": "댓글 백엔드 API 구현", "kind": "code",
     "does": "댓글 목록, 작성, 수정, 삭제 API 를 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 API 네 개와 응답 형식"},
     "notes": "응답은 항상 {data, error} 모양으로 감싼다."}
  ],
  "previous_edges": [
    {"from": 35, "to": 39},
    {"from": 34, "to": 39},
    {"from": 37, "to": 39},
    {"from": 34, "to": 37}
  ],
  "fixed_edges": [],
  "user_edges": {"link": [], "unlink": []}
}
```

출력
```json
{"edges": [
  {"from_id": 35, "to_id": 41},
  {"from_id": 34, "to_id": 41},
  {"from_id": 41, "to_id": 42},
  {"from_id": 42, "to_id": 43},
  {"from_id": 37, "to_id": 43},
  {"from_id": 34, "to_id": 37}
]}
```
- 와이어프레임(41)은 화면 구조(35)와 권한별 표시(34)를 받아 씁니다.
- API 를 부르는 일은 43 이 하므로 37 → 39 를 37 → 43 으로 옮깁니다.
- 34 → 37 은 바뀌지 않은 앞뒤 노드끼리의 간선이고, API 구현에 권한 확인이 필요하므로 남깁니다.

## 예시 2: 넣기

입력
```json
{
  "change": "36 과 37 사이에 45 \"API 명세 정하기\" 를 넣음",
  "original_nodes": [],
  "changed_nodes": [
    {"id": 45, "title": "API 명세 정하기", "kind": "document",
     "does": "테이블 설계를 보고 댓글 API 네 개의 요청·응답 예시를 정한다.",
     "output": {"form": "문서", "contents": "API 별 요청·응답 예시"},
     "notes": "응답은 항상 {data, error} 모양으로 감싼다."}
  ],
  "neighbor_nodes": [
    {"id": 36, "title": "댓글 테이블 설계", "kind": "code",
     "does": "댓글 테이블을 설계하고 마이그레이션을 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 테이블 마이그레이션과 컬럼 설명"},
     "notes": "외래 키는 걸지 않는다."},
    {"id": 37, "title": "댓글 백엔드 API 구현", "kind": "code",
     "does": "댓글 목록, 작성, 수정, 삭제 API 를 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 API 네 개"},
     "notes": ""},
    {"id": 38, "title": "댓글 API 테스트 작성", "kind": "code",
     "does": "댓글 API 네 개의 요청과 응답을 확인하는 테스트를 쓴다.",
     "output": {"form": "코드 변경", "contents": "API 별 테스트"},
     "notes": ""}
  ],
  "previous_edges": [
    {"from": 36, "to": 37}
  ],
  "fixed_edges": [
    {"from": 36, "to": 38},
    {"from": 37, "to": 38}
  ],
  "user_edges": {"link": [], "unlink": []}
}
```

출력
```json
{"edges": [
  {"from_id": 36, "to_id": 45},
  {"from_id": 45, "to_id": 37},
  {"from_id": 45, "to_id": 38},
  {"from_id": 36, "to_id": 37}
]}
```
- 명세(45)는 테이블 설계를 보고 정하므로 36 을 받습니다.
- API 구현(37)과 테스트(38)는 명세의 요청·응답 예시를 기준으로 쓰므로 45 를 받습니다.
- API 구현(37)은 명세와 함께 테이블 컬럼도 직접 써야 하므로 36 → 37 을 남깁니다.
- 36 → 38, 37 → 38 은 fixed_edges 라 답하지 않습니다. 그대로 남습니다.

## 출력
JSON 하나로 답합니다.
```json
{"edges": [{"from_id": 35, "to_id": 41}, {"from_id": 41, "to_id": 42}]}
```
- edges: changed_nodes 와 neighbor_nodes 사이의 간선 가운데 fixed_edges 를 뺀 전부. 지워진 original_nodes 는 쓰지 않습니다
- from_id, to_id: 노드 id(숫자). to_id 노드는 from_id 노드가 끝난 뒤 그 산출물을 받아 시작합니다
- 입력한 노드와 그 밖의 노드 사이의 간선은 쓰지 않습니다. 그 간선은 그대로 남습니다
