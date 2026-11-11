"""القسم 6: فحوص الثقة وجودة البيانات.

Owner: Abdulmajeed (@a-Nash1)
Run alone:  python -m src.quality_checks   (reads data/dataset.csv)

CONTRACT — run(df) must:
  * SRM check with srm_check(n_a, n_b, CONFIG["treatment_share"])
  * duplicate user_id count, missing values per column (order_value / cancelled are
    expected to be empty for users who did not order — say so), row count vs. days * daily_new_users
  * save outputs/results/quality_checks.csv
  * return True if all checks pass (SRM p >= 0.001 and no duplicates), else False
"""
import pandas as pd

from src.config import CONFIG  # noqa: F401
from src.utils import DATASET_PATH, save_table, say, section, srm_check  # noqa: F401


def run(df):
    section("6. فحوص الثقة وجودة البيانات")
    # TODO (Abdulmajeed)
    say("لم يُنفذ بعد — Abdulmajeed")
    return None


if __name__ == "__main__":
    from src.utils import load_dataset
    run(load_dataset())
