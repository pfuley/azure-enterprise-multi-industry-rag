def build_context(search_results: list[dict]) -> str:
    if not search_results:
        return ""

    context_blocks = []

    for result in search_results:
        source = result["file_name"]
        chunk_id = result["chunk_id"]
        content = result["content"]

        context_blocks.append(
            f"""
SOURCE: {source}
CHUNK_ID: {chunk_id}
CONTENT:
{content}
""".strip()
        )

    return "\n\n---\n\n".join(context_blocks)