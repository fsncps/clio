import uuid
from sqlalchemy import text
from ..db.db import engine

class GenusDB:
    """Handles CRUD operations for genus using raw SQL."""

    @staticmethod
    def create_genus(shortname: str, longname: str, genus_type_id: int):
        """Insert a new genus record with a UUID."""
        genus_id = str(uuid.uuid4())  # Generate UUID in Python
        query = text("INSERT INTO genus (id, shortname, longname, genus_type_id) VALUES (:id, :shortname, :longname, :genus_type_id);")
        with engine.connect() as connection:
            connection.execute(query, {"id": genus_id, "shortname": shortname, "longname": longname, "genus_type_id": genus_type_id})
            connection.commit()
        return genus_id  # Return UUID

    @staticmethod
    def get_genus(genus_id: str):
        """Retrieve a genus by UUID."""
        query = text("SELECT * FROM genus WHERE id = :genus_id;")
        with engine.connect() as connection:
            result = connection.execute(query, {"genus_id": genus_id})
            return result.fetchone()

    @staticmethod
    def update_genus(genus_id: str, shortname: str, longname: str):
        """Update a genus record by UUID."""
        query = text("UPDATE genus SET shortname = :shortname, longname = :longname WHERE id = :genus_id;")
        with engine.connect() as connection:
            connection.execute(query, {"genus_id": genus_id, "shortname": shortname, "longname": longname})
            connection.commit()

    @staticmethod
    def delete_genus(genus_id: str):
        """Delete a genus record by UUID."""
        query = text("DELETE FROM genus WHERE id = :genus_id;")
        with engine.connect() as connection:
            connection.execute(query, {"genus_id": genus_id})
            connection.commit()

