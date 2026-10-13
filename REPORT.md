# REPORT — Lab Day 9

> Điền **bằng lời và số liệu của chính bạn** (lấy từ đầu ra của `scripts/lab.sh step ...` và từ `report/evidence/*.json`). Bài làm công khai trên GitHub; giảng viên đối chiếu với lịch sử commit và với bài của các bạn khác. Mỗi câu 3 đến 8 dòng là đủ.

| | |
|---|---|
| Họ và tên | Đỗ Mạnh Nghĩa |
| MSSV (đúng bằng `LAB_STUDENT_ID` trong `.env`) | 2A202602971 |
| GitHub | domanhnghiaforwork-cloud |
| Trip dùng cho bài tập sập và chạy lại (xem GUIDE, bước 5) | trip-04868 |

## Kết quả cuối

- `dataset_version` của bạn: `<điền>`  (phải khớp `report/evidence/run_summary.json`)
- Số khung hình train / val / test của bạn: `<điền>`
- `report/verify.txt`: tạo bằng `python3 scripts/check_submission.py --save-verify` (phải có `27/27 checks passed`).
- Ảnh chụp trong `report/screenshots/`: `airflow_graph.png`, `minio_lake.png`, `metabase_dashboard.png`, và ảnh bài tập sập/chạy lại (log task đỏ thấy trip của bạn).

## Bước 1 · Bronze

### Câu 1
Liệt kê **ít nhất 4 khác biệt** giữa telemetry nguồn A và nguồn B mà bạn thấy ở bronze. Vì sao pipeline giữ **mỗi nguồn một bảng bronze** và để mọi cột ở dạng chữ, thay vì gộp và ép kiểu ngay?

Quan sát thực tế từ hai bảng thô `lake.bronze_raw_telemetry_a` (3021 dòng) và `lake.bronze_raw_telemetry_b` (3234 dòng), có các khác biệt cốt lõi sau:
1. **Tên cột và cấu trúc schema (Schema drift)**: Nguồn A dùng `ts_utc`, `speed_mps`, `heading_deg`, `lat`, `lon`, `alt_m`, `gas`, `brake`, `steer`; trong khi nguồn B dùng tên khác hoàn toàn: `timestamp_ms`, `spd_kmh`, `hdg`, `latitude`, `longitude`, `altitude`, `throttle_pct`, `brake_pct`, `steering`.
2. **Đơn vị vận tốc (Unit mismatch)**: Nguồn A đo bằng mét/giây (`speed_mps`), trong khi nguồn B đo bằng km/h (`spd_kmh`).
3. **Định dạng timestamp**: Nguồn A dùng chuỗi ISO 8601 UTC dạng chuỗi (ví dụ: `2025-10-07T08:00:00.014Z`), còn nguồn B dùng số nguyên Unix epoch theo mili-giây (ví dụ: `1759933801509`).
4. **Quy mô tín hiệu bàn đạp (Scale mismatch)**: Nguồn A chuẩn hóa giá trị từ `0.0 - 1.0` (`gas`, `brake`), còn nguồn B biểu diễn theo phần trăm `0 - 100` (`throttle_pct`, `brake_pct`).
5. **Độ lệch đồng hồ thiết bị (Clock offset)**: Bảng `bronze_video_files` cho thấy thiết bị ghi telemetry B bị lệch đồng hồ 1500 ms (1.5 giây) so với video (`telemetry_clock_offset_ms = 1500`), còn nguồn A không lệch (offset = 0).

**Lý do giữ mỗi nguồn một bảng Bronze và lưu kiểu chữ (string):**
Theo kiến trúc Medallion (Slide 14), lớp Bronze là lớp lưu trữ nguyên bản (Raw Ingestion, Append-only) nhằm đảm bảo tính toàn vẹn và bất biến của dữ liệu gốc. Nếu gộp hoặc ép kiểu ngay tại Bronze, khi thiết bị gửi dữ liệu lỗi (chuỗi rác, null bất thường, schema drift), pipeline nạp sẽ gãy ngay lập tức và gây mất mát dữ liệu (data loss). Lưu ở dạng text giúp nhận 100% dữ liệu an toàn. Việc làm sạch, bù lệch thời gian, ép kiểu và cách ly bản ghi lỗi sẽ được dbt thực hiện ở lớp Silver. Lịch sử Delta Lake (`bronze.raw_telemetry_a`) cũng chứng minh tính idempotent: nạp 2 lần liên tiếp vẫn chỉ sinh đúng 1 commit version 0 nhờ kiểm tra sha256.

## Bước 2 · Silver telemetry

### Câu 2
Pipeline đưa hai nguồn về một schema như thế nào (đơn vị, kiểu thời gian, **độ lệch đồng hồ**)? Bằng chứng nào trong kết quả bước 2 cho thấy đã đúng? Dán bảng quarantine của bạn (số dòng theo từng lý do, từng drive) và giải thích vì sao dòng lỗi vào `rejects` thay vì bị xoá.

