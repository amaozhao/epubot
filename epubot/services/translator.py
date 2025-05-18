import asyncio

from mistralai import Mistral, models
from tenacity import retry, stop_after_attempt, wait_exponential

from epubot.config.settings import settings


class Translator:
    _semaphore = asyncio.Semaphore(1)
    _last_request_time = 0
    model = "mistral-small-latest"
    # model = "mistral-medium-latest"
    # model = "open-mistral-nemo"

    def __init__(self, source_language="English", target_language="Chinese"):
        self.source_language = source_language
        self.target_language = target_language
        self.client = Mistral(api_key=settings.mistral_api_key)

    def _clean_symbol(self, text: str) -> str:
        """清理翻译结果中的代码标记.
        Args:
            text: 翻译结果文本
        Returns:
            清理后的文本
        """
        if not text:
            return text

        text = text.strip()
        # 处理开头的代码块标记
        # 可能的格式：```html、```xml、```、等
        if text.startswith("```"):
            # 找到第一个换行符
            first_newline = text.find("\n")
            if first_newline != -1:
                # 移除开头到第一个换行符之间的内容
                text = text[first_newline + 1:]
            else:
                # 如果没有换行符，说明整个文本就是一个标记
                text = text[3:]

        # 处理结尾的代码块标记
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]

        return text.strip()

    def _replace_designation(self, content: str) -> str:
        """替换文本中的指定标记."""
        if not content:
            return content

        # 替换指定的标记
        replacements = {
            "您": "你",
            "大型语言模型": " LLM ",
        }
        for old, new in replacements.items():
            content = content.replace(old, new)

        content = self._clean_symbol(content)

        return content

    async def _translate(
        self, text: str, source_lang: str, target_lang: str, **kwargs
    ) -> str:
        """Translate text using Mistral API."""
        # 构建提示内容
        prompt = f"""
        Translate the following HTML from {source_lang} to {target_lang}:

        ```html
        {text}
        ```
        """

        messages = [
            models.SystemMessage(
                content=f"""
                    You are an expert XML/HTML translator. Your primary task is to translate the *text content* found within the XML or HTML snippet provided by the user into the requested target language.

                    Translate from {source_lang} to {target_lang}. If languages are not specified, assume English as source and Chinese as target.

                    **CRITICAL STRUCTURE & CONTENT:**
                    Adhere strictly to the following rules to preserve markup integrity and translate only content:
                    - Translate ONLY the text content that appears BETWEEN the tags.
                    - Preserve ALL tags and attributes (XML/HTML) EXACTLY as they appear. The set of all tags (including both opening <tag> and closing </tag> tags) and attributes in output MUST be identical to original. **Absolutely NO tag or attribute must be lost, added, or changed.** # 强调不可丢失、添加、改变

                    **OUTPUT FORMAT:**
                    Your response MUST contain **ABSOLUTELY NOTHING EXCEPT** the translated XML or HTML content from the input snippet. Do NOT include any preamble, postamble, conversation, explanation, code block markers (```), markdown, or **any tags or attributes that were not present in the original input snippet.** Respond strictly with the raw, translated XML or HTML string. # 极度强调只输出原文片段的翻译，禁止添加

                    **QUALITY & FLOW:**
                    - Ensure the translated content is fluent, natural, uses correct punctuation, and standard written style.
                    - Adjust element order within the markup structure for natural target language flow, if needed. This reordering is an allowed exception to strict structural preservation, but you MUST NOT change, add, or remove any tags or attributes themselves during this reordering.
                    """
            ),
            models.UserMessage(content=prompt),
        ]

        response = await self.client.chat.complete_async(
            model=self.model,
            messages=messages,
            temperature=0.1,
            **kwargs,
        )
        result = response.choices[0].message.content

        return self._replace_designation(result)

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=2, min=10, max=30),
    )
    async def translate(
        self,
        content: str,
        source_lang: str = "English",
        target_lang: str = "Chinese",
        **kwargs,
    ) -> str:
        """Translate text with rate limiting and concurrency control."""
        async with self._semaphore:  # 使用信号量控制并发
            # 确保距离上次请求至少有1秒
            current_time = asyncio.get_event_loop().time()
            time_since_last_request = current_time - self._last_request_time
            if time_since_last_request < 3:
                await asyncio.sleep(3 - time_since_last_request)

            self.__class__._last_request_time = asyncio.get_event_loop().time()

            try:
                return await self._translate(
                    content, source_lang, target_lang, **kwargs
                )
            except Exception as e:
                raise e


if __name__ == "__main__":
    translator = Translator()
    text = """"""
    result = asyncio.run(
        translator.translate(
            text,
            source_lang="English",
            target_lang="Chinese",
        )
    )
    print(result)
