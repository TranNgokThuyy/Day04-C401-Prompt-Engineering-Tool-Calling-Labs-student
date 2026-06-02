from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version
from chat import run_model_tool_loop, safe_slug, trim_history

ROOT = Path(__file__).resolve().parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_transcript(path: Path, transcript: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(transcript, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def build_transcript_id(provider: str, version: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    return "streamlit_" + "_".join([safe_slug(version), safe_slug(provider), timestamp])


st.set_page_config(page_title="Research Agent Chat", layout="wide")
st.title("Research Agent Chat")
st.markdown("Ứng dụng chat-style cho research agent. Nhập prompt và nhấn Enter hoặc nút Gửi để chạy tool.")

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    version_label = st.text_input("Artifact version", value="v3")
    model_name = st.text_input("Model (optional)", value="")
    max_tool_rounds = st.slider("Max tool rounds", 1, 6, 4)
    history_window = st.slider("History window", 1, 10, 5)
    if st.button("Xóa lịch sử chat"):
        st.session_state.history = []
        st.session_state.query_input = ""
        st.experimental_rerun()

if "history" not in st.session_state:
    st.session_state.history = []
if "query_input" not in st.session_state:
    st.session_state.query_input = ""

system_prompt = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
system_prompt_text = system_prompt.read_text(encoding="utf-8")

st.markdown(
    """
    <style>
    .stApp .main .block-container { padding-bottom: 220px; }
    .chat-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 18px; }
    .chat-header h2 { margin: 0; }
    .chat-header .note { color: #475569; font-size: 0.95rem; }
    .chat-history { max-height: 64vh; overflow-y: auto; padding-right: 8px; }
    .chat-bubble { display: block; margin: 12px 0; padding: 16px 18px; border-radius: 24px; line-height: 1.6; max-width: 78%; word-break: break-word; }
    .chat-bubble.user { margin-left: auto; background: #dbeafe; color: #0f172a; border-bottom-right-radius: 8px; }
    .chat-bubble.agent { margin-right: auto; background: #e2e8f0; color: #0f172a; border-bottom-left-radius: 8px; }
    .chat-meta { font-size: 0.9rem; color: #475569; margin-bottom: 12px; }
    .chat-footer { position: fixed; bottom: 0; left: 0; right: 0; background: #ffffff; border-top: 1px solid #e2e8f0; padding: 18px 24px 20px 24px; box-shadow: 0 -14px 50px rgba(15, 23, 42, 0.08); z-index: 999; }
    .chat-footer .stTextInput > div > div > input { min-height: 48px; font-size: 1rem; }
    .chat-footer .stButton > button { min-width: 160px; font-weight: 600; }
    .system-prompt pre { max-height: 220px; overflow: auto; background: #ffffff; border: 1px solid #e2e8f0; padding: 14px; border-radius: 18px; }
    .stSidebar { background: #f8fafc; }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.container():
    st.markdown(
        "<div class='chat-header'><div><h2>Research Agent Chat</h2><div class='note'>Giao diện chat, prompt cố định phía dưới.</div></div></div>",
        unsafe_allow_html=True,
    )
    with st.expander("Xem system prompt và tool declaration", expanded=False):
        st.markdown("**System prompt hiện tại**")
        st.code(system_prompt_text, language="markdown")
        st.markdown("**Tool declarations**")
        st.write(
            "Các tool hiện có: clarify, timeline, social_search, lookup, fetch, format, send, policy, papers, paper_text, summarize, keywords, url_preview, sentiment, source_inspect, trend_analysis."
        )

    if st.session_state.history:
        st.markdown("<div class='chat-history'>", unsafe_allow_html=True)
        for index in range(0, len(st.session_state.history), 2):
            user_turn = st.session_state.history[index]
            assistant_turn = st.session_state.history[index + 1] if index + 1 < len(st.session_state.history) else None
            st.markdown(
                f"<div class='chat-bubble user'><strong>Bạn</strong><br>{user_turn['content']}</div>",
                unsafe_allow_html=True,
            )
            if assistant_turn:
                st.markdown(
                    f"<div class='chat-bubble agent'><strong>Agent</strong><br>{assistant_turn['content']}</div>",
                    unsafe_allow_html=True,
                )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("Chưa có lịch sử. Nhập prompt phía dưới để bắt đầu.")

with st.form("prompt_form"):
    st.markdown("<div class='chat-footer'>", unsafe_allow_html=True)
    query = st.text_input(
        "",
        key="query_input",
        placeholder="Gõ prompt và nhấn Enter hoặc Gửi...",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Gửi")
    st.markdown("</div>", unsafe_allow_html=True)

if submitted and query.strip():
    try:
        provider = make_provider(provider_name)
        tool_declarations = load_tool_declarations(tools_path)
        openai_tools = to_openai_tools(tool_declarations)
        messages = [
            {"role": "system", "content": system_prompt_text},
            *trim_history(st.session_state.history, history_window),
            {"role": "user", "content": query.strip()},
        ]

        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model_name or None,
            max_tool_rounds=max_tool_rounds,
        )

        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": query.strip()})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
        st.session_state.query_input = ""

        transcript_id = build_transcript_id(provider_name, version_label)
        artifact_version = build_artifact_version(version_label, system_prompt, tools_path)
        transcript = {
            "transcript_id": transcript_id,
            **artifact_version_dict(artifact_version),
            "provider": provider_name,
            "model": model_name or None,
            "system_prompt": str(system_prompt),
            "tools": str(tools_path),
            "history_window": history_window,
            "max_tool_rounds": max_tool_rounds,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "turns": [
                {
                    "turn_index": len(st.session_state.history) // 2,
                    "started_at": now_iso(),
                    "user": query.strip(),
                    "status": result.get("status", "answered"),
                    "assistant_text": assistant_text,
                    "rounds": result.get("rounds", []),
                    "tool_events": result.get("tool_events", []),
                    "ended_at": now_iso(),
                }
            ],
        }
        transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
        write_transcript(transcript_path, transcript)

        st.success("Yêu cầu đã gửi và transcript đã lưu.")
        st.markdown("**Agent trả lời:**")
        st.markdown(assistant_text)
        st.markdown("**Tool calls / kết quả:**")
        st.json(result)
        st.markdown(f"Transcript saved: `{transcript_path}`")
    except Exception as exc:
        st.error(f"Lỗi khi chạy agent: {type(exc).__name__}: {exc}")
