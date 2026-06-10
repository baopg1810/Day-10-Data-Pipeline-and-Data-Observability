# Quality Report - Lab Day 10

**run_id good:** `final-good-v3`  
**run_id inject:** `inject-bad`  
**Ngay:** 2026-06-10

## 1. Tom Tat So Lieu

| Chi so | Truoc (`baseline-before`) | Sau (`final-good-v3`) | Ghi chu |
|---|---:|---:|---|
| raw_records | 247 | 247 | Cung raw CSV |
| cleaned_records | 40 | 28 | Giam do them date floor, stale HR, noisy, SLA scope |
| quarantine_records | 207 | 219 | Tang 12 rows co ly do ro |
| Expectation halt? | Co | Khong | Baseline fail HR 10 ngay; final all pass |

## 2. Before / After Retrieval

Artifacts:

- Bad eval: `artifacts/eval/after_inject_bad.csv`
- Good eval: `artifacts/eval/eval_after_fix.csv`
- Bad grading: `artifacts/eval/grading_inject_bad.jsonl`
- Good grading: `artifacts/eval/grading_run.jsonl`

Refund window `q_refund_window`:

- Inject: `hits_forbidden=yes`, top preview chua "14 ngay lam viec".
- Good: 21/21 eval pass, khong co `hits_forbidden=yes`, khong co `top1_doc_expected=no`.

HR version:

- Good: `q_hr_annual_leave_under3` va `gq_d10_09` deu chua `12 ngay`, khong hit forbidden `10 ngay phep`.

## 3. Freshness & Monitor

`final-good-v3` freshness: `FAIL`, `latest_exported_at=2026-04-11T00:00:00`, `sla_hours=24`, `reason=freshness_sla_exceeded`. Ket qua nay phan anh dung viec raw export da cu; trong production can lay export moi hon truoc khi publish cho agent.

## 4. Corruption Inject

Lenh inject:

```bash
.venv\Scripts\python.exe etl_pipeline.py run --run-id inject-bad --no-refund-fix --skip-validate
```

Expectation `refund_no_stale_14d_window` fail voi `violations=1`. Do dung `--skip-validate`, stale chunk van duoc embed de chung minh retrieval xau: `gq_d10_01` co `hits_forbidden=true`. Sau do chay lai `final-good-v3` de prune vector xau va grading tro ve 10/10.

## 5. Han Che & Viec Chua Lam

- Chua co alert tu dong; moi co log, manifest, va runbook.
- Freshness can export moi neu dung that.
- Can dien thong tin thanh vien vao report ca nhan.
