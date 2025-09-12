import os
from vanna.chromadb import ChromaDB_VectorStore
from vanna.openai import OpenAI_Chat

class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        OpenAI_Chat.__init__(self, config=config)

# On récupère la clé depuis la variable d'environnement OPENAI_API_KEY
api_key = os.environ.get("OPENAI_API_KEY")

vn = MyVanna(
    config={
        'api_key': api_key,
        'model': 'gpt-4o-mini',  # utilisation du modèle GPT-4o mini
        'initial_prompt': "Vous êtes un expert SQL et vous répondez toujours en français."
    }
)

vn.connect_to_postgres(
    host="localhost",
    port=5432,
    dbname="planisware",
    user="planisware",
    password="planisware"
)


with open("ddl.txt", "r", encoding="utf-8") as f:
    ddl_plw = f.read()

vn.train(ddl=ddl_plw)

with open("documentation.txt", "r", encoding="utf-8") as f:
    docu_plw = f.read()

vn.train(documentation=docu_plw)

vn.train(
  question="Lister tous les projets avec leur nom et ID (numéro interne)",
  sql="""
    SELECT onb, name
    FROM ordo_project;
  """
)

vn.train(
  question="Chercher un projet par son nom contenant '038'",
  sql="""
    SELECT onb, name, real_start, real_finish
    FROM ordo_project
    WHERE name ILIKE '%038%';
  """
)

vn.train(
  question="Projets récemment modifiés (avec la date de mise à jour)",
  sql="""
    SELECT onb, name, update_date
    FROM ordo_project
    WHERE update_date IS NOT NULL
    ORDER BY update_date DESC
    LIMIT 20;
  """
)

vn.train(
  question="Nombre de projets par utilisateur créateur",
  sql="""
    SELECT owner, COUNT(*) AS nb_projets
    FROM ordo_project
    GROUP BY owner
    ORDER BY nb_projets DESC;
  """
)

vn.train(
  question="Projets avec leur description",
  sql="""
    SELECT name, opx2_comment AS description
    FROM ordo_project
    WHERE opx2_comment IS NOT NULL;
  """
)

vn.train(
  question="Projets en cours à l’instant présent",
  sql="""
    SELECT name, real_start, real_finish
    FROM ordo_project
    WHERE real_start <= NOW()
      AND (real_finish IS NULL OR real_finish >= NOW());
  """
)

vn.train(
  question="Durée des projets (en jours) quand les dates sont renseignées",
  sql="""
    SELECT onb, name,
           (real_finish - real_start) AS duree_jours
    FROM ordo_project
    WHERE real_start IS NOT NULL
      AND real_finish IS NOT NULL;
  """
)

vn.train(
  question="Projets dont le nom ou la description contient 'plan'",
  sql="""
    SELECT onb, name, opx2_comment
    FROM ordo_project
    WHERE name ILIKE '%plan%'
       OR opx2_comment ILIKE '%plan%';
  """
)

vn.train(
  question="Nombre de projets par année de début",
  sql="""
    SELECT EXTRACT(YEAR FROM real_start) AS annee,
           COUNT(*) AS nb_projets
    FROM ordo_project
    WHERE real_start IS NOT NULL
    GROUP BY annee
    ORDER BY annee DESC;
  """
)

vn.train(
  question="Statut des projets (En cours / Terminé / À venir)",
  sql="""
    SELECT name,
           CASE
             WHEN real_finish IS NOT NULL AND real_finish < NOW() THEN 'Terminé'
             WHEN real_start IS NOT NULL  AND real_start > NOW() THEN 'À venir'
             ELSE 'En cours'
           END AS statut
    FROM ordo_project;
  """
)

vn.train(
  question="Descriptions en doublon (avec le nombre d’occurrences)",
  sql="""
    SELECT opx2_comment, COUNT(*) AS occurrences
    FROM ordo_project
    GROUP BY opx2_comment
    HAVING COUNT(*) > 1
    ORDER BY occurrences DESC, opx2_comment;
  """
)

from vanna.flask import VannaFlaskApp

app = VannaFlaskApp(
    vn,
    title="Bienvenue sur Vanna.AI",
    subtitle="Votre copilote IA pour les requêtes SQL."
)
app.run(port=8004, debug=True)

