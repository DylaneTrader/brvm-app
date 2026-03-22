"""
Page Performances - Performances Calendaires et Glissantes
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_data, 
    calculate_returns_for_period, 
    calculate_calendar_performance,
    calculate_cumulative_returns
)

st.set_page_config(page_title="Performances - BRVM Analytics", page_icon="📈", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .perf-positive { color: #10B981; font-weight: bold; }
    .perf-negative { color: #EF4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Performances - Calendaires & Glissantes")

@st.cache_data
def get_data():
    return load_data()

def style_performance(val):
    """Style pour les cellules de performance"""
    if pd.isna(val):
        return ''
    color = '#10B981' if val >= 0 else '#EF4444'
    return f'color: {color}; font-weight: bold'

try:
    data = get_data()
    fiche_actions = data['fiche_actions']
    historique_actions = data['historique_actions']
    indices_info = data['indices_info']
    historique_indices = data['historique_indices']
    
    # Mappings
    symbol_to_name = dict(zip(fiche_actions['Symbol'], fiche_actions['Name']))
    symbol_to_sector = dict(zip(fiche_actions['Symbol'], fiche_actions['Sector']))
    indices_name_map = dict(zip(indices_info['Symbol'], indices_info['Name']))
    
    st.markdown("---")
    
    # Tabs pour Actions et Indices
    tab_actions, tab_indices = st.tabs(["📊 Actions", "📈 Indices"])
    
    # ==================== ONGLET ACTIONS ====================
    with tab_actions:
        st.subheader("Performances des Actions")
        
        # Filtres
        col_filter1, col_filter2 = st.columns([1, 2])
        
        with col_filter1:
            sectors = ['Tous les secteurs'] + sorted(fiche_actions['Sector'].dropna().unique().tolist())
            selected_sector = st.selectbox("🏭 Filtrer par secteur", sectors, key='sector_actions')
        
        # Filtrer les symboles par secteur
        if selected_sector != 'Tous les secteurs':
            filtered_symbols = fiche_actions[fiche_actions['Sector'] == selected_sector]['Symbol'].tolist()
            filtered_actions = historique_actions[[c for c in historique_actions.columns if c in filtered_symbols]]
        else:
            filtered_actions = historique_actions
        
        # Sous-tabs pour types de performance
        perf_tab1, perf_tab2, perf_tab3 = st.tabs(["📅 Performances Calendaires", "🔄 Performances Glissantes", "📊 Graphique Comparatif"])
        
        with perf_tab1:
            st.markdown("##### Performances Calendaires")
            st.markdown("*Performances depuis le début de chaque période calendaire*")
            
            # Calculer les performances calendaires
            calendar_perfs = {}
            for perf_type in ['WTD', 'MTD', 'QTD', 'STD', 'YTD']:
                calendar_perfs[perf_type] = calculate_calendar_performance(filtered_actions, perf_type)
            
            # Créer le DataFrame
            perf_df = pd.DataFrame(calendar_perfs)
            perf_df['Nom'] = perf_df.index.map(lambda x: symbol_to_name.get(x, x))
            perf_df['Secteur'] = perf_df.index.map(lambda x: symbol_to_sector.get(x, 'N/A'))
            
            # Réorganiser
            cols = ['Nom', 'Secteur', 'WTD', 'MTD', 'QTD', 'STD', 'YTD']
            perf_df = perf_df[[c for c in cols if c in perf_df.columns]]
            
            # Afficher
            st.dataframe(
                perf_df.style.applymap(
                    style_performance, 
                    subset=['WTD', 'MTD', 'QTD', 'STD', 'YTD']
                ).format({
                    'WTD': '{:.2f}%',
                    'MTD': '{:.2f}%',
                    'QTD': '{:.2f}%',
                    'STD': '{:.2f}%',
                    'YTD': '{:.2f}%'
                }),
                use_container_width=True,
                height=500
            )
        
        with perf_tab2:
            st.markdown("##### Performances Glissantes")
            st.markdown("*Performances sur les périodes glissantes*")
            
            # Calculer les performances glissantes
            rolling_perfs = {}
            periods_map = {'1W': '1 Sem', '1M': '1 Mois', '3M': '3 Mois', '6M': '6 Mois', '1Y': '1 An', '3Y': '3 Ans'}
            
            for period, label in periods_map.items():
                rolling_perfs[label] = calculate_returns_for_period(filtered_actions, period)
            
            # Créer le DataFrame
            rolling_df = pd.DataFrame(rolling_perfs)
            rolling_df['Nom'] = rolling_df.index.map(lambda x: symbol_to_name.get(x, x))
            rolling_df['Secteur'] = rolling_df.index.map(lambda x: symbol_to_sector.get(x, 'N/A'))
            
            # Réorganiser
            cols = ['Nom', 'Secteur'] + list(periods_map.values())
            rolling_df = rolling_df[[c for c in cols if c in rolling_df.columns]]
            
            # Afficher
            st.dataframe(
                rolling_df.style.applymap(
                    style_performance, 
                    subset=list(periods_map.values())
                ).format({col: '{:.2f}%' for col in periods_map.values()}),
                use_container_width=True,
                height=500
            )
        
        with perf_tab3:
            st.markdown("##### Graphique Comparatif d'Évolution")
            
            col_select, col_period = st.columns([2, 1])
            
            with col_select:
                # Sélection des actions
                available_actions = sorted(filtered_actions.columns.tolist())
                selected_actions = st.multiselect(
                    "📊 Sélectionnez les actions à comparer",
                    options=available_actions,
                    default=available_actions[:3] if len(available_actions) >= 3 else available_actions,
                    max_selections=10,
                    key='select_actions_compare'
                )
                
                # Option d'ajouter un indice
                add_index = st.checkbox("Ajouter un indice de référence", value=False, key='add_index_actions')
                if add_index:
                    selected_index = st.selectbox(
                        "Sélectionnez l'indice",
                        options=historique_indices.columns.tolist(),
                        format_func=lambda x: indices_name_map.get(x, x),
                        key='index_for_actions'
                    )
            
            with col_period:
                period_options = {
                    '1M': '1 Mois',
                    '3M': '3 Mois',
                    '6M': '6 Mois',
                    '1Y': '1 An',
                    '3Y': '3 Ans',
                    'MAX': 'Maximum'
                }
                selected_chart_period = st.selectbox(
                    "📅 Période du graphique",
                    options=list(period_options.keys()),
                    format_func=lambda x: period_options[x],
                    index=3,
                    key='chart_period_actions'
                )
            
            if selected_actions:
                # Déterminer la date de début
                if selected_chart_period == 'MAX':
                    start_date = None
                else:
                    days_map = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365, '3Y': 1095}
                    start_date = historique_actions.index[-1] - timedelta(days=days_map[selected_chart_period])
                
                # Préparer les données
                chart_data = filtered_actions[selected_actions].copy()
                
                if add_index and 'selected_index' in dir():
                    chart_data[f"{indices_name_map.get(selected_index, selected_index)} (Indice)"] = historique_indices[selected_index]
                
                # Calculer les rendements cumulés
                cumulative = calculate_cumulative_returns(chart_data, start_date)
                
                # Créer le graphique
                fig = go.Figure()
                colors = px.colors.qualitative.Set2
                
                for i, col in enumerate(cumulative.columns):
                    display_name = symbol_to_name.get(col.replace(' (Indice)', ''), col) if '(Indice)' not in col else col
                    fig.add_trace(go.Scatter(
                        x=cumulative.index,
                        y=cumulative[col],
                        mode='lines',
                        name=display_name,
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))
                
                # Ligne de référence à 100
                fig.add_hline(y=100, line_dash="dash", line_color="#8B7355", opacity=0.5)
                
                fig.update_layout(
                    title=f"Évolution Cumulée (base 100) - {period_options[selected_chart_period]}",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Date",
                    yaxis_title="Valeur (base 100)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    font=dict(color='#4A3728'),
                    hovermode='x unified'
                )
                fig.update_xaxes(gridcolor='#E8DDD4')
                fig.update_yaxes(gridcolor='#E8DDD4')
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sélectionnez au moins une action pour afficher le graphique.")
    
    # ==================== ONGLET INDICES ====================
    with tab_indices:
        st.subheader("Performances des Indices")
        
        # Sous-tabs pour types de performance
        idx_perf_tab1, idx_perf_tab2, idx_perf_tab3 = st.tabs(["📅 Performances Calendaires", "🔄 Performances Glissantes", "📊 Graphique Comparatif"])
        
        with idx_perf_tab1:
            st.markdown("##### Performances Calendaires des Indices")
            
            # Calculer les performances calendaires
            idx_calendar_perfs = {}
            for perf_type in ['WTD', 'MTD', 'QTD', 'STD', 'YTD']:
                idx_calendar_perfs[perf_type] = calculate_calendar_performance(historique_indices, perf_type)
            
            # Créer le DataFrame
            idx_perf_df = pd.DataFrame(idx_calendar_perfs)
            idx_perf_df['Nom'] = idx_perf_df.index.map(lambda x: indices_name_map.get(x, x))
            
            # Réorganiser
            cols = ['Nom', 'WTD', 'MTD', 'QTD', 'STD', 'YTD']
            idx_perf_df = idx_perf_df[[c for c in cols if c in idx_perf_df.columns]]
            
            st.dataframe(
                idx_perf_df.style.applymap(
                    style_performance, 
                    subset=['WTD', 'MTD', 'QTD', 'STD', 'YTD']
                ).format({
                    'WTD': '{:.2f}%',
                    'MTD': '{:.2f}%',
                    'QTD': '{:.2f}%',
                    'STD': '{:.2f}%',
                    'YTD': '{:.2f}%'
                }),
                use_container_width=True
            )
        
        with idx_perf_tab2:
            st.markdown("##### Performances Glissantes des Indices")
            
            # Calculer les performances glissantes
            idx_rolling_perfs = {}
            for period, label in periods_map.items():
                idx_rolling_perfs[label] = calculate_returns_for_period(historique_indices, period)
            
            # Créer le DataFrame
            idx_rolling_df = pd.DataFrame(idx_rolling_perfs)
            idx_rolling_df['Nom'] = idx_rolling_df.index.map(lambda x: indices_name_map.get(x, x))
            
            # Réorganiser
            cols = ['Nom'] + list(periods_map.values())
            idx_rolling_df = idx_rolling_df[[c for c in cols if c in idx_rolling_df.columns]]
            
            st.dataframe(
                idx_rolling_df.style.applymap(
                    style_performance, 
                    subset=list(periods_map.values())
                ).format({col: '{:.2f}%' for col in periods_map.values()}),
                use_container_width=True
            )
        
        with idx_perf_tab3:
            st.markdown("##### Graphique Comparatif des Indices")
            
            col_select_idx, col_period_idx = st.columns([2, 1])
            
            with col_select_idx:
                available_indices = historique_indices.columns.tolist()
                selected_indices = st.multiselect(
                    "📈 Sélectionnez les indices à comparer",
                    options=available_indices,
                    default=available_indices[:4] if len(available_indices) >= 4 else available_indices,
                    format_func=lambda x: indices_name_map.get(x, x),
                    key='select_indices_compare'
                )
            
            with col_period_idx:
                selected_idx_period = st.selectbox(
                    "📅 Période du graphique",
                    options=list(period_options.keys()),
                    format_func=lambda x: period_options[x],
                    index=3,
                    key='chart_period_indices'
                )
            
            if selected_indices:
                # Déterminer la date de début
                if selected_idx_period == 'MAX':
                    start_date_idx = None
                else:
                    days_map = {'1M': 30, '3M': 90, '6M': 180, '1Y': 365, '3Y': 1095}
                    start_date_idx = historique_indices.index[-1] - timedelta(days=days_map[selected_idx_period])
                
                # Préparer les données
                idx_chart_data = historique_indices[selected_indices].copy()
                
                # Calculer les rendements cumulés
                idx_cumulative = calculate_cumulative_returns(idx_chart_data, start_date_idx)
                
                # Créer le graphique
                fig_idx = go.Figure()
                colors = px.colors.qualitative.Set1
                
                for i, col in enumerate(idx_cumulative.columns):
                    fig_idx.add_trace(go.Scatter(
                        x=idx_cumulative.index,
                        y=idx_cumulative[col],
                        mode='lines',
                        name=indices_name_map.get(col, col),
                        line=dict(color=colors[i % len(colors)], width=2)
                    ))
                
                # Ligne de référence à 100
                fig_idx.add_hline(y=100, line_dash="dash", line_color="#8B7355", opacity=0.5)
                
                fig_idx.update_layout(
                    title=f"Évolution Cumulée des Indices (base 100) - {period_options[selected_idx_period]}",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Date",
                    yaxis_title="Valeur (base 100)",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    font=dict(color='#4A3728'),
                    hovermode='x unified'
                )
                fig_idx.update_xaxes(gridcolor='#E8DDD4')
                fig_idx.update_yaxes(gridcolor='#E8DDD4')
                
                st.plotly_chart(fig_idx, use_container_width=True)
            else:
                st.info("Sélectionnez au moins un indice pour afficher le graphique.")

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")
    st.info("Vérifiez que le fichier 'historical stock data.xlsx' est présent dans le dossier de l'application.")
