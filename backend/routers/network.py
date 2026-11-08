from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any
from backend.state import app_state
from utils.network_graph import build_actor_network

router = APIRouter(prefix="/api", tags=["network"])

@router.get("/network")
def get_network(
    region: Optional[str] = Query(None),
    min_connections: Optional[int] = Query(2)
):
    if app_state.df is None:
        raise HTTPException(status_code=503, detail="Dataset not initialized")

    df = app_state.df
    reg_filter = None if (not region or region == "All") else region
    min_conn = min_connections if min_connections is not None else 2

    try:
        G = build_actor_network(df, top_n_actors=40, region_filter=reg_filter)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Network calculation failed: {str(e)}")

    edges = []
    active_nodes = set()
    for u, v, data in G.edges(data=True):
        weight = int(data.get('weight', 1))
        if weight >= min_conn:
            edges.append({
                "source": str(u),
                "target": str(v),
                "weight": weight
            })
            active_nodes.add(str(u))
            active_nodes.add(str(v))

    # If min_conn was too aggressive and filtered out all edges, fallback to min_conn=1
    if not edges and len(G.edges) > 0:
        for u, v, data in G.edges(data=True):
            weight = int(data.get('weight', 1))
            edges.append({
                "source": str(u),
                "target": str(v),
                "weight": weight
            })
            active_nodes.add(str(u))
            active_nodes.add(str(v))

    nodes = []
    # Include all nodes if graph is small, or active connected nodes
    node_set = active_nodes if active_nodes else set(G.nodes())
    for n in node_set:
        data = G.nodes[n]
        nodes.append({
            "id": str(n),
            "label": str(data.get('label', n)),
            "centrality": float(data.get('betweenness_centrality', 0.0)),
            "crime_type": str(data.get('node_type', 'Entity')),
            "node_type": str(data.get('node_type', 'Entity')),
            "degree_centrality": float(data.get('degree_centrality', 0.0))
        })

    return {
        "nodes": nodes,
        "edges": edges
    }

