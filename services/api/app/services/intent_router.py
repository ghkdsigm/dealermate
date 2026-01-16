import re

INTENTS = [
    "recommend",
    "compare",
    "risk",
    "pricing",
    "negotiation",
    "followup",
    "kpi",
    "out_of_scope",
]


_OUT_OF_SCOPE_PAT = re.compile(r"(배고파|날씨|주식|연애|농담|게임|점심|저녁)")


def classify(message: str) -> str:
    m = message.strip().lower()

    if _OUT_OF_SCOPE_PAT.search(message):
        return "out_of_scope"

    # intent keywords (Korean + English-ish)
    if re.search(r"(추천|매물|조건|suv|sedan|top\s*3|3대)", m):
        return "recommend"
    if re.search(r"(비교|vs|차이|표)", m):
        return "compare"
    if re.search(r"(리스크|사고|성능|정비|원부|침수|교환)", m):
        return "risk"
    if re.search(r"(시세|가격|포지션|얼마|market|price)", m):
        return "pricing"
    if re.search(r"(협상|할인|깎|양보|방어가|제시가)", m):
        return "negotiation"
    if re.search(r"(팔로업|카톡|문자|메시지|follow)", m):
        return "followup"
    if re.search(r"(판매현황|kpi|장기재고|에이징|지표)", m):
        return "kpi"

    # default: recommend-like
    return "recommend"
