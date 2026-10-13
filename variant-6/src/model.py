"""Модель данных варианта 6. Все данные хранятся только в оперативной памяти."""
from datetime import datetime, timedelta, timezone
from copy import deepcopy


class DataModel:
    def __init__(self):
        self.members = []
        self.prompts = []
        self.responses = []
        self._next_ids = {"member": 1, "prompt": 1, "response": 1}

    def _create(self, table_name, values):
        table = getattr(self, table_name + "s")
        record = deepcopy(values)
        if "id" not in record:
            record["id"] = self._next_ids[table_name]
            self._next_ids[table_name] += 1
        elif any(item.get("id") == record["id"] for item in table):
            raise ValueError(f'{table_name}: запись с id={record["id"]} уже существует')
        else:
            if not isinstance(record["id"], int):
                raise ValueError("id должен быть целым числом")
            self._next_ids[table_name] = max(self._next_ids[table_name], record["id"] + 1)
        table.append(record)
        return deepcopy(record)

    def _delete(self, table_name, record_id):
        table = getattr(self, table_name + "s")
        for i, record in enumerate(table):
            if record.get("id") == record_id:
                del table[i]
                return True
        raise KeyError(f'{table_name}: запись с id={record_id} не найдена')

    def _get_all(self, table_name):
        return deepcopy(getattr(self, table_name + "s"))

    def _edit(self, table_name, record_id, changes):
        table = getattr(self, table_name + "s")
        for record in table:
            if record.get("id") == record_id:
                if "id" in changes and changes["id"] != record_id:
                    raise ValueError("Изменять id записи нельзя")
                record.update(deepcopy(changes))
                return deepcopy(record)
        raise KeyError(f'{table_name}: запись с id={record_id} не найдена')

    # Member: id плюс произвольные поля, например name.
    def create_member(self, values): return self._create("member", values)
    def delete_member(self, record_id): return self._delete("member", record_id)
    def get_all_members(self): return self._get_all("member")
    def edit_member(self, record_id, changes): return self._edit("member", record_id, changes)

    # Prompt: обычно содержит member (ссылка на Member.id) и parameter.
    def create_prompt(self, values): return self._create("prompt", values)
    def delete_prompt(self, record_id): return self._delete("prompt", record_id)
    def get_all_prompts(self): return self._get_all("prompt")
    def edit_prompt(self, record_id, changes): return self._edit("prompt", record_id, changes)

    # Response: обычно содержит prompt (ссылка на Prompt.id), time и duration.
    def create_response(self, values): return self._create("response", values)
    def delete_response(self, record_id): return self._delete("response", record_id)
    def get_all_responses(self): return self._get_all("response")
    def edit_response(self, record_id, changes): return self._edit("response", record_id, changes)

    def query_recent_parameter_duration(self, now=None):
        """π(P.parameter, R.duration)(σ(R.time > now-9min)(M ⋈ P ⋈ R))."""
        now = now or datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=9)
        result = []
        members = {m["id"] for m in self.members}
        prompts = {p["id"]: p for p in self.prompts if p.get("member") in members}
        for response in self.responses:
            prompt = prompts.get(response.get("prompt"))
            if not prompt or "parameter" not in prompt or "duration" not in response:
                continue
            raw_time = response.get("time")
            try:
                if isinstance(raw_time, (int, float)):
                    response_time = datetime.fromtimestamp(raw_time, tz=timezone.utc)
                elif isinstance(raw_time, str):
                    response_time = datetime.fromisoformat(raw_time.replace("Z", "+00:00"))
                    if response_time.tzinfo is None:
                        response_time = response_time.replace(tzinfo=timezone.utc)
                elif isinstance(raw_time, datetime):
                    response_time = raw_time
                    if response_time.tzinfo is None:
                        response_time = response_time.replace(tzinfo=timezone.utc)
                else:
                    continue
                if response_time > cutoff:
                    result.append({"parameter": prompt["parameter"], "duration": response["duration"]})
            except (ValueError, TypeError, OverflowError):
                continue
        return result
