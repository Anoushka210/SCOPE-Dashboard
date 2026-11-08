import pandas as pd
from typing import Optional, Any

class AppState:
    df: Optional[pd.DataFrame] = None
    model: Optional[Any] = None
    encoders: Optional[dict] = None

app_state = AppState()

