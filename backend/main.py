import os
import sys
import platform
import resource
from pathlib import Path
from contextlib import asynccontextmanager
import pickle
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path so utils and models can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from state import app_state
from routers import filters, kpis, map_data, predict, forecast, network, briefing, pdf

def get_process_memory_mb() -> float:
    """Return current process peak resident memory in Megabytes."""
    usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == 'Darwin':
        # macOS reports in bytes
        return round(usage / (1024 * 1024), 2)
    else:
        # Linux reports in kilobytes
        return round(usage / 1024, 2)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load dataset and ML models once
    base_dir = str(ROOT_DIR)
    deploy_csv = os.path.join(base_dir, 'data', 'processed', 'illicit_networks_deployed.csv')
    full_csv = os.path.join(base_dir, 'data', 'processed', 'illicit_networks.csv')
    csv_path = deploy_csv if os.path.exists(deploy_csv) else full_csv

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Processed dataset not found at {csv_path}")

    print(f"Loading dataset from {csv_path}...")
    df = pd.read_csv(csv_path, low_memory=False)
    df['event_date_dt'] = pd.to_datetime(df['event_date'], errors='coerce')
    app_state.df = df
    print(f"Dataset loaded: {len(df):,} records.")

    # Load ML Model and Encoders (Leakage-Free Version)
    model_path = os.path.join(base_dir, 'models', 'incident_prediction.pkl')
    encoder_path = os.path.join(base_dir, 'models', 'feature_encoders.pkl')

    if os.path.exists(model_path):
        print(f"Loading threat model from {model_path}...")
        with open(model_path, 'rb') as f:
            app_state.model = pickle.load(f)
        print("Winning LightGBM model (leakage-free) loaded successfully.")
    else:
        print(f"Warning: Model file not found at {model_path}")

    if os.path.exists(encoder_path):
        print(f"Loading feature encoders from {encoder_path}...")
        with open(encoder_path, 'rb') as f:
            app_state.encoders = pickle.load(f)
        print("Feature encoders loaded successfully.")
    else:
        print(f"Warning: Feature encoders not found at {encoder_path}")

    # Report memory footprint at startup
    mem_mb = get_process_memory_mb()
    print(f"📊 BACKEND STARTUP MEMORY FOOTPRINT: {mem_mb:.2f} MB RAM in use after loading 150k dataset and ML models.")

    yield

    # Shutdown
    print("Shutting down SCOPE backend...")

app = FastAPI(
    title="SCOPE-Dashboard API",
    description="Strategic Crime Observation & Prediction Engine API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Is-Capped"]
)

# Render Health Check endpoint
@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "memory_usage_mb": get_process_memory_mb()
    }

# Register routers
app.include_router(filters.router)
app.include_router(kpis.router)
app.include_router(map_data.router)
app.include_router(predict.router)
app.include_router(forecast.router)
app.include_router(network.router)
app.include_router(briefing.router)
app.include_router(pdf.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
