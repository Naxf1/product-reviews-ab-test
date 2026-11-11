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

from src.config import CONFIG
from src.utils import save_table, say, section, srm_check

SRM_THRESHOLD = 0.001
# أعمدة فارغة عمدًا لمن لم يطلب (لا توجد قيمة طلب ولا إلغاء بدون طلب)
EMPTY_BY_DESIGN = ("order_value", "cancelled")


def run(df):
    section("6. فحوص الثقة وجودة البيانات")
    rows = []

    def add(check, value, expected, ok, note=""):
        rows.append({"الفحص": check, "القيمة": value, "المتوقع": expected,
                     "النتيجة": "سليم" if ok else "فشل", "ملاحظة": note})
        return ok

    # 1) نسبة التوزيع (SRM)
    counts = df["variant"].value_counts()
    n_a, n_b = int(counts.get("A", 0)), int(counts.get("B", 0))
    p_srm = srm_check(n_a, n_b, CONFIG["treatment_share"])
    srm_ok = add("نسبة التوزيع (SRM): قيمة p", round(float(p_srm), 4), f">= {SRM_THRESHOLD}",
                 p_srm >= SRM_THRESHOLD, f"A={n_a:,}، B={n_b:,}")

    # 2) حصة B مقابل المتوقع
    share_b = n_b / (n_a + n_b) if (n_a + n_b) else float("nan")
    add("حصة النسخة B", round(share_b, 4), CONFIG["treatment_share"], srm_ok,
        "للعرض فقط، والحكم من فحص SRM")

    # 3) تكرار رقم المستخدم
    dup = int(df["user_id"].duplicated().sum())
    dup_ok = add("صفوف مكررة في user_id", dup, 0, dup == 0)

    # 4) عدد الصفوف مقابل المدة × المستخدمين يوميًا
    days = int(df["day"].max())
    expected_rows = days * CONFIG["daily_new_users"]
    add("عدد الصفوف", len(df), expected_rows, len(df) == expected_rows,
        f"{days} أيام × {CONFIG['daily_new_users']:,} مستخدم يوميًا")

    # 5) القيم الناقصة في كل عمود
    not_ordered = int((df["ordered"] == 0).sum())
    missing_ok = True
    for col in df.columns:
        n_missing = int(df[col].isna().sum())
        if col in EMPTY_BY_DESIGN:
            ok = n_missing == not_ordered
            note = "فارغ عمدًا لمن لم يطلب، فعدد القيم الناقصة يساوي عدد من لم يطلب"
            add(f"قيم ناقصة: {col}", n_missing, not_ordered, ok, note)
        else:
            ok = n_missing == 0
            add(f"قيم ناقصة: {col}", n_missing, 0, ok)
        missing_ok = missing_ok and ok

    table = pd.DataFrame(rows, dtype=object).set_index("الفحص")
    save_table(table, "quality_checks")

    passed = bool(srm_ok and dup_ok)
    say(f"حصة B: {share_b:.2%} (المتوقع {CONFIG['treatment_share']:.0%})")
    say(f"الصفوف المكررة: {dup}، وعدد الصفوف {len(df):,} من {expected_rows:,} متوقعة")
    say(f"القيم الناقصة: {'كلها متوقعة' if missing_ok else 'توجد قيم ناقصة غير متوقعة، راجع الجدول'}"
        f" (order_value وcancelled فارغان عمدًا لـ {not_ordered:,} مستخدم لم يطلبوا)")
    say("الخلاصة: البيانات سليمة، ويمكن الوثوق بالتحليل." if passed
        else "الخلاصة: فشل فحص أساسي (SRM أو التكرار)، فلا تثق بالنتائج قبل معرفة السبب.")
    return passed


if __name__ == "__main__":
    from src.utils import load_dataset
    run(load_dataset())
