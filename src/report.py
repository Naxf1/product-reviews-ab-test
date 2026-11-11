"""القسم 9: التقرير والتوصية (صفحة واحدة).

Owner: Naif (@Naxf1)
Source: notebook section 9
Run alone:  python -m src.report          (needs analysis to have run)
            python -m src.report --demo   (fixed sample numbers, only to test the report layout)

CONTRACT — run(results) receives the dict returned by analysis.run(), and must:
  * build the decision with decide(primary["أدنى 95%"], primary["أعلى 95%"], CONFIG["mde_abs"], guardrails_ok)
  * estimate annual profit change with ANNUAL_USERS
  * write outputs/results/report.md (Arabic, same tables as the notebook report)
  * print the decision and return it (str)
"""
from src.config import ANNUAL_USERS, CONFIG
from src.utils import RESULTS_DIR, ROOT, decide, ensure_dirs, say, section

REPORT_PATH = RESULTS_DIR / "report.md"
PROFIT_ROW = "الربح لكل مستخدم"

# التوصية والخطوة التالية لكل قرار ممكن من decide()
RECOMMENDATIONS = {
    "لا نقرر بعد. نمدد التجربة، أو نعيد تصميمها بقوة أعلى.": (
        "لا نطلق النسخة B الآن. النتيجة غير حاسمة: الأثر موجب لكن فترة الثقة تشمل الصفر، "
        "وتشمل أيضًا الأثر الذي يهمنا (نقطة واحدة)، فلا نستطيع الإطلاق ولا الاستبعاد.",
        "نمدد التجربة إلى أسبوعين أو ثلاثة لنصل إلى قوة أعلى، أو نقبل أثرًا أدنى أكبر من نقطة واحدة "
        "ونعيد حساب حجم العينة على أساسه، ثم نحلل مرة واحدة في نهاية المدة المحددة مسبقًا.",
    ),
    "نطلق، لأن الأثر إيجابي بثقة ومقاييس الحماية سليمة.": (
        "نطلق النسخة B (التقييمات أعلى الصفحة) لكل المستخدمين.",
        "نطلق تدريجيًا، ونبقي مجموعة ضابطة صغيرة لعدة أسابيع لنتأكد أن الأثر لا يتلاشى بعد زوال أثر الحداثة.",
    ),
    "لا نطلق الآن، لأن المقياس الرئيسي تحسن لكن أحد مقاييس الحماية ساء. نعالج المشكلة ثم نعيد التحقق.": (
        "لا نطلق الآن رغم تحسن نسبة الطلب، لأن أحد مقاييس الحماية تدهور.",
        "نحدد سبب تدهور مقياس الحماية ونعالجه، ثم نعيد التجربة للتحقق.",
    ),
    "لا نطلق، لأننا استبعدنا وجود أثر بالحجم الذي يهمنا.": (
        "لا نطلق، لأن فترة الثقة تستبعد أثرًا بحجم نقطة واحدة.",
        "نوقف هذه الفكرة، ونجرب تغييرات أخرى في صفحة المنتج.",
    ),
    "لا نطلق، لأن النسخة الجديدة أضرت بالمقياس الرئيسي.": (
        "لا نطلق، لأن النسخة B خفضت نسبة الطلب.",
        "نبقي التقييمات أسفل الصفحة، ونراجع سبب الضرر قبل أي تجربة جديدة.",
    ),
}


def pts(x):
    """نسبة (مثل 0.006) إلى نقاط مئوية بخانتين (0.60)."""
    return f"{x * 100:.2f}"


def millions(x):
    return f"{x / 1e6:.2f}"


