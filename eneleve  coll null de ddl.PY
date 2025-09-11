import json
import re
import sys

def filter_ddl(ddl_file, json_file, output_file):
    # Charger la liste des colonnes à exclure (null_frac == 1)
    with open(json_file, "r", encoding="utf-8") as f:
        schema = json.load(f)

    cols_to_remove = set()
    for table in schema["tables"]:
        for col in table["columns"]:
            if col.get("null_frac") == 1.0:
                cols_to_remove.add(col["name"].lower())

    # Charger le DDL
    with open(ddl_file, "r", encoding="utf-8") as f:
        ddl = f.read()

    # Découper chaque ligne de définition de colonne
    new_lines = []
    for line in ddl.splitlines():
        m = re.match(r'\s*("?)([a-zA-Z0-9_]+)\1', line.strip())
        if m:
            col_name = m.group(2).lower()
            if col_name in cols_to_remove:
                # ignorer la colonne
                continue
        new_lines.append(line)

    # Écrire le nouveau DDL
    with open(output_file, "w", encoding="utf-8") as out:
        out.write("\n".join(new_lines))

    print(f"✅ DDL nettoyé écrit dans {output_file}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python filter_ddl.py <ddl.sql> <stats.json> <output.sql>")
    else:
        filter_ddl(sys.argv[1], sys.argv[2], sys.argv[3])
