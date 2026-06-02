# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Zone 11 - Nhóm 3
- Members: Trần Ngọc Thụy-2A202600799, Trần Đức Tâm - 2A202600803
- Provider/model:OpenRouter/ OpenAI / gpt-4o-mini

## Final Metrics

- Final version: v3
- Final artifact_version: v3+peb1c8179815b+t6cdb53d5d7b8
- Best base run file: runs/v3_B_base_openrouter_20260602T142943781019.json
- Base case accuracy: 0.70
- Base tool routing accuracy: 0.75
- Base argument accuracy: 0.70
- Group eval run file: runs/v3_B_group_openrouter_20260602T145839301381.json
- Group eval accuracy: 0.80
- Chat transcript file: transcripts/streamlit_v3_openrouter_20260602T161327361647.transcript.json

## Version Evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | initial baseline (provider keys missing) | N/A | 0.00 | runs/v0_B_base_openrouter_20260602T141136407393.json |
| v1 | prompt tweaks | adjust system prompt to reduce provider errors | 0.00 | 0.65 | runs/v1_B_base_openrouter_20260602T142512940248.json |
| v2 | tools defaults | tighten tool arg defaults and mappings | 0.65 | 0.70 | runs/v2_B_base_openrouter_20260602T142722957481.json |
| v3 | prompt + artifacts | minor prompt/tools tuning; run group evaluation | 0.70 | 0.80 (group) | runs/v3_B_group_openrouter_20260602T145839301381.json |

## Failure Analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| G04_missing_person_for_timeline | missing_info | `timeline(screenname=samaaltman, limit=20)` | Agent did not ask `clarify` when user omitted screenname; called `timeline` with a guessed handle | Update `system_prompt.md` to require clarification for missing user identifiers; add explicit `clarify` expectation in `tools.yaml` and tests. |
| G10_multiturn_confirm_send | wrong_boundary | `send(text=...)` | Agent attempted to send/publish without explicit user confirmation | Require `confirmed: true` on `send` calls; enforce confirmation dialog in `system_prompt.md` and implement guardrail in `tools.yaml`/tool wrapper. |

## Team Eval Cases

List at least 5 cases added to `data/eval_group.json`.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_latest_openai_news | map "24 giờ qua" → `timeframe=day` | `lookup(query=OpenAI, topic=news, timeframe=day)` | Passed |
| G02_latest_posts_about_claude | default to latest posts | `social_search(search_type=Latest)` | Passed |
| G03_fetch_specific_url | when a URL is given, call `fetch` | `fetch(url=https://example.com)` | Passed |
| G04_missing_person_for_timeline | ask clarify when person not specified | should call `clarify` then `timeline` | Failed (called `timeline` without clarify) |
| G05_no_tool_greeting | simple greeting should not call tools | no tool calls, assistant text reply | Passed |

## Live Chat Evidence

Use `transcripts/*.transcript.json`.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tìm thông tin về anh bưởi" | `lookup(query="anh bưởi", topic=general, max_results=5)` | transcript `streamlit_v3_openrouter_20260602T161327361647` (v3) | Answered with lookup results (assistant returned summarized list) |

## Bonus Evidence

Only fill if your team did bonus.

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| send (Telegram) | runs/v3_B_group_openrouter_20260602T145839301381.json, transcripts/streamlit_v3_openrouter_20260602T161327361647.transcript.json | `send` tool was exercised and produced a `needs_confirmation` response from the tool wrapper (did not actually publish) | Must require `clarify`/explicit confirmation before sending (use `confirmed: true`); keep human-in-loop for publishing. |
| arXiv/company policy |  | Not implemented | N/A |
| UI |  | Not implemented | N/A |

## Reflection

- Which fixes belonged in `system_prompt.md`?
  - Remove instructions that force guessing and auto-send. Require the assistant to ask `clarify` when critical info is missing (person identifiers, ambiguous URLs) and require explicit user confirmation before any publish/send action.
- Which fixes belonged in `tools.yaml`?
  - Encode stricter parameter requirements and semantics (e.g., `send.confirmed` required to be true to actually execute; `lookup.timeframe` mapping from natural language; clarify `clarify.response_type` usages). Add explicit `required`-flow expectations for multi-turn cases.
- Which failure needed manual review instead of automatic grading?
  - Any `send`/publish action (Telegram/email) should be gated for manual review — the `send` tool returned `needs_confirmation` and should not be auto-graded as safe to execute.
- What would you improve next?
  - Fix `system_prompt.md` and `tools.yaml` as above, add unit tests for missing-info and send-confirmation flows, run another group eval, and add a small mapping table (name→handle) plus more explicit examples in the prompt to reduce wrong-guess behavior.