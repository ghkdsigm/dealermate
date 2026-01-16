from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="MCP Inventory", version="0.1.0")


# Demo dataset (replace with legacy API calls)
LISTINGS = [
    {
        "listing_id": "L001",
        "plate": "12가3456",
        "maker": "현대",
        "model": "제네시스 G330",
        "year": 2016,
        "km": 120000,
        "fuel": "가솔린",
        "gear": "자동",
        "color": "검정",
        "price": 1780,
        "branch_id": "BR01",
        "accident": False,
        "options": ["선루프", "통풍시트"],
    },
    {
        "listing_id": "L002",
        "plate": "34나7890",
        "maker": "기아",
        "model": "쏘렌토",
        "year": 2018,
        "km": 98000,
        "fuel": "디젤",
        "gear": "자동",
        "color": "흰색",
        "price": 1840,
        "branch_id": "BR01",
        "accident": False,
        "options": ["4WD", "네비"],
    },
    {
        "listing_id": "L003",
        "plate": "11다2222",
        "maker": "BMW",
        "model": "320d",
        "year": 2017,
        "km": 110000,
        "fuel": "디젤",
        "gear": "자동",
        "color": "회색",
        "price": 1690,
        "branch_id": "BR01",
        "accident": True,
        "options": ["스마트키"],
    },
    {
        "listing_id": "L004",
        "plate": "88라7777",
        "maker": "현대",
        "model": "투싼",
        "year": 2019,
        "km": 65000,
        "fuel": "가솔린",
        "gear": "자동",
        "color": "파랑",
        "price": 1720,
        "branch_id": "BR02",
        "accident": False,
        "options": ["ADAS"],
    },
]


class GetCarByPlateRequest(BaseModel):
    plate: str
    branch_id: str | None = None
    dealer_employee_id: str | None = None


class SearchListingsRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=10)
    branch_id: str | None = None
    dealer_employee_id: str | None = None


class CompareListingsRequest(BaseModel):
    query: str
    top_k: int = Field(default=3, ge=1, le=5)


class MonthlySalesStatsRequest(BaseModel):
    branch_id: str
    range_months: int = Field(default=6, ge=1, le=24)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/tools/get_car_by_plate")
def get_car_by_plate(payload: GetCarByPlateRequest):
    for l in LISTINGS:
        if l["plate"] == payload.plate and (payload.branch_id is None or l["branch_id"] == payload.branch_id):
            return {"ok": True, "data": l}
    return {"ok": True, "data": {"plate": payload.plate, "model": None, "year": None, "km": None}}


@app.post("/tools/search_listings")
def search_listings(payload: SearchListingsRequest):
    q = payload.query
    # demo heuristic: if contains '무사고' filter out accident True; if 'suv' prefer sorento/tucson
    must_no_acc = ("무사고" in q) or ("사고없" in q)
    prefer_suv = ("suv" in q.lower()) or ("suv" in q.upper()) or ("suv" in q) or ("쏘렌토" in q) or ("투싼" in q) or ("suv" in q.lower())

    cand = []
    for l in LISTINGS:
        if payload.branch_id and l["branch_id"] != payload.branch_id:
            continue
        if must_no_acc and l["accident"]:
            continue
        score = 0
        if prefer_suv and any(k in l["model"] for k in ["쏘렌토", "투싼", "싼타페", "스포티지"]):
            score += 2
        if "제네시스" in q and "제네시스" in l["model"]:
            score += 2
        if "디젤" in q and l["fuel"] == "디젤":
            score += 1
        if "가솔린" in q and l["fuel"] == "가솔린":
            score += 1
        cand.append((score, l))

    cand.sort(key=lambda x: (-x[0], x[1]["price"]))
    top = [x[1] for x in cand[: payload.top_k]]

    # "정제 3개" 컨셉
    return {
        "ok": True,
        "data": {
            "items": top,
            "explain": "검색 결과를 조건/선호에 맞춰 3개로 정제했습니다.",
            "filters": {"no_accident": must_no_acc, "prefer_suv": prefer_suv},
        },
    }


@app.post("/tools/compare_listings")
def compare_listings(payload: CompareListingsRequest):
    # naive: reuse search and build a compare sheet
    items = LISTINGS[: payload.top_k]
    rows = []
    for l in items:
        rows.append(
            {
                "listing_id": l["listing_id"],
                "model": l["model"],
                "year": l["year"],
                "km": l["km"],
                "accident": l["accident"],
                "price": l["price"],
                "highlight": "무사고" if not l["accident"] else "사고이력",
            }
        )
    return {"ok": True, "data": {"rows": rows, "notes": "핵심 항목 기준 비교표입니다."}}


@app.post("/tools/get_monthly_sales_stats")
def get_monthly_sales_stats(payload: MonthlySalesStatsRequest):
    # demo numbers
    today = date.today()
    series = []
    for i in range(payload.range_months):
        m = ((today.month - i - 1) % 12) + 1
        y = today.year - ((today.month - i - 1) // 12 + (1 if today.month - i <= 0 else 0))
        series.append({"yyyy_mm": f"{y:04d}-{m:02d}", "sold": 12 + (i % 5), "avg_margin": 85 + (i % 7)})
    return {"ok": True, "data": {"branch_id": payload.branch_id, "series": list(reversed(series))}}
