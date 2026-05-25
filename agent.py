import os
import sys
from pathlib import Path

from openai import OpenAI


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


MODEL_NAME = "deepseek-chat"
REVIEW_PROMPT_PREFIX = "Please perform a professional code review."

TEXT = {
    "missing_key": "\u8bf7\u5728\u540c\u76ee\u5f55\u7684 .env \u6587\u4ef6\u91cc\u586b\u5199 DEEPSEEK_API_KEY\u3002",
    "system": "\u4f60\u662f\u4e00\u4e2a\u4e13\u4e1a\u7684\u4ee3\u7801\u5ba1\u67e5\u5de5\u7a0b\u5e08\uff0c\u64c5\u957f Python\u3001C \u548c C++\u3002",
    "cli_start": "\u4ee3\u7801 Review Agent \u542f\u52a8\uff08\u8f93\u5165 exit \u9000\u51fa\uff09",
    "cli_prompt": "\u4f60\uff1a",
    "agent": "Agent\uff1a",
    "page_title": "\u4ee3\u7801 Review Agent",
    "caption": "\u4e0a\u4f20\u6216\u7c98\u8d34\u4ee3\u7801\uff0c\u751f\u6210\u53ef\u4e0b\u8f7d\u7684\u5ba1\u67e5\u62a5\u544a",
    "chat_input": "\u7ee7\u7eed\u8ffd\u95ee\u4ee3\u7801\u95ee\u9898",
    "spinner": "\u6b63\u5728\u5ba1\u67e5...",
    "sidebar_title": "\u5ba1\u67e5\u8bbe\u7f6e",
    "model": "\u6a21\u578b",
    "language": "\u4ee3\u7801\u8bed\u8a00",
    "api_status": "API Key \u72b6\u6001",
    "api_ready": "\u5df2\u4ece .env \u8bfb\u53d6",
    "api_missing": "\u672a\u627e\u5230",
    "clear_chat": "\u6e05\u7a7a\u5bf9\u8bdd",
    "chat_cleared": "\u5bf9\u8bdd\u5df2\u6e05\u7a7a",
    "usage_title": "\u5de5\u4f5c\u6d41",
    "usage": "1. \u9009\u62e9\u5ba1\u67e5\u7c7b\u578b\u548c\u8be6\u7ec6\u5ea6\n2. \u4e0a\u4f20\u6587\u4ef6\u6216\u7c98\u8d34\u4ee3\u7801\n3. \u751f\u6210\u62a5\u544a\u540e\u7ee7\u7eed\u8ffd\u95ee",
    "review_type": "\u5ba1\u67e5\u7c7b\u578b",
    "detail_level": "\u8f93\u51fa\u8be6\u7ec6\u5ea6",
    "upload": "\u4e0a\u4f20\u4ee3\u7801\u6587\u4ef6",
    "code_input": "\u4ee3\u7801\u8f93\u5165\u533a",
    "code_placeholder": "\u5728\u8fd9\u91cc\u7c98\u8d34\u8981 review \u7684\u4ee3\u7801...",
    "extra_request": "\u989d\u5916\u8981\u6c42",
    "extra_placeholder": "\u4f8b\u5982\uff1a\u91cd\u70b9\u770b\u5185\u5b58\u6cc4\u6f0f\u3001SQL \u6ce8\u5165\u3001\u65b0\u624b\u80fd\u770b\u61c2\u7684\u89e3\u91ca...",
    "start_review": "\u751f\u6210\u5ba1\u67e5\u62a5\u544a",
    "no_code": "\u8bf7\u5148\u4e0a\u4f20\u6587\u4ef6\u6216\u7c98\u8d34\u4ee3\u7801\u3002",
    "latest_report": "\u6700\u65b0\u5ba1\u67e5\u62a5\u544a",
    "download_report": "\u4e0b\u8f7d Markdown \u62a5\u544a",
    "tab_review": "\u4ee3\u7801\u5ba1\u67e5",
    "tab_report": "\u5ba1\u67e5\u62a5\u544a",
    "tab_chat": "\u8ffd\u95ee\u8bb0\u5f55",
    "empty_report": "\u8fd8\u6ca1\u6709\u751f\u6210\u62a5\u544a\u3002",
    "empty_chat": "\u8fd8\u6ca1\u6709\u8ffd\u95ee\u8bb0\u5f55\u3002",
    "uploaded": "\u5df2\u8bfb\u53d6\u6587\u4ef6",
}


