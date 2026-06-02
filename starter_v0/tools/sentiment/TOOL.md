---
name: sentiment
track: bonus
kind: local_formatter
provider: none
requires_env: []
inputs:
  - text
outputs:
  - sentiment
  - score
  - positive_terms
  - negative_terms
  - summary
side_effect: false
requires_confirmation: false
---

Tool này phân tích xu hướng cảm xúc trong văn bản tiếng Việt/tiếng Anh. Nó giúp đánh giá nhanh nội dung tweet, bài tin tức hoặc bình luận để xác định nếu chủ đề đang tích cực, tiêu cực hay trung tính.
