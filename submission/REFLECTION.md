# Reflection — Nguyen Van An, 2A202602782

**Anti-pattern dễ vướng nhất: vector index bên ngoài lệch vòng đời so với bảng gốc.**

Các project AI của tôi (như RAG ở Lab 8) tách dữ liệu gốc khỏi vector index và đồng bộ định kỳ. Ở NB7, tôi xoá `user_042` (8 tài liệu) khỏi lakehouse: bảng trả **0 hit**, nhưng index ngoài vẫn trả **8 hit**. Nếu sync chỉ là upsert một chiều, index sẽ đưa dữ liệu đã xoá vào prompt RAG — thành lỗi tuân thủ, và khó thấy vì mọi truy vấn vẫn chạy bình thường.

Cách phòng tránh: coi lakehouse là system-of-record, index chỉ là bản dẫn xuất dựng lại được; truyền sự kiện `delete` qua Change Data Feed (NB7 phát đúng 8 sự kiện); nếu quy mô cho phép, giữ vector ngay trong dòng. NB8 nhắc thêm: xoá ở version hiện tại chưa xoá bản cũ, cần xử lý retention/VACUUM.

**AI:** Claude Code giải thích, chạy kiểm tra, dựng bản nộp; chi tiết ở [AI_USAGE.md](AI_USAGE.md).
