import json
import os
from pathlib import Path
import yaml
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

TRAINING_DATA_PATH = Path("training_data/user_training_data.json")


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        self.training_data_path = TRAINING_DATA_PATH
        self.training_data_path.parent.mkdir(parents=True, exist_ok=True)

        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

    def _read_training_file(self):
        if not self.training_data_path.exists():
            return []

        try:
            data = json.loads(self.training_data_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            print(
                f"Impossible de décoder {self.training_data_path}. Le fichier sera ignoré."
            )

        return []

    def _write_training_file(self, data):
        self.training_data_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _persist_training_example(self, entry):
        data = self._read_training_file()

        # Évite d'ajouter des doublons si l'ID existe déjà
        existing_ids = {item.get("id") for item in data}
        if entry.get("id") not in existing_ids:
            data.append(entry)
            self._write_training_file(data)

    def _remove_persisted_entry(self, entry_id: str):
        data = self._read_training_file()
        updated = [item for item in data if item.get("id") != entry_id]

        if len(updated) != len(data):
            self._write_training_file(updated)

    def load_persisted_training_data(self):
        data = self._read_training_file()

        for item in data:
            question = item.get("question")
            sql = item.get("sql")

            if not question or not sql:
                continue

            try:
                super(MyVanna, self).train(question=question, sql=sql)
            except Exception as exc:  # pragma: no cover - dépend des implémentations
                print(
                    "Impossible de recharger une donnée d'entraînement persistée:",
                    exc,
                )

    def train(
        self,
        question: str = None,
        sql: str = None,
        ddl: str = None,
        documentation: str = None,
        plan=None,
        persist: bool = True,
    ):
        entry_id = super().train(
            question=question, sql=sql, ddl=ddl, documentation=documentation, plan=plan
        )

        if persist and entry_id and question and sql:
            self._persist_training_example(
                {"id": entry_id, "question": question, "sql": sql}
            )

        return entry_id

    def remove_training_data(self, id: str, **kwargs) -> bool:
        removed = super().remove_training_data(id=id, **kwargs)

        if removed and id.endswith("-sql"):
            self._remove_persisted_entry(id)

        return removed

# On récupère la clé depuis la variable d'environnement OPENAI_API_KEY
api_key = os.environ.get("OPENAI_API_KEY")

vn = MyVanna(config={
    'api_key': api_key,
    'model': 'gpt-4o-mini'  # utilisation du modèle GPT-4o mini
})

vn.connect_to_postgres(
    host="localhost",
    port=5432,
    dbname="planisware",
    user="planisware",
    password="planisware"
)


with open("10_class.sql", "r", encoding="utf-16") as f:
    ddl_plw = f.read()

vn.train(ddl=ddl_plw)

with open("description_10class.txt", "r", encoding="utf-8") as f:
    docu_plw = f.read()

vn.train(documentation=docu_plw)
def load_sql_qa(path: str | Path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    ext = p.suffix.lower()
    text = p.read_text(encoding="utf-8")

    if ext == ".json":
        return json.loads(text) or []

    if ext in (".yaml", ".yml"):
        if yaml is None:
            raise RuntimeError(
                "PyYAML n’est pas installé. Fais: pip install pyyaml, ou utilise un .json"
            )
        data = yaml.safe_load(text)
        # Autorise soit une liste d’objets {question, sql}, soit un dict avec clé "items"
        if isinstance(data, dict) and "items" in data:
            return data["items"] or []
        return data or []

    raise ValueError("Extension non supportée (utilise .json, .yaml ou .yml)")

# ... ton code existant (création vn, connect_to_postgres, train(ddl), train(documentation)) ...

# 🔹 Charge toutes les paires question/SQL depuis un fichier
examples = load_sql_qa("sql_qa.yaml")  # ou "training_data/sql_qa.yaml"

for ex in examples:
    q = ex.get("question")
    s = ex.get("sql")
    if q and s:
        vn.train(question=q, sql=s, persist=False) 
        
vn.load_persisted_training_data()

from vanna.flask import VannaFlaskApp

app = VannaFlaskApp(vn)
app.run(port=8004, debug=True)

