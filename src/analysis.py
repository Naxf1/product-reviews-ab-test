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

    # 7.1 المقياس الرئيسي، مع CUPED
    A, B = df[df["variant"] == "A"], df[df["variant"] == "B"]
    rate_a = float(A["ordered"].mean())
    rate_b = float(B["ordered"].mean())
    primary = diff_ci(A["ordered"], B["ordered"])

    theta = np.cov(df["ordered"], df["pre_orders_90d"])[0, 1] / df["pre_orders_90d"].var(ddof=1)
    adjusted = df["ordered"] - theta * (df["pre_orders_90d"] - df["pre_orders_90d"].mean())
    primary_cuped = diff_ci(adjusted[df["variant"] == "A"], adjusted[df["variant"] == "B"])
    cuped_variance_reduction = float(1 - (primary_cuped["SE"] / primary["SE"]) ** 2)

    primary_table = pd.DataFrame([primary, primary_cuped], index=["بدون تعديل", "مع CUPED"])
    say(f"نسبة الطلب في A: {rate_a:.2%}، وفي B: {rate_b:.2%}")
    say(f"الأثر (بدون تعديل): {primary['الفرق'] * 100:.3f} نقطة "
        f"(95% CI: {primary['أدنى 95%'] * 100:.3f} إلى {primary['أعلى 95%'] * 100:.3f}، p = {primary['p']:.3f})")
    say(f"الأثر (مع CUPED): {primary_cuped['الفرق'] * 100:.3f} نقطة "
        f"(95% CI: {primary_cuped['أدنى 95%'] * 100:.3f} إلى {primary_cuped['أعلى 95%'] * 100:.3f}، p = {primary_cuped['p']:.3f})")
    say(f"انخفاض التباين بطريقة CUPED: {cuped_variance_reduction:.0%}")
    save_table(primary_table, "primary")

    # 7.2 المقاييس الثانوية، مع تصحيح الاختبارات المتعددة (BH)
    secondary = {
        "قيمة الطلب (لمن طلب)": diff_ci(A["order_value"].dropna(), B["order_value"].dropna()),
        "الإيراد لكل مستخدم": diff_ci(A["revenue"], B["revenue"]),
    }
    sec = pd.DataFrame(secondary).T
    sec["دال بعد تصحيح BH"] = multipletests(sec["p"].astype(float), alpha=0.05, method="fdr_bh")[0]
    save_table(sec, "secondary")

    # 7.3 مقاييس الحماية
    guardrail_defs = {
        "profit": ("الربح لكل مستخدم", "down"),
        "cancelled": ("نسبة إلغاء الطلبات", "up"),
        "contacted_support": ("التواصل مع الدعم", "up"),
    }
    rows, guard_status = [], {}
    for col, (label, bad) in guardrail_defs.items():
        res = diff_ci(A[col].dropna(), B[col].dropna())
        harmful = res["أعلى 95%"] < 0 if bad == "down" else res["أدنى 95%"] > 0
        status = "تدهور دال" if harmful else "سليم"
        guard_status[label] = status
        rows.append({"المقياس": label, "A": A[col].mean(), "B": B[col].mean(), **res, "الحالة": status})
        say(f"مقياس الحماية «{label}»: {status}")
    guard_table = pd.DataFrame(rows).set_index("المقياس")
    guardrails_ok = all(s == "سليم" for s in guard_status.values())
    save_table(guard_table, "guardrails")

    # 7.4 فحص أثر الحداثة
    plt.figure()
    daily = df.groupby(["day", "variant"])["ordered"].mean().unstack()
    daily_lift = (daily["B"] - daily["A"]) * 100
    plt.plot(daily_lift.index, daily_lift.values, marker="o", color=TEAL, label=ar("الأثر في كل يوم"))
    plt.axhline(primary["الفرق"] * 100, color=ORANGE, linestyle="--", label=ar("الأثر الكلي"))
    plt.axhline(0, color=GRAY, linewidth=0.8)
    plt.xlabel(ar("يوم دخول المستخدم"))
    plt.ylabel(ar("الأثر (نقطة مئوية)"))
    plt.title(ar("هل الأثر ثابت مع الوقت؟"))
    plt.legend()
    save_fig("novelty_daily_lift")

    # رسم نسبة الطلب في كل نسخة مع فترة الثقة 95%
    plt.figure()
    rates = [rate_a * 100, rate_b * 100]
    ci_95 = [
        1.96 * A["ordered"].std(ddof=1) / np.sqrt(len(A)) * 100,
        1.96 * B["ordered"].std(ddof=1) / np.sqrt(len(B)) * 100,
    ]
    labels = [ar("النسخة A (أسفل الصفحة)"), ar("النسخة B (أعلى الصفحة)")]
    bars = plt.bar(labels, rates, yerr=ci_95, capsize=6, color=[TEAL, ORANGE], edgecolor=NAVY, width=0.45)
    for bar, r in zip(bars, rates):
        plt.text(bar.get_x() + bar.get_width() / 2, r + max(ci_95) + 0.3, f"{r:.2f}%", ha="center", color=NAVY)
    plt.ylabel(ar("نسبة الطلب (%)"))
    plt.title(ar("نسبة الطلب في كل نسخة (مع فترة الثقة 95%)"))
    plt.ylim(0, max(rates) + max(ci_95) + 2.5)
    save_fig("conversion_by_variant")

    # رسم مقاييس الحماية (الفرق مع فترة الثقة 95% وخط الصفر)
    plt.figure()
    g_labels = [ar(idx) for idx in guard_table.index]
    diffs = guard_table["الفرق"].values
    err_low = diffs - guard_table["أدنى 95%"].values
    err_high = guard_table["أعلى 95%"].values - diffs
    y_pos = np.arange(len(g_labels))
    plt.errorbar(diffs, y_pos, xerr=[err_low, err_high], fmt="o", color=TEAL, ecolor=ORANGE,
                 elinewidth=2, capsize=5, label=ar("الفرق (B - A) مع 95% CI"))
    plt.axvline(0, color=GRAY, linestyle="--", linewidth=1, label=ar("خط الصفر"))
    plt.yticks(y_pos, g_labels)
    plt.xlabel(ar("الفرق بين النسختين (B - A)"))
    plt.title(ar("مقاييس الحماية: الفرق وفترة الثقة 95%"))
    plt.legend()
    save_fig("guardrails")

    return {
        "rate_a": rate_a,
        "rate_b": rate_b,
        "primary": primary,
        "primary_cuped": primary_cuped,
        "cuped_variance_reduction": cuped_variance_reduction,
        "guard_table": guard_table,
        "guardrails_ok": guardrails_ok,
    }


if __name__ == "__main__":
    from src.utils import load_dataset
    run(load_dataset())
