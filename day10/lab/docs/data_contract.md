# Data Contract - Lab Day 10

## 1. Nguon Du Lieu

| Nguon | Phuong thuc ingest | Failure mode chinh | Metric / alert |
|---|---|---|---|
| `policy_refund_v4` | CSV export tu CS policy | stale refund window 14 ngay, duplicate, old effective_date | `refund_no_stale_14d_window`, `stale_doc_effective_date` |
| `sla_p1_2026` | CSV export tu IT support | chunk P2/P3/P4 lan vao scope P1, missing escalation/update | `sla_p1_no_other_priority_chunks`, eval P1 |
| `it_helpdesk_faq` | CSV export tu IT helpdesk | missing date, duplicate FAQ, noisy text | ISO date expectation, quarantine count |
| `hr_leave_policy` | CSV export tu HR | HR 2025 10 ngay phep nam lan vao ban 2026 | `hr_leave_no_stale_10d_annual`, `stale_hr_policy_content` |
| `access_control_sop` | CSV export tu IT Security | source hop le bi allowlist baseline bo sot | `required_grading_doc_ids_present` |

## 2. Schema Cleaned

| Cot | Kieu | Bat buoc | Ghi chu |
|---|---|---|---|
| `chunk_id` | string | Co | ID on dinh theo `doc_id`, text sau clean, va seq |
| `doc_id` | string | Co | Nam trong allowlist 5 nguon canonical |
| `chunk_text` | string | Co | Min length 8, khong noisy marker, khong stale forbidden |
| `effective_date` | date | Co | ISO `YYYY-MM-DD`, khong cu hon floor cua doc |
| `exported_at` | datetime | Co | Normalize `YYYY/MM/DDT...` thanh ISO |

## 3. Quarantine Vs Drop

Moi record bi loai duoc ghi vao `artifacts/quarantine/quarantine_<run-id>.csv` kem `reason`. Pipeline khong drop im lang. Owner kiem tra quarantine khi `quarantine_records` tang bat thuong hoac expectation halt. Chi merge lai khi source owner xac nhan doc_id, effective_date, va content la canonical.

## 4. Phien Ban & Canonical

Canonical docs nam trong `data/docs/`. Version dang publish:

- Refund: `policy_refund_v4`, min effective date `2026-02-01`, window dung la 7 ngay lam viec.
- SLA P1: `sla_p1_2026`, min effective date `2026-01-15`, chi publish scope P1.
- FAQ: `it_helpdesk_faq`, min effective date `2026-01-20`.
- HR: `hr_leave_policy`, min effective date `2026-01-01`, annual leave under 3 years = 12 ngay.
- Access: `access_control_sop`, min effective date `2026-01-01`.
