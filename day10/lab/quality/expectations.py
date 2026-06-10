"""
Expectation suite đơn giản (không bắt buộc Great Expectations).

Sinh viên có thể thay bằng GE / pydantic / custom — miễn là có halt có kiểm soát.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


REQUIRED_GRADING_DOC_IDS = {
    "policy_refund_v4",
    "sla_p1_2026",
    "it_helpdesk_faq",
    "hr_leave_policy",
    "access_control_sop",
}

DOC_EFFECTIVE_DATE_FLOOR = {
    "policy_refund_v4": "2026-02-01",
    "sla_p1_2026": "2026-01-15",
    "it_helpdesk_faq": "2026-01-20",
    "hr_leave_policy": "2026-01-01",
    "access_control_sop": "2026-01-01",
}


@dataclass
class ExpectationResult:
    name: str
    passed: bool
    severity: str  # "warn" | "halt"
    detail: str


def run_expectations(cleaned_rows: List[Dict[str, Any]]) -> Tuple[List[ExpectationResult], bool]:
    """
    Trả về (results, should_halt).

    should_halt = True nếu có bất kỳ expectation severity halt nào fail.
    """
    results: List[ExpectationResult] = []

    # E1: có ít nhất 1 dòng sau clean
    ok = len(cleaned_rows) >= 1
    results.append(
        ExpectationResult(
            "min_one_row",
            ok,
            "halt",
            f"cleaned_rows={len(cleaned_rows)}",
        )
    )

    # E2: không doc_id rỗng
    bad_doc = [r for r in cleaned_rows if not (r.get("doc_id") or "").strip()]
    ok2 = len(bad_doc) == 0
    results.append(
        ExpectationResult(
            "no_empty_doc_id",
            ok2,
            "halt",
            f"empty_doc_id_count={len(bad_doc)}",
        )
    )

    # E3: policy refund không được chứa cửa sổ sai 14 ngày (sau khi đã fix)
    bad_refund = [
        r
        for r in cleaned_rows
        if r.get("doc_id") == "policy_refund_v4"
        and "14 ngày làm việc" in (r.get("chunk_text") or "")
    ]
    ok3 = len(bad_refund) == 0
    results.append(
        ExpectationResult(
            "refund_no_stale_14d_window",
            ok3,
            "halt",
            f"violations={len(bad_refund)}",
        )
    )

    # E4: chunk_text đủ dài
    short = [r for r in cleaned_rows if len((r.get("chunk_text") or "")) < 8]
    ok4 = len(short) == 0
    results.append(
        ExpectationResult(
            "chunk_min_length_8",
            ok4,
            "warn",
            f"short_chunks={len(short)}",
        )
    )

    # E5: effective_date đúng định dạng ISO sau clean (phát hiện parser lỏng)
    iso_bad = [
        r
        for r in cleaned_rows
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", (r.get("effective_date") or "").strip())
    ]
    ok5 = len(iso_bad) == 0
    results.append(
        ExpectationResult(
            "effective_date_iso_yyyy_mm_dd",
            ok5,
            "halt",
            f"non_iso_rows={len(iso_bad)}",
        )
    )

    # E6: không còn marker phép năm cũ 10 ngày trên doc HR (conflict version sau clean)
    bad_hr_annual = [
        r
        for r in cleaned_rows
        if r.get("doc_id") == "hr_leave_policy"
        and "10 ngày phép năm" in (r.get("chunk_text") or "")
    ]
    ok6 = len(bad_hr_annual) == 0
    results.append(
        ExpectationResult(
            "hr_leave_no_stale_10d_annual",
            ok6,
            "halt",
            f"violations={len(bad_hr_annual)}",
        )
    )

    # E7: Ä‘á»§ 5 nguá»“n cáº§n cho grading chÃ­nh thá»©c
    present_doc_ids = {str(r.get("doc_id") or "").strip() for r in cleaned_rows}
    missing_required = sorted(REQUIRED_GRADING_DOC_IDS - present_doc_ids)
    ok7 = len(missing_required) == 0
    results.append(
        ExpectationResult(
            "required_grading_doc_ids_present",
            ok7,
            "halt",
            f"missing={missing_required}",
        )
    )

    # E8: khÃ´ng cÃ²n chunk nhiá»…u/khÃ´ng rÃµ rÃ ng sau clean
    noisy = [
        r
        for r in cleaned_rows
        if "nội dung không rõ ràng" in (r.get("chunk_text") or "").lower()
        or "!!!" in (r.get("chunk_text") or "")
    ]
    ok8 = len(noisy) == 0
    results.append(
        ExpectationResult(
            "no_ambiguous_or_noisy_chunks",
            ok8,
            "halt",
            f"violations={len(noisy)}",
        )
    )

    # E9: doc effective_date khÃ´ng Ä‘Æ°á»£c cÅ© hÆ¡n contract/version Ä‘ang publish
    stale_by_floor = [
        r
        for r in cleaned_rows
        if r.get("doc_id") in DOC_EFFECTIVE_DATE_FLOOR
        and (r.get("effective_date") or "") < DOC_EFFECTIVE_DATE_FLOOR[str(r.get("doc_id"))]
    ]
    ok9 = len(stale_by_floor) == 0
    results.append(
        ExpectationResult(
            "effective_date_not_before_doc_floor",
            ok9,
            "halt",
            f"violations={len(stale_by_floor)}",
        )
    )

    # E10: collection SLA P1 khÃ´ng publish chunk scope P2/P3/P4 gÃ¢y nhiá»…u retrieval
    non_p1_sla = [
        r
        for r in cleaned_rows
        if r.get("doc_id") == "sla_p1_2026"
        and re.match(r"ticket p[234]\b", (r.get("chunk_text") or "").strip().lower())
    ]
    ok10 = len(non_p1_sla) == 0
    results.append(
        ExpectationResult(
            "sla_p1_no_other_priority_chunks",
            ok10,
            "halt",
            f"violations={len(non_p1_sla)}",
        )
    )

    halt = any(not r.passed and r.severity == "halt" for r in results)
    return results, halt
