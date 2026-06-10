# Báo Cáo Cá Nhân - Lab Day 10: Data Pipeline & Data Observability

**Họ và tên:** Phùng Gia Bảo  
**Ngày nộp:** 2026-06-10  
**File nộp:** `report.md`

## 1. Phần việc tôi đã thực hiện

Trong lab này, tôi xử lý pipeline dữ liệu từ file raw `data/raw/policy_export_dirty.csv`. File raw có 247 records, gồm nhiều nguồn hợp lệ và không hợp lệ. Pipeline baseline bị thiếu `access_control_sop`, để lọt version HR cũ, và có khả năng publish chunk stale của chính sách hoàn tiền. Tôi đã sửa phần cleaning, expectation, contract và report để pipeline có thể clean/quarantine dữ liệu, validate bằng expectation suite, embed vào Chroma, rồi chạy eval/grading.

Run chính tôi dùng để nộp là `final-good-v3`. Manifest nằm ở:

```text
artifacts/manifests/manifest_final-good-v3.json
```

Lệnh chạy pipeline:

```bash
cd day10/lab
.venv\Scripts\python.exe etl_pipeline.py run --run-id final-good-v3
```

## 2. Pipeline và kết quả tổng quan

Pipeline đọc raw CSV, sau đó chạy `clean_rows`, ghi hai output: cleaned CSV và quarantine CSV. Dữ liệu cleaned được validate bằng `run_expectations`; nếu có expectation severity `halt` fail thì pipeline dừng trước khi embed. Khi pass, pipeline upsert vào Chroma collection `day10_kb` và prune các vector không còn trong cleaned run để tránh retrieval lấy dữ liệu cũ.

Kết quả run `final-good-v3`:

```text
raw_records=247
cleaned_records=28
quarantine_records=219
PIPELINE_OK
```

Artifacts chính:

```text
artifacts/cleaned/cleaned_final-good-v3.csv
artifacts/quarantine/quarantine_final-good-v3.csv
artifacts/manifests/manifest_final-good-v3.json
artifacts/eval/eval_after_fix.csv
artifacts/eval/grading_run.jsonl
```

## 3. Cleaning rules tôi đã sửa

Baseline chỉ cho phép 4 `doc_id`, nên câu grading về Level 4 Admin Access không có nguồn đúng. Tôi thêm `access_control_sop` vào allowlist và đồng bộ contract. Ngoài ra, tôi thêm các rule có tác động đo được:

| Rule | Tác động |
|---|---|
| Thêm `access_control_sop` vào allowlist | Giúp `gq_d10_10` retrieve đúng top-1 từ `access_control_sop` |
| `stale_doc_effective_date` | Quarantine 81 rows có effective_date cũ hơn version canonical |
| `stale_hr_policy_content` | Quarantine 8 rows HR 2025 có nội dung "10 ngày phép năm" |
| `ambiguous_or_noisy_chunk_text` | Quarantine chunk có marker "Nội dung không rõ ràng" hoặc `!!!` |
| `repeated_noise_chunk_text` | Loại chunk lặp câu/lặp từ bất thường |
| `non_p1_sla_scope` | Loại chunk P2/P3/P4 khỏi doc `sla_p1_2026` để tránh nhiễu câu hỏi P1 |
| Normalize `exported_at` | Đổi timestamp dạng `YYYY/MM/DDT...` thành ISO để freshness parse được |

Baseline `baseline-before` có:

```text
cleaned_records=40
quarantine_records=207
expectation[hr_leave_no_stale_10d_annual] FAIL
```

Sau khi sửa, `final-good-v3` có:

```text
cleaned_records=28
quarantine_records=219
tất cả expectations pass
```

## 4. Expectations tôi đã bổ sung

Tôi thêm các expectation để pipeline không chỉ clean dữ liệu mà còn bắt regression khi dữ liệu xấu quay lại:

