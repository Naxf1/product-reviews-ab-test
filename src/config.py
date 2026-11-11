"""إعدادات التجربة: مصدر واحد لكل القيم. لا تغيّر القيم بعد تثبيتها، لأن أي تغيير يغير كل النتائج.

Owner: Naif. Frozen values — copied from the notebook (Section 3).
"""

CONFIG = {
    "project": "اختبار عرض التقييمات أعلى صفحة المنتج",
    # ---- التصميم (معروف قبل التجربة) ----
    "baseline_conversion": 0.10,   # نسبة الطلب الحالية
    "mde_abs": 0.010,              # أصغر أثر يغير القرار (نقطة مئوية واحدة)
    "alpha": 0.05,
    "power": 0.80,
    "daily_new_users": 5_000,
    "treatment_share": 0.5,
    # ---- المحاكاة ("الحقيقة" المخفية، للتدريب فقط) ----
    "true_lift_abs": 0.008,
    "order_value_mean": 120,
    "order_value_sd": 50,
    "order_value_effect": 0,
    "margin": 0.25,
    "extra_cost_per_order_b": 0,
    "cancel_rate": 0.05, "cancel_effect": 0.000,
    "support_rate": 0.03, "support_effect": 0.000,
    "activity_strength": 0.8,
    "novelty_boost": 0.0,
    "srm_bug_share": 0.0,
    "seed": 2026,
}

# عدد المستخدمين في السنة الذين يتأثرون بالقرار (لتقدير الأثر المالي في التقرير)
ANNUAL_USERS = 2_000_000
