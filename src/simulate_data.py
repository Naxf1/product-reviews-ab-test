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
import numpy as np
import pandas as pd

from src.config import CONFIG
from src.utils import DATASET_PATH, ROOT, ensure_dirs, say, section


def simulate_experiment(cfg, duration_days):
    """كل المستخدمين الذين يدخلون خلال مدة التجربة (المدة مضروبة في عدد المستخدمين اليومي)."""
    # منسوخة من الدفتر بدون تغيير، إلا سطر user_id قبل return (بعد كل السحب العشوائي)
    r = np.random.default_rng(cfg["seed"])
    n = duration_days * cfg["daily_new_users"]
    is_b = (r.random(n) < cfg["treatment_share"]).astype(int)
    day = r.integers(1, duration_days + 1, n)
    activity = r.normal(0, 1, n)                                             # نشاط المستخدم (لا نقيسه مباشرة)
    base = cfg["baseline_conversion"]
    logit = np.log(base / (1 - base)) + cfg["activity_strength"] * activity
    p0 = 1 / (1 + np.exp(-logit))
    p0 = np.clip(p0 * base / p0.mean(), 0, 1)                                # نضبط المتوسط ليساوي خط الأساس
    pre_orders_90d = r.poisson(5 * p0 / base)                                # الطلبات في آخر 90 يومًا
    lift = cfg["true_lift_abs"] * (1 + cfg["novelty_boost"] * np.exp(-(day - 1) / 3))
    ordered = r.binomial(1, np.clip(p0 + lift * is_b, 0, 1))
    value = np.maximum(10, r.normal(cfg["order_value_mean"] + cfg["order_value_effect"] * is_b, cfg["order_value_sd"]))
    order_value = np.where(ordered == 1, value, np.nan)
    revenue = ordered * value
    profit = ordered * (cfg["margin"] * value - cfg["extra_cost_per_order_b"] * is_b)
    cancelled = np.where(ordered == 1, r.binomial(1, np.clip(cfg["cancel_rate"] + cfg["cancel_effect"] * is_b, 0, 1)), np.nan)
    support = r.binomial(1, np.clip(cfg["support_rate"] + cfg["support_effect"] * is_b, 0, 1))
    df = pd.DataFrame({"variant": np.where(is_b == 1, "B", "A"), "day": day, "pre_orders_90d": pre_orders_90d,
                       "ordered": ordered, "order_value": order_value, "revenue": revenue, "profit": profit,
                       "cancelled": cancelled, "contacted_support": support})
    if cfg["srm_bug_share"] > 0:                                              # خلل: سجلات ضائعة من B لقليلي النشاط
        lost = (df["variant"] == "B") & (activity < 0) & (r.random(n) < cfg["srm_bug_share"] * 2)
        df = df[~lost]
    df = df.reset_index(drop=True)
    # رقم المستخدم: يُضاف بعد كل السحب العشوائي، فتبقى البيانات مطابقة للدفتر
    df.insert(0, "user_id", np.arange(1, len(df) + 1))
    return df


def run(days):
    section("5. إنشاء البيانات بالمحاكاة")
    ensure_dirs()
    data = simulate_experiment(CONFIG, days)
    data.to_csv(DATASET_PATH, index=False)
    say(f"عدد المستخدمين: {len(data):,}")
    say(f"حُفظت البيانات: {DATASET_PATH.relative_to(ROOT)}")
    return data


if __name__ == "__main__":
    from src.sample_size import run as sample_size_run
    plan = sample_size_run()
    if plan:
        run(plan["days"])
