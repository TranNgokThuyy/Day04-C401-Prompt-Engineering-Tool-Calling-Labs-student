# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Zone 11 nhóm 3
- Members: Trần Đức Tâm - 2A202600803, Trần Ngọc Thuỵ - 2A202600799
- Provider/model: openrouter / openai/gpt-4o-mini

## Final Metrics

- Final version: v3
- Final artifact_version: v3+peb1c8179815b+t6cdb53d5d7b8
- Best base run file: runs/v3_B_base_openrouter_20260602T142943781019.json
- Base case accuracy: 0.70
- Base tool routing accuracy: 0.75
- Base argument accuracy: 0.70
- Group eval run file: runs/v3_B_group_openrouter_20260602T145839301381.json
- Group eval accuracy: 0.80
- Chat transcript file: transcripts/streamlit_v3_openrouter_20260602T155343620008.transcript.json

## Version Evidence

Fill from artifacts/version_log.csv and runs/*.json.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Khởi tạo baseline với prompt gốc và tool declaration ban đầu |  |  |  |
| v1 | artifacts/system_prompt.md | Giảm nhầm lẫn giữa tool routing và trả lời trực tiếp bằng hệ thống prompt |  |  |  |
| v2 | artifacts/tools.yaml | Bổ sung trường args giúp model chọn đúng tool và giá trị |  |  |  |
| v3 | artifacts/system_prompt.md, artifacts/tools.yaml | Hoàn thiện vòng tool loop, thêm luật routing cụ thể và bảo toàn thông tin multiround |  |  | runs/v3_B_base_openrouter_20260602T142943781019.json |

## Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R01_user_tweets_routing | wrong_tool | timeline(screenname=sama, limit=1) | Model route đúng tool nhưng chưa bó hạn chế đúng | Giữ nguyên hành vi timeline và chuẩn hoá args trong prompt/tool declaration |
| G01_latest_openai_news | wrong_arg_value | lookup(query=OpenAI, timeframe=day, topic=news) | Model cần map timeframe=day cho query 24h | Cải thiện yêu cầu thành khoảng thời gian cụ thể và gợi ý field timeframe |

## Team Eval Cases

List at least 5 cases added to data/eval_group.json.

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_latest_openai_news | Map yêu cầu 24 giờ qua thành timeframe=day | lookup với topic=news và timeframe=day | passed |
| G02_latest_posts_about_claude | Mặc định bài viết mới nhất thành Latest | social_search với search_type=Latest | passed |
| G03_fetch_specific_url | URL cụ thể phải dùng fetch | fetch với url | passed |
| G04_missing_person_for_timeline | Thiếu thông tin cần hỏi lại | clarify text | passed |
| G05_no_tool_greeting | Greeting không cần tool | no_tool | passed |

## Live Chat Evidence

Use transcripts/*.transcript.json.

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | "Tin OpenAI trong 24 giờ qua" | lookup(topic=news, timeframe=day) | streamlit_v3_openrouter_20260602T155343620008.transcript.json | Agent gọi đúng lookup và trả kết quả tin tức |
| 2 | "Lấy tweet của Sam Altman" | timeline(screenname=sama) | streamlit_v3_openrouter_20260602T155343620008.transcript.json | Model duy trì context và trả kết quả tweet |

## Bonus Evidence

| Bonus | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| UI | starter_v0/streamlit_chat.py | Tạo giao diện chat-style với prompt cố định dưới cùng | Cần test thêm trên trình duyệt thực tế để đảm bảo submit Enter hoạt động và không bị lỗi layout |

## Reflection

- Which fixes belonged in artifacts/system_prompt.md?
  - Những luật routing, cách chọn tool, và khi nào cần hỏi lại.
- Which fixes belonged in artifacts/tools.yaml?
  - Các mô tả tool, args, và giới hạn phạm vi tool.
- Which failure needed manual review instead of automatic grading?
  - Các trường hợp out_of_scope và wrong_boundary cần đọc kỹ actual tool_calls và content trả về.
- What would you improve next?
  - Hoàn thiện version_log.csv với ghi chép mỗi lần thay đổi.
  - Thêm nhiều case group coverage về URLs, confirm send, và multi-tool requests.
  - Test UI thực tế bằng Streamlit, sửa layout nếu cần.