def load_local_env():
    env_path = Path(__file__).with_name(".env")
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ[key] = value


def get_client():
    load_local_env()

    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not api_key or "DeepSeekKey" in api_key:
        raise RuntimeError(TEXT["missing_key"])

    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com",
    )


def has_api_key():
    load_local_env()
    api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    return bool(api_key and "DeepSeekKey" not in api_key)


def make_system_message(language="Python"):
    return {
        "role": "system",
        "content": f'{TEXT["system"]}\n\u5f53\u524d\u4e3b\u8981\u5ba1\u67e5\u8bed\u8a00\uff1a{language}\u3002',
    }


def ask_agent(client, messages, user_input):
    messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )
    reply = response.choices[0].message.content
    messages.append({"role": "assistant", "content": reply})
    return reply


def build_review_prompt(language, review_type, detail_level, code, extra_request="", filename=""):
    file_label = filename or "\u672a\u547d\u540d\u4ee3\u7801"
    extra = extra_request.strip() or "\u65e0"
    return f"""{REVIEW_PROMPT_PREFIX}

File: {file_label}
Language: {language}
Review type: {review_type}
Detail level: {detail_level}
Extra request: {extra}

Please respond in Chinese Markdown and include:
1. Overall assessment
2. Main issues, sorted by severity
3. Improvement suggestions
4. Key code examples when useful

Code:
```{language.lower()}
{code}
```"""


