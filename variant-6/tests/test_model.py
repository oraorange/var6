from datetime import datetime, timezone, timedelta
import pytest
from src.model import DataModel


def test_crud_for_all_entities():
    m = DataModel()
    member = m.create_member({"name": "A"})
    assert member["id"] == 1
    assert m.edit_member(1, {"name": "B"})["name"] == "B"
    assert m.get_all_members()[0]["name"] == "B"
    assert m.delete_member(1) is True
    with pytest.raises(KeyError): m.delete_member(1)

    prompt = m.create_prompt({"member": 2, "parameter": "p"})
    assert m.edit_prompt(prompt["id"], {"parameter": "q"})["parameter"] == "q"
    assert m.get_all_prompts()
    assert m.delete_prompt(prompt["id"])

    response = m.create_response({"prompt": 1, "time": datetime.now(timezone.utc).isoformat(), "duration": 3})
    assert m.edit_response(response["id"], {"duration": 4})["duration"] == 4
    assert m.get_all_responses()
    assert m.delete_response(response["id"])


def test_query_recent_join():
    m = DataModel()
    now = datetime.now(timezone.utc)
    m.create_member({"name": "A"})
    m.create_prompt({"member": 1, "parameter": "speed"})
    m.create_response({"prompt": 1, "time": now.isoformat(), "duration": 17})
    m.create_response({"prompt": 1, "time": (now - timedelta(minutes=10)).isoformat(), "duration": 99})
    assert m.query_recent_parameter_duration(now) == [{"parameter": "speed", "duration": 17}]


def test_duplicate_id_and_edit_missing():
    m = DataModel()
    m.create_member({"id": 10, "name": "A"})
    with pytest.raises(ValueError): m.create_member({"id": 10})
    with pytest.raises(KeyError): m.edit_member(77, {"name": "X"})
