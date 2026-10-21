"""CỬA 1 – review before handing over: python tools/chung/cua1.py <folder> [--min 80] [--free]

Four reviewers (buyer, marketplace reviewer, lawyer, competitor) score the product 0-100 from its files
(BAN-GIAO.md, LEADER.md, LICENSES.md, store copy, CUA0.json). Passes when the average >= min (80 original,
70 for free pulls), the leader table shows >= 8/10, and an upgrade shows >= 2 measurable wins.
Uses the shared AI (tools/chung/ai.py). No AI key -> writes "chờ khóa AI" and fails closed (nothing is handed
over unreviewed). A human/controller review can be recorded with --manual <json file> (same fields).
Writes <folder>/CUA1.json.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ai  # noqa: E402

ROLES = ["buyer", "marketplace_reviewer", "lawyer", "competitor"]


def gather(f):
    parts = []
    for name in ["BAN-GIAO.md", "LEADER.md", "LICENSES.md", "STORE.md", "CUA0.json"]:
        p = f / name
        if p.exists():
            parts.append(f"===== {name}\n" + p.read_text(encoding="utf-8", errors="replace")[:9000])
    for p in sorted(f.glob("*/STORE.md"))[:3]:
        parts.append(f"===== {p.parent.name}/STORE.md\n" + p.read_text(encoding="utf-8", errors="replace")[:3000])
    return "\n\n".join(parts)


def review(folder, minimum=80, manual=None):
    f = Path(folder)
    if manual:
        res = json.loads(Path(manual).read_text(encoding="utf-8"))
        res["by"] = res.get("by", "manual")
    elif not ai.available():
        res = {"pass": False, "by": "none", "note": "chờ khóa AI (N24_AI_KEY / GEMINI_API_KEY) – không nộp khi chưa chấm"}
        (f / "CUA1.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
        return res
    else:
        res = ai.ask_json(
            "Act as four strict reviewers of a digital product before it goes on sale: " + ", ".join(ROLES) + ". "
            "Score each 0-100 with 2 concrete reasons. Check: quality vs the leader, honesty of claims, licenses and legal risk, "
            "whether a buyer would pay the price, AI-disclosure. Also return leader_match (how many of the 10 leader features the "
            "product matches, 0-10) and wins (list of measurable advantages over the leader). JSON keys: scores {role: {score, reasons}}, "
            "average, leader_match, wins, must_fix (list).\n\nPRODUCT FILES:\n" + gather(f), max_tokens=2500) or {}
        res["by"] = "ai"
    avg = res.get("average") or (sum(v["score"] for v in res.get("scores", {}).values()) / max(1, len(res.get("scores", {}))))
    res["average"] = round(float(avg), 1)
    res["pass"] = res["average"] >= minimum and int(res.get("leader_match", 0)) >= (0 if minimum < 80 else 8)
    res["minimum"] = minimum
    (f / "CUA1.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    return res


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    a = argparse.ArgumentParser()
    a.add_argument("folder")
    a.add_argument("--min", type=float, default=80)
    a.add_argument("--free", action="store_true")
    a.add_argument("--manual")
    x = a.parse_args()
    r = review(x.folder, 70 if x.free else x.min, x.manual)
    print(("CỬA 1 QUA " if r.get("pass") else "CỬA 1 CHƯA QUA ") + str(r.get("average", "")) + " " + r.get("note", ""))
    sys.exit(0 if r.get("pass") else 1)
