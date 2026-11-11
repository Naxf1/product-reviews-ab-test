"""أدوات مشتركة لكل السكربتات: المسارات، والرسوم، والدوال الإحصائية.

Owner: Naif. Ported from the notebook's "أدوات جاهزة" cell, without IPython/Colab.
Everyone imports from here:  from src.utils import ...
"""
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # يحفظ الرسوم في ملفات بدون نافذة عرض
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cycler import cycler
from matplotlib import ft2font
from scipy import stats

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------- المسارات
# كل المسارات نسبية لجذر المستودع، فتعمل على أي جهاز
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CHARTS_DIR = ROOT / "outputs" / "charts"
RESULTS_DIR = ROOT / "outputs" / "results"
DATASET_PATH = DATA_DIR / "dataset.csv"


def ensure_dirs():
    for d in (DATA_DIR, CHARTS_DIR, RESULTS_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------- العربية في الرسوم
NATIVE_ARABIC = hasattr(ft2font, "__libraqm_version__")
if not NATIVE_ARABIC:
    import arabic_reshaper  # من requirements.txt
    from bidi.algorithm import get_display


def ar(text):
    """يجهز النص العربي ليظهر صحيحًا داخل الرسوم."""
    text = str(text)
    return text if NATIVE_ARABIC else get_display(arabic_reshaper.reshape(text))


def say(*parts, sep=" "):
    """يطبع رسالة في الطرفية (بديل say في الدفتر)."""
    print(sep.join(str(p) for p in parts))


def load_dataset():
    """يقرأ data/dataset.csv، أو يوقف التشغيل برسالة واضحة إذا لم يُنشأ بعد."""
    if not DATASET_PATH.exists():
        raise SystemExit("لا يوجد data/dataset.csv بعد. شغّل أولًا: python -m src.simulate_data  (أو python main.py)")
    return pd.read_csv(DATASET_PATH)


def section(title):
    print(f"\n{'=' * 60}\n{title}\n{'=' * 60}")


# ---------------------------------------------------------------- نمط الرسوم
TEAL, ORANGE, NAVY, GRAY = "#0E7490", "#E58A1F", "#0F2A3F", "#A9B4BC"
plt.rcParams.update({
    "figure.figsize": (9, 4.5), "figure.dpi": 110,
    "axes.prop_cycle": cycler(color=[TEAL, ORANGE, NAVY, GRAY]),
    "axes.edgecolor": "#56656F", "axes.labelcolor": NAVY, "text.color": NAVY,
    "xtick.color": "#3D4F5C", "ytick.color": "#3D4F5C",
    "axes.grid": True, "grid.color": "#D8E1E7", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.titlesize": 13, "axes.titleweight": "bold", "font.size": 11,
    "legend.frameon": False,
})
pd.set_option("display.precision", 4)
pd.set_option("display.width", 140)


def save_fig(name):
    """يحفظ الرسم الحالي في outputs/charts/<name>.png ويغلقه."""
    ensure_dirs()
    path = CHARTS_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight")
    plt.close()
    say(f"حُفظ الرسم: {path.relative_to(ROOT)}")
    return path


def save_table(df, name):
    """يحفظ جدولًا في outputs/results/<name>.csv (بترميز يفتح في Excel)."""
    ensure_dirs()
    path = RESULTS_DIR / f"{name}.csv"
    df.to_csv(path, encoding="utf-8-sig")
    say(f"حُفظ الجدول: {path.relative_to(ROOT)}")
    return path


# ---------------------------------------------------------------- الدوال الإحصائية (كما في الدفتر)
def n_per_group_proportions(p_control, p_treatment, alpha=0.05, power=0.80):
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    var = p_control * (1 - p_control) + p_treatment * (1 - p_treatment)
    return int(np.ceil((z_a + z_b) ** 2 * var / (p_treatment - p_control) ** 2))


def mde_proportions(p_control, n_per_group, alpha=0.05, power=0.80):
    z_a, z_b = stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)
    return (z_a + z_b) * np.sqrt(2 * p_control * (1 - p_control) / n_per_group)


def duration_days(n_per_group, daily_new_users, groups=2, round_to_weeks=True):
    days = int(np.ceil(n_per_group * groups / daily_new_users))
    return int(np.ceil(days / 7) * 7) if round_to_weeks else days


def srm_check(n_a, n_b, expected_share_b=0.5, threshold=0.001):
    total = n_a + n_b
    chi2, p = stats.chisquare([n_a, n_b], f_exp=[total * (1 - expected_share_b), total * expected_share_b])
    verdict = "خلل في التوزيع (SRM)، لا تثق بالنتائج" if p < threshold else "التوزيع سليم"
    say(f"A={n_a:,}   B={n_b:,}   chi2={chi2:.2f}   p={p:.2g}   النتيجة: {verdict}")
    return p


def diff_ci(a, b, alpha=0.05):
    """الفرق بين B وA مع فترة الثقة وقيمة p (بالتقريب الطبيعي)."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    diff = b.mean() - a.mean()
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    z = stats.norm.ppf(1 - alpha / 2)
    return {"الفرق": diff, "أدنى 95%": diff - z * se, "أعلى 95%": diff + z * se, "SE": se,
            "p": 2 * stats.norm.sf(abs(diff / se))}


def decide(ci_low, ci_high, mde, guardrails_ok=True):
    if ci_high < 0:
        return "لا نطلق، لأن النسخة الجديدة أضرت بالمقياس الرئيسي."
    if ci_low > 0 and not guardrails_ok:
        return "لا نطلق الآن، لأن المقياس الرئيسي تحسن لكن أحد مقاييس الحماية ساء. نعالج المشكلة ثم نعيد التحقق."
    if ci_low > 0:
        return "نطلق، لأن الأثر إيجابي بثقة ومقاييس الحماية سليمة."
    if ci_high < mde:
        return "لا نطلق، لأننا استبعدنا وجود أثر بالحجم الذي يهمنا."
    return "لا نقرر بعد. نمدد التجربة، أو نعيد تصميمها بقوة أعلى."
