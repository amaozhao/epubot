class HTMLBuilder:
    def build(self, chunks: list) -> str:
        if not isinstance(chunks, list):
            raise ValueError("input chunks must be a list")
        html_parts = []
        for chunk in chunks:
            _content = chunk.translated if chunk.translated else chunk.content
            html_parts.append(_content)

        return "".join(html_parts)
