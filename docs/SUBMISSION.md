# K4-Track02-Day18 — Hướng dẫn nộp bài

**Bài làm cá nhân, gồm cả phần bắt buộc và bonus.** Mỗi học viên nộp repo riêng,
tự thực thi notebook, giữ output và giải thích kết quả. Không nộp repo nhóm hay `TEAM.md`.

Các lệnh và đường dẫn bài nộp trong tài liệu được tính từ **thư mục gốc repo**,
không phải từ thư mục `docs/`.

## 1. Fork và đặt tên repo

Repo đề bài: [K4-Track02-Day18-Lakehouse-Lab](https://github.com/VinUni-AI20k/K4-Track02-Day18-Lakehouse-Lab).
Mỗi học viên **fork repo đề bài về tài khoản GitHub cá nhân** và **bắt buộc đổi tên fork** theo mẫu:

```text
K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab
```

Ví dụ minh họa:

```text
K4-Track02-Day18-NguyenVanAn-20260001-Lakehouse-Lab
```

Họ tên viết không dấu, không khoảng trắng; ngăn cách các phần bằng `-`.
Giữ nguyên mã `K4-Track02-Day18` và hậu tố `Lakehouse-Lab`, dùng MSSV của chính bạn.
`HoVaTen` là họ tên, còn `TEN_GITHUB` trong URL là tên tài khoản GitHub.

1. Mở repo đề bài và chọn **Fork** vào tài khoản cá nhân.
2. Đặt tên fork đúng mẫu ngay khi tạo. Nếu fork đã có tên gốc,
   đổi tên repository trên GitHub trước khi clone; đổi tên thư mục trên máy không đủ.
3. Clone fork đã đổi tên. Thay các placeholder bằng thông tin của bạn:

```bash
git clone https://github.com/TEN_GITHUB/K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab.git
cd K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab
git remote -v
```

**Kiểm tra:** URL `origin` thuộc tài khoản của bạn và có tên repository đúng mẫu.
Repo upstream vẫn là repo đề bài liên kết ở trên; bài làm được push lên fork cá nhân.

Nếu đã clone trước khi đổi tên fork, chạy trong repo bài làm để cập nhật remote
(thay các placeholder trước khi chạy):

```bash
git remote set-url origin https://github.com/TEN_GITHUB/K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab.git
git remote -v
```

## 2. Cấu trúc bài phải nộp

Giữ mã nguồn và cấu hình cần thiết để chạy lab. Thêm phần bài nộp:

```text
submission/
├── INFO.md
├── notebooks/
│   ├── 01_delta_basics.ipynb
│   ├── 02_optimize_zorder.ipynb
│   ├── 03_time_travel.ipynb
│   ├── 04_medallion.ipynb
│   ├── 05_iceberg_catalog.ipynb
│   ├── 06_maintenance.ipynb
│   ├── 07_vectors_multimodal.ipynb
│   └── 08_agents_provenance.ipynb
├── screenshots/
│   ├── nb01_delta_log.png
│   ├── nb02_optimize.png
│   └── ...
├── REFLECTION.md
├── AI_USAGE.md                  # nếu phần khai AI cần tách riêng
└── bonus/                      # tùy chọn, làm cá nhân
    ├── ARCHITECTURE.md
    └── poc/                    # code minh họa tùy chọn
```

- **`INFO.md`:** họ tên, MSSV, mã bài `K4-Track02-Day18`, đường chạy đã dùng
  (lightweight/Spark), phiên bản Python và hệ điều hành; ghi rõ nếu NB1–NB4 dùng Spark.
- **8 notebook đã thực thi:** giữ output, thứ tự cell và phần giải thích số liệu.
  Không chỉ nộp `.py` hoặc notebook đã xóa output. Có thể thêm Markdown cell để giải thích.
- **Screenshots:** ít nhất một ảnh cho mỗi notebook thể hiện kết quả chính theo
  [RUBRIC.md](RUBRIC.md). NB1 cần bằng chứng `_delta_log/` và nội dung một commit JSON
  hoặc ảnh MinIO tương ứng. NB2 cần số trước/sau; NB3 cần history sau RESTORE;
  NB4 cần kết quả Gold; NB5–NB8 cần các metric/check chính.
- **`REFLECTION.md` (≤ 200 từ):** chọn một anti-pattern lakehouse, giải thích vì sao
  hệ thống/dữ liệu bạn quan tâm dễ gặp nó và cách phòng tránh. Ghi phạm vi sử dụng AI
  hoặc liên kết `AI_USAGE.md` nếu có.
- **Bonus:** tài liệu 3–6 trang khi render theo [BONUS-CHALLENGE.md](bonus/BONUS-CHALLENGE.md).
  Code không bắt buộc. Không làm bonus không mất điểm phần bắt buộc.

Không commit `.venv/`, toàn bộ `_lakehouse/`, cache hoặc blobs sinh ra. Giữ scripts
sinh dữ liệu để tái lập. Các notebook `.ipynb` trong `notebooks/` và `notebooks-spark/`
đang bị `.gitignore` loại trừ; bản nộp trong `submission/notebooks/` không bị loại trừ.

## 3. Thực thi và lưu output

`make run-all` chạy file Python để kiểm tra, **không** lưu output vào notebook.
Để có bản nộp, mở `.ipynb` trong Jupyter, chạy từ đầu đến cuối, lưu rồi chép vào
`submission/notebooks/`. Nếu NB1–NB4 dùng Spark, chép 4 bản đã chạy từ
`notebooks-spark/`; NB5–NB8 lấy từ `notebooks/`.

Ví dụ sao chép sau khi đã chạy và lưu cả 8 notebook lightweight:

```bash
mkdir -p submission/notebooks
cp notebooks/[0-9]*.ipynb submission/notebooks/
```

PowerShell:

```powershell
New-Item -ItemType Directory -Force submission/notebooks | Out-Null
Copy-Item notebooks/[0-9]*.ipynb submission/notebooks/
```

Đối chiếu số file: phải có đủ 8 notebook, không đưa `_setup.ipynb` vào bài nộp.

## 4. Kiểm tra trước khi nộp

Chạy trên đường lightweight:

```bash
make smoke
make test
make run-all
```

PowerShell:

```powershell
.\.venv\Scripts\python.exe scripts/verify_lite.py
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe scripts/run_all.py
```

Nếu dùng Spark cho NB1–NB4, chạy thêm `make spark-smoke` và thực thi 4 notebook Spark.
Các kiểm tra lightweight vẫn dùng để xác nhận môi trường và phần NB5–NB8.

Checklist:

- [ ] Đã fork vào tài khoản cá nhân và đổi tên fork đúng mẫu; `origin` trỏ tới fork đó.
- [ ] `INFO.md` có họ tên và MSSV khớp tên repo.
- [ ] Có đủ 8 `.ipynb` đã chạy; không có lỗi chưa xử lý hoặc output giả.
- [ ] Có ảnh và phần giải thích cho từng notebook; đối chiếu các ngưỡng trong rubric.
- [ ] Reflection không quá 200 từ, có khai phạm vi dùng AI khi áp dụng.
- [ ] Bonus nếu có là bài cá nhân, nằm đúng thư mục và có nguồn tham khảo.
- [ ] Không có secrets/dữ liệu thật nhạy cảm, venv hoặc dữ liệu lakehouse sinh ra.
- [ ] `git status` hiển thị đúng file; đã commit/push và kiểm tra file trên GitHub.
- [ ] Có liên kết repo/PR và commit SHA của bản nộp để chốt phiên bản chấm.

## 5. Nơi nộp và deadline

Push bài vào repo GitHub cá nhân đặt tên theo mục 1, mở PR về
[repo đề bài](https://github.com/VinUni-AI20k/K4-Track02-Day18-Lakehouse-Lab) và gửi
**liên kết repo + liên kết PR + commit SHA** qua kênh nộp
bài của lớp. Nếu coach dùng kênh thu bài khác, làm theo thông báo chính thức đó.
Không coi việc chỉ tạo repo hoặc chỉ push code là đã gửi bài.

Tiêu đề PR:

```text
[K4-Track02-Day18] HoVaTen - MSSV - Lakehouse Lab
```

Nếu có bonus, thêm ` [+bonus]` cuối tiêu đề. Mô tả PR ghi họ tên, MSSV,
đường chạy, kết quả kiểm tra và liên kết đến notebook/screenshots/reflection.
Key coach công bố kênh thu bài và ngày deadline cụ thể theo lịch học.

**Deadline mặc định: 23:59 ngày tổ chức lab, Asia/Ho_Chi_Minh (UTC+7).** Ngày cụ thể
theo lịch học. Thay đổi deadline phải theo thông báo của key coach; quy ước 48 giờ
là thời hạn thông báo thay đổi, không phải thời gian gia hạn tự động.
Nộp muộn và cập nhật sau deadline theo [RULES.md](RULES.md).
