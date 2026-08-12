import streamlit as st
from config import setup_page_config
from utils.ui_components import load_illicit_data, render_global_sidebar_filters
from utils.network_graph import build_actor_network, get_network_plotly_figure, get_centrality_dataframe

setup_page_config("Network Analysis")

st.title("🕸️ Actor & Regional Co-Occurrence Network Analysis")

df = load_illicit_data()
filtered_df = render_global_sidebar_filters(df)

st.sidebar.markdown("---")
st.sidebar.subheader("🕸️ Network Parameters")
top_n = st.sidebar.slider("Top N Actors to Graph", min_value=10, max_value=80, value=35)

selected_region = st.session_state.get('selected_region', 'All')
selected_crime = st.session_state.get('selected_crime_type', 'All')

with st.spinner("Constructing Graph Network & Centrality Metrics..."):
    G = build_actor_network(
        filtered_df, 
        top_n_actors=top_n, 
        region_filter=selected_region if selected_region != 'All' else None,
        crime_filter=selected_crime if selected_crime != 'All' else None
    )
    fig_net = get_network_plotly_figure(G)
    df_cent = get_centrality_dataframe(G)

col_graph, col_stats = st.columns([2, 1])

with col_graph:
    st.subheader("Interactive Graph Network")
    st.plotly_chart(fig_net, width='stretch')
    
with col_stats:
    st.subheader("Centrality Metrics Leaderboard")
    st.write("Nodes sized and ranked by Degree & Betweenness Centrality:")
    if not df_cent.empty:
        st.dataframe(
            df_cent,
            column_config={
                "Degree Centrality": st.column_config.NumberColumn(format="%.4f"),
                "Betweenness Centrality": st.column_config.NumberColumn(format="%.4f")
            },
            height=500,
            width='stretch'
        )
    else:
        st.info("No nodes in network graph.")