**Cách pipeline đưa hai nguồn về một schema thống nhất:**
Dựa vào hai dbt staging model (`stg_telemetry_a.sql` và `stg_telemetry_b.sql`):
1. **Đơn vị vận tốc**: Nguồn A giữ nguyên `speed_mps` (m/s). Nguồn B chia `spd_kmh / 3.6` để quy về cùng chuẩn m/s.
2. **Kiểu thời gian**: Nguồn A parse chuỗi ISO thành `ts_utc::timestamptz`. Nguồn B đổi Unix millisecond thành timestamp bằng `epoch_ms`.
3. **Bàn đạp ga/phanh**: Nguồn B chia cho 100.0 (`throttle_pct / 100.0`, `brake_pct / 100.0`) để cùng thang đo `[0, 1]` như A.
4. **Bù độ lệch đồng hồ (Clock offset)**: File cấu hình `sources.json` khai báo nguồn B bị lệch đồng hồ 1500 ms. Staging của B trừ trực tiếp độ lệch này trước khi convert thời gian: `epoch_ms(timestamp_ms - 1500)`.

**Bằng chứng cho thấy đã chuẩn hóa đúng:**
- Thời điểm bắt đầu của telemetry B (`min(ts)`) sau khi trừ 1.5 giây là `2025-10-08 14:30:00.009000+00:00`, trùng khớp hoàn toàn với thời điểm bắt đầu video của drive B (`2025-10-08 14:30:00`). Test tự động module 2 xác nhận: `PASS: drive B clock offset removed (first sample within 0.5 s of video start)`.
- Vận tốc tối đa sau khi quy đổi của cả 2 drive đều nằm trong giới hạn thực tế: drive A là 71 km/h (~19.7 m/s), drive B là 100 km/h (~27.8 m/s).

**Bảng cách ly dữ liệu lỗi (Quarantine table) thực tế:**
| drive_id | reject_reason | so_dong |
|---|---|---|
| drive_a | duplicate | 20 |
| drive_a | speed_missing | 30 |
| drive_a | speed_out_of_range | 3 |
| drive_b | duplicate | 20 |
| drive_b | speed_missing | 30 |
| drive_b | speed_out_of_range | 3 |

Tổng số dòng bị cách ly vào `silver.silver_telemetry_rejects` là 106 dòng (mỗi drive 53 dòng lỗi). Bảng sạch `silver.silver_telemetry` có 6149 dòng (drive A: 2968, drive B: 3181). Tổng `sạch + cách ly` bằng chính xác số dòng thô nhận vào: Drive A (2968 + 53 = 3021), Drive B (3181 + 53 = 3234).

**Vì sao dòng lỗi vào `rejects` thay vì bị xoá:**
Theo nguyên tắc Data Quality & Quarantine (Slide 29), việc xoá âm thầm (silent discard) là phản mẫu (anti-pattern) vì gây mất dấu vết kiểm toán (audit trail) và làm che giấu sự cố phần cứng. Đưa dòng lỗi vào bảng `rejects` kèm lý do cụ thể (`reject_reason`) vừa giữ bảng phân tích sạch sẽ, vừa cung cấp khả năng quan sát (Data Observability) để kỹ sư xe biết cảm biến nào đang chập chờn, mất tín hiệu hoặc sai lệch mà kịp thời bảo dưỡng.

### Câu 3
Vì sao test `max_gap_ms` là `warn` còn `in_range` là `error`? Kết quả thí nghiệm `break-gate` của bạn (`break_gate.json`): test nào bắt được, bao nhiêu dòng, và điều đó cho biết gì về vai trò của "cổng chất lượng"?

1. **Khác biệt giữa `max_gap_ms` (WARN) và `in_range` (ERROR)**:
   - `max_gap_ms` được cấu hình `severity: warn` vì trong điều kiện vận hành thực tế của xe tự lái, cảm biến truyền dữ liệu qua mạng CAN bus / mạng không dây đôi lúc có hiện tượng rớt gói tín hiệu (sensor dropouts) làm khoảng cách giữa 2 mẫu > 1000 ms. Đây là khiếm khuyết vật lý được chấp nhận (tolerated defect); hệ thống cảnh báo để kỹ sư ghi nhận nhưng không dừng pipeline vì phần lớn dữ liệu còn lại vẫn có giá trị sử dụng.
   - `in_range` (0..70 m/s) bắt buộc là `ERROR` vì nếu giá trị phi vật lý (như tốc độ 1000 m/s ~ 3600 km/h) lọt vào dataset huấn luyện, mô hình thị giác và điều khiển xe tự lái sẽ học sai nghiêm trọng, dẫn tới nguy cơ tai nạn chết người. Đây là lỗi vi phạm toàn vẹn dữ liệu chí mạng nên phải dừng pipeline ngay lập tức.

