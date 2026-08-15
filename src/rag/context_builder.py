def build_context(search_results: list[dict]) -> str:
    if not search_results:
        return ""

    context_blocks = []

    for result in search_results:
        source = result["file_name"]
        chunk_id = result["chunk_id"]
        page_number = result.get("page_number")
        content = result["content"]

        page_label = (
            f"Page {page_number}"
            if page_number is not None
            else "Page unavailable"
        )

        context_blocks.append(
            f"""
SOURCE: {source}
PAGE: {page_label}
CHUNK_ID: {chunk_id}
CONTENT:
{content}
""".strip()
        )

    return "\n\n---\n\n".join(context_blocks)