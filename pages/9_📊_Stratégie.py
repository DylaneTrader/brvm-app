"""
Page Stratégie - Construction et optimisation de portefeuilles
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_data

st.set_page_config(page_title="Stratégie - BRVM Analytics", page_icon="📊", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .strategy-card {
        background: linear-gradient(135deg, #E8DDD4, #FAF9F6);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #8B7355;
    }
    
    .portfolio-item {
        background-color: #FAF9F6;
        border: 1px solid #E8DDD4;
        border-radius: 10px;
        padding: 15px;
        margin: 5px 0;
    }
    
    .weight-positive { color: #10B981; font-weight: bold; }
    .weight-negative { color: #EF4444; font-weight: bold; }
    
    .info-box {
        background-color: #E8F4FD;
        border-left: 4px solid #3B82F6;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
    
    .success-box {
        background-color: #ECFDF5;
        border-left: 4px solid #10B981;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
    
    .maintenance-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 60px 20px;
        text-align: center;
    }
    
    .maintenance-emoji {
        font-size: 120px;
        margin-bottom: 20px;
    }
    
    .maintenance-text {
        font-size: 28px;
        color: #8B7355;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .maintenance-subtext {
        font-size: 18px;
        color: #4A3728;
        font-style: italic;
    }
    
    .frontier-info {
        background-color: #FFF3CD;
        border-left: 4px solid #FFC107;
        padding: 15px;
        border-radius: 0 10px 10px 0;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Stratégie - Construction de Portefeuille")

# ==================== FONCTIONS D'OPTIMISATION ====================

def calculate_portfolio_metrics(weights, returns, cov_matrix):
    """Calcule les métriques du portefeuille"""
    portfolio_return = np.sum(returns.mean() * weights) * 365
    portfolio_volatility = np.sqrt(np.dot(weights.T, np.dot(cov_matrix * 365, weights)))
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
    return portfolio_return, portfolio_volatility, sharpe_ratio

def optimize_markowitz(returns, target_return=None, risk_free_rate=0.0):
    """
    Optimisation Markowitz (Moyenne-Variance)
    Si target_return est None, cherche le portefeuille tangent (max Sharpe)
    """
    n_assets = len(returns.columns)
    cov_matrix = returns.cov()
    mean_returns = returns.mean()
    
    # Génération de portefeuilles aléatoires pour la frontière efficiente
    n_portfolios = 5000
    results = np.zeros((3, n_portfolios))
    weights_record = []
    
    for i in range(n_portfolios):
        weights = np.random.random(n_assets)
        weights /= np.sum(weights)
        weights_record.append(weights)
        
        portfolio_return, portfolio_volatility, sharpe = calculate_portfolio_metrics(
            weights, returns, cov_matrix
        )
        
        results[0, i] = portfolio_volatility * 100  # En %
        results[1, i] = portfolio_return * 100  # En %
        results[2, i] = sharpe
    
    # Trouver le portefeuille optimal (max Sharpe)
    max_sharpe_idx = np.argmax(results[2])
    optimal_weights = weights_record[max_sharpe_idx]
    
    # Trouver le portefeuille minimum variance
    min_vol_idx = np.argmin(results[0])
    min_vol_weights = weights_record[min_vol_idx]
    
    return {
        'optimal_weights': optimal_weights,
        'min_vol_weights': min_vol_weights,
        'results': results,
        'weights_record': weights_record,
        'max_sharpe_idx': max_sharpe_idx,
        'min_vol_idx': min_vol_idx
    }

def optimize_risk_parity(returns):
    """
    Optimisation Risk Parity (Parité des risques)
    Chaque actif contribue également au risque total du portefeuille
    """
    n_assets = len(returns.columns)
    cov_matrix = returns.cov()
    
    # Estimation initiale : inverse de la volatilité
    volatilities = returns.std()
    weights = (1 / volatilities) / (1 / volatilities).sum()
    
    # Itération pour affiner les poids
    for _ in range(100):
        # Calcul de la contribution au risque marginal
        portfolio_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        marginal_contrib = np.dot(cov_matrix, weights) / portfolio_vol
        risk_contrib = weights * marginal_contrib
        
        # Ajuster les poids
        target_risk_contrib = portfolio_vol / n_assets
        adjustment = target_risk_contrib / (risk_contrib + 1e-10)
        weights = weights * adjustment
        weights = weights / weights.sum()
    
    return weights.values

# ==================== CHARGEMENT DES DONNÉES ====================

@st.cache_data
def get_data():
    return load_data()

# Initialiser l'état du portefeuille dans la session
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}

if 'saved_portfolios' not in st.session_state:
    st.session_state.saved_portfolios = {}

try:
    data = get_data()
    fiche_actions = data['fiche_actions']
    historique_actions = data['historique_actions']
    
    # Mappings
    symbol_to_name = dict(zip(fiche_actions['Symbol'], fiche_actions['Name']))
    symbol_to_sector = dict(zip(fiche_actions['Symbol'], fiche_actions['Sector']))
    
    # Disponibles
    available_symbols = list(historique_actions.columns)
    
    st.markdown("---")
    
    # ==================== ONGLETS ====================
    tab_classique, tab_ml = st.tabs(["📈 Classique", "🤖 Machine Learning"])
    
    # ==================== ONGLET CLASSIQUE ====================
    with tab_classique:
        st.subheader("Construction de Portefeuille")
        
        # Sous-onglets pour les méthodes
        method_tab1, method_tab2, method_tab3 = st.tabs(["✋ Manuel", "📐 Markowitz", "⚖️ Risk Parity"])
        
        # ==================== MÉTHODE MANUELLE ====================
        with method_tab1:
            st.markdown("""
            <div class="info-box">
                <strong>📝 Construction Manuelle</strong><br>
                Sélectionnez les actions et définissez les poids de votre portefeuille.
            </div>
            """, unsafe_allow_html=True)
            
            col_select, col_portfolio = st.columns([1, 1])
            
            with col_select:
                st.markdown("##### Ajouter des actifs")
                
                # Sélection de l'action
                selected_action = st.selectbox(
                    "📌 Sélectionner une action",
                    options=[''] + available_symbols,
                    format_func=lambda x: f"{x} - {symbol_to_name.get(x, x)}" if x else "Choisir une action..."
                )
                
                # Poids
                weight = st.number_input(
                    "⚖️ Poids (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=10.0,
                    step=1.0
                )
                
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("➕ Ajouter", use_container_width=True):
                        if selected_action:
                            st.session_state.portfolio[selected_action] = weight
                            st.rerun()
                
                with col_btn2:
                    if st.button("🗑️ Vider tout", use_container_width=True):
                        st.session_state.portfolio = {}
                        st.rerun()
            
            with col_portfolio:
                st.markdown("##### Votre Portefeuille")
                
                if st.session_state.portfolio:
                    total_weight = sum(st.session_state.portfolio.values())
                    
                    # Afficher les actifs
                    for symbol, w in list(st.session_state.portfolio.items()):
                        col_sym, col_w, col_del = st.columns([3, 2, 1])
                        with col_sym:
                            st.write(f"**{symbol}** - {symbol_to_name.get(symbol, symbol)[:20]}")
                        with col_w:
                            new_w = st.number_input(
                                "Poids",
                                min_value=0.0,
                                max_value=100.0,
                                value=float(w),
                                step=1.0,
                                key=f"weight_{symbol}",
                                label_visibility="collapsed"
                            )
                            if new_w != w:
                                st.session_state.portfolio[symbol] = new_w
                        with col_del:
                            if st.button("❌", key=f"del_{symbol}"):
                                del st.session_state.portfolio[symbol]
                                st.rerun()
                    
                    st.markdown("---")
                    
                    # Total
                    color = "#10B981" if abs(total_weight - 100) < 0.1 else "#EF4444"
                    st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background-color: #E8DDD4; border-radius: 10px;">
                        <strong>Total des poids :</strong> 
                        <span style="color: {color}; font-size: 20px; font-weight: bold;">{total_weight:.1f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if abs(total_weight - 100) > 0.1:
                        st.warning("⚠️ Le total des poids doit être égal à 100%")
                    
                    # Normaliser
                    if st.button("🔄 Normaliser à 100%", use_container_width=True):
                        if total_weight > 0:
                            for sym in st.session_state.portfolio:
                                st.session_state.portfolio[sym] = (st.session_state.portfolio[sym] / total_weight) * 100
                            st.rerun()
                else:
                    st.info("📭 Aucun actif dans le portefeuille. Ajoutez des actions à gauche.")
            
            # ==================== ANALYSE DU PORTEFEUILLE MANUEL ====================
            if st.session_state.portfolio and abs(sum(st.session_state.portfolio.values()) - 100) < 0.1:
                st.markdown("---")
                st.markdown("##### 📊 Analyse du Portefeuille")
                
                # Préparer les données
                portfolio_symbols = list(st.session_state.portfolio.keys())
                portfolio_weights = np.array([st.session_state.portfolio[s] / 100 for s in portfolio_symbols])
                
                # Calculer les rendements
                portfolio_prices = historique_actions[portfolio_symbols].dropna()
                portfolio_returns = portfolio_prices.pct_change().dropna()
                
                if len(portfolio_returns) > 0:
                    cov_matrix = portfolio_returns.cov()
                    
                    # Métriques
                    port_return, port_vol, port_sharpe = calculate_portfolio_metrics(
                        portfolio_weights, portfolio_returns, cov_matrix
                    )
                    
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    
                    with col_m1:
                        st.metric("Rendement Annualisé", f"{port_return*100:.2f}%")
                    with col_m2:
                        st.metric("Volatilité Annualisée", f"{port_vol*100:.2f}%")
                    with col_m3:
                        st.metric("Ratio de Sharpe", f"{port_sharpe:.3f}")
                    with col_m4:
                        st.metric("Nb d'actifs", len(portfolio_symbols))
                    
                    # Graphique de répartition
                    col_chart1, col_chart2 = st.columns(2)
                    
                    with col_chart1:
                        fig_pie = px.pie(
                            values=portfolio_weights * 100,
                            names=[f"{s} ({symbol_to_name.get(s, s)[:15]})" for s in portfolio_symbols],
                            title="Répartition du Portefeuille",
                            color_discrete_sequence=px.colors.sequential.RdBu
                        )
                        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                        fig_pie.update_layout(
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            showlegend=False
                        )
                        st.plotly_chart(fig_pie, use_container_width=True)
                    
                    with col_chart2:
                        # Performance cumulée
                        weighted_returns = (portfolio_returns * portfolio_weights).sum(axis=1)
                        cumulative = (1 + weighted_returns).cumprod() * 100
                        
                        fig_perf = go.Figure()
                        fig_perf.add_trace(go.Scatter(
                            x=cumulative.index,
                            y=cumulative.values,
                            mode='lines',
                            fill='tozeroy',
                            fillcolor='rgba(139, 115, 85, 0.3)',
                            line=dict(color='#8B7355', width=2),
                            name='Portefeuille'
                        ))
                        fig_perf.update_layout(
                            title="Performance Cumulée (Base 100)",
                            xaxis_title="Date",
                            yaxis_title="Valeur",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            hovermode='x unified'
                        )
                        fig_perf.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
                        st.plotly_chart(fig_perf, use_container_width=True)
        
        # ==================== MÉTHODE MARKOWITZ ====================
        with method_tab2:
            st.markdown("""
            <div class="info-box">
                <strong>📐 Optimisation Markowitz (Moyenne-Variance)</strong><br>
                Cette méthode trouve le portefeuille qui maximise le ratio de Sharpe 
                (rendement ajusté au risque) sur la frontière efficiente.
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection des actifs
            st.markdown("##### Sélection des actifs")
            
            col_select_mkw1, col_select_mkw2 = st.columns([2, 1])
            
            with col_select_mkw1:
                selected_assets_mkw = st.multiselect(
                    "📌 Sélectionner les actions pour l'optimisation (min. 2)",
                    options=available_symbols,
                    format_func=lambda x: f"{x} - {symbol_to_name.get(x, x)}",
                    default=available_symbols[:5] if len(available_symbols) >= 5 else available_symbols[:2]
                )
            
            with col_select_mkw2:
                period_mkw = st.selectbox(
                    "📅 Période d'analyse",
                    options=['6 mois', '1 an', '2 ans', '3 ans', 'Tout'],
                    index=1
                )
                
                period_days_mkw = {
                    '6 mois': 182,
                    '1 an': 365,
                    '2 ans': 730,
                    '3 ans': 1095,
                    'Tout': None
                }
            
            if len(selected_assets_mkw) >= 2:
                if st.button("🚀 Lancer l'optimisation Markowitz", use_container_width=True, key="btn_mkw"):
                    with st.spinner("Optimisation en cours..."):
                        # Préparer les données
                        prices_mkw = historique_actions[selected_assets_mkw].dropna()
                        if period_days_mkw[period_mkw]:
                            prices_mkw = prices_mkw.tail(period_days_mkw[period_mkw])
                        returns_mkw = prices_mkw.pct_change().dropna()
                        
                        # Optimisation
                        optim_result = optimize_markowitz(returns_mkw)
                        
                        st.markdown("---")
                        st.markdown("##### 📊 Résultats de l'Optimisation")
                        
                        # Frontière efficiente
                        fig_frontier = go.Figure()
                        
                        # Tous les portefeuilles
                        fig_frontier.add_trace(go.Scatter(
                            x=optim_result['results'][0],
                            y=optim_result['results'][1],
                            mode='markers',
                            marker=dict(
                                size=5,
                                color=optim_result['results'][2],
                                colorscale='RdYlGn',
                                showscale=True,
                                colorbar=dict(title="Sharpe")
                            ),
                            name='Portefeuilles',
                            hovertemplate='Vol: %{x:.2f}%<br>Ret: %{y:.2f}%<extra></extra>'
                        ))
                        
                        # Portefeuille optimal
                        fig_frontier.add_trace(go.Scatter(
                            x=[optim_result['results'][0, optim_result['max_sharpe_idx']]],
                            y=[optim_result['results'][1, optim_result['max_sharpe_idx']]],
                            mode='markers',
                            marker=dict(size=20, color='gold', symbol='star'),
                            name='Max Sharpe'
                        ))
                        
                        # Minimum variance
                        fig_frontier.add_trace(go.Scatter(
                            x=[optim_result['results'][0, optim_result['min_vol_idx']]],
                            y=[optim_result['results'][1, optim_result['min_vol_idx']]],
                            mode='markers',
                            marker=dict(size=15, color='blue', symbol='diamond'),
                            name='Min Volatilité'
                        ))
                        
                        fig_frontier.update_layout(
                            title="Frontière Efficiente",
                            xaxis_title="Volatilité (%)",
                            yaxis_title="Rendement Annualisé (%)",
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            legend=dict(orientation="h", yanchor="bottom", y=1.02)
                        )
                        
                        st.plotly_chart(fig_frontier, use_container_width=True)
                        
                        # Afficher les poids optimaux
                        col_opt1, col_opt2 = st.columns(2)
                        
                        with col_opt1:
                            st.markdown("**⭐ Portefeuille Max Sharpe**")
                            weights_df = pd.DataFrame({
                                'Action': selected_assets_mkw,
                                'Nom': [symbol_to_name.get(s, s) for s in selected_assets_mkw],
                                'Poids (%)': optim_result['optimal_weights'] * 100
                            }).sort_values('Poids (%)', ascending=False)
                            
                            st.dataframe(
                                weights_df.style.format({'Poids (%)': '{:.2f}%'}),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Métriques
                            opt_ret, opt_vol, opt_sharpe = calculate_portfolio_metrics(
                                optim_result['optimal_weights'],
                                returns_mkw,
                                returns_mkw.cov()
                            )
                            st.metric("Rendement", f"{opt_ret*100:.2f}%")
                            st.metric("Volatilité", f"{opt_vol*100:.2f}%")
                            st.metric("Ratio de Sharpe", f"{opt_sharpe:.3f}")
                            
                            # Bouton pour appliquer
                            if st.button("✅ Appliquer ce portefeuille", key="apply_mkw_opt"):
                                st.session_state.portfolio = {}
                                for i, sym in enumerate(selected_assets_mkw):
                                    st.session_state.portfolio[sym] = optim_result['optimal_weights'][i] * 100
                                st.success("Portefeuille appliqué ! Voir l'onglet Manuel.")
                        
                        with col_opt2:
                            st.markdown("**🛡️ Portefeuille Min Volatilité**")
                            weights_df_min = pd.DataFrame({
                                'Action': selected_assets_mkw,
                                'Nom': [symbol_to_name.get(s, s) for s in selected_assets_mkw],
                                'Poids (%)': optim_result['min_vol_weights'] * 100
                            }).sort_values('Poids (%)', ascending=False)
                            
                            st.dataframe(
                                weights_df_min.style.format({'Poids (%)': '{:.2f}%'}),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Métriques
                            min_ret, min_vol, min_sharpe = calculate_portfolio_metrics(
                                optim_result['min_vol_weights'],
                                returns_mkw,
                                returns_mkw.cov()
                            )
                            st.metric("Rendement", f"{min_ret*100:.2f}%")
                            st.metric("Volatilité", f"{min_vol*100:.2f}%")
                            st.metric("Ratio de Sharpe", f"{min_sharpe:.3f}")
                            
                            # Bouton pour appliquer
                            if st.button("✅ Appliquer ce portefeuille", key="apply_mkw_min"):
                                st.session_state.portfolio = {}
                                for i, sym in enumerate(selected_assets_mkw):
                                    st.session_state.portfolio[sym] = optim_result['min_vol_weights'][i] * 100
                                st.success("Portefeuille appliqué ! Voir l'onglet Manuel.")
            else:
                st.warning("⚠️ Sélectionnez au moins 2 actifs pour l'optimisation.")
        
        # ==================== MÉTHODE RISK PARITY ====================
        with method_tab3:
            st.markdown("""
            <div class="info-box">
                <strong>⚖️ Optimisation Risk Parity (Parité des Risques)</strong><br>
                Cette méthode alloue les poids de sorte que chaque actif contribue 
                également au risque total du portefeuille.
            </div>
            """, unsafe_allow_html=True)
            
            # Sélection des actifs
            st.markdown("##### Sélection des actifs")
            
            col_select_rp1, col_select_rp2 = st.columns([2, 1])
            
            with col_select_rp1:
                selected_assets_rp = st.multiselect(
                    "📌 Sélectionner les actions pour l'optimisation (min. 2)",
                    options=available_symbols,
                    format_func=lambda x: f"{x} - {symbol_to_name.get(x, x)}",
                    default=available_symbols[:5] if len(available_symbols) >= 5 else available_symbols[:2],
                    key="rp_select"
                )
            
            with col_select_rp2:
                period_rp = st.selectbox(
                    "📅 Période d'analyse",
                    options=['6 mois', '1 an', '2 ans', '3 ans', 'Tout'],
                    index=1,
                    key="rp_period"
                )
                
                period_days_rp = {
                    '6 mois': 182,
                    '1 an': 365,
                    '2 ans': 730,
                    '3 ans': 1095,
                    'Tout': None
                }
            
            if len(selected_assets_rp) >= 2:
                if st.button("🚀 Lancer l'optimisation Risk Parity", use_container_width=True, key="btn_rp"):
                    with st.spinner("Optimisation en cours..."):
                        # Préparer les données
                        prices_rp = historique_actions[selected_assets_rp].dropna()
                        if period_days_rp[period_rp]:
                            prices_rp = prices_rp.tail(period_days_rp[period_rp])
                        returns_rp = prices_rp.pct_change().dropna()
                        
                        # Optimisation
                        rp_weights = optimize_risk_parity(returns_rp)
                        
                        st.markdown("---")
                        st.markdown("##### 📊 Résultats de l'Optimisation")
                        
                        col_rp1, col_rp2 = st.columns(2)
                        
                        with col_rp1:
                            st.markdown("**⚖️ Portefeuille Risk Parity**")
                            
                            weights_df_rp = pd.DataFrame({
                                'Action': selected_assets_rp,
                                'Nom': [symbol_to_name.get(s, s) for s in selected_assets_rp],
                                'Poids (%)': rp_weights * 100
                            }).sort_values('Poids (%)', ascending=False)
                            
                            st.dataframe(
                                weights_df_rp.style.format({'Poids (%)': '{:.2f}%'}),
                                use_container_width=True,
                                hide_index=True
                            )
                            
                            # Métriques
                            cov_rp = returns_rp.cov()
                            rp_ret, rp_vol, rp_sharpe = calculate_portfolio_metrics(
                                rp_weights,
                                returns_rp,
                                cov_rp
                            )
                            st.metric("Rendement Annualisé", f"{rp_ret*100:.2f}%")
                            st.metric("Volatilité Annualisée", f"{rp_vol*100:.2f}%")
                            st.metric("Ratio de Sharpe", f"{rp_sharpe:.3f}")
                            
                            # Bouton pour appliquer
                            if st.button("✅ Appliquer ce portefeuille", key="apply_rp"):
                                st.session_state.portfolio = {}
                                for i, sym in enumerate(selected_assets_rp):
                                    st.session_state.portfolio[sym] = rp_weights[i] * 100
                                st.success("Portefeuille appliqué ! Voir l'onglet Manuel.")
                        
                        with col_rp2:
                            # Graphique des poids
                            fig_rp = px.bar(
                                weights_df_rp,
                                x='Action',
                                y='Poids (%)',
                                color='Poids (%)',
                                color_continuous_scale='RdYlGn',
                                title="Répartition Risk Parity"
                            )
                            fig_rp.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                showlegend=False
                            )
                            st.plotly_chart(fig_rp, use_container_width=True)
                            
                            # Contribution au risque
                            st.markdown("**📊 Contribution au risque**")
                            
                            # Calcul des contributions
                            portfolio_vol = np.sqrt(np.dot(rp_weights.T, np.dot(cov_rp, rp_weights)))
                            marginal_contrib = np.dot(cov_rp, rp_weights) / portfolio_vol
                            risk_contrib = rp_weights * marginal_contrib
                            risk_contrib_pct = risk_contrib / risk_contrib.sum() * 100
                            
                            contrib_df = pd.DataFrame({
                                'Action': selected_assets_rp,
                                'Contribution (%)': risk_contrib_pct
                            })
                            
                            fig_contrib = px.pie(
                                contrib_df,
                                values='Contribution (%)',
                                names='Action',
                                title="Contribution au Risque",
                                color_discrete_sequence=px.colors.sequential.RdBu
                            )
                            fig_contrib.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)'
                            )
                            st.plotly_chart(fig_contrib, use_container_width=True)
            else:
                st.warning("⚠️ Sélectionnez au moins 2 actifs pour l'optimisation.")
    
    # ==================== ONGLET MACHINE LEARNING ====================
    with tab_ml:
        st.markdown("""
        <div class="maintenance-container">
            <div class="maintenance-emoji">😊</div>
            <div class="maintenance-text">Allez les jeunes ! Cherchez un peu oub ! :)</div>
            <div class="maintenance-subtext">Cette section est en cours de développement...</div>
            <br><br>
            <div style="font-size: 50px;">🚧 🔧 👷 🛠️ 🚧</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("""
        <div class="frontier-info">
            <strong>🔮 Fonctionnalités à venir :</strong><br><br>
            • Prédiction des prix avec LSTM/GRU<br>
            • Classification des tendances (Haussier/Baissier/Neutre)<br>
            • Optimisation par algorithmes génétiques<br>
            • Apprentissage par renforcement pour trading<br>
            • Détection d'anomalies de marché
        </div>
        """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error("❌ Le fichier de données n'a pas été trouvé. Veuillez vérifier le chemin.")
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #8B7355; font-size: 12px;">
    📊 BRVM Analytics - Stratégie | Optimisation de Portefeuilles
</div>
""", unsafe_allow_html=True)
