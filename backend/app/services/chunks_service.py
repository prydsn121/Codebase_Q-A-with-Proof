import tiktoken

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

encoding = tiktoken.get_encoding("cl100k_base")

def chunk_text(text, file_path):
    lines = text.split("\n")
    tokens = encoding.encode(text)

    chunks = []
    start_token = 0

    while start_token < len(tokens):
        end_token = start_token + CHUNK_SIZE
        chunk_tokens = tokens[start_token:end_token]
        chunk_text_content = encoding.decode(chunk_tokens)

        # Estimate line numbers
        decoded_before = encoding.decode(tokens[:start_token])
        start_line = len(decoded_before.split("\n"))
        end_line = start_line + len(chunk_text_content.split("\n"))

        chunks.append({
            "file_path": file_path,
            "content": chunk_text_content,
            "start_line": start_line,
            "end_line": end_line
        })

        start_token += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks
