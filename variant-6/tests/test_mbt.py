"""Model-based tests: Hypothesis генерирует действия для всех 13 операций модели."""
from datetime import datetime, timezone
from hypothesis.stateful import RuleBasedStateMachine, rule, initialize
from hypothesis import strategies as st
from src.model import DataModel


class ModelMachine(RuleBasedStateMachine):
    @initialize()
    def setup_models(self):
        self.real = DataModel()
        self.expected = DataModel()

    @rule(name=st.text(min_size=1, max_size=12))
    def create_member(self, name):
        assert self.real.create_member({"name": name}) == self.expected.create_member({"name": name})

    @rule()
    def get_all_members(self):
        assert self.real.get_all_members() == self.expected.get_all_members()

    @rule(name=st.text(min_size=1, max_size=12))
    def edit_member(self, name):
        if self.expected.members:
            rid = self.expected.members[0]["id"]
            assert self.real.edit_member(rid, {"name": name}) == self.expected.edit_member(rid, {"name": name})

    @rule()
    def delete_member(self):
        if self.expected.members:
            rid = self.expected.members[0]["id"]
            assert self.real.delete_member(rid) == self.expected.delete_member(rid)

    @rule(parameter=st.text(min_size=1, max_size=12), member=st.integers(min_value=1, max_value=10))
    def create_prompt(self, parameter, member):
        values = {"member": member, "parameter": parameter}
        assert self.real.create_prompt(values) == self.expected.create_prompt(values)

    @rule()
    def get_all_prompts(self):
        assert self.real.get_all_prompts() == self.expected.get_all_prompts()

    @rule(parameter=st.text(min_size=1, max_size=12))
    def edit_prompt(self, parameter):
        if self.expected.prompts:
            rid = self.expected.prompts[0]["id"]
            assert self.real.edit_prompt(rid, {"parameter": parameter}) == self.expected.edit_prompt(rid, {"parameter": parameter})

    @rule()
    def delete_prompt(self):
        if self.expected.prompts:
            rid = self.expected.prompts[0]["id"]
            assert self.real.delete_prompt(rid) == self.expected.delete_prompt(rid)

    @rule(prompt=st.integers(min_value=1, max_value=10), duration=st.integers(min_value=0, max_value=100))
    def create_response(self, prompt, duration):
        values = {"prompt": prompt, "time": datetime.now(timezone.utc).isoformat(), "duration": duration}
        assert self.real.create_response(values) == self.expected.create_response(values)

    @rule()
    def get_all_responses(self):
        assert self.real.get_all_responses() == self.expected.get_all_responses()

    @rule(duration=st.integers(min_value=0, max_value=100))
    def edit_response(self, duration):
        if self.expected.responses:
            rid = self.expected.responses[0]["id"]
            assert self.real.edit_response(rid, {"duration": duration}) == self.expected.edit_response(rid, {"duration": duration})

    @rule()
    def delete_response(self):
        if self.expected.responses:
            rid = self.expected.responses[0]["id"]
            assert self.real.delete_response(rid) == self.expected.delete_response(rid)

    @rule()
    def query_recent_parameter_duration(self):
        # Одинаковые модели имеют эквивалентное состояние; время передаём одинаковое.
        now = datetime.now(timezone.utc)
        assert self.real.query_recent_parameter_duration(now) == self.expected.query_recent_parameter_duration(now)


TestModelMachine = ModelMachine.TestCase
