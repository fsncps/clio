from clio.core.state import app_state
from clio.utils.logging import log_message
from ..db.db import get_db
from sqlalchemy import text

def get_all_descendants(record_uuid):
    """Retrieve all descendant records of a given record UUID."""
    descendants = set()

    def fetch_children(parent_uuid):
        with next(get_db()) as db:
            query = text("""
                SELECT record.UUID FROM record 
                WHERE parent_UUID = :parent_uuid
            """)
            children = db.execute(query, {"parent_uuid": parent_uuid}).fetchall()

            for child in children:
                child_uuid = child[0]
                descendants.add(child_uuid)
                fetch_children(child_uuid)  # ✅ Recursively get deeper children

    fetch_children(record_uuid)
    return descendants  # ✅ Returns a set of all child UUIDs

