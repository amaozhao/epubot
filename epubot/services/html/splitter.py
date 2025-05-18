import re

import tiktoken

from epubot.schemas.chunk import Chunk


class HTMLSplitter:
    """
    Splits HTML content into chunks based on a maximum token count,
    prioritizing splitting at the end of closing HTML tags within the token limit.
    """

    def __init__(self, count: int = 6000):
        # Count is now the maximum token count per chunk
        if not isinstance(count, int) or count <= 0:
            raise ValueError("count must be a positive integer token count")
        self.count = count
        # Regex to find closing tags (e.g., </p>, </div>)
        self.tag_pattern = re.compile(r"</[^>]+>")
        # Tokenizer for counting tokens
        # Using cl100k_base is standard for general text
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def get_token_count(self, content: str) -> int:
        if not content:
            return 0
        return len(self.tokenizer.encode(content))

    def split(self, html: str) -> list[Chunk]:
        """
        Splits the provided HTML string into Chunk objects.

        The splitting process prioritizes staying within the self.count token limit
        and, within that limit, prefers splitting at the end of closing HTML tags.

        Args:
            html: The input HTML content as a string.

        Returns:
            A list of Chunk objects.
        """
        if not isinstance(html, str):
            raise ValueError("html content must be a string")

        chunks: list[Chunk] = []  # List to store the resulting chunks
        pos = 0  # Current position in the HTML string
        cid = 0  # Chunk ID counter
        n = len(html)  # Total length of the HTML string

        while pos < n:
            cid += 1
            token_limit_char_end = pos
            for i in range(pos + 1, n + 1):
                current_substring = html[pos:i]
                token_count = self.get_token_count(current_substring)

                if token_count <= self.count:
                    token_limit_char_end = i
                else:
                    break

            if token_limit_char_end == pos and pos < n:
                token_limit_char_end = pos + 1

            # final_split_at = token_limit_char_end
            last_valid_tag_end = pos

            for m in self.tag_pattern.finditer(html, pos=pos):
                tag_end = m.end()
                if tag_end <= token_limit_char_end:
                    last_valid_tag_end = tag_end
                else:
                    break

            if last_valid_tag_end > pos:
                split_at = last_valid_tag_end
            else:
                split_at = token_limit_char_end

            if split_at <= pos and pos < n:
                split_at = pos + 1

            # 4. Create the chunk object
            chunk_content = html[pos:split_at]
            if chunk_content.strip():
                chunk = Chunk(
                    id=f"{cid}",
                    file_id="",
                    content=chunk_content.strip(),
                    translated=None,
                    tokens=self.get_token_count(chunk_content),
                    retry_count=0,
                )
                chunks.append(chunk)

            pos = split_at

        chunks = [chunk for chunk in chunks if chunk.content.strip()]
        return chunks
