from clio.core.state import app_state
from clio.utils.logging import log_message



##############################################################################################
########################### RENDER MARKDOWN TEXT FROM CONTENT DICT OBJECT#####################


def render_markdown(content_instance):
    """Render the markdown content based on the dynamic content object."""

    # ✅ Log app_state details for debugging
    log_message(f"app_state.current_UUID: {app_state.current_UUID}", "info")
    log_message(f"app_state.current_rectype: {app_state.current_rectype}", "info")
    log_message(f"app_state.current_schema: {app_state.current_schema}", "info")
    log_message(f"app_state.current_record_name: {app_state.current_record_name}", "info")
    log_message(f"app_state.current_content: {app_state.current_content}", "info")
    log_message(f"app_state.current_render_class: {app_state.current_render_class}", "info")
    log_message(f"app_state.current_content_markdown: {app_state.current_content_markdown}", "info")

    rectype = app_state.current_rectype or "UNKNOWN"
    record_name = content_instance.header.get("title", "Untitled")  # ✅ Use structured header
    content_caption = app_state.current_content_caption or "Content"
    log_message(f"Rendering Markdown for {rectype}: {record_name}", "debug")

    # ✅ Start Markdown text
    markdown_text = f"# {rectype}: {record_name}\n\n"

    # ✅ Header Fields (handling `None` values)
    for field, value in content_instance.header.items():
        markdown_text += f"- **{field.capitalize()}**: {value if value is not None else 'N/A'}\n"

    # ✅ Add a single content section header
    markdown_text += f"\n## {content_caption}\n\n"

    # ✅ Join all content fields into a single text block (handling `None`)
    content_text = "\n\n".join(str(value) if value is not None else "" for value in content_instance.content.values())
    markdown_text += f"{content_text}\n\n"

    # ✅ Appendix Sections
    if hasattr(content_instance, "appendix"):
        if "notes" in content_instance.appendix and content_instance.appendix["notes"]:
            markdown_text += "\n### Notes\n"
            for note in content_instance.appendix["notes"]:
                markdown_text += f"- {note if note else 'Empty Note'}\n"

        if "sources" in content_instance.appendix and content_instance.appendix["sources"]:
            markdown_text += "\n### Sources\n"
            for source in content_instance.appendix["sources"]:
                markdown_text += f"- **{source.get('name', 'Unknown')}** ({source.get('author', 'Unknown')}, {source.get('year', 'N/A')})\n"

        if "urls" in content_instance.appendix and content_instance.appendix["urls"]:
            markdown_text += "\n### URLs\n"
            for url in content_instance.appendix["urls"]:
                url_title = url.get("title", "Untitled")
                url_link = url.get("url")
                url_href = url_link if url_link is not None else "#"  # ✅ If URL is None, set it to "#"

                markdown_text += f"- [{url_title}]({url_href})\n"




    log_message(f"Final Markdown Output:\n{markdown_text}", "debug")
    return markdown_text

