from typing import NamedTuple, Optional
from .db import get_db
from typing import Dict, Any
import json
from openai import OpenAI
from clio.core.state import app_state
from clio.utils.log_util import log_message
from sqlalchemy import text
from uuid import uuid4
import uuid

##############################################################################################
################################ UPDATE RECORD TITLE IN DB ###################################
##############################################################################################
##############################################################################################

def update_record_title(record_uuid: str, new_title: str):
    """Update `record.name` in the database with the AI-generated title."""
    if not new_title:
        log_message("Error: Cannot update record with an empty title.", "error")
        return False

    with next(get_db()) as db:
        update_query = text("UPDATE record SET name = :title WHERE UUID = :uuid")
        db.execute(update_query, {"title": new_title, "uuid": record_uuid})
        db.commit()

    log_message(f"Updated record {record_uuid} with new title: {new_title}", "info")
    return True


##############################################################################################
####################### FETCH RECORD METADATA FOR STORAGE IN TREE NODES ######################
##############################################################################################
##############################################################################################

def fetch_tree_data():
        """Retrieve all records and genus entries needed to populate the tree."""
        
        with next(get_db()) as db:
            # ✅ Fetch genus entries
            genus_query = """
                SELECT UUID, name, description, genus_type_id
                FROM genus;
            """
            genus_result = db.execute(text(genus_query)).mappings().all()

            # ✅ Fetch records along with `rectype.icon`
            record_query = """
                SELECT record.UUID, record.parent_UUID, record.name, record.rectype_id, 
                       rectype.name AS rectype, rectype.icon as icon, rectype.content_schema, 
                       rectype.content_caption, rectype.content_render_class
                FROM record
                JOIN rectype ON record.rectype_id = rectype.id;
            """
            record_result = db.execute(text(record_query)).mappings().all()

        return {"genera": genus_result, "records": record_result}

##############################################################################################
#### FETCH CONTENT FROM DB AND STORE IN APP_STATE VARIABLES (SCHEMA and CONTENT are DICT) ####
##############################################################################################
##############################################################################################

def create_dynamic_class(schema: Dict[str, Any]):
    """Create a dynamic class based on the schema and include necessary fields like rectype, name, etc."""
    
    # Define the class attributes based on the schema's "header" and other fields
    attributes = {field: None for field in schema.get("header", [])}
    
    # Add other essential fields (rectype, name, content) to the dynamic class
    attributes["rectype"] = None
    attributes["name"] = None
    attributes["content"] = None  # Default content field
    
    # Create the dynamic class using type()
    return type("DynamicContent", (object,), attributes)

###############################################################################################
def fetch_content(record_UUID: str):
    """Fetch content and dynamically create an object using the current schema."""

    # ✅ Ensure `app_state.current_schema` is always a dictionary
    if isinstance(app_state.current_schema, str):
        try:
            parsed_schema = json.loads(app_state.current_schema)
            app_state.current_schema = parsed_schema  # Store as dict
            log_message("✅ Converted `app_state.current_schema` from string to dictionary", "info")
        except json.JSONDecodeError:
            log_message(f"❌ Error parsing `app_state.current_schema`: {app_state.current_schema}", "error")
            return

    schema = app_state.current_schema  # ✅ Now guaranteed to be a dictionary
    rectype = app_state.current_rectype

    if not schema or not rectype:
        log_message("Missing schema or rectype in app_state", "error")
        return

    # Create a dynamic class using the schema
    ContentClass = create_dynamic_class(schema)
    content_instance = ContentClass()

    # ✅ Fetch header fields
    header_columns = schema.get("header", [])
    if isinstance(header_columns, str):
        header_columns = [header_columns]  # Convert single field to list if necessary

    content_columns = schema.get("content", ["content"])  # Allow multiple content fields in future
    if isinstance(content_columns, str):
        content_columns = [content_columns]

    columns_to_fetch = ", ".join(header_columns + content_columns)

    content_query = f"""
        SELECT {columns_to_fetch}
        FROM {rectype}
        WHERE rec_UUID = :record_UUID
    """

    with next(get_db()) as db:
        content_result = db.execute(text(content_query), {"record_UUID": record_UUID}).mappings().first()

        if not content_result:
            log_message(f"No content found for {record_UUID}", "warning")
            return

        # Store fields inside dictionary
        header_data = {key: content_result.get(key, "N/A") for key in header_columns}
        content_data = {key: content_result.get(key, "") for key in content_columns}

        # Fetch and store appendix items
        appendix = schema.get("appendix", [])
        appendix_data = {}

        if appendix:
            for item in appendix:
                if item == "note":
                    notes_query = "SELECT note FROM rec_note WHERE rec_UUID = :record_UUID"
                    notes = db.execute(text(notes_query), {"record_UUID": record_UUID}).mappings().all()
                    appendix_data["notes"] = [note["note"] for note in notes] if notes else []

                elif item == "source":
                    sources_query = "SELECT name, author, year FROM rec_source WHERE rec_UUID = :record_UUID"
                    sources = db.execute(text(sources_query), {"record_UUID": record_UUID}).mappings().all()
                    appendix_data["sources"] = [{"name": s["name"], "author": s["author"], "year": s["year"]} for s in sources] if sources else []

                elif item == "url":
                    urls_query = "SELECT title, url FROM rec_url WHERE rec_UUID = :record_UUID"
                    urls = db.execute(text(urls_query), {"record_UUID": record_UUID}).mappings().all()
                    appendix_data["urls"] = [{"title": u["title"], "url": u["url"]} for u in urls] if urls else []

        # ✅ Store final structured object in `app_state`
        setattr(content_instance, "header", header_data)
        setattr(content_instance, "content", content_data)
        setattr(content_instance, "appendix", appendix_data)

        app_state.current_content = content_instance
        app_state.current_content_markdown = content_data.get("summary", "")  # Default to summary

        log_message(f"✅ Content fetched and stored for {record_UUID}: {vars(content_instance)}", "info")

    return content_instance


