"""DefaultCounterReader: counter.json 을 읽는다. 파일이 없으면 0."""

from __future__ import annotations

from task_planner.common import files
from task_planner.model.counter.counter import Counter
from task_planner.port.local.counter.counter_file import counter_file
from task_planner.port.local.counter.counter_file_converter import CounterFileConverter
from task_planner.port.local.counter.counter_reader import CounterReader


class DefaultCounterReader(CounterReader):
    def read(self) -> Counter:
        p = counter_file()
        return CounterFileConverter().to_data(files.read_json(p)) if p.exists() else Counter(0)
