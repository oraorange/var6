"""Небольшая демонстрация всех 13 RPC-операций."""
from datetime import datetime, timezone
from src.client import RPCClient

def main():
    c = RPCClient()
    member = c.create_member({"name": "Демо-пользователь"})
    prompt = c.create_prompt({"member": member["id"], "parameter": "temperature"})
    response = c.create_response({
        "prompt": prompt["id"],
        "time": datetime.now(timezone.utc).isoformat(),
        "duration": 12
    })
    print("Создано:", member, prompt, response)
    print("Все Member:", c.get_all_members())
    print("Все Prompt:", c.get_all_prompts())
    print("Все Response:", c.get_all_responses())
    print("Запрос за 9 минут:", c.query_recent_parameter_duration())
    print("Редактирование:", c.edit_member(member["id"], {"name": "Изменённый пользователь"}))
    print("Удаление Response:", c.delete_response(response["id"]))
    print("Удаление Prompt:", c.delete_prompt(prompt["id"]))
    print("Удаление Member:", c.delete_member(member["id"]))
    # Повторно вызываем методы редактирования и удаления на тестовых записях,
    # чтобы показать все методы без зависимости от предыдущего состояния.
    m = c.create_member({"name": "Для редактирования"})
    p = c.create_prompt({"member": m["id"], "parameter": "x"})
    r = c.create_response({"prompt": p["id"], "time": datetime.now(timezone.utc).isoformat(), "duration": 1})
    print(c.edit_prompt(p["id"], {"parameter": "y"}))
    print(c.edit_response(r["id"], {"duration": 2}))
    print(c.delete_response(r["id"]))
    print(c.delete_prompt(p["id"]))
    print(c.delete_member(m["id"]))

if __name__ == "__main__":
    main()