##############################################################################################
################################## SAVE BACK TO DB ###########################################
##############################################################################################
##############################################################################################

def save_record_to_db():
    """Save the current content in `app_state.current_content` to the correct database table."""
    
    if not app_state.current_UUID:
        log_message("❌ Cannot save: No record selected.", "error")
        return False

    # ✅ Use `next(get_db())` to correctly retrieve the session
    with next(get_db()) as session:
    
        # ✅ Determine the correct table based on rectype
        table_name = app_state.current_rectype
        if not table_name:
            log_message("❌ Cannot save: No rectype found in app_state.", "error")
            return False

        # ✅ Get actual table columns from schema
        schema = app_state.current_schema
        if isinstance(schema, str):
            schema = json.loads(schema)

        # ✅ Ensure both `header` and `content` are lists before merging
        header_fields = schema.get("header", [])
        content_fields = schema.get("content", [])

        if isinstance(header_fields, str):
            header_fields = [header_fields]  # ✅ Convert single string to list
        if isinstance(content_fields, str):
            content_fields = [content_fields]  # ✅ Convert single string to list

        table_columns = set(header_fields + content_fields)  # ✅ Now both are lists

        # ✅ Extract structured content data
        content_data = {}

        # ✅ Flatten `header` and `content` fields
        if hasattr(app_state.current_content, "header"):
            content_data.update(app_state.current_content.header)
        if hasattr(app_state.current_content, "content"):
            content_data.update(app_state.current_content.content)

        # ✅ Remove fields that are not in the schema (appendix excluded)
        content_data = {k: v for k, v in content_data.items() if k in table_columns}

        # ✅ Ensure we don't update UUID directly
        if "rec_UUID" in content_data:
            del content_data["rec_UUID"]

        # ✅ Convert dictionary to column assignments
        columns = ", ".join([f"{key} = :{key}" for key in content_data.keys()])
        values = {**content_data, "record_UUID": app_state.current_UUID}  # Add UUID for WHERE clause

        # ✅ Construct the UPDATE query (explicitly wrap in text())
        query = text(f"""
        UPDATE {table_name}
        SET {columns}
        WHERE rec_UUID = :record_UUID
        """)

        try:
            session.execute(query, values)  # ✅ Query is now correctly wrapped
            session.commit()
            log_message(f"✅ Successfully saved content to `{table_name}` for UUID: {app_state.current_UUID}", "info")
            return True

        except Exception as e:
            log_message(f"❌ Error saving content to `{table_name}`: {str(e)}", "error")
            session.rollback()
            return False

########### APPENDICES ###########



