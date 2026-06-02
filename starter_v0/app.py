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


st.set_page_config(page_title="Research Agent UI", layout="wide")
st.title("Research Agent Research UI")
st.markdown(
    "Ứng dụng Streamlit cho research agent: chọn provider, nhập truy vấn, xem lịch sử và kết quả tool." 
)

with st.sidebar:
    st.header("Cấu hình")
    provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"], index=0)
    version_label = st.text_input("Artifact version", value="v3")
    model_name = st.text_input("Model (optional)", value="")
    max_tool_rounds = st.slider("Max tool rounds", 1, 6, 4)
    history_window = st.slider("History window", 1, 10, 5)
    if st.button("Xóa lịch sử chat"):
        st.session_state.history = []
        st.experimental_rerun()

if "history" not in st.session_state:
    st.session_state.history = []

system_prompt = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
system_prompt_text = system_prompt.read_text(encoding="utf-8")

st.subheader("System prompt hiện tại")
st.code(system_prompt_text, language="markdown")

query = st.text_area("Nhập câu hỏi hoặc yêu cầu research", height=140)
submitted = st.button("Gửi yêu cầu")

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
        st.write("**Agent trả lời:**")
        st.markdown(assistant_text)
        st.write("**Tool calls / kết quả:**")
        st.json(result)
        st.write(f"Transcript saved: `{transcript_path}`")
    except Exception as exc:
        st.error(f"Lỗi khi chạy agent: {type(exc).__name__}: {exc}")

if st.session_state.history:
    st.subheader("Lịch sử hội thoại")
    for index in range(0, len(st.session_state.history), 2):
        user_turn = st.session_state.history[index]
        assistant_turn = st.session_state.history[index + 1] if index + 1 < len(st.session_state.history) else None
        st.markdown(f"**Bạn:** {user_turn['content']}")
        if assistant_turn:
            st.markdown(f"**Agent:** {assistant_turn['content']}" )
