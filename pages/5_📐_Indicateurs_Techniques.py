"""
Page Indicateurs Techniques - RSI, SMA/EMA, MACD
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    load_data, 
    calculate_rsi, 
    calculate_sma, 
    calculate_ema, 
    calculate_macd
)

st.set_page_config(page_title="Indicateurs Techniques - BRVM Analytics", page_icon="📐", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .indicator-box {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #8B7355;
        margin: 10px 0;
    }
    
    .oversold { color: #10B981; font-weight: bold; }
    .overbought { color: #EF4444; font-weight: bold; }
    .neutral { color: #8B7355; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📐 Indicateurs Techniques")
st.markdown("*Analyse technique pour les actions uniquement*")

@st.cache_data
def get_data():
    return load_data()

try:
    data = get_data()
    fiche_actions = data['fiche_actions']
    historique_actions = data['historique_actions']
    
    # Mapping
    symbol_to_name = dict(zip(fiche_actions['Symbol'], fiche_actions['Name']))
    
    st.markdown("---")
    
    # Sélection de l'action
    col_select, col_info = st.columns([1, 2])
    
    with col_select:
        available_actions = sorted(historique_actions.columns.tolist())
        selected_action = st.selectbox(
            "📊 Sélectionnez une action",
            options=available_actions,
            format_func=lambda x: f"{x} - {symbol_to_name.get(x, x)}",
            key='action_tech'
        )
    
    with col_info:
        if selected_action:
            action_info = fiche_actions[fiche_actions['Symbol'] == selected_action]
            if not action_info.empty:
                st.markdown(f"""
                **{symbol_to_name.get(selected_action, selected_action)}**  
                Secteur: {action_info['Sector'].values[0] if 'Sector' in action_info.columns else 'N/A'}  
                Catégorie: {action_info['Category'].values[0] if 'Category' in action_info.columns else 'N/A'}
                """)
    
    if selected_action:
        prices = historique_actions[selected_action].dropna()
        
        st.markdown("---")
        
        # Tabs pour les différents indicateurs
        tab_rsi, tab_sma_ema, tab_macd = st.tabs(["📊 RSI", "📈 Prix + SMA/EMA", "📉 MACD"])
        
        # ==================== RSI ====================
        with tab_rsi:
            st.subheader("RSI - Relative Strength Index")
            
            col_params, col_legend = st.columns([1, 2])
            
            with col_params:
                rsi_period = st.slider(
                    "Période RSI",
                    min_value=5,
                    max_value=30,
                    value=14,
                    key='rsi_period'
                )
            
            with col_legend:
                st.markdown("""
                <div class="indicator-box">
                    <strong>Interprétation du RSI :</strong><br>
                    • <span class="overbought">RSI > 70</span> : Suracheté (signal de vente potentiel)<br>
                    • <span class="oversold">RSI < 30</span> : Survendu (signal d'achat potentiel)<br>
                    • <span class="neutral">30 ≤ RSI ≤ 70</span> : Zone neutre
                </div>
                """, unsafe_allow_html=True)
            
            # Calculer le RSI
            rsi = calculate_rsi(prices, period=rsi_period)
            
            # Créer le graphique avec 2 sous-graphiques
            fig_rsi = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4],
                subplot_titles=(f"Prix de {selected_action}", f"RSI ({rsi_period} périodes)")
            )
            
            # Prix
            fig_rsi.add_trace(
                go.Scatter(x=prices.index, y=prices, mode='lines', name='Prix', line=dict(color='#8B7355')),
                row=1, col=1
            )
            
            # RSI
            fig_rsi.add_trace(
                go.Scatter(x=rsi.index, y=rsi, mode='lines', name='RSI', line=dict(color='#4A3728')),
                row=2, col=1
            )
            
            # Zones de surachat/survente
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="#EF4444", row=2, col=1)
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="#10B981", row=2, col=1)
            fig_rsi.add_hline(y=50, line_dash="dot", line_color="#8B7355", opacity=0.5, row=2, col=1)
            
            # Zone colorée
            fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(239, 68, 68, 0.1)", line_width=0, row=2, col=1)
            fig_rsi.add_hrect(y0=0, y1=30, fillcolor="rgba(16, 185, 129, 0.1)", line_width=0, row=2, col=1)
            
            fig_rsi.update_layout(
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A3728'),
                showlegend=False,
                hovermode='x unified'
            )
            fig_rsi.update_xaxes(gridcolor='#E8DDD4')
            fig_rsi.update_yaxes(gridcolor='#E8DDD4')
            fig_rsi.update_yaxes(range=[0, 100], row=2, col=1)
            
            st.plotly_chart(fig_rsi, use_container_width=True)
            
            # Valeur actuelle du RSI
            current_rsi = rsi.iloc[-1]
            if current_rsi > 70:
                status = "🔴 Suracheté"
                status_class = "overbought"
            elif current_rsi < 30:
                status = "🟢 Survendu"
                status_class = "oversold"
            else:
                status = "⚪ Neutre"
                status_class = "neutral"
            
            st.markdown(f"""
            <div class="indicator-box">
                <strong>RSI actuel :</strong> <span class="{status_class}">{current_rsi:.2f}</span> - {status}
            </div>
            """, unsafe_allow_html=True)
        
        # ==================== SMA / EMA ====================
        with tab_sma_ema:
            st.subheader("Prix avec Moyennes Mobiles")
            
            col_sma, col_ema = st.columns(2)
            
            with col_sma:
                st.markdown("**SMA - Simple Moving Average**")
                sma_period_1 = st.slider("SMA courte", 5, 50, 20, key='sma1')
                sma_period_2 = st.slider("SMA longue", 20, 200, 50, key='sma2')
            
            with col_ema:
                st.markdown("**EMA - Exponential Moving Average**")
                ema_period_1 = st.slider("EMA courte", 5, 50, 12, key='ema1')
                ema_period_2 = st.slider("EMA longue", 20, 200, 26, key='ema2')
            
            # Calculer les moyennes mobiles
            sma_short = calculate_sma(prices, sma_period_1)
            sma_long = calculate_sma(prices, sma_period_2)
            ema_short = calculate_ema(prices, ema_period_1)
            ema_long = calculate_ema(prices, ema_period_2)
            
            # Graphique
            fig_ma = go.Figure()
            
            # Prix
            fig_ma.add_trace(go.Scatter(
                x=prices.index, y=prices,
                mode='lines', name='Prix',
                line=dict(color='#4A3728', width=2)
            ))
            
            # SMA
            fig_ma.add_trace(go.Scatter(
                x=sma_short.index, y=sma_short,
                mode='lines', name=f'SMA {sma_period_1}',
                line=dict(color='#3B82F6', width=1.5)
            ))
            
            fig_ma.add_trace(go.Scatter(
                x=sma_long.index, y=sma_long,
                mode='lines', name=f'SMA {sma_period_2}',
                line=dict(color='#1D4ED8', width=1.5, dash='dash')
            ))
            
            # EMA
            fig_ma.add_trace(go.Scatter(
                x=ema_short.index, y=ema_short,
                mode='lines', name=f'EMA {ema_period_1}',
                line=dict(color='#10B981', width=1.5)
            ))
            
            fig_ma.add_trace(go.Scatter(
                x=ema_long.index, y=ema_long,
                mode='lines', name=f'EMA {ema_period_2}',
                line=dict(color='#059669', width=1.5, dash='dash')
            ))
            
            fig_ma.update_layout(
                title=f"Prix et Moyennes Mobiles - {selected_action}",
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A3728'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified',
                xaxis_title="Date",
                yaxis_title="Prix"
            )
            fig_ma.update_xaxes(gridcolor='#E8DDD4')
            fig_ma.update_yaxes(gridcolor='#E8DDD4')
            
            st.plotly_chart(fig_ma, use_container_width=True)
            
            # Signaux
            st.markdown("##### Signaux de Trading")
            
            col_sig1, col_sig2 = st.columns(2)
            
            with col_sig1:
                # Signal SMA
                if sma_short.iloc[-1] > sma_long.iloc[-1] and sma_short.iloc[-2] <= sma_long.iloc[-2]:
                    sma_signal = "🟢 **Golden Cross** (SMA courte croise au-dessus de la longue)"
                elif sma_short.iloc[-1] < sma_long.iloc[-1] and sma_short.iloc[-2] >= sma_long.iloc[-2]:
                    sma_signal = "🔴 **Death Cross** (SMA courte croise en dessous de la longue)"
                elif sma_short.iloc[-1] > sma_long.iloc[-1]:
                    sma_signal = "🟢 Tendance haussière (SMA courte > SMA longue)"
                else:
                    sma_signal = "🔴 Tendance baissière (SMA courte < SMA longue)"
                
                st.markdown(f"""
                <div class="indicator-box">
                    <strong>Signal SMA :</strong><br>{sma_signal}
                </div>
                """, unsafe_allow_html=True)
            
            with col_sig2:
                # Signal EMA
                if ema_short.iloc[-1] > ema_long.iloc[-1] and ema_short.iloc[-2] <= ema_long.iloc[-2]:
                    ema_signal = "🟢 **Golden Cross** (EMA courte croise au-dessus de la longue)"
                elif ema_short.iloc[-1] < ema_long.iloc[-1] and ema_short.iloc[-2] >= ema_long.iloc[-2]:
                    ema_signal = "🔴 **Death Cross** (EMA courte croise en dessous de la longue)"
                elif ema_short.iloc[-1] > ema_long.iloc[-1]:
                    ema_signal = "🟢 Tendance haussière (EMA courte > EMA longue)"
                else:
                    ema_signal = "🔴 Tendance baissière (EMA courte < EMA longue)"
                
                st.markdown(f"""
                <div class="indicator-box">
                    <strong>Signal EMA :</strong><br>{ema_signal}
                </div>
                """, unsafe_allow_html=True)
        
        # ==================== MACD ====================
        with tab_macd:
            st.subheader("MACD - Moving Average Convergence Divergence")
            
            col_macd_params, col_macd_info = st.columns([1, 2])
            
            with col_macd_params:
                macd_fast = st.slider("EMA rapide", 5, 20, 12, key='macd_fast')
                macd_slow = st.slider("EMA lente", 15, 40, 26, key='macd_slow')
                macd_signal = st.slider("Signal", 5, 15, 9, key='macd_signal')
            
            with col_macd_info:
                st.markdown("""
                <div class="indicator-box">
                    <strong>Interprétation du MACD :</strong><br>
                    • MACD au-dessus de la ligne signal → Tendance haussière<br>
                    • MACD en dessous de la ligne signal → Tendance baissière<br>
                    • Croisement vers le haut → Signal d'achat<br>
                    • Croisement vers le bas → Signal de vente<br>
                    • Histogramme positif → Momentum haussier<br>
                    • Histogramme négatif → Momentum baissier
                </div>
                """, unsafe_allow_html=True)
            
            # Calculer le MACD
            macd_data = calculate_macd(prices, fast=macd_fast, slow=macd_slow, signal=macd_signal)
            
            # Créer le graphique avec 2 sous-graphiques
            fig_macd = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.1,
                row_heights=[0.6, 0.4],
                subplot_titles=(f"Prix de {selected_action}", "MACD")
            )
            
            # Prix
            fig_macd.add_trace(
                go.Scatter(x=prices.index, y=prices, mode='lines', name='Prix', line=dict(color='#8B7355')),
                row=1, col=1
            )
            
            # MACD Line
            fig_macd.add_trace(
                go.Scatter(
                    x=macd_data['macd'].index, y=macd_data['macd'],
                    mode='lines', name='MACD',
                    line=dict(color='#3B82F6', width=1.5)
                ),
                row=2, col=1
            )
            
            # Signal Line
            fig_macd.add_trace(
                go.Scatter(
                    x=macd_data['signal'].index, y=macd_data['signal'],
                    mode='lines', name='Signal',
                    line=dict(color='#EF4444', width=1.5)
                ),
                row=2, col=1
            )
            
            # Histogram
            colors_hist = ['#10B981' if v >= 0 else '#EF4444' for v in macd_data['histogram']]
            fig_macd.add_trace(
                go.Bar(
                    x=macd_data['histogram'].index, y=macd_data['histogram'],
                    name='Histogramme',
                    marker_color=colors_hist,
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Ligne zéro
            fig_macd.add_hline(y=0, line_dash="dash", line_color="#8B7355", opacity=0.5, row=2, col=1)
            
            fig_macd.update_layout(
                height=600,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A3728'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode='x unified'
            )
            fig_macd.update_xaxes(gridcolor='#E8DDD4')
            fig_macd.update_yaxes(gridcolor='#E8DDD4')
            
            st.plotly_chart(fig_macd, use_container_width=True)
            
            # Signal MACD actuel
            current_macd = macd_data['macd'].iloc[-1]
            current_signal_line = macd_data['signal'].iloc[-1]
            current_histogram = macd_data['histogram'].iloc[-1]
            
            if current_macd > current_signal_line:
                if macd_data['macd'].iloc[-2] <= macd_data['signal'].iloc[-2]:
                    macd_trend = "🟢 **Signal d'achat** (croisement haussier)"
                else:
                    macd_trend = "🟢 Tendance haussière"
            else:
                if macd_data['macd'].iloc[-2] >= macd_data['signal'].iloc[-2]:
                    macd_trend = "🔴 **Signal de vente** (croisement baissier)"
                else:
                    macd_trend = "🔴 Tendance baissière"
            
            col_macd1, col_macd2, col_macd3 = st.columns(3)
            
            with col_macd1:
                st.metric("MACD", f"{current_macd:.4f}")
            
            with col_macd2:
                st.metric("Signal", f"{current_signal_line:.4f}")
            
            with col_macd3:
                st.metric("Histogramme", f"{current_histogram:.4f}", 
                         delta="Positif" if current_histogram > 0 else "Négatif")
            
            st.markdown(f"""
            <div class="indicator-box">
                <strong>Signal MACD actuel :</strong> {macd_trend}
            </div>
            """, unsafe_allow_html=True)

except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")
    st.info("Vérifiez que le fichier 'historical stock data.xlsx' est présent dans le dossier de l'application.")
