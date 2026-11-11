"""القسم 3: حجم العينة والمدة.

Owner: Abdulmajeed (@a-Nash1)
Source: notebook cell under "## 3. حجم العينة والمدة"
Run alone:  python -m src.sample_size

CONTRACT — run() must return a dict with these keys (main.py passes "days" to the simulation):
    {"n_per_group": int, "days": int, "n_planned": int, "mde_planned": float, "mde_one_week": float}
and save outputs/results/sample_size.csv with save_table().
"""
import pandas as pd

from src.config import CONFIG
from src.utils import (duration_days, mde_proportions, n_per_group_proportions,
                       save_table, say, section)


def run():
    section("3. حجم العينة والمدة")
    c = CONFIG

    # نفس حسابات الدفتر حرفيًا
    n_per_group = n_per_group_proportions(c["baseline_conversion"], c["baseline_conversion"] + c["mde_abs"],
                                          c["alpha"], c["power"])
    days = duration_days(n_per_group, c["daily_new_users"])
    say(f"المشروع: {c['project']}")
    say(f"حجم العينة: {n_per_group:,} في كل مجموعة، أي {2 * n_per_group:,} مستخدم في المجموع")
    say(f"المدة: {days} يومًا، وعدد الأسابيع الكاملة: {days // 7}")
    n_planned = days * c["daily_new_users"] // 2
    say(f"عدد المستخدمين المتوقع خلال المدة: {n_planned:,} في كل مجموعة")

    n_one_week = 7 * c["daily_new_users"] // 2
    mde = {}
    for key, label, n_g in [("mde_planned", "في المدة المخططة", n_planned),
                            ("mde_one_week", "إذا اكتفينا بأسبوع واحد", n_one_week)]:
        m = mde_proportions(c["baseline_conversion"], n_g, c["alpha"], c["power"])
        mde[key] = float(m)
        say(f"{label}: أصغر أثر قابل للاكتشاف حوالي {m * 100:.2f} نقطة")

    table = pd.DataFrame(
        {"القيمة": [c["baseline_conversion"], c["mde_abs"], c["alpha"], c["power"], c["daily_new_users"],
                    n_per_group, 2 * n_per_group, days, days // 7, n_planned,
                    mde["mde_planned"], mde["mde_one_week"]]},
        dtype=object,
        index=pd.Index(["نسبة الطلب الحالية", "أصغر أثر يغير القرار", "alpha", "القوة الإحصائية",
                        "المستخدمون الجدد يوميًا", "حجم العينة لكل مجموعة", "حجم العينة الكلي",
                        "المدة (أيام)", "عدد الأسابيع الكاملة", "المتوقع لكل مجموعة خلال المدة",
                        "أصغر أثر قابل للاكتشاف في المدة المخططة",
                        "أصغر أثر قابل للاكتشاف في أسبوع واحد"], name="البند"),
    )
    save_table(table, "sample_size")

    return {"n_per_group": int(n_per_group), "days": int(days), "n_planned": int(n_planned),
            "mde_planned": mde["mde_planned"], "mde_one_week": mde["mde_one_week"]}


if __name__ == "__main__":
    run()
