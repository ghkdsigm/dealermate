from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP Pricing", version="0.1.0")


class MarketPriceRequest(BaseModel):
    query: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/tools/get_market_price")
def get_market_price(payload: MarketPriceRequest):
    q = payload.query.lower()
    # demo pricing band
    base = 1750
    if "bmw" in q or "320" in q:
        base = 1650
    if "쏘렌토" in payload.query:
        base = 1850
    band = {
        "p25": base - 120,
        "p50": base,
        "p75": base + 130,
        "range_3m": [base - 250, base + 250],
        "basis": "최근 3개월 유사매물/거래가 기반(데모)",
    }
    return {"ok": True, "data": {"query": payload.query, "band": band, "insight": "중앙값 기준으로 합리적 제시가를 잡고, 옵션/상태에 따라 ± 조정하세요."}}
