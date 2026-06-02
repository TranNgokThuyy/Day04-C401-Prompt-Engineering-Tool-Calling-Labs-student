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

    path.write_text(
        json.dumps(
            transcript,
            ensure_ascii=False,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )


def build_transcript_id(
    provider: str,
    version: str,
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%dT%H%M%S%f"
    )

    return (
        "streamlit_"
        + "_".join(
            [
                safe_slug(version),
                safe_slug(provider),
                timestamp,
            ]
        )
    )

st.set_page_config(
    page_title="Research Agent",
    page_icon="🤖",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None

with st.sidebar:

    st.title("⚙️ Agent Settings")

    provider_name = st.selectbox(
        "Provider",
        [
            "openrouter",
            "openai",
            "anthropic",
            "gemini",
        ],
    )

    version_label = st.text_input(
        "Artifact Version",
        value="v3",
    )

    model_name = st.text_input(
        "Model Override",
        value="",
    )

    max_tool_rounds = st.slider(
        "Max Tool Rounds",
        min_value=1,
        max_value=10,
        value=4,
    )

    history_window = st.slider(
        "History Window",
        min_value=1,
        max_value=20,
        value=5,
    )

    st.divider()

    if st.button(
        "🗑️ New Chat",
        use_container_width=True,
    ):
        st.session_state.messages = []
        st.session_state.last_result = None
        st.rerun()

system_prompt = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"

system_prompt_text = system_prompt.read_text(
    encoding="utf-8"
)

st.markdown(
    """
<style>

.block-container{
    max-width: 950px;
    padding-top: 1.5rem;
    padding-bottom: 7rem;
}

h1{
    text-align:center;
}

.chat-subtitle{
    text-align:center;
    color:#888;
    margin-bottom:2rem;
}

[data-testid="stChatMessage"]{
    padding:14px;
    border-radius:18px;
}

[data-testid="stSidebar"]{
    border-right:1px solid #e5e7eb;
}

</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<h1>🤖 Research Agent</h1>
<p class="chat-subtitle">
Production-Grade Tool Calling Agent
</p>
""",
    unsafe_allow_html=True,
)

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

prompt = st.chat_input(
    "Ask anything..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):

        placeholder = st.empty()

        placeholder.markdown(
            "⏳ Researching..."
        )

        try:

            provider = make_provider(
                provider_name
            )

            tool_declarations = (
                load_tool_declarations(
                    tools_path
                )
            )

            openai_tools = (
                to_openai_tools(
                    tool_declarations
                )
            )

            messages = [
                {
                    "role": "system",
                    "content": system_prompt_text,
                },
                *trim_history(
                    st.session_state.messages,
                    history_window,
                ),
            ]

            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model_name or None,
                max_tool_rounds=max_tool_rounds,
            )

            assistant_text = result[
                "assistant_text"
            ]

            placeholder.markdown(
                assistant_text
            )

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": assistant_text,
                }
            )

            st.session_state.last_result = result

            transcript_id = (
                build_transcript_id(
                    provider_name,
                    version_label,
                )
            )

            artifact_version = (
                build_artifact_version(
                    version_label,
                    system_prompt,
                    tools_path,
                )
            )

            transcript = {
                "transcript_id":
                    transcript_id,

                **artifact_version_dict(
                    artifact_version
                ),

                "provider":
                    provider_name,

                "model":
                    model_name or None,

                "system_prompt":
                    str(system_prompt),

                "tools":
                    str(tools_path),

                "history_window":
                    history_window,

                "max_tool_rounds":
                    max_tool_rounds,

                "created_at":
                    now_iso(),

                "updated_at":
                    now_iso(),

                "turns": [
                    {
                        "turn_index":
                            len(
                                st.session_state.messages
                            ) // 2,

                        "started_at":
                            now_iso(),

                        "user":
                            prompt,

                        "status":
                            result.get(
                                "status",
                                "answered",
                            ),

                        "assistant_text":
                            assistant_text,

                        "rounds":
                            result.get(
                                "rounds",
                                []
                            ),

                        "tool_events":
                            result.get(
                                "tool_events",
                                []
                            ),

                        "ended_at":
                            now_iso(),
                    }
                ],
            }

            transcript_path = (
                TRANSCRIPTS_DIR
                / f"{transcript_id}.transcript.json"
            )

            write_transcript(
                transcript_path,
                transcript,
            )

        except Exception as exc:

            placeholder.error(
                f"{type(exc).__name__}: {exc}"
            )

if st.session_state.last_result:

    st.divider()

    with st.expander(
        "🔧 Tool Calls",
        expanded=False,
    ):
        st.json(
            st.session_state.last_result.get(
                "tool_events",
                []
            )
        )

    with st.expander(
        "🧠 Reasoning Trace",
        expanded=False,
    ):
        st.json(
            st.session_state.last_result.get(
                "rounds",
                []
            )
        )

    with st.expander(
        "📄 Raw Result",
        expanded=False,
    ):
        st.json(
            st.session_state.last_result
        )