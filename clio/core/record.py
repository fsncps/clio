from sqlalchemy import text
from ..db.db import get_db
from clio.utils.log_util import log_message
import uuid



def update_record_title(record_uuid: str, title: str):
    with next(get_db()) as db:
        db.execute(
            text("UPDATE record SET name = :title WHERE UUID = :uuid"),
            {"title": title, "uuid": record_uuid}
        )
        db.commit()

def move_record(self, record_uuid: str, new_parent_uuid: str):
        """Update the record's parent UUID in the database."""
        with next(get_db()) as db:
            update_query = text("UPDATE record SET parent_UUID = :new_parent WHERE UUID = :record")
            db.execute(update_query, {"new_parent": new_parent_uuid, "record": record_uuid})
            db.commit()
            log_message(f"Record {record_uuid} moved under parent {new_parent_uuid}.", "info")

def create_record(rectype: str, current_UUID: str):
    """Create a new record with the given rectype, using current_UUID as the parent."""
    new_UUID = str(uuid.uuid4())  # Generate a unique UUID

    with next(get_db()) as db:
        # Get the rectype_id from the rectype table
        result = db.execute(
            text("SELECT id FROM rectype WHERE name = :rectype"),
            {"rectype": rectype.lower()},
        )
        rectype_id_row = result.fetchone()

        if not rectype_id_row:
            raise ValueError(f"Record type '{rectype}' not found in rectype table")

        rectype_id = rectype_id_row[0]  # Extract rectype_id

        # Insert the record into the `record` table
        db.execute(
            text("""
                INSERT INTO record (UUID, parent_UUID, rectype_id)
                VALUES (:UUID, :parent_UUID, :rectype_id)
            """),
            {"UUID": new_UUID, "parent_UUID": current_UUID, "rectype_id": rectype_id},
        )

        # Insert into the specific rectype table
        query = f"""
            INSERT INTO `{rectype}` (rec_UUID)
            VALUES (:UUID)
        """

        db.execute(text(query), {"UUID": new_UUID})
        db.commit()
    
    return new_UUID  # Return the new record UUID

from sqlalchemy.sql import text

def recursive_delete(record_uuid):
    """Recursively delete a record and all its children."""
    
    def query_children(uuid):
        """Retrieve all child records of a given parent UUID."""
        with next(get_db()) as db:
            child_query = text("""
                SELECT record.UUID, rectype.name AS rectype 
                FROM record 
                JOIN rectype ON record.rectype_id = rectype.id 
                WHERE parent_UUID = :parent_uuid
            """)
            return db.execute(child_query, {"parent_uuid": uuid}).mappings().all()

    def delete_record(uuid, rectype):
        """Delete a single record from the content and record tables."""
        with next(get_db()) as db:
            delete_content_query = text(f"DELETE FROM `{rectype}ì` WHERE rec_UUID = :record_uuid")
            db.execute(delete_content_query, {"record_uuid": uuid})

            delete_record_query = text("DELETE FROM record WHERE UUID = :record_uuid")
            db.execute(delete_record_query, {"record_uuid": uuid})

            db.commit()
            log_message(f"Deleted record {uuid} from '{rectype}' and 'record' tables.", "info")

    # Step 1: Fetch children
    children = query_children(record_uuid)

    if not children:  
        # Step 2: If no children, delete the record
        with next(get_db()) as db:
            result = db.execute(
                text("SELECT rectype.name FROM record JOIN rectype ON record.rectype_id = rectype.id WHERE record.UUID = :uuid"),
                {"uuid": record_uuid}
            ).fetchone()
        
        if result:
            rectype = result[0]
            delete_record(record_uuid, rectype)
    else:
        # Step 3: If there are children, recursively delete them first
        for child in children:
            recursive_delete(child["UUID"])

        # After deleting children, delete the parent
        recursive_delete(record_uuid)


