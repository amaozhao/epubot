# 导入 Agno 必要的组件
from agno.agent import Agent
from agno.models.mistral.mistral import MistralChat
from agno.team.team import Team

# 可能需要其他导入


class Translator:
    def __init__(self, source_language="English", target_language="Chinese"):
        self.source_language = source_language
        self.target_language = target_language

        # Agent 指令保持不变 (它们已经期望接收字典输入)
        self.translator = Agent(
            name="Translator",
            role="Translate HTML content preserving structure. Revise based on feedback.",
            model=MistralChat(id="mistral-small-latest"),
            instructions=[
                "Context: {'original_html', 'source_language', 'target_language'} (+ optional 'suggestions', 'previous_translation_html').",
                "Translate text in 'original_html' from 'source_language' to 'target_language'.",
                "**CRITICAL:** Preserve all HTML tags/attributes EXACTLY. Translate ONLY text content between tags.",
                "If 'suggestions' provided, revise 'previous_translation_html' based on 'original_html' and 'suggestions', maintaining structure/target language.",
                "Output ONLY resulting valid HTML.",
            ],
        )

        self.reviewer = Agent(
            name="Reviewer",
            role="Review HTML translation for content and structure. Provide suggestions or approve.",
            model=MistralChat(id="mistral-small-latest"),
            instructions=[
                "Context: {'original_html', 'translated_html', 'source_language', 'target_language'}.",
                "Review 'translated_html' against 'original_html' ({source_language} to {target_language}).",
                "Check content accuracy/fluency AND strict HTML structure preservation (only text translated, tags/attributes intact).",
                "Provide specific suggestions for improvement (list format).",
                "If perfect (content+structure), output ONLY the marker '[APPROVED_NO_SUGGESTIONS]'.",
                "If suggesting, output ONLY the suggestions list.",
            ],
        )

        # 协调者 Team (进一步精简和修改指令，使其更加流程化、无对话)
        self.team = Team(
            name="HTML Translation Coordinator",
            mode="coordinate",
            model=MistralChat(
                id="mistral-small-latest"
            ),  # 注意模型能力对复杂指令执行的影响
            members=[self.translator, self.reviewer],
            description="Manages HTML translation, review, and revision loop.",
            instructions=[
                # **核心修改:** 直接进入输入处理和流程执行
                "**PROCESS_START**",  # 明确标记流程开始
                "GET_INPUT: Extract 'original_html' from context default key ('input'). Get 'source_language' (default 'English'). Get 'target_language' (default 'Chinese').",
                "STORE_CONTEXT: Store 'original_html', 'current_source_language', 'current_target_language'.",
                "**WORKFLOW_STEPS**",  # 明确标记工作流步骤的开始
                "STEP 1: TRANSLATE. Input to Translator: {'original_html': stored_original_html, 'source_language': stored_source_language, 'target_language': stored_target_language}. Output: 'current_translated_html'.",  # 使用更简洁的步骤描述
                "STEP 2: REVIEW. Input to Reviewer: {'original_html': stored_original_html, 'translated_html': current_translated_html, 'source_language': stored_source_language, 'target_language': stored_target_language}. Output: Reviewer_response.",
                "STEP 3: CHECK_LOOP. Reviewer_response == '[APPROVED_NO_SUGGESTIONS]'?",
                "  IF TRUE: **PROCESS_COMPLETE**. Final Output: current_translated_html.",
                "  IF FALSE (suggestions): Extract_suggestions from Reviewer_response. Input to Translator: {'original_html': stored_original_html, 'previous_translation_html': current_translated_html, 'source_language': stored_source_language, 'target_language': stored_target_language, 'suggestions': extracted_suggestions}. Output: 'revised_html'.",
                "  UPDATE: current_translated_html = revised_html.",
                "  Input to Reviewer: {'original_html': stored_original_html, 'translated_html': current_translated_html, 'source_language': stored_source_language, 'target_language': stored_target_language}. REPEAT_STEP 3.",  # 明确重复步骤
                # 保留输入输出格式约束 (可以精简措辞)
                "INPUT_FORMAT_TO_MEMBERS: Always dict with keys: 'original_html', 'translated_html'/'previous_translation_html', 'source_language', 'target_language' (+optional 'suggestions').",
                "OUTPUT_FORMAT_FROM_MEMBERS: Only HTML OR Only '[APPROVED_NO_SUGGESTIONS]' OR Only suggestions list.",
                "LANGS_IN_INPUT: Always include 'source_language', 'target_language' in member input dicts.",
                "**FINAL_OUTPUT_ONLY**: Output ONLY the final translated HTML upon **PROCESS_COMPLETE**. No extra text.",  # 明确最终输出约束
            ],
            add_datetime_to_instructions=True,
            add_member_tools_to_system_message=False,
            enable_agentic_context=True,
            share_member_interactions=True,
            show_members_responses=True,
            # markdown=True,
        )

    # --- 运行 Team 的方法 ---
    def translate(self, content):
        translated = self.team.run(
            content,  # 原始 HTML 字符串作为主要输入
            source_language=self.source_language,  # 作为关键字参数传入
            target_language=self.target_language,  # 作为关键字参数传入
            stream=False,  # 获取最终结果而不是流式打印
        )
        return translated.content


# --- 4. 使用 Translator 类 ---

# 示例文本 (纯 HTML)
html_content_1 = """
<div>
  <h1>Hello World</h1>
  <p>This is a test.</p>
</div>
"""

# 示例 1: 使用默认语言 (English -> Chinese)
my_translator_default = Translator()
print(f"--- Translating (Default: En->Zh) ---")
final_translation_1 = my_translator_default.translate(html_content_1)
print(f"--- Final Translation (Default: En->Zh): ---\n{final_translation_1}\n---")


print("\n\n" + "=" * 50 + "\n\n")  # 分隔线


# 示例 2: 指定语言 (French -> Chinese)
html_content_2 = """
<div>
  <h1>Bonjour le monde</h1>
  <p>Ceci est un test.</p>
</div>
"""
my_translator_fr_zh = Translator(source_language="French", target_language="Chinese")
print(f"--- Translating (Fr->Zh) ---")
final_translation_2 = my_translator_fr_zh.translate(html_content_2)
print(f"--- Final Translation (Fr->Zh): ---\n{final_translation_2}\n---")


# 可以添加更多示例来测试不同语言和修订循环

print("\n--- All Translation Processes Finished ---")
