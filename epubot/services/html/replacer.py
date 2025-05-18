import re
import secrets
import string
from typing import Dict

from bs4 import BeautifulSoup, Tag

from epubot.config.logger import logger


class Placeholder:
    characters = string.ascii_letters + string.digits  # 62种字符

    def __init__(self):
        self.placer_map: Dict[str, str] = {}
        self.generated = set()

    def _generate_placeholder(self, original_tag):
        while True:
            candidate = "".join(secrets.choice(self.characters) for _ in range(8))
            if candidate not in self.generated:
                self.generated.add(candidate)
                holder = f"{{{candidate}}}"
                self.placer_map[holder] = str(original_tag)
                return holder


class HTMLReplacer:
    IGNORE_TAGS = {
        # 脚本和样式
        "script",
        "style",
        # 代码相关
        "code",
        "pre",
        "kbd",
        "var",
        "samp",
        # 特殊内容
        "svg",
        "math",
        "canvas",
        "address",
        "applet",
        # 多媒体标签
        "img",
        "audio",
        "video",
        "track",
        "source",
        # 表单相关
        "input",
        "button",
        "select",
        "option",
        "textarea",
        "form",
        # 元数据和链接
        "meta",
        "link",
        # "a", # User commented out 'a', keeping consistent
        # 嵌入内容
        "iframe",
        "embed",
        "object",
        "param",
        # 技术标记
        "time",
        "data",
        "meter",
        "progress",
        # XML相关
        "xml",
        "xmlns",
        # EPUB特有标签
        "epub:switch",
        "epub:case",
        "epub:default",
        "annotation",
        "note",
    }

    def __init__(self, parser: str = "html.parser"):
        self.parser = parser
        self.placeholder = Placeholder()

    def _replace(self, node):
        # from bs4 import Tag
        for child in list(node.contents):
            if isinstance(child, Tag):
                if child.name in self.IGNORE_TAGS:
                    placeholder = self.placeholder._generate_placeholder(child)
                    child.replace_with(placeholder)
                else:
                    self._replace(child)
        return str(node)

    def replace(self, content: str) -> str:
        soup = BeautifulSoup(content, self.parser)
        return self._replace(soup)

    def restore(self, content: str) -> str:
        for placeholder, original_content in self.placeholder.placer_map.items():
            content = content.replace(placeholder, original_content)

        # Optional: Check for any remaining placeholder
        remaining_placeholders = re.findall(r"{{[a-f0-9]+}}", content)
        if remaining_placeholders:
            logger.warning(
                "Found remaining placeholder comments after restoration",
                count=len(remaining_placeholders),
                examples=remaining_placeholders[:5],
            )
        return content
