import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.artifact import Artifact, ArtifactType
from app.models.audit_log import AuditLog
from app.models.deal import Deal
from app.models.user import User
from app.services.intent_router import classify
from app.services.mcp_client import McpClient


OUT_OF_SCOPE_MESSAGE = (
    "딜러메이트는 차량 상담·추천·비교·리스크·가격/협상·팔로업 등 업무 질문만 도와드립니다.\n"
    "차량번호 또는 고객 조건(예산/차종/금기사항)을 입력해 주세요."
)


class AssistantService:
    def __init__(self) -> None:
        self.mcp = McpClient()

    async def assist(
        self,
        db: Session,
        user: User,
        message: str,
        deal_id: int | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        intent = classify(message)
        used_tools: list[str] = []

        if intent == "out_of_scope":
            return {
                "intent": intent,
                "used_tools": used_tools,
                "result": {"type": "out_of_scope", "text": OUT_OF_SCOPE_MESSAGE},
            }

        deal = None
        if deal_id is not None:
            deal = db.query(Deal).filter(Deal.id == deal_id, Deal.owner_user_id == user.id).first()

        # If no deal, create an anonymous customer token deal for continuity
        if deal is None:
            deal = Deal(owner_user_id=user.id, customer_token=f"CST-{user.id}-{abs(hash(message))%99999}")
            db.add(deal)
            db.commit()
            db.refresh(deal)

        # Tooling decisions (MVP-grade)
        payload: dict[str, Any] = {"deal_id": deal.id, "customer_token": deal.customer_token}

        if intent == "recommend":
            used_tools.append("inventory.search_listings")
            if filters:
                used_tools[-1] = "inventory.search_listings_filtered"
                tool_res = await self.mcp.call_tool(
                    "inventory.search_listings_filtered",
                    {
                        "query": message,
                        "top_k": 3,
                        "branch_id": user.branch_id,
                        "dealer_employee_id": user.employee_id,
                        "filters": filters,
                    },
                )
            else:
                tool_res = await self.mcp.call_tool(
                    "inventory.search_listings",
                    {"query": message, "top_k": 3, "branch_id": user.branch_id, "dealer_employee_id": user.employee_id},
                )
            payload["recommendations"] = tool_res.get("data")
            payload["summary"] = "조건에 맞는 매물을 3개로 정제해 추천했습니다."

        elif intent == "risk":
            used_tools += ["inventory.get_car_by_plate", "history.get_vehicle_registry_summary", "history.get_maintenance_history"]
            # naive plate extraction
            plate = self._extract_plate(message) or "12가3456"
            car = await self.mcp.call_tool(
                "inventory.get_car_by_plate",
                {"plate": plate, "branch_id": user.branch_id, "dealer_employee_id": user.employee_id},
            )
            car_data = car.get("data") or {}
            registry = await self.mcp.call_tool("history.get_vehicle_registry_summary", {"plate": plate})
            maint = await self.mcp.call_tool("history.get_maintenance_history", {"plate": plate})

            payload["car"] = car_data
            payload["registry"] = registry.get("data")
            payload["maintenance"] = maint.get("data")
            payload["briefing"] = self._make_risk_briefing(car_data, registry.get("data"), maint.get("data"))

        elif intent == "pricing":
            used_tools.append("pricing.get_market_price")
            tool_res = await self.mcp.call_tool("pricing.get_market_price", {"query": message})
            payload["pricing"] = tool_res.get("data")
            payload["summary"] = "최근 3개월 시세 범위와 현재 포지션을 요약했습니다."

        elif intent == "compare":
            used_tools.append("inventory.compare_listings")
            tool_res = await self.mcp.call_tool("inventory.compare_listings", {"query": message, "top_k": 3})
            payload["compare"] = tool_res.get("data")
            payload["summary"] = "핵심 차이점과 비교표를 생성했습니다."

        elif intent == "followup":
            payload["followup"] = {
                "kakao": "안녕하세요! 문의주신 차량 관련해서 추가로 궁금하신 점 있으실까요? 원하시면 조건에 맞는 추천 3대도 바로 보내드릴게요.",
                "sms": "안녕하세요. 차량 상담 관련해 추가 문의 있으시면 편하게 답장 주세요. 조건 맞는 매물 3대 추천도 가능합니다.",
            }
            payload["summary"] = "팔로업 메시지 템플릿을 생성했습니다."

        elif intent == "negotiation":
            payload["negotiation"] = {
                "guardrail": "시세 하단을 방어가로 두고, 감가 사유(주행/옵션/사고/재고기간)를 근거로 단계적 양보폭을 설정하세요.",
                "script": "가격은 시세 기준으로 이미 합리적으로 맞춰드린 상태입니다. 대신 고객님 상황에 맞춰 추가 혜택(정비/보증/탁송) 쪽으로 조정해드릴 수 있어요.",
            }
            payload["summary"] = "협상 가이드와 멘트 초안을 제안했습니다."

        elif intent == "kpi":
            used_tools.append("boss.get_monthly_sales_stats")
            tool_res = await self.mcp.call_tool("boss.get_monthly_sales_stats", {"branch_id": user.branch_id, "range_months": 6})
            payload["kpi"] = tool_res.get("data")
            payload["summary"] = "최근 판매 현황과 KPI 요약을 가져왔습니다."

        # Persist artifact (latest response snapshot)
        artifact = Artifact(
            deal_id=deal.id,
            owner_user_id=user.id,
            type=ArtifactType.briefing,
            title=f"{intent} response",
            content=json.dumps(payload, ensure_ascii=False),
        )
        db.add(artifact)

        # audit
        audit = AuditLog(
            actor_user_id=user.id,
            action="assist",
            resource="assistant",
            request_json=json.dumps({"message": message, "intent": intent, "used_tools": used_tools}, ensure_ascii=False),
            response_json=json.dumps(payload, ensure_ascii=False),
        )
        db.add(audit)
        db.commit()

        return {"intent": intent, "used_tools": used_tools, "result": payload}

    def _extract_plate(self, message: str) -> str | None:
        # very loose Korean plate extractor (demo)
        import re

        m = re.search(r"\b\d{2,3}[가-힣]\d{4}\b", message)
        return m.group(0) if m else None

    def _make_risk_briefing(self, car: dict[str, Any], registry: dict[str, Any] | None, maintenance: dict[str, Any] | None) -> dict[str, Any]:
        reg = registry or {}
        maint = maintenance or {}
        points = []

        if reg.get("owner_changes") is not None:
            points.append(f"소유자 변경: {reg['owner_changes']}회")
        if reg.get("lien"):
            points.append("저당/압류 이력: 있음 (추가 확인 필요)")
        if maint.get("total_records") is not None:
            points.append(f"정비 이력: {maint['total_records']}건")

        return {
            "summary": " / ".join(points) or "추가 조회 데이터가 제한적입니다. 원부/정비/성능을 확인해 고지 포인트를 정리하세요.",
            "disclosure_script": "확인된 이력 기준으로 투명하게 안내드리고, 성능기록부/정비이력 기준으로 상태를 함께 확인해드리겠습니다.",
            "next_actions": ["성능기록부 확인", "정비이력 주요 항목 체크", "시세 대비 가격 포지션 확인"],
            "car_snapshot": {
                "plate": car.get("plate"),
                "model": car.get("model"),
                "year": car.get("year"),
                "km": car.get("km"),
            },
        }
