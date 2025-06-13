from clio.core.state import app_state
from clio.utils.log_util import log_message
from textual.containers import Container, Vertical
from textual.widgets import Input, TextArea, Label
from textual.app import ComposeResult

##############################################################################################
#################### DYNAMIC FORM FOR HEADER AND CONTENT DATA INPUT ##########################
##############################################################################################
##############################################################################################

class DynamicFormWidget(Vertical):
    """Dynamically generated form based on `app_state.current_schema`."""

    def __init__(self):
        super().__init__()
        self.header_inputs = {}  # Stores header input fields
        self.content_inputs = {}  # Stores content input fields

    def compose(self) -> ComposeResult:
        """Define the form structure (but do not populate values yet)."""
        log_message("🔍 Debug: Composing DynamicFormWidget structure...", "debug")

        self.header_container = Container(id="header-form", classes="form-section")
        self.content_container = Container(id="content-form", classes="form-section")

        yield self.header_container  # ✅ Yield individual containers
        yield self.content_container


    def on_mount(self):
        """Populate form fields with values after mounting."""
        log_message("🔍 Debug: Entering DynamicFormWidget.on_mount()", "debug")

        # ✅ Check if schema exists
        if not app_state.current_schema:
            log_message("❌ ERROR: Schema is empty, cannot build form.", "error")
            return

        # ✅ Get content data
        log_message("🔍 Debug: Fetching `app_state.current_content`...", "debug")
        content_data = app_state.current_content
        if not content_data:
            log_message("❌ ERROR: `app_state.current_content` is empty, aborting form generation.", "error")
            return

        log_message(f"🟢 Content Instance Fields: {vars(content_data)}", "debug")

        # ✅ Populate Header Fields
        log_message("🔍 Debug: Populating header fields...", "debug")
        self.populate_header_fields(content_data)

        # ✅ Populate Content Fields
        log_message("🔍 Debug: Populating content fields...", "debug")
        self.populate_content_fields(content_data)

        log_message("✅ DynamicFormWidget populated successfully.", "info")


#################### POPULATE HEADER FIELDS FROM APP_STATE ##########################

    def populate_header_fields(self, content_data):
        """Fill header fields with values."""

        # ✅ Ensure header_fields is always a list
        header_fields = app_state.current_schema.get("header", [])
        if isinstance(header_fields, str):
            header_fields = [header_fields]  # ✅ Convert single string to list

        existing_ids = set()  # ✅ Track IDs to prevent duplicates

        for field in header_fields:
            field_value = content_data.header.get(field, "")

            # ✅ Fix: Convert all values to strings
            if field_value is None:
                log_message(f"⚠ Warning: Header field '{field}' is None. Converting to empty string.", "warning")
                field_value = ""
            else:
                field_value = str(field_value)  # ✅ Ensure it's a string

            log_message(f"🔹 Setting header field '{field}' to '{field_value}'", "debug")

            field_id = f"field-{field}".replace(" ", "-").lower()

            # ✅ Ensure unique IDs
            counter = 1
            original_field_id = field_id
            while field_id in existing_ids:
                field_id = f"{original_field_id}-{counter}"
                counter += 1

            existing_ids.add(field_id)

            label = Label(f"{field.capitalize()}:", classes="input-label")
            input_field = Input(id=field_id, value=field_value, classes="form-textfield")  # ✅ Fix: `value` is always a string

            self.header_inputs[field] = input_field  # Store reference for updates
            self.header_container.mount(label, input_field)


####################   POPULATE CONTENT FIELD   ##########################


    def populate_content_fields(self, content_data):
        """Fill content fields with values."""

        # ✅ Ensure content_fields is always a list
        content_fields = app_state.current_schema.get("content", [])
        if isinstance(content_fields, str):
            content_fields = [content_fields]  # ✅ Convert single string to list

        content_caption = app_state.current_content_caption or "Content"

        existing_ids = set()  # ✅ Track IDs to prevent duplicates

        for field in content_fields:
            content_value = content_data.content.get(field, "")

            # ✅ Fix: Convert None or non-string values to strings
            if content_value is None:
                log_message(f"⚠ Warning: Content field '{field}' is None. Converting to empty string.", "warning")
                content_value = ""
            else:
                content_value = str(content_value)

            field_id = f"content-{field}".replace(" ", "-").lower()

            # ✅ Ensure unique IDs
            counter = 1
            original_field_id = field_id
            while field_id in existing_ids:
                field_id = f"{original_field_id}-{counter}"
                counter += 1

            existing_ids.add(field_id)

            log_message(f"🔹 Setting content field '{field}' as '{field_id}' with value: {content_value}", "debug")

            content_label = Label(f"{content_caption}:", classes="input-label")
            content_input = TextArea(id=field_id, text=content_value, classes="form-textarea")  # ✅ Ensures non-null text

            self.content_inputs[field] = content_input  # Store reference for updates
            self.content_container.mount(content_label, content_input)

