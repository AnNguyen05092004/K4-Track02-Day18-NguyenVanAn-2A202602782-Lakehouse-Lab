# K4-Track02-Day18 — Quy định làm bài

Áp dụng cho Lakehouse Lab của Khóa 4, Track 02, Day 18. **Bài làm cá nhân cho cả phần
bắt buộc và bonus.** Cách nộp bài
được ghi tại [SUBMISSION.md](SUBMISSION.md); tiêu chí điểm tại [RUBRIC.md](RUBRIC.md).

## Sử dụng AI

Được dùng AI để giải thích khái niệm, hỗ trợ đọc code, tìm nguyên nhân lỗi và đề xuất sửa đổi.
Người nộp phải tự chạy, kiểm tra và giải thích được mã nguồn cùng kết quả của mình.
Khai công cụ AI và phạm vi hỗ trợ trong reflection; nếu cần nhiều chỗ hơn, dùng
`submission/AI_USAGE.md` và dẫn liên kết từ reflection.

Không dùng AI để tạo số liệu/output giả, viết lời khẳng định về những lần chạy chưa thực hiện,
hoặc bỏ assertion/hạ ngưỡng để báo PASS. Khi sửa mã, giữ tiêu chí gốc và giải thích lý do sửa.

## Hợp tác và sao chép

Được trao đổi khái niệm và cách xử lý lỗi. Mỗi người tự thực thi,
thu thập bằng chứng và viết giải thích/reflection. Không nộp notebook có output hoặc reflection
của người khác như bài của mình. Dẫn nguồn khi dùng đoạn mã, tài liệu hoặc ý tưởng bên ngoài.

Mỗi học viên fork repo đề bài về tài khoản cá nhân và bắt buộc đổi tên fork thành
`K4-Track02-Day18-HoVaTen-MSSV-Lakehouse-Lab` theo [SUBMISSION.md](SUBMISSION.md).
Mỗi học viên nộp fork riêng; không nộp một repo chung thay cho nhiều người.
Sao chép không khai báo và bằng chứng giả được chuyển cho key coach
xử lý theo quy định khóa học; không mặc định một mức phạt chưa được công bố.

## Deadline và nộp muộn

Deadline mặc định là **23:59 ngày tổ chức lab**, múi giờ **Asia/Ho_Chi_Minh (UTC+7)**.
Ngày cụ thể lấy từ lịch học do key coach công bố. Nếu key coach có thông báo thay đổi
trong vòng 48 giờ sau lab theo quy ước chung, áp dụng mốc trong thông báo đó;
không tự hiểu rằng mọi bài đều được gia hạn 48 giờ.

Bài nộp sau deadline có thể bị trừ điểm theo mức key coach công bố.
Repo này chưa quy định một tỷ lệ trừ điểm cụ thể; cần kiểm tra thông báo trên kênh nộp bài.
Nếu có sự cố, báo key coach kèm thời điểm và bằng chứng thay vì tự đổi deadline.

## Chốt bài và sửa sau deadline

Khi nộp, cung cấp liên kết repo/PR cùng commit SHA để xác định phiên bản chấm.
Sau deadline, không sửa/xóa bằng chứng đã nộp hoặc force-push làm mất commit đó.
Có thể bổ sung bằng commit mới, ghi rõ nội dung và thời điểm; việc chấm bản bổ sung
phải theo thông báo hoặc chấp thuận của key coach. Giữ lịch sử Git để đối chiếu khi chấm lại.

## Bảo mật API key và dữ liệu

Đường lightweight không yêu cầu API key và dùng dữ liệu giả. Không đưa dữ liệu thật có PII,
khóa API, token, mật khẩu cá nhân hoặc file `.env` chứa bí mật vào repo hay screenshots.
Credentials MinIO mặc định chỉ phục vụ môi trường lab cục bộ; không dùng cho hệ thống thật.

Nếu vô tình commit bí mật, thu hồi/thay khóa ngay và báo key coach; xóa file ở commit mới
không loại bỏ bí mật khỏi lịch sử. Khi dùng AI, không gửi bí mật hoặc dữ liệu riêng tư vào prompt.

## Bonus

Bonus làm cá nhân, tự nguyện, cộng tối đa 10 điểm; điểm lab cuối cùng tối đa 100 theo [RUBRIC.md](RUBRIC.md).
Không làm bonus không mất điểm phần bắt buộc. Điểm bonus lab tách khỏi điểm giơ tay,
phát biểu hoặc pitching. Cách nộp bonus theo [SUBMISSION.md](SUBMISSION.md).
