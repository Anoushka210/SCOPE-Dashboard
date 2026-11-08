import networkx as nx
import pandas as pd
import numpy as np
import plotly.graph_objects as go

def build_actor_network(df, top_n_actors=40, region_filter=None, crime_filter=None):
    """
    Build a NetworkX graph of genuine actor groups (from GTD & Cartel datasets) 
    co-occurring with regions and crime types.
    CRITICAL: Excludes ACLED disorder types (which are conflict classifications, not distinct groups).
    """
    filtered = df.copy()
    if region_filter and region_filter != 'All':
        filtered = filtered[filtered['region'] == region_filter]
    if crime_filter and crime_filter != 'All':
        filtered = filtered[filtered['crime_type'] == crime_filter]

    # Filter out ACLED disorder types and generic unknowns
    generic_non_actors = {
        'Unknown', 'Unknown Group', 'Unspecified', 
        'Armed Group/Civilian Disorder', 'Demonstrations', 
        'Political violence', 'Political violence; Demonstrations',
        'Civilian Disorder', 'Other'
    }

    actor_mask = (
        filtered['source_dataset'].isin(['GTD', 'Cartel']) &
        filtered['actor_group'].notna() &
        ~filtered['actor_group'].isin(generic_non_actors)
    )
    filtered = filtered[actor_mask]
    
    if filtered.empty:
        # Fallback to any non-generic groups if filtered region has no GTD records
        fallback_mask = (
            filtered['actor_group'].notna() &
            ~filtered['actor_group'].isin(generic_non_actors)
        )
        filtered = df[fallback_mask]
        if region_filter and region_filter != 'All':
            filtered = filtered[filtered['region'] == region_filter]

    top_actors = filtered['actor_group'].value_counts().head(top_n_actors).index.tolist()
    filtered = filtered[filtered['actor_group'].isin(top_actors)]
    
    G = nx.Graph()
    
    for _, row in filtered.iterrows():
        actor = str(row['actor_group'])
        crime = str(row['crime_type'])
        region = str(row['region'])
        
        G.add_node(actor, node_type='Actor', label=actor)
        G.add_node(crime, node_type='Crime Type', label=crime)
        G.add_node(region, node_type='Region', label=region)
        
        if G.has_edge(actor, crime):
            G[actor][crime]['weight'] += 1
        else:
            G.add_edge(actor, crime, weight=1)
            
        if G.has_edge(actor, region):
            G[actor][region]['weight'] += 1
        else:
            G.add_edge(actor, region, weight=1)
            
    deg_centrality = nx.degree_centrality(G) if len(G) > 0 else {}
    bet_centrality = nx.betweenness_centrality(G) if len(G) > 0 else {}
    
    for n in G.nodes():
        G.nodes[n]['degree_centrality'] = round(deg_centrality.get(n, 0.0), 4)
        G.nodes[n]['betweenness_centrality'] = round(bet_centrality.get(n, 0.0), 4)
        
    return G

def get_network_plotly_figure(G):
    """
    Generate an interactive Plotly figure from NetworkX graph.
    """
    if len(G.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title="No network data available for selected filters.", template="plotly_white")
        return fig
        
    pos = nx.spring_layout(G, k=0.5, seed=42)
    
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.8, color='rgba(100, 116, 139, 0.4)'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    color_map = {
        'Actor': '#DC2626',      # Deep red
        'Crime Type': '#2563EB',  # Royal blue
        'Region': '#059669'      # Emerald green
    }
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        ntype = G.nodes[node].get('node_type', 'Entity')
        deg = G.nodes[node].get('degree_centrality', 0)
        bet = G.nodes[node].get('betweenness_centrality', 0)
        
        hover = f"<b>{node}</b><br>Type: {ntype}<br>Degree Centrality: {deg}<br>Betweenness Centrality: {bet}"
        node_text.append(hover)
        node_color.append(color_map.get(ntype, '#D97706'))
        node_size.append(12 + deg * 40)
        
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[node if G.nodes[node].get('node_type') != 'Actor' else '' for node in G.nodes()],
        textfont=dict(color='#0F172A', size=11),
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_color,
            size=node_size,
            line_width=1.5,
            line_color='#FFFFFF'
        )
    )
    
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    template='plotly_white',
                    margin=dict(b=20, l=5, r=5, t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                ))
    return fig

def get_centrality_dataframe(G):
    """Return top nodes sorted by degree and betweenness centrality."""
    data = []
    for n in G.nodes():
        data.append({
            'Node': n,
            'Type': G.nodes[n].get('node_type', 'Entity'),
            'Degree Centrality': G.nodes[n].get('degree_centrality', 0),
            'Betweenness Centrality': G.nodes[n].get('betweenness_centrality', 0)
        })
    df_cent = pd.DataFrame(data)
    if not df_cent.empty:
        df_cent = df_cent.sort_values(by='Degree Centrality', ascending=False)
    return df_cent
