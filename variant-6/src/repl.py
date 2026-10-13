"""Интерактивный REPL для прямой проверки модели данных."""
import json
from src.model import DataModel

HELP = """Команды:
  create member|prompt|response JSON
  delete member|prompt|response ID
  all member|prompt|response
  edit member|prompt|response ID JSON
  query
  help
  exit

Пример: create member {"name":"Кирилл"}
Пример: create prompt {"member":1,"parameter":"temperature"}
Пример: create response {"prompt":1,"time":"2026-10-13T08:00:00+00:00","duration":12}
"""
def main():
    model = DataModel()
    print("REPL модели варианта 6. Введите help для справки.")
    while True:
        try:
            line = input("model> ").strip()
            if not line: continue
            if line in ("exit", "quit"): break
            if line in ("help", "?"):
                print(HELP); continue
            if line == "query":
                print(json.dumps(model.query_recent_parameter_duration(), ensure_ascii=False, indent=2)); continue
            parts = line.split(" ", 2)
            command = parts[0]
            if command == "all" and len(parts) >= 2:
                print(json.dumps(getattr(model, f"get_all_{parts[1]}s")(), ensure_ascii=False, indent=2)); continue
            if command == "create" and len(parts) == 3:
                print(getattr(model, f"create_{parts[1]}")(json.loads(parts[2]))); continue
            if command == "delete" and len(parts) == 3:
                print(getattr(model, f"delete_{parts[1]}")(int(parts[2]))); continue
            if command == "edit" and len(parts) == 3:
                rest = parts[2].split(" ", 1)
                print(getattr(model, f"edit_{parts[1]}")(int(rest[0]), json.loads(rest[1]))); continue
            print("Команда не распознана. Введите help.")
        except Exception as exc:
            print(f"Ошибка: {type(exc).__name__}: {exc}")
if __name__ == "__main__":
    main()
