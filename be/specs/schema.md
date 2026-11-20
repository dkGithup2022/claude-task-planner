# Schema (테이블)

Postgres. migration 은 `packages/schema/alembic/versions/`. DB FK 제약은 두지 않는다.

주의: autogenerate 가 자식 테이블 생성문 안에 FK 제약을 넣는다. `env.py` 필터가 거르지 못하므로 migration 마다 손으로 지운다.

## plans (migration `0edad69db71e_plan`)

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BIGINT IDENTITY | PK |
| title | TEXT | |
| request | TEXT | 명령서 md |
| status | VARCHAR(255) | drafting, reviewing, approved, rejected, running, done (값을 소문자로 저장) |
| is_deleted, deleted_at, created_at, updated_at | | 공통 4컬럼 |

## plan_personas (같은 migration)

계획의 참여 페르소나. 공통 4컬럼 없음.

| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | BIGINT IDENTITY | PK |
| plan_id | BIGINT | 인덱스 `ix_plan_personas_plan_id` |
| persona_id | BIGINT | |
| position | INTEGER | persona_ids 안의 순서 |

## plan_nodes (migration `69138c91383e_plan_node_edge`)

id, plan_id (인덱스), title TEXT, kind VARCHAR (document, research, code, hitl), output_spec TEXT, status VARCHAR (todo, running, done, failed, skipped), 공통 4컬럼

## plan_node_personas (같은 migration)

id, node_id (인덱스), persona_id, position. 공통 4컬럼 없음

## plan_edges (같은 migration)

id, plan_id (인덱스), from_node_id, to_node_id, 공통 4컬럼

## memories (migration `5054c231fd89_memory`)

id, kind VARCHAR (knowledge, attitude, plan), theme TEXT, body TEXT, 공통 4컬럼

## memory_personas, memory_sources (같은 migration)

- memory_personas: id, memory_id (인덱스), persona_id, position
- memory_sources: id, memory_id (인덱스), quote TEXT, plan_id, position

## personas (migration `persona`)

id, name VARCHAR(255), description TEXT, 공통 4컬럼. 부분 유일 인덱스 `uq_personas_name_active` (name, is_deleted = false 인 행만)
