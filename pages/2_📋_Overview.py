"""
Page Overview - Statistiques Descriptives
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_data, calculate_descriptive_stats

st.set_page_config(page_title="Overview - BRVM Analytics", page_icon="📋", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .stat-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #8B7355;
        text-align: center;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4A3728;
    }
    
    .stat-label {
        color: #8B7355;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("📋 Overview - Statistiques Descriptives")

@st.cache_data
def get_data():
    return load_data()

try:
    data = get_data()
    fiche_actions = data['fiche_actions']
    historique_actions = data['historique_actions']
    indices_info = data['indices_info']
    historique_indices = data['historique_indices']
    
    st.markdown("---")
    
    # Métriques globales
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Actions suivies</div>
        </div>
        """.format(len(historique_actions.columns)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Indices suivis</div>
        </div>
        """.format(len(historique_indices.columns)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">Jours de données</div>
        </div>
        """.format(len(historique_actions)), unsafe_allow_html=True)
    
    with col4:
        first_date = historique_actions.index[0].strftime('%d/%m/%Y')
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="font-size: 1.2rem;">{first_date}</div>
            <div class="stat-label">Première date</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        last_date = historique_actions.index[-1].strftime('%d/%m/%Y')
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="font-size: 1.2rem;">{last_date}</div>
            <div class="stat-label">Dernière date</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs pour Actions et Indices
    tab_actions, tab_indices = st.tabs(["📊 Actions", "📈 Indices"])
    
    with tab_actions:
        st.subheader("Statistiques des Actions")
        
        # Répartition par secteur
        if 'Sector' in fiche_actions.columns:
            col_chart, col_table = st.columns([1, 1])
            
            with col_chart:
                sector_counts = fiche_actions['Sector'].value_counts()
                fig_sector = px.pie(
                    values=sector_counts.values,
                    names=sector_counts.index,
                    title="Répartition par Secteur",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig_sector.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#4A3728')
                )
                st.plotly_chart(fig_sector, use_container_width=True)
            
            with col_table:
                st.markdown("##### Liste des secteurs")
                sector_df = pd.DataFrame({
                    'Secteur': sector_counts.index,
                    'Nombre d\'actions': sector_counts.values
                })
                st.dataframe(sector_df, use_container_width=True, hide_index=True)
        
        # Statistiques descriptives
        st.markdown("##### Statistiques descriptives par action")
        stats_actions = calculate_descriptive_stats(historique_actions)
        
        # Ajouter les noms
        symbol_to_name = dict(zip(fiche_actions['Symbol'], fiche_actions['Name']))
        stats_actions['Nom'] = stats_actions.index.map(lambda x: symbol_to_name.get(x, x))
        
        # Réorganiser les colonnes
        cols = ['Nom'] + [c for c in stats_actions.columns if c != 'Nom']
        stats_actions = stats_actions[cols]
        
        st.dataframe(
            stats_actions.style.format({
                'Dernier Prix': '{:.2f}',
                'Prix Min': '{:.2f}',
                'Prix Max': '{:.2f}',
                'Prix Moyen': '{:.2f}',
                'Volatilité (annualisée)': '{:.2f}%',
                'Rendement Total (%)': '{:.2f}%',
                'Nb Observations': '{:.0f}'
            }),
            use_container_width=True,
            height=500
        )
        
        # Distribution des volatilités
        st.markdown("##### Distribution des Volatilités Annualisées")
        fig_vol = px.histogram(
            stats_actions,
            x='Volatilité (annualisée)',
            nbins=30,
            title="Distribution des volatilités des actions",
            color_discrete_sequence=['#8B7355']
        )
        fig_vol.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Volatilité (%)",
            yaxis_title="Nombre d'actions",
            font=dict(color='#4A3728')
        )
        st.plotly_chart(fig_vol, use_container_width=True)
    
    with tab_indices:
        st.subheader("Statistiques des Indices")
        
        # Informations sur les indices
        col_info, col_stats = st.columns([1, 1])
        
        with col_info:
            st.markdown("##### Informations sur les indices")
            st.dataframe(indices_info, use_container_width=True, hide_index=True)
        
        with col_stats:
            st.markdown("##### Statistiques descriptives")
            stats_indices = calculate_descriptive_stats(historique_indices)
            
            # Ajouter les noms
            indices_name_map = dict(zip(indices_info['Symbol'], indices_info['Name']))
            stats_indices['Nom'] = stats_indices.index.map(lambda x: indices_name_map.get(x, x))
            
            cols = ['Nom'] + [c for c in stats_indices.columns if c != 'Nom']
            stats_indices = stats_indices[cols]
            
            st.dataframe(
                stats_indices.style.format({
                    'Dernier Prix': '{:.2f}',
                    'Prix Min': '{:.2f}',
                    'Prix Max': '{:.2f}',
                    'Prix Moyen': '{:.2f}',
                    'Volatilité (annualisée)': '{:.2f}%',
                    'Rendement Total (%)': '{:.2f}%',
                    'Nb Observations': '{:.0f}'
                }),
                use_container_width=True
            )
        
        # Graphique d'évolution normalisée des indices
        st.markdown("##### Évolution normalisée des indices (base 100)")
        normalized_indices = (historique_indices / historique_indices.iloc[0]) * 100
        
        fig_indices = go.Figure()
        colors = px.colors.qualitative.Set2
        
        for i, col in enumerate(normalized_indices.columns):
            fig_indices.add_trace(go.Scatter(
                x=normalized_indices.index,
                y=normalized_indices[col],
                mode='lines',
                name=indices_name_map.get(col, col),
                line=dict(color=colors[i % len(colors)])
            ))
        
        fig_indices.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_title="Date",
            yaxis_title="Valeur (base 100)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font=dict(color='#4A3728'),
            hovermode='x unified'
        )
        fig_indices.update_xaxes(gridcolor='#E8DDD4')
        fig_indices.update_yaxes(gridcolor='#E8DDD4')
        
        st.plotly_chart(fig_indices, use_container_width=True)

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")
    st.info("Vérifiez que le fichier 'historical stock data.xlsx' est présent dans le dossier de l'application.")
