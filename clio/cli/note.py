from clio.db.db import get_db
from sqlalchemy import text
import uuid
import sys
from clio.utils.generate_title import generate_title_from_text
from clio.core.record import update_record_title

DEFAULT_GENUS = "_in"

def create_note_to_inbox(note_text: str):
    with next(get_db()) as db:
        # Step 1: Lookup `_in` genus UUID
        result = db.execute(
            text("SELECT UUID FROM genus WHERE name = :name"),
            {"name": DEFAULT_GENUS}
        ).fetchone()

        if not result:
            print(f"Error: genus '{DEFAULT_GENUS}' does not exist.")
            sys.exit(1)

        parent_UUID = result[0]

        # Step 2: Lookup rectype_id for 'note'
        rectype_row = db.execute(
            text("SELECT id FROM rectype WHERE name = 'note'")
        ).fetchone()

        if not rectype_row:
            print("Error: 'note' rectype not found.")
            sys.exit(1)

        rectype_id = rectype_row[0]
        new_UUID = str(uuid.uuid4())

        # Step 3: Insert into `record`
        db.execute(
            text("""
                INSERT INTO record (UUID, parent_UUID, rectype_id)
                VALUES (:uuid, :parent_uuid, :rectype_id)
            """),
            {"uuid": new_UUID, "parent_uuid": parent_UUID, "rectype_id": rectype_id}
        )

        # Step 4: Insert into `note`
        db.execute(
            text("""
                INSERT INTO note (rec_UUID, note_content)
                VALUES (:uuid, :content)
            """),
            {"uuid": new_UUID, "content": note_text}
        )

        db.commit()

        # Step 5: Generate title after DB insert
        try:
            short_text = note_text[:1000]  # Limit to first 1000 characters to save tokens
            title = generate_title_from_text(short_text)
            final_title = title if title else "Note"
            update_record_title(new_UUID, final_title)
            print(f"✓ Note saved with title: {final_title}")
        except Exception as e:
            fallback_title = "Note"
            update_record_title(new_UUID, fallback_title)
            print(f"✓ Note saved (AI title generation failed, used fallback '{fallback_title}'): {e}")


    return new_UUID

