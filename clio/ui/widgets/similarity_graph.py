from textual.widgets import Tree, Static
from textual.containers import Vertical
from clio.utils.logging import log_message
import numpy as np

import json
import numpy as np
from sqlalchemy.sql import text

##############################################################################################
############################## Cosine Similarity Matching / Graph ############################
##############################################################################################



class SimilarityGraphWidget(Vertical):
    """Displays a tree visualization of similar records using embeddings."""

    def __init__(self):
        super().__init__()
        self.tree = Tree("Similar Records", id="similarity-tree")
        self.status = Static("No similar records found.", id="similarity-status")
        self.append(self.tree)
        self.append(self.status)

    def update_graph(self, query_text):
        """Finds and displays similar records."""
        log_message(f"🔍 Finding similar records for: {query_text}", "info")

        similar_records = find_similar_records(query_text, top_n=5)
        self.tree.clear()  # Clear previous results

        if not similar_records:
            self.status.update("No similar records found.")
            return
        
        root = self.tree.root
        root.set_label(f"Records similar to: {query_text[:30]}...")

        for rec_UUID, score in similar_records:
            root.add_leaf(f"{rec_UUID} (Score: {score:.2f})")

        self.status.update(f"🔗 Found {len(similar_records)} similar records.")
        self.tree.expand_all()





############################## FIND RECORDS ############################

def find_similar_records(query_text, top_n=5):
    """Find similar records using cosine similarity from embeddings table."""

    # ✅ Generate embedding for the query
    client = OpenAI()
    response = client.embeddings.create(input=query_text, model="text-embedding-ada-002")
    query_embedding = response.data[0].embedding

    with next(get_db()) as db:
        try:
            query = text("""
                SELECT rec_UUID, embedding
                FROM embeddings
                WHERE model = 'text-embedding-ada-002'
            """)
            results = db.execute(query).fetchall()

            # ✅ Compute cosine similarity for each record
            similarities = []
            for rec_UUID, stored_embedding in results:
                stored_embedding = json.loads(stored_embedding)  # Convert from JSON
                similarity = np.dot(query_embedding, stored_embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(stored_embedding)
                )
                similarities.append((rec_UUID, similarity))

            # ✅ Sort by similarity (higher = more similar)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # ✅ Return the top N results
            return similarities[:top_n]

        except Exception as e:
            log_message(f"❌ Error in similarity search: {str(e)}", "error")
            return []

