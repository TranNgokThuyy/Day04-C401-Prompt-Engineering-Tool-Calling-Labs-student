---
name: trend_analysis
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs:
  - texts
  - focus_topic
  - top_k
outputs:
  - top_topics
  - summary
  - item_count
side_effect: false
requires_confirmation: false
---

Tool này phân tích một tập đoạn văn và rút ra các chủ đề nổi bật. Nó rất phù hợp để xác định xu hướng chính từ tweet, tin tức hoặc báo cáo nghiên cứu.
