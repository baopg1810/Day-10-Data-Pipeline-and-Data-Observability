# Runbook - Lab Day 10

## Symptom

Agent/retrieval tra loi sai version, vi du "14 ngay lam viec" thay vi "7 ngay lam viec", HR tra "10 ngay phep nam" thay vi "12 ngay", hoac cau access Level 4 khong tim thay nguon.

## Detection

- `etl_pipeline.py run` in `PIPELINE_HALT` khi expectation halt fail.
- `eval_retrieval.py` co `hits_forbidden=yes` hoac `contains_expected=no`.
- `grading_run.py` co `hits_forbidden=true`, `contains_expected=false`, hoac `top1_doc_matches=false`.
- Freshness check doc manifest tra `FAIL` neu `latest_exported_at` cu hon SLA.

## Diagnosis

| Buoc | Viec lam | Ket qua mong doi |
|---|---|---|
| 1 | Mo `artifacts/logs/run_<run-id>.log` | Thay `raw_records`, `cleaned_records`, `quarantine_records`, expectation fail |
| 2 | Mo `artifacts/quarantine/quarantine_<run-id>.csv` | Xac dinh reason: unknown doc, stale date, stale HR, noisy chunk |
| 3 | Chay `eval_retrieval.py --out artifacts/eval/debug.csv` | Xac dinh cau nao `hits_forbidden` hoac top1 sai |
| 4 | Mo `artifacts/manifests/manifest_<run-id>.json` | Kiem tra `latest_exported_at`, `run_id`, Chroma collection |

## Mitigation

1. Neu stale/forbidden: sua cleaning rule hoac source export, chay lai pipeline khong dung `--skip-validate`.
2. Neu inject demo da lam ban Chroma xau: publish lai good run, vi embed co upsert theo `chunk_id` va prune id khong con trong cleaned.
3. Neu freshness `FAIL`: yeu cau source owner cap export moi hon, hoac gan banner "data stale" cho agent.
4. Neu thieu source: dong bo `ALLOWED_DOC_IDS`, `contracts/data_contract.yaml`, va expectation `required_grading_doc_ids_present`.

## Prevention

Them expectation halt cho moi failure mode co anh huong retrieval: stale refund 14 ngay, HR 10 ngay, missing doc access, noisy chunk, non-P1 SLA chunks. Duy tri eval/grading trong CI hoac pre-submit de bat regression truoc khi publish collection.
