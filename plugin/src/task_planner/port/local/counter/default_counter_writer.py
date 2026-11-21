"""DefaultCounterWriter: counter.json 을 쓴다."""

from __future__ import annotations

from task_planner.common import files
from task_planner.model.counter.counter import Counter
from task_planner.port.local.counter.counter_file import counter_file
from task_planner.port.local.counter.counter_file_converter import CounterFileConverter
from task_planner.port.local.counter.counter_writer import CounterWriter


class DefaultCounterWriter(CounterWriter):
    def save(self, counter: Counter) -> None:
        files.write_json(counter_file(), CounterFileConverter().to_file(counter))
