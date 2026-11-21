"""작업 트리. 작업을 위치(item_key) 순서로 펼쳐 담고, 새 트리를 돌려주는 동작만 둔다."""

from __future__ import annotations

from dataclasses import dataclass, replace

from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind

ROOT_KEY = "0"


@dataclass(frozen=True, slots=True)
class TaskTree:
    items: tuple[WorkItem, ...]  # 맨 위부터, 부모 다음에 그 자식들이 오는 순서

    @classmethod
    def start(cls, title: str, scope: str) -> TaskTree:
        """명령서 전체를 맨 위 작업 하나로 둔 트리."""
        return cls((WorkItem(item_key=ROOT_KEY, name=title, scope=scope, kind=WorkKind.TASK, depth=0),))

    def item(self, item_key: str) -> WorkItem:
        for work_item in self.items:
            if work_item.item_key == item_key:
                return work_item
        raise KeyError(f"작업 트리에 {item_key} 가 없습니다")

    def children(self, item_key: str) -> tuple[WorkItem, ...]:
        return tuple(work_item for work_item in self.items if work_item.parent_key == item_key)

    def leaves(self) -> tuple[WorkItem, ...]:
        """자식이 없는 작업. 이것들이 계획의 노드가 된다."""
        parent_keys = {work_item.parent_key for work_item in self.items}
        return tuple(work_item for work_item in self.items if work_item.item_key not in parent_keys)

    def leaves_under(self, item_key: str) -> tuple[WorkItem, ...]:
        """그 작업 아래의 맨 아래 작업. 그 작업이 맨 아래면 자기 자신."""
        return tuple(leaf for leaf in self.leaves() if _is_within(leaf.item_key, item_key))

    def path_of(self, item_key: str) -> str:
        """맨 위부터 그 작업까지의 이름을 " / " 로 이은 것."""
        names = []
        current: str | None = item_key
        while current is not None:
            work_item = self.item(current)
            names.append(work_item.name)
            current = work_item.parent_key
        return " / ".join(reversed(names))

    def with_why(self, item_key: str, why: str) -> TaskTree:
        """그 작업의 판단 근거를 적은 새 트리."""
        return TaskTree(tuple(replace(item, why=why) if item.item_key == item_key else item for item in self.items))

    def with_children(self, parent_key: str, children: tuple[WorkItem, ...]) -> TaskTree:
        """부모 바로 뒤(부모의 기존 자손 뒤)에 자식들을 넣은 새 트리."""
        insert_at = max(index for index, item in enumerate(self.items) if _is_within(item.item_key, parent_key)) + 1
        return TaskTree(self.items[:insert_at] + children + self.items[insert_at:])

    def with_local_ids(self) -> TaskTree:
        """맨 아래 작업에 트리 순서대로 n1, n2 … 를 붙인 새 트리."""
        leaf_keys = [leaf.item_key for leaf in self.leaves()]
        local_ids = {item_key: f"n{order}" for order, item_key in enumerate(leaf_keys, start=1)}
        return TaskTree(tuple(replace(item, local_id=local_ids.get(item.item_key)) for item in self.items))

    def render(self, marked_key: str | None = None, mark_text: str = "◀ 판단 대상") -> str:
        """프롬프트에 넣는 들여쓴 목록. HITL 은 [HITL] 을 앞에, 표시할 작업 뒤에 mark_text."""
        return "".join(_render_line(item, item.item_key == marked_key, mark_text) for item in self.items)


def _is_within(item_key: str, ancestor_key: str) -> bool:
    return item_key == ancestor_key or item_key.startswith(ancestor_key + ".")


def _render_line(item: WorkItem, marked: bool, mark_text: str) -> str:
    indent = "  " * item.depth
    hitl = "[HITL] " if item.kind is WorkKind.HITL else ""
    scope = f": {item.scope}" if item.scope else ""
    mark = f" {mark_text}" if marked else ""
    return f"{indent}- {hitl}{item.name}{scope}{mark}\n"
