"""القسم 9: التقرير والتوصية (صفحة واحدة).

Owner: Abdulaziz (@A-EDU)
Source: notebook section 9
Run alone:  python -m src.report   (needs analysis to have run)

CONTRACT — run(results) receives the dict returned by analysis.run(), and must:
  * build the decision with decide(primary["أدنى 95%"], primary["أعلى 95%"], CONFIG["mde_abs"], guardrails_ok)
  * estimate annual profit change with ANNUAL_USERS
  * write outputs/results/report.md (Arabic, same tables as the notebook report)
  * print the decision and return it (str)
"""
from src.config import ANNUAL_USERS, CONFIG  # noqa: F401
from src.utils import RESULTS_DIR, decide, ensure_dirs, say, section  # noqa: F401


def run(results):
    section("9. التقرير والتوصية")
    # TODO (Abdulaziz)
    say("لم يُنفذ بعد — Abdulaziz")
    return None


if __name__ == "__main__":
    from src.analysis import run as analysis_run
    from src.utils import load_dataset
    results = analysis_run(load_dataset())
    if results:
        run(results)
