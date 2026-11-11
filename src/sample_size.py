"""القسم 3: حجم العينة والمدة.

Owner: Abdulmajeed (@a-Nash1)
Source: notebook cell under "## 3. حجم العينة والمدة"
Run alone:  python -m src.sample_size

CONTRACT — run() must return a dict with these keys (main.py passes "days" to the simulation):
    {"n_per_group": int, "days": int, "n_planned": int, "mde_planned": float, "mde_one_week": float}
and save outputs/results/sample_size.csv with save_table().
"""
from src.config import CONFIG
from src.utils import (duration_days, mde_proportions, n_per_group_proportions,  # noqa: F401
                       save_table, say, section)


def run():
    section("3. حجم العينة والمدة")
    # TODO (Abdulmajeed): port the notebook code here, save the table, return the dict above.
    say("لم يُنفذ بعد — Abdulmajeed")
    return None


if __name__ == "__main__":
    run()