def build_report(results, decision):
    rate_a, rate_b = results["rate_a"], results["rate_b"]
    primary, cuped = results["primary"], results["primary_cuped"]
    guard_table = results["guard_table"]
    profit = guard_table.loc[PROFIT_ROW]
    reduction = results.get("cuped_variance_reduction")

    guard_rows = "\n".join(f"| {name} | {row['الحالة']} |" for name, row in guard_table.iterrows())
    recommendation, next_step = RECOMMENDATIONS.get(decision, (decision, "نراجع النتائج مع الفريق قبل أي قرار."))
    reduction_text = f"حوالي {reduction:.0%}" if reduction is not None else "قليلًا"

    return f"""<div dir="rtl">

### تقرير التجربة: {CONFIG['project']}

**القرار:** {decision}

| البند | القيمة |
|---|---|
| المقياس الرئيسي | نسبة الطلب من {rate_a:.2%} إلى {rate_b:.2%} |
| الأثر | {pts(primary['الفرق'])} نقطة (فترة الثقة 95%: من {pts(primary['أدنى 95%'])} إلى {pts(primary['أعلى 95%'])})، وقيمة p = {primary['p']:.3f} |
| الأثر مع CUPED | {pts(cuped['الفرق'])} نقطة (من {pts(cuped['أدنى 95%'])} إلى {pts(cuped['أعلى 95%'])}) |
| التغير التقديري في الربح السنوي | {millions(profit['الفرق'] * ANNUAL_USERS)} مليون ريال (من {millions(profit['أدنى 95%'] * ANNUAL_USERS)} إلى {millions(profit['أعلى 95%'] * ANNUAL_USERS)}) |

| مقياس الحماية | الحالة |
|---|---|
{guard_rows}

#### التوصية والخطوة التالية والقيود

- **التوصية:** {recommendation}
- **الخطوة التالية:** {next_step}
- **القيود:** البيانات من محاكاة وليست من مستخدمين حقيقيين، والتجربة أسبوع واحد فقط فلا نعرف هل يستمر الأثر.
  قلل CUPED التباين {reduction_text} فقط لأن المقياس الرئيسي نعم أو لا. والأثر الحقيقي في المحاكاة
  ({CONFIG['true_lift_abs'] * 100:.1f} نقطة) أصغر من الأثر الأدنى الذي صممنا التجربة لاكتشافه ({CONFIG['mde_abs'] * 100:.0f} نقطة)، فقوة التجربة أقل من 80%.
- **التقدير المالي:** الفرق في الربح لكل مستخدم مضروب في {ANNUAL_USERS:,} مستخدم في السنة، وهو تقدير تقريبي.

</div>
"""


def run(results):
    section("9. التقرير والتوصية")
    primary = results["primary"]
    decision = decide(primary["أدنى 95%"], primary["أعلى 95%"], CONFIG["mde_abs"], results["guardrails_ok"])

    ensure_dirs()
    REPORT_PATH.write_text(build_report(results, decision), encoding="utf-8")
    say(f"حُفظ التقرير: {REPORT_PATH.relative_to(ROOT)}")
    say(f"القرار: {decision}")
    return decision


def demo_results():
    """أرقام ثابتة لاختبار شكل التقرير قبل اكتمال analysis.py. لا تُستخدم في التشغيل الكامل."""
    import pandas as pd

    def ci(diff, low, high, p=None):
        se = (high - low) / 3.92
        return {"الفرق": diff, "أدنى 95%": low, "أعلى 95%": high, "SE": se, "p": p}

    primary = ci(0.00596, -0.00044, 0.01235, 0.068)
    cuped = ci(0.00615, -0.00012, 0.01241, 0.054)
    guard_table = pd.DataFrame([
        {"المقياس": "الربح لكل مستخدم", "A": 3.00, "B": 3.20, **ci(0.2044, -0.003, 0.412, 0.053), "الحالة": "سليم"},
        {"المقياس": "نسبة إلغاء الطلبات", "A": 0.050, "B": 0.050, **ci(0.0, -0.011, 0.011, 0.99), "الحالة": "سليم"},
        {"المقياس": "التواصل مع الدعم", "A": 0.030, "B": 0.030, **ci(0.0, -0.004, 0.004, 0.99), "الحالة": "سليم"},
    ]).set_index("المقياس")
    return {
        "rate_a": 0.1009, "rate_b": 0.1069,
        "primary": primary, "primary_cuped": cuped,
        "cuped_variance_reduction": 1 - (cuped["SE"] / primary["SE"]) ** 2,
        "guard_table": guard_table, "guardrails_ok": True,
    }


if __name__ == "__main__":
    import sys

    if "--demo" in sys.argv:
        run(demo_results())
    else:
        from src.analysis import run as analysis_run
        from src.utils import load_dataset
        results = analysis_run(load_dataset())
        if results:
            run(results)
        else:
            say("التحليل لم يرجع نتائج بعد. للتجربة بأرقام ثابتة: python -m src.report --demo")