2. **Kết quả thí nghiệm `break-gate` (`report/evidence/break_gate.json`)**:
   - Khi nới luật làm sạch từ 70 m/s lên 1000 m/s, 6 giá trị tốc độ vô lý (3 dòng của A, 3 dòng của B) không bị cách ly nữa mà lọt thẳng vào bảng Silver.
   - Cổng chất lượng dbt test đã lập tức bắt được lỗi: test `in_range_silver_telemetry_speed_mps__70__0` chuyển sang `FAIL` và bắt chính xác **6 dòng** vi phạm. Kết quả chạy test chuyển thành `PASS=5 WARN=1 ERROR=1 SKIP=0`.
   - Sau khi khôi phục lại luật 70 m/s, dbt test quay về trạng thái đạt toàn bộ: `PASS=6 WARN=1 ERROR=0 SKIP=0`.

3. **Vai trò của "Cổng chất lượng" (Quality Gate)**:
   Cổng chất lượng đóng vai trò là "chốt chặn phòng thủ chiều sâu" (defense-in-depth). Ngay cả khi logic ETL/làm sạch bị cấu hình sai, bị nới lỏng hay gặp bug ngoài ý muốn, Quality Gate độc lập sẽ phát hiện vi phạm và chặn đứng pipeline, kiên quyết không cho dữ liệu "bẩn" lọt sang các tầng Gold hoặc kho dữ liệu phục vụ kinh doanh và AI.

## Bước 3 · Silver frames

### Câu 4
Dựa vào `idempotency.json`: số dòng trước và sau hai lần chạy lại, và khi ghi kiểu `append`. Vì sao Delta `overwrite` theo partition (một trip) an toàn hơn xoá rồi ghi lại, nhất là khi giữa chừng có lỗi?

**Số liệu thực tế từ thí nghiệm `report/evidence/idempotency.json`:**
- **Trước khi chạy lại**: Bảng `silver.frames` có **1246 dòng**, dấu vân tay (fingerprint băm nội dung) là `6c7480dfde7e`.
- **Sau 2 lần chạy lại partition (`trip-00003`, có 60 khung)**: Số dòng vẫn giữ nguyên chính xác **1246 dòng**, dấu vân tay vẫn là `6c7480dfde7e` -> Kết quả **KHÔNG ĐỔI (`unchanged: true`)**.
- **Khi ghi kiểu sai (`append` 2 lần vào bảng thử `_scratch_append`)**: Trip có 60 khung ban đầu sau 2 lần chạy đã bị tích luỹ thành **120 dòng**, làm dữ liệu bị **NHÂN ĐÔI (2x)**!

**Vì sao Delta `overwrite` theo partition an toàn hơn "Xoá rồi Ghi lại" (Delete-then-Insert):**
1. **Tính nguyên tử ACID (Atomicity)**: Delta Lake sử dụng transaction log (`_delta_log`). Khi thực hiện `overwrite` có điều kiện partition (`replaceWhere="trip_id = '...'"`), các file dữ liệu mới được ghi vào object storage trước. Chỉ khi toàn bộ file mới ghi xong thành công, Delta mới commit 1 entry nguyên tử vào transaction log. Người đọc (reader) luôn nhìn thấy trạng thái nhất quán, không bao giờ thấy bảng bị trống hay dở dang.
2. **Kháng lỗi sập giữa chừng (Crash resilience)**: Nếu dùng cơ chế truyền thống "Delete rồi Insert", đây là 2 thao tác rời rạc. Nếu lệnh insert bị chết giữa chừng (mất điện, OOM, đứt mạng), dữ liệu cũ đã bị xóa mất vĩnh viễn dẫn tới mất mát dữ liệu (data loss). Với Delta `overwrite`, nếu quá trình ghi bị sập giữa chừng, commit log không được tạo -> hệ thống tự động giữ nguyên phiên bản cũ nguyên vẹn 100%, bảo đảm an toàn tuyệt đối khi backfill hoặc retry task lỗi.

### Câu 5
Khung hình **đen** và khung hình **tối** khác nhau thế nào, pipeline xử lý khác nhau ra sao, bạn có đồng ý không? Dựa vào `threshold.json`: nếu chọn ngưỡng 0, 2, 6 thì bao nhiêu khung bị coi là trùng ở mỗi drive? Bạn chọn ngưỡng nào, vì sao, và ngưỡng đó phụ thuộc vào tốc độ xe thế nào?

