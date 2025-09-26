import yaml

# Lecture du YAML
with open("sql_qa.yaml", "r", encoding="utf-8") as f:
    examples = yaml.safe_load(f)

# Vérif simple
for ex in examples:
    print("Question:", ex["question"])
    print("SQL:", ex["sql"])
    print("-" * 40)
