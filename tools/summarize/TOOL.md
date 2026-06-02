---
name: summarize
track: bonus
kind: local_formatter
provider: local
requires_env: []
inputs: [text, max_sentences]
outputs: [summary, sentence_count, used_sentences]
side_effect: false
---
# summarize

Tóm tắt một đoạn văn bản dài thành các câu chính, giúp chuyển nội dung thô thành kết luận ngắn gọn.
