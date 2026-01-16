from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MCP History", version="0.1.0")


class PlateRequest(BaseModel):
    plate: str


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/tools/get_vehicle_registry_summary")
def get_vehicle_registry_summary(payload: PlateRequest):
    # demo output, replace with 원부/압류/저당 API
    owner_changes = 2 if payload.plate.endswith("3456") else 1
    return {
        "ok": True,
        "data": {
            "plate": payload.plate,
            "owner_changes": owner_changes,
            "lien": payload.plate.endswith("2222"),
            "notes": "원부 요약(데모): 실서비스에서는 원천 원부 API에서 조회합니다.",
        },
    }


@app.post("/tools/get_maintenance_history")
def get_maintenance_history(payload: PlateRequest):
    # demo output, replace with 정비이력 API
    total = 7 if payload.plate.endswith("3456") else 3
    items = [
        {"date": "2025-08-12", "type": "엔진오일", "memo": "정기 교환"},
        {"date": "2025-03-21", "type": "브레이크", "memo": "패드 교체"},
    ]
    return {
        "ok": True,
        "data": {
            "plate": payload.plate,
            "total_records": total,
            "recent": items,
            "notes": "정비 이력 요약(데모)"
        },
    }