def read_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return "", ""

    raw = uploaded_file.getvalue()
    for encoding in ("utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(encoding), uploaded_file.name
        except UnicodeDecodeError:
            continue

    return raw.decode("utf-8", errors="replace"), uploaded_file.name


def run_cli():
    client = get_client()
    messages = [make_system_message()]

    print(TEXT["cli_start"])
    print("-" * 40)

    while True:
        try:
            user_input = input(TEXT["cli_prompt"]).strip()
        except EOFError:
            print()
            break

        if user_input.lower() == "exit":
            break

        if not user_input:
            continue

        reply = ask_agent(client, messages, user_input)
        print(f'{TEXT["agent"]}{reply}')
        print("-" * 40)


def init_session_state(st, language):
    if "messages" not in st.session_state:
        st.session_state.messages = [make_system_message(language)]
    if "last_report" not in st.session_state:
        st.session_state.last_report = ""
    if "code_text" not in st.session_state:
        st.session_state.code_text = ""
    if "uploaded_name" not in st.session_state:
        st.session_state.uploaded_name = ""

    system_message = make_system_message(language)
    if st.session_state.messages[0]["content"] != system_message["content"]:
        st.session_state.messages[0] = system_message


def render_sidebar(st):
    with st.sidebar:
        st.title(TEXT["sidebar_title"])
        st.text_input(TEXT["model"], value=MODEL_NAME, disabled=True)
        language = st.selectbox(TEXT["language"], ["Python", "C", "C++"], index=0)
        review_type = st.selectbox(
            TEXT["review_type"],
            [
                "\u5168\u9762\u5ba1\u67e5",
                "Bug \u98ce\u9669",
                "\u6027\u80fd\u4f18\u5316",
                "\u5b89\u5168\u95ee\u9898",
                "\u4ee3\u7801\u98ce\u683c",
                "\u65b0\u624b\u89e3\u91ca",
            ],
            index=0,
        )
        detail_level = st.radio(
            TEXT["detail_level"],
            ["\u7b80\u6d01", "\u6807\u51c6", "\u8be6\u7ec6"],
            index=1,
        )

        st.divider()
        st.subheader(TEXT["api_status"])
        if has_api_key():
            st.success(TEXT["api_ready"])
        else:
            st.error(TEXT["api_missing"])

        st.divider()
        st.subheader(TEXT["usage_title"])
        st.write(TEXT["usage"])

        if st.button(TEXT["clear_chat"], use_container_width=True):
            st.session_state.messages = [make_system_message(language)]
            st.session_state.last_report = ""
            st.toast(TEXT["chat_cleared"])
            st.rerun()

    return language, review_type, detail_level


def render_review_tab(st, language, review_type, detail_level):
    uploaded_file = st.file_uploader(
        TEXT["upload"],
        type=["py", "c", "cpp", "h", "hpp", "txt", "md"],
    )
    uploaded_code, uploaded_name = read_uploaded_file(uploaded_file)
    if uploaded_code and uploaded_name != st.session_state.uploaded_name:
        st.session_state.code_text = uploaded_code
        st.session_state.uploaded_name = uploaded_name

    if st.session_state.uploaded_name:
        st.info(f'{TEXT["uploaded"]}\uff1a{st.session_state.uploaded_name}')

    with st.form("review_form"):
        code = st.text_area(
            TEXT["code_input"],
            key="code_text",
            placeholder=TEXT["code_placeholder"],
            height=320,
        )
        extra_request = st.text_input(
            TEXT["extra_request"],
            placeholder=TEXT["extra_placeholder"],
        )
        submitted = st.form_submit_button(TEXT["start_review"], type="primary", use_container_width=True)

    if not submitted:
        return

    if not code.strip():
        st.warning(TEXT["no_code"])
        return

    prompt = build_review_prompt(
        language=language,
        review_type=review_type,
        detail_level=detail_level,
        code=code.strip(),
        extra_request=extra_request,
        filename=st.session_state.uploaded_name,
    )
    try:
        client = get_client()
        with st.spinner(TEXT["spinner"]):
            reply = ask_agent(client, st.session_state.messages, prompt)
            st.session_state.last_report = reply
            st.rerun()
    except Exception as exc:
        st.error(str(exc))


def render_report_tab(st):
    if not st.session_state.last_report:
        st.info(TEXT["empty_report"])
        return

    st.subheader(TEXT["latest_report"])
    st.markdown(st.session_state.last_report)
    st.download_button(
        TEXT["download_report"],
        data=st.session_state.last_report,
        file_name="code_review.md",
        mime="text/markdown",
        use_container_width=True,
    )


def render_chat_tab(st):
    visible_messages = []
    for message in st.session_state.messages[1:]:
        if message["role"] == "user" and message["content"].startswith(REVIEW_PROMPT_PREFIX):
            continue
        if message["role"] == "assistant" and message["content"] == st.session_state.last_report:
            continue
        visible_messages.append(message)

    if not visible_messages:
        st.info(TEXT["empty_chat"])

    for message in visible_messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input(TEXT["chat_input"])
    if not user_input:
        return

    with st.chat_message("user"):
        st.write(user_input)

    try:
        client = get_client()
        with st.chat_message("assistant"):
            with st.spinner(TEXT["spinner"]):
                reply = ask_agent(client, st.session_state.messages, user_input)
                st.write(reply)
    except Exception as exc:
        st.error(str(exc))


def run_streamlit():
    import streamlit as st

    st.set_page_config(
        page_title=TEXT["page_title"],
        page_icon="code",
        layout="wide",
    )

    language, review_type, detail_level = render_sidebar(st)
    init_session_state(st, language)

    st.title(TEXT["page_title"])
    st.caption(TEXT["caption"])

    review_tab, report_tab, chat_tab = st.tabs(
        [TEXT["tab_review"], TEXT["tab_report"], TEXT["tab_chat"]]
    )

    with review_tab:
        render_review_tab(st, language, review_type, detail_level)
    with report_tab:
        render_report_tab(st)
    with chat_tab:
        render_chat_tab(st)


def running_in_streamlit():
    try:
        import streamlit as st
    except Exception:
        return False

    return st.runtime.exists()


if __name__ == "__main__":
    if running_in_streamlit():
        run_streamlit()
    else:
        run_cli()
