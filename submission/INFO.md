# Thông tin người nộp

| Mục | Giá trị |
|---|---|
| Họ tên | Nguyen Van An |
| MSSV | 2A202602782 |
| Mã bài | K4-Track02-Day18 |
| Repo | `K4-Track02-Day18-NguyenVanAn-2A202602782-Lakehouse-Lab` (fork cá nhân, `origin` = `AnNguyen05092004/...`) |
| Đường chạy | **Lightweight** cho cả 8 notebook (không dùng Spark/Docker) |
| Python | 3.11.17 |
| Hệ điều hành | macOS 26.5.2 (Apple silicon, arm64) |

## Phiên bản thư viện đã dùng
`deltalake 1.6.6` · `pyiceberg 0.12.0` · `duckdb 1.5.6` · `polars 1.44.2` · `pyarrow 25.0.1` · `numpy 2.4.6` · `jupyterlab 4.6.4` · `pytest 9.1.1`

## Kết quả kiểm tra (chạy từ gốc repo)
- `make smoke` — 9/9 ✓
- `make test` — 24/24 pytest PASS
- `make run-all` — 8/8 notebook PASS

## Nội dung bài nộp
- `notebooks/` — 8 notebook đã chạy, **giữ output**, kèm cell bằng chứng (chỉ đọc) và cell Markdown giải thích. Dựng bằng `build_notebooks.py` từ nguồn `notebooks/*.py` của đề; script không bỏ assert hay hạ ngưỡng nào.
- `screenshots/` — ảnh bằng chứng cho từng notebook (`nb01_*` … `nb08_*`), chụp trực tiếp từ output của các notebook đã chạy.
- `REFLECTION.md` — reflection (≤ 200 từ), `AI_USAGE.md` — khai báo phạm vi dùng AI.
- Có **một thay đổi** so với đề, ở `notebooks/06_maintenance.py` (hàm `find_orphans` thêm `unquote`), lý do ghi trong NB6 và `AI_USAGE.md`.
- Bonus: không làm.
