from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from collections import Counter
from blockchain import Blockchain

app = FastAPI(title="EventChain API")
bc = Blockchain()


class TicketRequest(BaseModel):
    buyer: str
    event: str
    seat: str
    price: float


class TamperRequest(BaseModel):
    index: int
    new_buyer: str


@app.get("/")
def serve_ui():
    return FileResponse("static/index.html")


@app.get("/api/chain")
def get_chain():
    return {"chain": bc.get_chain(), "validation": bc.validate_chain()}


@app.post("/api/tickets")
def mint_ticket(req: TicketRequest):
    try:
        block = bc.issue_ticket(req.buyer, req.event, req.seat, req.price)
        return {"message": "Ticket mined & added to ledger", "block": block}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/analytics")
def analytics():
    tickets = [b["data"] for b in bc.get_chain()[1:] if b["data"].get("type") == "TICKET_MINT"]
    total_revenue = sum(t.get("price", 0) for t in tickets)
    by_event = Counter(t.get("event") for t in tickets)
    return {
        "total_tickets": len(tickets),
        "total_revenue": round(total_revenue, 2),
        "event_breakdown": dict(by_event)
    }


@app.post("/api/tamper")
def tamper(req: TamperRequest):
    try:
        bc.simulate_tamper(req.index, req.new_buyer)
        return {"message": f"Block #{req.index} altered in SQLite.", "validation": bc.validate_chain()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


app.mount("/static", StaticFiles(directory="static"), name="static")