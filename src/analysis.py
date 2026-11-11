"""القسم 7: التحليل (المقياس الرئيسي مع CUPED، المقاييس الثانوية مع BH، مقاييس الحماية، أثر الحداثة).

Owner: Khaled (@k-alh)
Source: notebook sections 7.1–7.4
Run alone:  python -m src.analysis   (reads data/dataset.csv)

CONTRACT — run(df) must save:
  outputs/results/primary.csv      rows: "بدون تعديل", "مع CUPED"; cols: الفرق, أدنى 95%, أعلى 95%, SE, p
                                   (keep values as proportions, NOT x100 — report.py does the formatting)
  outputs/results/secondary.csv    + column "دال بعد تصحيح BH"
  outputs/results/guardrails.csv   index "المقياس"; cols A, B, الفرق, أدنى 95%, أعلى 95%, SE, p, الحالة
  outputs/charts/novelty_daily_lift.png, conversion_by_variant.png, guardrails.png
and return a dict:
  {"rate_a": float, "rate_b": float, "primary": dict, "primary_cuped": dict,
   "cuped_variance_reduction": float, "guard_table": DataFrame, "guardrails_ok": bool}
"""
import matplotlib.pyplot as plt  # noqa: F401
import numpy as np  # noqa: F401
import pandas as pd
from statsmodels.stats.multitest import multipletests  # noqa: F401

from src.utils import (DATASET_PATH, GRAY, NAVY, ORANGE, TEAL, ar, diff_ci,  # noqa: F401
                       save_fig, save_table, say, section)


def run(df):
    section("7. التحليل")
    # TODO (Khaled)
    say("لم يُنفذ بعد — Khaled")
    return None


if __name__ == "__main__":
    from src.utils import load_dataset
    run(load_dataset())
