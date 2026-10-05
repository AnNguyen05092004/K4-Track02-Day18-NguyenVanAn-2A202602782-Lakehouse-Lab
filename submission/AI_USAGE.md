# Khai báo sử dụng AI

**Công cụ:** Claude Code (mô hình Claude Sonnet 5.5) trong VS Code, chạy trên máy của tôi.

## AI đã làm gì
1. **Giải thích khái niệm và đọc code** từng checkpoint (Delta log, Z-order, MERGE/RESTORE, Iceberg catalog, maintenance, vector, provenance).
2. **Chạy kiểm tra** `make smoke`, `make test`, `make run-all` và đọc output để đối chiếu với ngưỡng trong `docs/RUBRIC.md`.
3. **Dựng bản nộp:** viết `build_notebooks.py` để thực thi thật 8 notebook bằng kernel Jupyter và lưu output; thêm
   - cell bằng chứng **chỉ đọc** (nội dung `_delta_log/`, lỗi enforcement + chứng minh không để lại commit, kiểm tra chất lượng Gold NB4…),
   - cell Markdown giải thích số liệu (đã đối chiếu từng con số với output của lần chạy nộp).
4. **Soạn nháp** `INFO.md`, `REFLECTION.md`, file này.

## Thay đổi mã so với đề (có chủ đích, giữ nguyên tiêu chí)
- `notebooks/06_maintenance.py`, hàm `find_orphans`: thêm `urllib.parse.unquote` khi so khớp đường dẫn.
  - **Lý do:** `DeltaTable.file_uris()` trả đường dẫn mã hoá phần trăm (`VIN AI` → `VIN%20AI`). Với thư mục có dấu cách, bản gốc coi **mọi** file đang dùng là "không được tham chiếu" và chỉ nhờ age guard 24 giờ mà chưa xoá nhầm; file đang dùng cũ hơn 24 giờ sẽ bị xoá.
  - **Kết quả sau sửa:** vẫn tìm đúng 3 orphan; `make test` và `make run-all` vẫn xanh.

## AI không làm
- Không tạo số liệu/output giả: mọi con số trong `.ipynb` đều sinh từ lần chạy thật.
- Không bỏ assert, không hạ ngưỡng. NB1 vẫn còn cờ `True` hardcode của đề; bằng chứng enforcement thật là cell bổ sung phía dưới nó.
- Không commit, không push, không mở PR.

## Trách nhiệm
Tôi tự chạy lại các lệnh, đọc phần giải thích và có thể giải thích lại kết quả; các nhận định trong reflection là của tôi.
