import os
import tempfile
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
from fastapi import APIRouter, HTTPException, Query, Response
from typing import Optional
from state import app_state
from utils.ai_summary import generate_threat_narrative
from utils.pdf_generator import create_pdf_briefing

router = APIRouter(prefix="/api", tags=["pdf"])

@router.get("/pdf")
def download_pdf(
    region: Optional[str] = Query("Western Africa"),
    crime_type: Optional[str] = Query(None),
    date_start: Optional[str] = Query(None),
    date_end: Optional[str] = Query(None)
):
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")

    df = app_state.df
    filtered = df.copy()

    reg_val = None if (not region or region == "All") else region
    if reg_val:
        filtered = filtered[filtered['region'] == reg_val]

    if crime_type and crime_type != "All":
        filtered = filtered[filtered['crime_type'] == crime_type]

    date_range = None
    if date_start and date_end:
        date_range = [date_start, date_end]
        start_dt = pd.to_datetime(date_start, errors='coerce')
        end_dt = pd.to_datetime(date_end, errors='coerce')
        if pd.notna(start_dt) and pd.notna(end_dt):
            filtered = filtered[(filtered['event_date_dt'] >= start_dt) & (filtered['event_date_dt'] <= end_dt)]

    narrative = generate_threat_narrative(filtered, region=reg_val, date_range=date_range)

    total_incidents = len(filtered)
    fatalities_subset = filtered[filtered['source_dataset'] != 'ASAM']['fatalities'].dropna()
    total_fatalities = int(fatalities_subset.sum()) if not fatalities_subset.empty else 0
    primary_driver = str(filtered['crime_type'].mode()[0]) if not filtered['crime_type'].empty else 'N/A'

    kpis = {
        "total_incidents": f"{total_incidents:,}",
        "total_fatalities": f"{total_fatalities:,} (Excludes ASAM)",
        "primary_driver": primary_driver,
        "region": reg_val or "Global"
    }

    # Generate a temporary chart image for embedding in the PDF
    chart_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            chart_path = tmp_file.name

        fig, ax = plt.subplots(figsize=(8, 3.5), facecolor='#FFFFFF')
        ax.set_facecolor('#F8FAFC')
        top_crimes = filtered['crime_type'].value_counts().head(5)
        if not top_crimes.empty:
            top_crimes.plot(kind='barh', ax=ax, color='#1D4ED8')
        ax.set_title(f"Top Incident Categories ({reg_val or 'Global'})", fontsize=10, fontweight='bold', color='#0F172A')
        ax.set_xlabel("Incident Count", fontsize=9, color='#0F172A')
        ax.tick_params(colors='#0F172A')
        for spine in ax.spines.values():
            spine.set_color('#CBD5E1')
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)

        pdf_bytes = create_pdf_briefing(narrative, kpis, chart_img_path=chart_path)
    except Exception as e:
        # Fallback without chart if chart generation fails
        pdf_bytes = create_pdf_briefing(narrative, kpis, chart_img_path=None)
    finally:
        if chart_path and os.path.exists(chart_path):
            try:
                os.remove(chart_path)
            except Exception:
                pass

    safe_region_name = (reg_val or "Global").replace(" ", "_").replace("/", "_")
    filename = f"SCOPE_Briefing_{safe_region_name}.pdf"

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )

