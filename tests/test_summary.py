import pandas as pd

from vanna.mock import MockEmbedding, MockLLM, MockVectorDB


class SimpleVanna(MockLLM, MockVectorDB, MockEmbedding):
    def __init__(self):
        MockLLM.__init__(self)
        MockVectorDB.__init__(self)
        MockEmbedding.__init__(self)
        self.run_sql_is_set = True
        self.language = None

    def generate_sql(self, question: str, allow_llm_to_see_data: bool = False, **kwargs) -> str:
        return "SELECT 1"

    def run_sql(self, sql: str, **kwargs):
        return pd.DataFrame({"a": [1]})

    def add_question_sql(self, question: str, sql: str):
        pass

    def generate_plotly_code(self, question: str, sql: str, df: pd.DataFrame, **kwargs) -> str:
        return ""

    def get_plotly_figure(self, plotly_code: str, df: pd.DataFrame, **kwargs):
        return None


def test_ask_returns_summary():
    vn = SimpleVanna()
    sql, df, fig, summary = vn.ask("test", print_results=False, visualize=False)
    assert sql == "SELECT 1"
    assert summary == "Mock LLM response"
    assert vn.language is None
