from fastapi import FastAPI

app = FastAPI(title="B-Wave Fleet View", version="0.1.0")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/v1/vessels")
async def list_vessels():
    return []


@app.get("/api/v1/dashboard/overview")
async def dashboard_overview():
    return {
        "total_vessels": 0,
        "active_inspections": 0,
        "critical_defects": 0,
        "detention_risk": 0,
    }
