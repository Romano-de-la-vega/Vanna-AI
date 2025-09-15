from vanna.base import VannaBase
from vanna.flask import VannaFlaskApp
import importlib.metadata

# Stub version lookup for tests
importlib.metadata.version = lambda name: "0.0"

class DummyVanna(VannaBase):
    def generate_embedding(self, data: str, **kwargs):
        return [0.0]
    def get_similar_question_sql(self, question: str, **kwargs):
        return []
    def get_related_ddl(self, question: str, **kwargs):
        return []
    def get_related_documentation(self, question: str, **kwargs):
        return []
    def add_question_sql(self, question: str, sql: str, **kwargs):
        return "id"
    def add_ddl(self, ddl: str, **kwargs):
        return "id"
    def add_documentation(self, documentation: str, **kwargs):
        return "id"
    def get_training_data(self, **kwargs):
        return []
    def remove_training_data(self, id: str, **kwargs):
        return True
    def system_message(self, message: str):
        return {"role": "system", "content": message}
    def user_message(self, message: str):
        return {"role": "user", "content": message}
    def assistant_message(self, message: str):
        return {"role": "assistant", "content": message}
    def submit_prompt(self, prompt, **kwargs):
        return ""

def test_logo_served():
    api = VannaFlaskApp(vn=DummyVanna(), debug=False)
    client = api.flask_app.test_client()
    resp = client.get('/logo.png')
    assert resp.status_code == 200
    assert resp.mimetype == 'image/png'
