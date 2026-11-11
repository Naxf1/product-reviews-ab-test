"""القسم 5: إنشاء البيانات بالمحاكاة.

Owner: Abdulmajeed (@a-Nash1)
Source: notebook function simulate_experiment()
Run alone:  python -m src.simulate_data   (needs sample_size to work first)

CONTRACT — run(days) must:
  * build the data with simulate_experiment(CONFIG, days), ADDING a "user_id" column (1..n)
  * save it to DATASET_PATH (data/dataset.csv), index=False
  * return the DataFrame
Columns: user_id, variant, day, pre_orders_90d, ordered, order_value, revenue, profit,
         cancelled, contacted_support
"""
import numpy as np  # noqa: F401
import pandas as pd  # noqa: F401

from src.config import CONFIG  # noqa: F401
from src.utils import DATASET_PATH, ensure_dirs, say, section  # noqa: F401


def simulate_experiment(cfg, duration_days):
    # TODO (Abdulmajeed): paste simulate_experiment() from the notebook and add user_id.
    raise NotImplementedError


def run(days):
    section("5. إنشاء البيانات بالمحاكاة")
    say("لم يُنفذ بعد — Abdulmajeed")
    return None


if __name__ == "__main__":
    from src.sample_size import run as sample_size_run
    plan = sample_size_run()
    if plan:
        run(plan["days"])
