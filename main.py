"""يشغّل المشروع كاملًا بالترتيب: حجم العينة ← البيانات ← فحوص الثقة ← التحليل ← التقرير.

التشغيل من جذر المستودع:
    pip install -r requirements.txt
    python main.py

Owner: Naif. Each step lives in src/ and is owned by one teammate (see the file headers).
"""
import sys

from src import analysis, quality_checks, report, sample_size, simulate_data
from src.config import CONFIG
from src.utils import ensure_dirs, say


def stop_if_missing(result, step):
    if result is None:
        say(f"\nتوقف التشغيل: الخطوة «{step}» لم تُنفذ بعد، والخطوات التالية تعتمد عليها.")
        sys.exit(0)


def main():
    ensure_dirs()
    say(f"المشروع: {CONFIG['project']}")

    plan = sample_size.run()
    stop_if_missing(plan, "حجم العينة")

    data = simulate_data.run(plan["days"])
    stop_if_missing(data, "إنشاء البيانات")

    checks_ok = quality_checks.run(data)
    stop_if_missing(checks_ok, "فحوص الثقة")
    if not checks_ok:
        say("تحذير: فشل أحد فحوص الثقة. راجع outputs/results/quality_checks.csv قبل الوثوق بالنتائج.")

    results = analysis.run(data)
    stop_if_missing(results, "التحليل")

    decision = report.run(results)
    stop_if_missing(decision, "التقرير")

    say("\nاكتمل التشغيل. المخرجات في outputs/charts و outputs/results")


if __name__ == "__main__":
    main()
