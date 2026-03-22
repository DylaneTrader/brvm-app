"""
Page Corrélations & Bêta - Matrices de corrélation et analyse du bêta
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_data, calculate_correlation_matrix, calculate_beta, calculate_rolling_beta

st.set_page_config(page_title="Corrélations & Bêta - BRVM Analytics", page_icon="🔗", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .beta-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #8B7355;
        margin: 15px 0;
    }
    
    .info-card {
        background: #E8DDD4;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .interpretation-card {
        background: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        margin: 10px 0;
    }
    
    .warning-card {
        background: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #F59E0B;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🔗 Corrélations & Bêta")

@st.cache_data
def get_data():
    return load_data()

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
    
    # Tabs pour Actions, Indices et Bêta
    tab_actions, tab_indices, tab_beta = st.tabs(["📊 Corrélations Actions", "📈 Corrélations Indices", "📉 Analyse Bêta"])
    
    # ==================== CORRÉLATIONS ACTIONS ====================
    with tab_actions:
        st.subheader("Matrice de Corrélation des Actions")
        
        # Filtres
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            sectors = ['Tous les secteurs'] + sorted(fiche_actions['Sector'].dropna().unique().tolist())
            selected_sector = st.selectbox(
                "🏭 Filtrer par secteur",
                sectors,
                key='sector_corr'
            )
        
        with col2:
            corr_method = st.selectbox(
                "📐 Méthode de corrélation",
                ['pearson', 'spearman'],
                format_func=lambda x: 'Pearson (linéaire)' if x == 'pearson' else 'Spearman (monotone)',
                key='corr_method_actions'
            )
        
        with col3:
            max_assets = st.slider(
                "📊 Nombre max d'actifs",
                min_value=5,
                max_value=50,
                value=20,
                key='max_assets_corr'
            )
        
        # Filtrer par secteur
        if selected_sector != 'Tous les secteurs':
            sector_symbols = fiche_actions[fiche_actions['Sector'] == selected_sector]['Symbol'].tolist()
            filtered_actions = historique_actions[[c for c in historique_actions.columns if c in sector_symbols]]
        else:
            filtered_actions = historique_actions
        
        # Limiter le nombre d'actifs pour la lisibilité
        if len(filtered_actions.columns) > max_assets:
            st.info(f"Affichage limité aux {max_assets} premières actions. Utilisez le filtre secteur pour cibler.")
            filtered_actions = filtered_actions.iloc[:, :max_assets]
        
        # Calculer la matrice de corrélation
        corr_matrix = calculate_correlation_matrix(filtered_actions, method=corr_method)
        
        # Heatmap avec Plotly
        fig = px.imshow(
            corr_matrix,
            labels=dict(x="Actions", y="Actions", color="Corrélation"),
            x=corr_matrix.columns,
            y=corr_matrix.index,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            aspect='equal'
        )
        
        fig.update_layout(
            title=f"Matrice de Corrélation ({corr_method.capitalize()}) - {selected_sector}",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#4A3728'),
            height=700
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Statistiques de corrélation
        st.markdown("---")
        st.markdown("##### 📊 Statistiques de Corrélation")
        
        # Extraire les corrélations (triangulaire supérieur)
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        corr_values = corr_matrix.where(mask).stack()
        
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Corrélation moyenne", f"{corr_values.mean():.3f}")
        
        with col_stat2:
            st.metric("Corrélation médiane", f"{corr_values.median():.3f}")
        
        with col_stat3:
            st.metric("Corrélation max", f"{corr_values.max():.3f}")
        
        with col_stat4:
            st.metric("Corrélation min", f"{corr_values.min():.3f}")
        
        # Top paires corrélées
        with st.expander("🔝 Top 10 paires les plus corrélées", expanded=False):
            corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_pairs.append({
                        'Action 1': corr_matrix.columns[i],
                        'Action 2': corr_matrix.columns[j],
                        'Corrélation': corr_matrix.iloc[i, j]
                    })
            
            pairs_df = pd.DataFrame(corr_pairs)
            pairs_df = pairs_df.sort_values('Corrélation', ascending=False).head(10)
            pairs_df['Action 1 Nom'] = pairs_df['Action 1'].map(lambda x: symbol_to_name.get(x, x))
            pairs_df['Action 2 Nom'] = pairs_df['Action 2'].map(lambda x: symbol_to_name.get(x, x))
            
            st.dataframe(
                pairs_df[['Action 1', 'Action 1 Nom', 'Action 2', 'Action 2 Nom', 'Corrélation']].style.format({'Corrélation': '{:.3f}'}),
                use_container_width=True,
                hide_index=True
            )
        
        # Paires les moins corrélées
        with st.expander("📉 Top 10 paires les moins corrélées", expanded=False):
            pairs_df_low = pd.DataFrame(corr_pairs)
            pairs_df_low = pairs_df_low.sort_values('Corrélation', ascending=True).head(10)
            pairs_df_low['Action 1 Nom'] = pairs_df_low['Action 1'].map(lambda x: symbol_to_name.get(x, x))
            pairs_df_low['Action 2 Nom'] = pairs_df_low['Action 2'].map(lambda x: symbol_to_name.get(x, x))
            
            st.dataframe(
                pairs_df_low[['Action 1', 'Action 1 Nom', 'Action 2', 'Action 2 Nom', 'Corrélation']].style.format({'Corrélation': '{:.3f}'}),
                use_container_width=True,
                hide_index=True
            )
    
    # ==================== CORRÉLATIONS INDICES ====================
    with tab_indices:
        st.subheader("Matrice de Corrélation des Indices")
        
        col1_idx, col2_idx = st.columns([1, 1])
        
        with col1_idx:
            corr_method_idx = st.selectbox(
                "📐 Méthode de corrélation",
                ['pearson', 'spearman'],
                format_func=lambda x: 'Pearson (linéaire)' if x == 'pearson' else 'Spearman (monotone)',
                key='corr_method_indices'
            )
        
        # Calculer la matrice de corrélation des indices
        corr_matrix_idx = calculate_correlation_matrix(historique_indices, method=corr_method_idx)
        
        # Renommer avec les noms complets
        corr_matrix_idx_named = corr_matrix_idx.copy()
        corr_matrix_idx_named.columns = [indices_name_map.get(c, c) for c in corr_matrix_idx.columns]
        corr_matrix_idx_named.index = [indices_name_map.get(c, c) for c in corr_matrix_idx.index]
        
        # Heatmap avec Plotly
        fig_idx = px.imshow(
            corr_matrix_idx_named,
            labels=dict(x="Indices", y="Indices", color="Corrélation"),
            x=corr_matrix_idx_named.columns,
            y=corr_matrix_idx_named.index,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            aspect='equal',
            text_auto='.2f'
        )
        
        fig_idx.update_layout(
            title=f"Matrice de Corrélation des Indices ({corr_method_idx.capitalize()})",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#4A3728'),
            height=600
        )
        
        st.plotly_chart(fig_idx, use_container_width=True)
        
        # Tableau des corrélations
        st.markdown("##### Tableau des Corrélations")
        
        # Créer un tableau lisible
        corr_pairs_idx = []
        for i in range(len(corr_matrix_idx.columns)):
            for j in range(i+1, len(corr_matrix_idx.columns)):
                corr_pairs_idx.append({
                    'Indice 1': indices_name_map.get(corr_matrix_idx.columns[i], corr_matrix_idx.columns[i]),
                    'Indice 2': indices_name_map.get(corr_matrix_idx.columns[j], corr_matrix_idx.columns[j]),
                    'Corrélation': corr_matrix_idx.iloc[i, j]
                })
        
        pairs_idx_df = pd.DataFrame(corr_pairs_idx).sort_values('Corrélation', ascending=False)
        
        st.dataframe(
            pairs_idx_df.style.format({'Corrélation': '{:.3f}'}).background_gradient(
                subset=['Corrélation'],
                cmap='RdBu_r',
                vmin=-1,
                vmax=1
            ),
            use_container_width=True,
            hide_index=True
        )
        
        # Analyse des corrélations
        st.markdown("---")
        st.markdown("##### 📊 Interprétation des Corrélations")
        
        st.markdown("""
        | Valeur | Interprétation |
        |--------|----------------|
        | **0.8 à 1.0** | Très forte corrélation positive |
        | **0.6 à 0.8** | Forte corrélation positive |
        | **0.4 à 0.6** | Corrélation modérée positive |
        | **0.2 à 0.4** | Faible corrélation positive |
        | **-0.2 à 0.2** | Pas de corrélation significative |
        | **-0.4 à -0.2** | Faible corrélation négative |
        | **-0.6 à -0.4** | Corrélation modérée négative |
        | **-0.8 à -0.6** | Forte corrélation négative |
        | **-1.0 à -0.8** | Très forte corrélation négative |
        """)
    
    # ==================== ANALYSE BÊTA ====================
    with tab_beta:
        st.subheader("📉 Analyse du Bêta")
        
        # Carte pédagogique
        st.markdown("""
        <div class="beta-card">
            <h4>📚 Qu'est-ce que le Bêta ?</h4>
            <p>Le <strong>bêta (β)</strong> mesure la sensibilité d'une action aux mouvements du marché (indice de référence).</p>
            <ul>
                <li><strong>β = 1</strong> : L'action évolue comme le marché</li>
                <li><strong>β > 1</strong> : L'action est plus volatile que le marché (amplifie les mouvements)</li>
                <li><strong>β < 1</strong> : L'action est moins volatile que le marché (atténue les mouvements)</li>
                <li><strong>β < 0</strong> : L'action évolue en sens inverse du marché (rare)</li>
            </ul>
            <p><em>Formule : β = Cov(Raction, Rmarché) / Var(Rmarché)</em></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Filtres pour l'analyse du bêta
        st.markdown("##### 🎯 Sélection de l'analyse")
        
        col_beta1, col_beta2, col_beta3 = st.columns([1, 1, 1])
        
        with col_beta1:
            # Sélection de l'action
            action_symbols = sorted(historique_actions.columns.tolist())
            selected_action = st.selectbox(
                "📈 Sélectionner une action",
                action_symbols,
                format_func=lambda x: f"{x} - {symbol_to_name.get(x, x)[:30]}",
                key='beta_action'
            )
        
        with col_beta2:
            # Sélection de l'indice de référence
            indice_symbols = sorted(historique_indices.columns.tolist())
            selected_indice = st.selectbox(
                "📊 Indice de référence",
                indice_symbols,
                format_func=lambda x: f"{x} - {indices_name_map.get(x, x)[:30]}",
                key='beta_indice'
            )
        
        with col_beta3:
            # Période d'analyse
            period_options = {
                'Toute la période': None,
                '1 mois (30 jours)': 30,
                '3 mois (91 jours)': 91,
                '6 mois (182 jours)': 182,
                '1 an (365 jours)': 365,
                '2 ans (730 jours)': 730,
                '3 ans (1095 jours)': 1095
            }
            selected_period_label = st.selectbox(
                "📅 Période d'analyse",
                list(period_options.keys()),
                index=4,  # Par défaut 1 an
                key='beta_period'
            )
            selected_period = period_options[selected_period_label]
        
        st.markdown("---")
        
        # Calcul et affichage du bêta
        if selected_action and selected_indice:
            stock_prices = historique_actions[selected_action]
            index_prices = historique_indices[selected_indice]
            
            # Calcul du bêta
            beta_value = calculate_beta(stock_prices, index_prices, selected_period)
            
            # Résultats
            st.markdown("##### 📊 Résultats de l'analyse")
            
            col_result1, col_result2, col_result3, col_result4 = st.columns(4)
            
            with col_result1:
                if not np.isnan(beta_value):
                    st.metric(
                        "Bêta",
                        f"{beta_value:.3f}",
                        delta=f"{'Agressif' if beta_value > 1.1 else 'Défensif' if beta_value < 0.9 else 'Neutre'}"
                    )
                else:
                    st.metric("Bêta", "N/A")
            
            with col_result2:
                # Volatilité de l'action
                stock_returns = stock_prices.pct_change().dropna()
                if selected_period:
                    stock_returns = stock_returns.tail(selected_period)
                stock_vol = stock_returns.std() * np.sqrt(365) * 100
                st.metric("Volatilité Action", f"{stock_vol:.1f}%")
            
            with col_result3:
                # Volatilité de l'indice
                index_returns = index_prices.pct_change().dropna()
                if selected_period:
                    index_returns = index_returns.tail(selected_period)
                index_vol = index_returns.std() * np.sqrt(365) * 100
                st.metric("Volatilité Indice", f"{index_vol:.1f}%")
            
            with col_result4:
                # Corrélation
                if selected_period:
                    corr = stock_prices.tail(selected_period).pct_change().corr(index_prices.tail(selected_period).pct_change())
                else:
                    corr = stock_prices.pct_change().corr(index_prices.pct_change())
                st.metric("Corrélation", f"{corr:.3f}" if not np.isnan(corr) else "N/A")
            
            # Interprétation
            if not np.isnan(beta_value):
                if beta_value > 1.5:
                    interpretation = "🔴 **Très agressif** : Cette action amplifie fortement les mouvements du marché. Potentiel de gain élevé mais risque important."
                elif beta_value > 1.1:
                    interpretation = "🟠 **Agressif** : Cette action est plus volatile que le marché. Elle amplifie les hausses et les baisses."
                elif beta_value >= 0.9:
                    interpretation = "🟢 **Neutre** : Cette action évolue globalement comme le marché."
                elif beta_value >= 0.5:
                    interpretation = "🔵 **Défensif** : Cette action est moins volatile que le marché. Elle atténue les mouvements."
                else:
                    interpretation = "⚪ **Très défensif** : Cette action est beaucoup moins volatile que le marché ou évolue de manière indépendante."
                
                st.markdown(f"""
                <div class="interpretation-card">
                    {interpretation}
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # ==================== BÊTA GLISSANT ====================
            st.markdown("##### 📈 Bêta Glissant")
            
            col_rolling1, col_rolling2 = st.columns([1, 3])
            
            with col_rolling1:
                # Fenêtre glissante
                rolling_window_options = {
                    '1 mois (30 jours)': 30,
                    '2 mois (60 jours)': 60,
                    '3 mois (91 jours)': 91,
                    '6 mois (182 jours)': 182,
                    '1 an (365 jours)': 365
                }
                selected_rolling_label = st.selectbox(
                    "📅 Fenêtre glissante",
                    list(rolling_window_options.keys()),
                    index=2,  # Par défaut 3 mois
                    key='rolling_window'
                )
                rolling_window = rolling_window_options[selected_rolling_label]
            
            # Calcul du bêta glissant
            rolling_beta = calculate_rolling_beta(stock_prices, index_prices, window=rolling_window)
            
            if not rolling_beta.empty:
                with col_rolling2:
                    # Période d'affichage
                    display_periods = {
                        '6 mois': 182,
                        '1 an': 365,
                        '2 ans': 730,
                        '3 ans': 1095,
                        'Tout': len(rolling_beta)
                    }
                    display_period_label = st.selectbox(
                        "📆 Période d'affichage",
                        list(display_periods.keys()),
                        index=1,
                        key='display_period'
                    )
                    display_period = display_periods[display_period_label]
                
                # Graphique du bêta glissant
                rolling_beta_display = rolling_beta.dropna().tail(display_period)
                
                fig_rolling = go.Figure()
                
                # Ligne du bêta
                fig_rolling.add_trace(go.Scatter(
                    x=rolling_beta_display.index,
                    y=rolling_beta_display.values,
                    mode='lines',
                    name=f'Bêta glissant ({selected_rolling_label})',
                    line=dict(color='#8B7355', width=2)
                ))
                
                # Ligne de référence β = 1
                fig_rolling.add_hline(
                    y=1, 
                    line_dash="dash", 
                    line_color="#4A3728",
                    annotation_text="β = 1 (Marché)"
                )
                
                # Zones
                fig_rolling.add_hrect(y0=1.1, y1=rolling_beta_display.max() + 0.2 if rolling_beta_display.max() > 1.1 else 1.5, 
                                     fillcolor="rgba(239, 68, 68, 0.1)", line_width=0,
                                     annotation_text="Agressif", annotation_position="top left")
                fig_rolling.add_hrect(y0=rolling_beta_display.min() - 0.2 if rolling_beta_display.min() < 0.9 else 0.5, y1=0.9, 
                                     fillcolor="rgba(59, 130, 246, 0.1)", line_width=0,
                                     annotation_text="Défensif", annotation_position="bottom left")
                
                fig_rolling.update_layout(
                    title=f"Évolution du Bêta Glissant - {symbol_to_name.get(selected_action, selected_action)} vs {indices_name_map.get(selected_indice, selected_indice)}",
                    xaxis_title="Date",
                    yaxis_title="Bêta",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#4A3728'),
                    height=450,
                    hovermode='x unified'
                )
                fig_rolling.update_xaxes(gridcolor='#E8DDD4')
                fig_rolling.update_yaxes(gridcolor='#E8DDD4')
                
                st.plotly_chart(fig_rolling, use_container_width=True)
                
                # Statistiques du bêta glissant
                col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
                
                with col_stat1:
                    st.metric("Bêta actuel", f"{rolling_beta_display.iloc[-1]:.3f}")
                with col_stat2:
                    st.metric("Bêta moyen", f"{rolling_beta_display.mean():.3f}")
                with col_stat3:
                    st.metric("Bêta max", f"{rolling_beta_display.max():.3f}")
                with col_stat4:
                    st.metric("Bêta min", f"{rolling_beta_display.min():.3f}")
            else:
                st.warning("Données insuffisantes pour calculer le bêta glissant avec cette fenêtre.")
            
            st.markdown("---")
            
            # Graphique de dispersion (rendements)
            st.markdown("##### 📊 Régression des Rendements")
            
            # Aligner les données
            aligned = pd.DataFrame({
                'Action': stock_prices.pct_change() * 100,
                'Indice': index_prices.pct_change() * 100
            }).dropna()
            
            if selected_period:
                aligned = aligned.tail(selected_period)
            
            # Créer le scatter plot
            fig_scatter = go.Figure()
            
            fig_scatter.add_trace(go.Scatter(
                x=aligned['Indice'],
                y=aligned['Action'],
                mode='markers',
                marker=dict(color='#8B7355', size=5, opacity=0.6),
                name='Rendements journaliers'
            ))
            
            # Ligne de régression
            if not np.isnan(beta_value):
                x_range = np.linspace(aligned['Indice'].min(), aligned['Indice'].max(), 100)
                y_pred = beta_value * x_range
                
                fig_scatter.add_trace(go.Scatter(
                    x=x_range,
                    y=y_pred,
                    mode='lines',
                    line=dict(color='#EF4444', width=2),
                    name=f'Régression (β={beta_value:.2f})'
                ))
            
            fig_scatter.update_layout(
                title=f"Rendements de {symbol_to_name.get(selected_action, selected_action)} vs {indices_name_map.get(selected_indice, selected_indice)}",
                xaxis_title=f"Rendements {indices_name_map.get(selected_indice, selected_indice)} (%)",
                yaxis_title=f"Rendements {symbol_to_name.get(selected_action, selected_action)} (%)",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A3728'),
                height=400
            )
            fig_scatter.update_xaxes(gridcolor='#E8DDD4')
            fig_scatter.update_yaxes(gridcolor='#E8DDD4')
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            st.markdown("""
            <div class="info-card">
                <strong>💡 Lecture du graphique :</strong><br>
                La pente de la droite de régression représente le bêta. Plus la pente est raide, plus l'action est sensible aux mouvements du marché.
                Les points dispersés autour de la droite indiquent le risque spécifique (non systématique) de l'action.
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")
    st.info("Vérifiez que le fichier 'historical stock data.xlsx' est présent dans le dossier de l'application.")