| Expectation | Mục đích | Severity |
|---|---|---|
| `required_grading_doc_ids_present` | Bắt pipeline halt nếu thiếu một trong 5 nguồn grading | halt |
| `no_ambiguous_or_noisy_chunks` | Không publish chunk có marker noisy/không rõ ràng | halt |
| `effective_date_not_before_doc_floor` | Đảm bảo effective_date không cũ hơn version canonical | halt |
| `sla_p1_no_other_priority_chunks` | Không để chunk P2/P3/P4 vào scope SLA P1 | halt |

Expectation fail có chủ đích trong Sprint 3 là:

```text
expectation[refund_no_stale_14d_window] FAIL (halt) :: violations=1
```

Fail này xuất hiện khi tôi chạy inject corruption với `--no-refund-fix --skip-validate`.

## 5. Before / after retrieval

Tôi tạo dữ liệu xấu bằng lệnh:

```bash
.venv\Scripts\python.exe etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate
.venv\Scripts\python.exe eval_retrieval.py --out artifacts/eval/after_inject_bad.csv
.venv\Scripts\python.exe grading_run.py --out artifacts/eval/grading_inject_bad.jsonl
```

Kết quả inject cho thấy nếu pipeline bỏ qua validate thì stale chunk refund sẽ được embed. Câu `q_refund_window` trong `after_inject_bad.csv` có:

```text
top1_doc_id=policy_refund_v4
top1_preview=Yêu cầu hoàn tiền được chấp nhận trong vòng 14 ngày làm việc kể từ xác nhận đơn.
contains_expected=yes
hits_forbidden=yes
```

Trong grading inject, `gq_d10_01` cũng có `hits_forbidden=true`. Sau đó tôi publish lại good run `final-good-v3`, Chroma prune vector xấu và kết quả cuối cùng đạt:

```text
eval_after_fix.csv: 21/21 pass, không có hits_forbidden, không có top1 sai
grading_run.jsonl: 10/10 pass, contains_expected=true, hits_forbidden=false, top1_doc_matches=true
```

## 6. Kết quả grading chính thức

Tôi đã chạy:

```bash
.venv\Scripts\python.exe grading_run.py --out artifacts/eval/grading_run.jsonl
.venv\Scripts\python.exe instructor_quick_check.py --grading artifacts/eval/grading_run.jsonl
```

Instructor quick check báo OK cho tất cả 10 câu:

```text
gq_d10_01 refund window 7 ngày
gq_d10_02 refund exception hàng kỹ thuật số
gq_d10_03 Finance 3-5 ngày
gq_d10_04 SLA P1 first response 15 phút
gq_d10_05 SLA P1 resolution 4 giờ
gq_d10_06 SLA P1 escalation 10 phút
gq_d10_07 IT lockout 5 lần
gq_d10_08 VPN 2 thiết bị
gq_d10_09 HR 12 ngày phép năm
gq_d10_10 Level 4 Admin Access IT Manager + CISO
```

## 7. Freshness và monitoring

Tôi chạy freshness trên manifest:

```bash
.venv\Scripts\python.exe etl_pipeline.py freshness --manifest artifacts/manifests/manifest_final-good-v3.json
```

Kết quả là `FAIL`:

```text
latest_exported_at=2026-04-11T00:00:00
sla_hours=24
reason=freshness_sla_exceeded
```

Đây là kết quả hợp lý vì ngày chạy lab là 2026-06-10, trong khi export mới nhất là 2026-04-11. Pipeline clean và grading vẫn pass, nhưng nếu dùng production thì cần lấy export mới hơn trước khi publish cho agent.

## 8. Bài học và việc có thể cải tiến

Bài học lớn nhất của tôi là lỗi retrieval không chỉ đến từ model mà thường đến từ data versioning và source scope. Nếu allowlist thiếu nguồn, top-1 không thể đúng; nếu để lọt stale chunk, câu trả lời có thể vừa chứa keyword đúng vừa hit forbidden. Nếu có thêm thời gian, tôi sẽ đưa eval và instructor quick check vào một lệnh CI nhỏ, để mỗi lần sửa cleaning rule đều tự động kiểm tra 21 câu eval và 10 câu grading trước khi nộp.