def save_appendix_entry_to_db(appendix_type, data):
    """Save appendix data to the correct table."""
    log_message(f"💾 Attempting to save {appendix_type}: {data}", "debug")

    if not app_state.current_UUID:
        log_message("❌ Cannot save: No record selected.", "error")
        return False

    new_uuid = str(uuid.uuid4())  # Generate a new UUID for the record

    with next(get_db()) as db:
        try:
            if appendix_type == "note":
                query = text("""
                    INSERT INTO rec_note (UUID, rec_UUID, note)
                    VALUES (:uuid, :record_UUID, :note)
                """)
                params = {
                    "uuid": new_uuid,
                    "record_UUID": app_state.current_UUID,
                    "note": data["note"]
                }

            elif appendix_type == "source":
                query = text("""
                    INSERT INTO rec_source (UUID, rec_UUID, name, type, author, year)
                    VALUES (:uuid, :record_UUID, :name, :type, :author, :year)
                """)
                params = {
                    "uuid": new_uuid,
                    "record_UUID": app_state.current_UUID,
                    "name": data["name"],
                    "type": data["type"],
                    "author": data.get("author", None),
                    "year": data.get("year", None)
                }

            elif appendix_type == "url":
                query = text("""
                    INSERT INTO rec_url (UUID, rec_UUID, title, url)
                    VALUES (:uuid, :record_UUID, :title, :url)
                """)
                params = {
                    "uuid": new_uuid,
                    "record_UUID": app_state.current_UUID,
                    "title": data["title"],
                    "url": data["url"]
                }

            else:
                log_message(f"❌ Invalid appendix type: {appendix_type}", "error")
                return False

            # ✅ Log query and params before execution
            log_message(f"📝 SQL Query: {query}", "debug")
            log_message(f"📌 SQL Params: {params}", "debug")

            result = db.execute(query, params)  # Try executing the query
            log_message(f"✅ SQL Execution Result: {result.rowcount} row(s) affected", "info")

            db.commit()
            log_message(f"✅ Commit successful for {appendix_type}.", "info")
            return True

        except Exception as e:
            log_message(f"❌ SQL Error: {str(e)}", "error")
            db.rollback()
            return False

##############################################################################################
################################## DELETE FROM DB ############################################
##############################################################################################


########### APPENDICES ###########

def delete_from_database(appendix_type: str, uuid: str):
    """Delete an appendix item from the database by UUID."""
    with next(get_db()) as db:
        try:
            if appendix_type == "note":
                query = text("DELETE FROM rec_note WHERE UUID = :uuid")
            elif appendix_type == "source":
                query = text("DELETE FROM rec_source WHERE UUID = :uuid")
            elif appendix_type == "url":
                query = text("DELETE FROM rec_url WHERE UUID = :uuid")
            else:
                log_message(f"❌ Invalid appendix type for deletion: {appendix_type}", "error")
                return

            params = {"uuid": uuid}
            db.execute(query, params)
            db.commit()
            log_message(f"✅ Deleted {appendix_type} with UUID {uuid} from database.", "info")

        except Exception as e:
            log_message(f"❌ SQL Error while deleting {appendix_type}: {str(e)}", "error")
            db.rollback()

#############################################################################################
################################## EMBEDDINGS ###############################################
#############################################################################################
#############################################################################################

def save_embeddings(record):
    """Generate and store embeddings for a given record."""

    if not app_state.current_UUID:
        log_message("❌ Cannot save embeddings: No record selected.", "error")
        return

    # ✅ Ensure valid content
    content_text = "\n".join(str(value) for value in record.content.values() if value)

    if not content_text.strip():
        log_message(f"⚠ Skipping embedding generation for {app_state.current_UUID}: Empty content", "warning")
        return

    # ✅ Generate embedding
    client = OpenAI()
    response = client.embeddings.create(input=content_text, model="text-embedding-ada-002")
    embedding_vector = response.data[0].embedding

    # ✅ Convert to JSON
    embedding_json = json.dumps(embedding_vector)

    with next(get_db()) as db:
        try:
            # ✅ Insert or Update embedding
            query = text("""
                INSERT INTO embeddings (rec_UUID, embedding, model)
                VALUES (:record_UUID, :embedding, 'text-embedding-ada-002')
                ON DUPLICATE KEY UPDATE embedding = :embedding, model = 'text-embedding-ada-002'
            """)
            params = {
                "record_UUID": app_state.current_UUID,  # ✅ Corrected
                "embedding": embedding_json
            }

            db.execute(query, params)
            db.commit()
            log_message(f"✅ Embedding stored for record {app_state.current_UUID}", "info")

        except Exception as e:
            log_message(f"❌ Error storing embedding: {str(e)}", "error")
            db.rollback()

