---
name: source_inspect
track: bonus
kind: live_api
provider: none
requires_env: []
inputs:
  - url
outputs:
  - title
  - description
  - canonical_url
  - https
  - status_code
  - content_snippet
side_effect: false
requires_confirmation: false
---

Tool này kiểm tra nhanh một đường dẫn web, lấy tiêu đề, mô tả, canonical URL và sơ bộ đánh giá tính an toàn/HTTPS. Rất hữu ích khi model cần xác nhận tính nguồn tin trước khi tóm tắt hoặc trình bày.
