# Kien Truc Pipeline - Lab Day 10

**Nhom:** Day 10 Lab Team  
**Cap nhat:** 2026-06-10

## 1. So Do Luong

```text
data/raw/policy_export_dirty.csv
  -> load_raw_csv
  -> clean_rows
       -> cleaned CSV: artifacts/cleaned/cleaned_<run-id>.csv
       -> quarantine CSV: artifacts/quarantine/quarantine_<run-id>.csv
  -> run_expectations
       -> halt neu co expectation severity=halt fail
  -> Chroma upsert/prune
  -> manifest + freshness check
  -> eval_retrieval / grading_run
```

`run_id` duoc tao tu timestamp UTC hoac truyen bang `--run-id`, va xuat hien trong log, manifest, metadata Chroma.

## 2. Ranh Gioi Trach Nhiem

| Thanh phan | Input | Output | Owner nhom |
|---|---|---|---|
| Ingest | raw CSV | list row dict | Ingestion Owner |
| Transform | raw rows | cleaned + quarantine | Cleaning Owner |
| Quality | cleaned rows | expectation results + halt flag | Quality Owner |
| Embed | cleaned CSV | Chroma collection `day10_kb` | Embed Owner |
| Monitor | manifest | PASS/WARN/FAIL freshness | Monitoring Owner |

## 3. Idempotency & Rerun

Pipeline tao `chunk_id` on dinh tu `doc_id`, text sau clean, va seq. Embed dung `col.upsert(ids=...)`; truoc khi upsert, pipeline lay danh sach id cu va prune cac id khong con trong cleaned run hien tai. Vi vay rerun khong tao duplicate vector, va inject-bad co the duoc rollback bang cach publish lai good run.

## 4. Lien He Day 09

Day 10 tao data layer sach hon cho retrieval/agent Day 09. Corpus van cung chu de CS + IT Helpdesk, nhung collection `day10_kb` duoc tach rieng de demo before/after va inject corruption ma khong pha corpus Day 09.

## 5. Rui Ro Da Biet

- Freshness final `FAIL` vi source export moi nhat la `2026-04-11T00:00:00`, qua SLA 24h so voi ngay chay `2026-06-10`.
- Neu model embedding thay doi, ranking co the thay doi; can chay lai `eval_retrieval.py` va `grading_run.py`.
- Report ca nhan chua dien ten thanh vien thuc te.