1. **Khác biệt giữa khung hình ĐEN và khung hình TỐI**:
   - **Khung đen (`is_black`)**: Độ sáng trung bình xấp xỉ 0 (do nắp camera chưa mở, mất nguồn cảm biến, lỗi phần cứng ghi hình). Khung này hoàn toàn vô giá trị và không có thông tin quang học -> Pipeline **loại bỏ** (không đưa vào tập Gold huấn luyện). Tôi hoàn toàn đồng ý vì đưa khung đen vào chỉ làm hỏng trọng số mô hình AI.
   - **Khung tối (`toi_giu_lai` / `is_low_light`)**: Xe chạy vào đường hầm, dưới bóng râm rậm rạp hoặc ban đêm (kết quả bước 3 ghi nhận Drive B có tới 61 khung tối). Khung tối vẫn chứa thông tin thế giới thực (vệt sáng đèn xe, biển báo phản quang, vạch kẻ đường) -> Pipeline **gắn cờ cảnh báo nhưng giữ lại**. Tôi hoàn toàn đồng ý vì đây là các trường hợp biên (edge cases) vô cùng quý giá để mô hình AI học cách lái xe an toàn trong điều kiện thiếu sáng.

2. **Bảng số khung trùng thực tế theo ngưỡng dHash (`report/evidence/threshold.json`)**:

| dHash khác tối đa | số khung trùng, drive A | số khung trùng, drive B |
|---|---|---|
| 0 | 61 | 8 |
| 2 | 149 | 53 |
| 6 | 363 | 244 |

3. **Lựa chọn ngưỡng và sự phụ thuộc vào tốc độ xe**:
   - **Chọn ngưỡng 2**: Ngưỡng 0 quá khắt khe (chỉ bắt khung giống hệt từng bit, bỏ sót khung trùng do rung lắc nhẹ hoặc nhiễu nén video); ngưỡng 6 quá lỏng (loại tới 363/602 khung của A và 244/644 khung của B, làm mất nhiều cảnh thực tế đã di chuyển). Ngưỡng 2 cân bằng hoàn hảo, phát hiện chính xác đoạn camera đứng hình 6 giây ở Drive A (149 khung trùng) và lọc bớt khung lặp khi xe dừng.
   - **Phụ thuộc vào tốc độ xe**: Khi xe chạy chậm hoặc dừng chờ đèn đỏ, sự biến đổi cảnh vật giữa 2 khung hình liên tiếp (lấy mẫu 2 fps) là cực kỳ nhỏ, khoảng cách Hamming giữa hai mã dHash <= 2 -> bị gắn cờ trùng. Khi xe chạy tốc độ cao (như Drive B đạt 100 km/h trên cao tốc), cảnh vật thay đổi liên tục và mã dHash thay đổi rất nhiều bit -> số lượng khung trùng giảm rõ rệt (ngưỡng 2 ở Drive B chỉ có 53 khung so với 149 khung ở Drive A).

## Bước 4 · Gold

### Câu 6
Dựa vào `leakage.json`: chia theo khung hình làm bao nhiêu trip bị chia cắt, so với chia theo trip? Vì sao điều này làm điểm kiểm thử đẹp một cách giả tạo?

(trả lời ở đây)

### Câu 7
Vì sao `dataset_version` là **băm nội dung** chứ không phải ngày giờ hay số đếm? Hai lần chạy liên tiếp cho kết quả gì? Vì sao `dataset_version` của bạn **khác** bạn bè dù cùng dữ liệu (liên hệ MSSV)?

(trả lời ở đây)

### Câu 8
Đọc phần `lineage` trong `manifest.json` của dataset bạn. Trả lời "dataset này được tạo từ dữ liệu nào?" bằng chính nội dung đó. Nếu một người hỏi 3 tháng sau, thông tin nào giúp tái tạo lại đúng dataset này?

(trả lời ở đây)

## Bước 5 · Điều phối và phục vụ

### Câu 9
Mô tả chính xác điều xảy ra khi trip của bạn sập rồi chạy lại: bao nhiêu task chuyển đỏ, bao nhiêu task `upstream_failed`, bạn clear gì, dữ liệu có nhân đôi không, `dataset_version` có đổi không? Bằng chứng (ảnh, số) là gì?

(trả lời ở đây)

### Câu 10
Nâng từ 2 drive lên **500 xe mỗi ngày**: ba thành phần nào của pipeline này sẽ vỡ đầu tiên, và bạn thay bằng gì (nối với slide 12, 22, 23)?

(trả lời ở đây)

## Câu hỏi riêng của bạn trên Metabase

Câu SQL bạn thêm vào dashboard và điều nó cho biết:

(trả lời ở đây)

## Nhìn lại

Điều bạn thấy bất ngờ nhất, điều gì còn chưa rõ, và một lỗi dữ liệu mà bạn nghĩ pipeline **chưa** bắt được (nếu có). Tối đa 8 dòng.

(trả lời ở đây)
