"""
Page À propos - Documentation des formules et indicateurs
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(page_title="À propos - BRVM Analytics", page_icon="ℹ️", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3, h4 { color: #4A3728 !important; }
    
    .formula-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #8B7355;
        margin: 15px 0;
        font-family: 'Courier New', monospace;
    }
    
    .example-box {
        background: #E8DDD4;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .interpretation-box {
        background: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #10B981;
        margin: 10px 0;
    }
    
    .warning-box {
        background: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #F59E0B;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("ℹ️ À propos - Documentation")

st.markdown("""
Cette page explique les formules de calcul utilisées dans l'application et comment interpréter les différents indicateurs.
""")

st.markdown("---")

# Navigation par sections
section = st.selectbox(
    "📚 Sélectionnez une section",
    [
        "📈 Formules de Performance",
        "📐 Indicateurs Techniques",
        "🔗 Corrélations",
        "� Bêta (Beta)",
        "�📊 Statistiques Descriptives",
        "ℹ️ À propos de l'application"
    ]
)

# ==================== FORMULES DE PERFORMANCE ====================
if section == "📈 Formules de Performance":
    st.header("📈 Formules de Performance")
    
    st.subheader("1. Rendement Simple (Return)")
    
    st.markdown("""
    Le rendement mesure la variation en pourcentage du prix d'un actif sur une période donnée.
    """)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule :</strong><br><br>
        Rendement (%) = ((Prix Final - Prix Initial) / Prix Initial) × 100<br><br>
        <em>ou de façon équivalente :</em><br><br>
        Rendement (%) = ((Prix Final / Prix Initial) - 1) × 100
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="example-box">
        <strong>📝 Exemple :</strong><br>
        Si une action vaut 100€ le 1er janvier et 115€ le 31 décembre :<br>
        Rendement = ((115 - 100) / 100) × 100 = <strong>+15%</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("2. Performances Calendaires")
    
    st.markdown("""
    Les performances calendaires mesurent le rendement depuis le début d'une période calendaire spécifique :
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        | Sigle | Signification | Début de période |
        |-------|---------------|------------------|
        | **WTD** | Week-to-Date | Lundi de la semaine en cours |
        | **MTD** | Month-to-Date | 1er jour du mois |
        | **QTD** | Quarter-to-Date | 1er jour du trimestre |
        """)
    
    with col2:
        st.markdown("""
        | Sigle | Signification | Début de période |
        |-------|---------------|------------------|
        | **STD** | Semester-to-Date | 1er janvier ou 1er juillet |
        | **YTD** | Year-to-Date | 1er janvier |
        """)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Interprétation :</strong><br>
        Un YTD de +20% signifie que l'actif a gagné 20% depuis le 1er janvier de l'année en cours.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("3. Performances Glissantes (Rolling)")
    
    st.markdown("""
    Les performances glissantes mesurent le rendement sur une fenêtre de temps mobile :
    """)
    
    st.markdown("""
    | Période | Nombre de jours de trading (~) |
    |---------|--------------------------------|
    | 1 Semaine | 7 jours |
    | 1 Mois | 30 jours |
    | 3 Mois | 91 jours |
    | 6 Mois | 182 jours |
    | 1 An | 365 jours |
    | 3 Ans | 1095 jours |
    """)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Note :</strong><br>
        Nous utilisons 365 jours par an pour les calculs de périodes.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("4. Rendement Cumulé Normalisé (Base 100)")
    
    st.markdown("""
    Pour comparer l'évolution de plusieurs actifs, on normalise les prix à une base 100 :
    """)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule :</strong><br><br>
        Valeur Normalisée(t) = (Prix(t) / Prix(t₀)) × 100<br><br>
        <em>où t₀ est la date de début de la période</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemple graphique
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    price1 = 100 * (1 + np.random.randn(100).cumsum() * 0.02)
    price2 = 50 * (1 + np.random.randn(100).cumsum() * 0.015)
    
    norm1 = (price1 / price1[0]) * 100
    norm2 = (price2 / price2[0]) * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=norm1, name='Action A (départ 100€)', line=dict(color='#8B7355')))
    fig.add_trace(go.Scatter(x=dates, y=norm2, name='Action B (départ 50€)', line=dict(color='#10B981')))
    fig.add_hline(y=100, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title="Exemple : Comparaison de deux actions avec normalisation base 100",
        xaxis_title="Date",
        yaxis_title="Valeur normalisée (base 100)",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4A3728')
    )
    fig.update_xaxes(gridcolor='#E8DDD4')
    fig.update_yaxes(gridcolor='#E8DDD4')
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Interprétation :</strong><br>
        Grâce à la normalisation, on peut comparer directement deux actifs ayant des prix très différents.
        Une valeur de 120 signifie +20% depuis le début, quelle que soit la valeur initiale.
    </div>
    """, unsafe_allow_html=True)

# ==================== INDICATEURS TECHNIQUES ====================
elif section == "📐 Indicateurs Techniques":
    st.header("📐 Indicateurs Techniques")
    
    st.subheader("1. RSI - Relative Strength Index")
    
    st.markdown("""
    Le RSI mesure la vitesse et l'amplitude des mouvements de prix récents pour évaluer les conditions de surachat ou de survente.
    """)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule (étapes) :</strong><br><br>
        1. Calculer les variations journalières : Δ = Prix(t) - Prix(t-1)<br><br>
        2. Séparer les gains et les pertes :<br>
           • Gains = Δ si Δ > 0, sinon 0<br>
           • Pertes = |Δ| si Δ < 0, sinon 0<br><br>
        3. Calculer les moyennes sur N périodes :<br>
           • Moyenne des Gains = Moyenne(Gains sur N jours)<br>
           • Moyenne des Pertes = Moyenne(Pertes sur N jours)<br><br>
        4. Calculer le RS (Relative Strength) :<br>
           RS = Moyenne des Gains / Moyenne des Pertes<br><br>
        5. Calculer le RSI :<br>
           <strong>RSI = 100 - (100 / (1 + RS))</strong>
    </div>
    """, unsafe_allow_html=True)
    
    # Graphique explicatif RSI
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig_rsi = go.Figure()
        
        # Zones
        fig_rsi.add_hrect(y0=70, y1=100, fillcolor="rgba(239, 68, 68, 0.2)", line_width=0)
        fig_rsi.add_hrect(y0=0, y1=30, fillcolor="rgba(16, 185, 129, 0.2)", line_width=0)
        
        # Lignes
        fig_rsi.add_hline(y=70, line_color="#EF4444", line_dash="dash", annotation_text="Surachat (70)")
        fig_rsi.add_hline(y=30, line_color="#10B981", line_dash="dash", annotation_text="Survente (30)")
        fig_rsi.add_hline(y=50, line_color="gray", line_dash="dot", annotation_text="Neutre (50)")
        
        # Exemple de RSI
        x = np.linspace(0, 4*np.pi, 100)
        rsi_example = 50 + 30 * np.sin(x) + np.random.randn(100) * 5
        rsi_example = np.clip(rsi_example, 0, 100)
        
        fig_rsi.add_trace(go.Scatter(y=rsi_example, mode='lines', name='RSI', line=dict(color='#4A3728', width=2)))
        
        fig_rsi.update_layout(
            title="Exemple de RSI avec zones d'interprétation",
            yaxis_title="RSI",
            yaxis=dict(range=[0, 100]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            font=dict(color='#4A3728')
        )
        fig_rsi.update_xaxes(gridcolor='#E8DDD4')
        fig_rsi.update_yaxes(gridcolor='#E8DDD4')
        
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    with col2:
        st.markdown("""
        <div class="interpretation-box">
            <strong>💡 Interprétation :</strong><br><br>
            • <span style="color: #EF4444; font-weight: bold;">RSI > 70</span><br>
              Zone de surachat<br>
              Signal de vente potentiel<br><br>
            • <span style="color: #10B981; font-weight: bold;">RSI < 30</span><br>
              Zone de survente<br>
              Signal d'achat potentiel<br><br>
            • <span style="font-weight: bold;">30 ≤ RSI ≤ 70</span><br>
              Zone neutre
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("2. Moyennes Mobiles (SMA & EMA)")
    
    col_sma, col_ema = st.columns(2)
    
    with col_sma:
        st.markdown("#### SMA - Simple Moving Average")
        st.markdown("""
        <div class="formula-box">
            <strong>Formule :</strong><br><br>
            SMA(N) = (P₁ + P₂ + ... + Pₙ) / N<br><br>
            <em>= Moyenne arithmétique des N derniers prix</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="example-box">
            <strong>📝 Exemple (SMA 5 jours) :</strong><br>
            Prix : 10, 11, 12, 11, 13<br>
            SMA = (10+11+12+11+13) / 5 = <strong>11.4</strong>
        </div>
        """, unsafe_allow_html=True)
    
    with col_ema:
        st.markdown("#### EMA - Exponential Moving Average")
        st.markdown("""
        <div class="formula-box">
            <strong>Formule :</strong><br><br>
            EMA(t) = Prix(t) × k + EMA(t-1) × (1-k)<br><br>
            où k = 2 / (N + 1)<br><br>
            <em>= Moyenne pondérée donnant plus de poids aux prix récents</em>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="example-box">
            <strong>📝 Différence avec SMA :</strong><br>
            L'EMA réagit plus rapidement aux changements de prix récents car elle leur attribue un poids plus important.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Signaux de Trading :</strong><br><br>
        • <strong>Golden Cross</strong> 🟢 : La MA courte croise au-dessus de la MA longue → Signal d'achat<br>
        • <strong>Death Cross</strong> 🔴 : La MA courte croise en dessous de la MA longue → Signal de vente<br>
        • <strong>Prix > MA</strong> : Tendance haussière<br>
        • <strong>Prix < MA</strong> : Tendance baissière
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("3. MACD - Moving Average Convergence Divergence")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formules :</strong><br><br>
        1. <strong>Ligne MACD</strong> = EMA(12) - EMA(26)<br><br>
        2. <strong>Ligne Signal</strong> = EMA(9) de la ligne MACD<br><br>
        3. <strong>Histogramme</strong> = Ligne MACD - Ligne Signal
    </div>
    """, unsafe_allow_html=True)
    
    # Graphique MACD explicatif
    x = np.linspace(0, 4*np.pi, 200)
    macd_line = 2 * np.sin(x) + 0.5 * np.sin(2*x)
    signal_line = 2 * np.sin(x - 0.3) + 0.5 * np.sin(2*x - 0.3)
    histogram = macd_line - signal_line
    
    fig_macd = go.Figure()
    
    # Histogramme
    colors = ['#10B981' if h >= 0 else '#EF4444' for h in histogram]
    fig_macd.add_trace(go.Bar(y=histogram, marker_color=colors, name='Histogramme', opacity=0.7))
    
    # Lignes
    fig_macd.add_trace(go.Scatter(y=macd_line, mode='lines', name='MACD', line=dict(color='#3B82F6', width=2)))
    fig_macd.add_trace(go.Scatter(y=signal_line, mode='lines', name='Signal', line=dict(color='#EF4444', width=2)))
    
    fig_macd.add_hline(y=0, line_color="gray", line_dash="dash")
    
    fig_macd.update_layout(
        title="Composantes du MACD",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4A3728'),
        legend=dict(orientation="h", yanchor="bottom", y=1.02)
    )
    fig_macd.update_xaxes(gridcolor='#E8DDD4')
    fig_macd.update_yaxes(gridcolor='#E8DDD4')
    
    st.plotly_chart(fig_macd, use_container_width=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Interprétation du MACD :</strong><br><br>
        • <strong>MACD > Signal</strong> : Momentum haussier → Tendance à la hausse<br>
        • <strong>MACD < Signal</strong> : Momentum baissier → Tendance à la baisse<br>
        • <strong>Croisement vers le haut</strong> : Signal d'achat potentiel<br>
        • <strong>Croisement vers le bas</strong> : Signal de vente potentiel<br>
        • <strong>Histogramme positif croissant</strong> : Accélération haussière<br>
        • <strong>Histogramme négatif décroissant</strong> : Accélération baissière
    </div>
    """, unsafe_allow_html=True)

# ==================== CORRÉLATIONS ====================
elif section == "🔗 Corrélations":
    st.header("🔗 Corrélations")
    
    st.subheader("Coefficient de Corrélation")
    
    st.markdown("""
    La corrélation mesure la force et la direction de la relation linéaire entre deux variables.
    """)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule (Corrélation de Pearson) :</strong><br><br>
        ρ(X,Y) = Cov(X,Y) / (σ_X × σ_Y)<br><br>
        où :<br>
        • Cov(X,Y) = Covariance entre X et Y<br>
        • σ_X = Écart-type de X<br>
        • σ_Y = Écart-type de Y
    </div>
    """, unsafe_allow_html=True)
    
    # Exemples visuels de corrélation
    st.markdown("##### Exemples visuels de corrélation")
    
    np.random.seed(42)
    n = 100
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        x1 = np.random.randn(n)
        y1 = 0.9 * x1 + 0.1 * np.random.randn(n)
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=x1, y=y1, mode='markers', marker=dict(color='#10B981')))
        fig1.update_layout(title="Corrélation forte positive (ρ ≈ 0.95)", height=300,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        x2 = np.random.randn(n)
        y2 = np.random.randn(n)
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=x2, y=y2, mode='markers', marker=dict(color='#8B7355')))
        fig2.update_layout(title="Pas de corrélation (ρ ≈ 0)", height=300,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
    
    with col3:
        x3 = np.random.randn(n)
        y3 = -0.9 * x3 + 0.1 * np.random.randn(n)
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=x3, y=y3, mode='markers', marker=dict(color='#EF4444')))
        fig3.update_layout(title="Corrélation forte négative (ρ ≈ -0.95)", height=300,
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Interprétation des valeurs de corrélation :</strong><br><br>
        <table>
            <tr><td><strong>0.8 à 1.0</strong></td><td>Très forte corrélation positive</td></tr>
            <tr><td><strong>0.6 à 0.8</strong></td><td>Forte corrélation positive</td></tr>
            <tr><td><strong>0.4 à 0.6</strong></td><td>Corrélation modérée positive</td></tr>
            <tr><td><strong>-0.2 à 0.2</strong></td><td>Corrélation faible ou nulle</td></tr>
            <tr><td><strong>-0.6 à -0.4</strong></td><td>Corrélation modérée négative</td></tr>
            <tr><td><strong>-1.0 à -0.8</strong></td><td>Très forte corrélation négative</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Attention :</strong><br>
        Corrélation ≠ Causalité ! Deux actifs corrélés ne signifie pas que l'un cause les mouvements de l'autre.
    </div>
    """, unsafe_allow_html=True)

# ==================== BÊTA ====================
elif section == "📉 Bêta (Beta)":
    st.header("📉 Bêta (Beta)")
    
    st.markdown("""
    Le **bêta (β)** est un indicateur fondamental qui mesure la sensibilité d'une action aux mouvements du marché (représenté par un indice de référence).
    """)
    
    st.subheader("1. Formule du Bêta")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule :</strong><br><br>
        β = Cov(Raction, Rmarché) / Var(Rmarché)<br><br>
        où :<br>
        • Cov(Raction, Rmarché) = Covariance entre les rendements de l'action et du marché<br>
        • Var(Rmarché) = Variance des rendements du marché<br><br>
        <em>Le bêta peut aussi s'écrire :</em><br><br>
        β = ρ × (σaction / σmarché)<br><br>
        où ρ est la corrélation et σ les volatilités
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("2. Interprétation du Bêta")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        | Valeur du Bêta | Interprétation |
        |----------------|----------------|
        | **β > 1.5** | Très agressif |
        | **1 < β ≤ 1.5** | Agressif |
        | **β ≈ 1** | Neutre (suit le marché) |
        | **0.5 ≤ β < 1** | Défensif |
        | **β < 0.5** | Très défensif |
        | **β < 0** | Inversé (rare) |
        """)
    
    with col2:
        st.markdown("""
        <div class="interpretation-box">
            <strong>💡 Exemples concrets :</strong><br><br>
            • <strong>β = 1.5</strong> : Si le marché monte de 10%, l'action monte en moyenne de 15%<br><br>
            • <strong>β = 1.0</strong> : L'action suit exactement le marché<br><br>
            • <strong>β = 0.5</strong> : Si le marché monte de 10%, l'action monte en moyenne de 5%<br><br>
            • <strong>β = -0.5</strong> : Si le marché monte de 10%, l'action baisse en moyenne de 5%
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("3. Illustration Graphique")
    
    # Créer des exemples visuels
    np.random.seed(42)
    n_points = 100
    market_returns = np.random.randn(n_points) * 2  # Rendements marché
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Beta > 1 (Agressif)
        aggressive_returns = 1.5 * market_returns + np.random.randn(n_points) * 1
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=market_returns, y=aggressive_returns, mode='markers', 
                                  marker=dict(color='#EF4444', size=6, opacity=0.7)))
        x_line = np.linspace(-6, 6, 50)
        fig1.add_trace(go.Scatter(x=x_line, y=1.5*x_line, mode='lines', 
                                  line=dict(color='#4A3728', width=2)))
        fig1.update_layout(title="β = 1.5 (Agressif)", height=300,
                          xaxis_title="Marché (%)", yaxis_title="Action (%)",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig1, use_container_width=True)
        st.markdown("🔴 Amplifie les mouvements")
    
    with col2:
        # Beta = 1 (Neutre)
        neutral_returns = 1.0 * market_returns + np.random.randn(n_points) * 0.8
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=market_returns, y=neutral_returns, mode='markers', 
                                  marker=dict(color='#8B7355', size=6, opacity=0.7)))
        fig2.add_trace(go.Scatter(x=x_line, y=1.0*x_line, mode='lines', 
                                  line=dict(color='#4A3728', width=2)))
        fig2.update_layout(title="β = 1.0 (Neutre)", height=300,
                          xaxis_title="Marché (%)", yaxis_title="Action (%)",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown("🟢 Suit le marché")
    
    with col3:
        # Beta < 1 (Défensif)
        defensive_returns = 0.5 * market_returns + np.random.randn(n_points) * 0.6
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(x=market_returns, y=defensive_returns, mode='markers', 
                                  marker=dict(color='#3B82F6', size=6, opacity=0.7)))
        fig3.add_trace(go.Scatter(x=x_line, y=0.5*x_line, mode='lines', 
                                  line=dict(color='#4A3728', width=2)))
        fig3.update_layout(title="β = 0.5 (Défensif)", height=300,
                          xaxis_title="Marché (%)", yaxis_title="Action (%)",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig3, use_container_width=True)
        st.markdown("🔵 Atténue les mouvements")
    
    st.markdown("---")
    
    st.subheader("4. Bêta Glissant (Rolling Beta)")
    
    st.markdown("""
    Le **bêta glissant** calcule le bêta sur une fenêtre mobile de temps, permettant de voir comment la sensibilité au marché évolue.
    """)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Calcul :</strong><br><br>
        β(t) = Bêta calculé sur les N derniers jours se terminant à la date t<br><br>
        <em>Fenêtres courantes : 30 jours (1 mois), 91 jours (3 mois), 365 jours (1 an)</em>
    </div>
    """, unsafe_allow_html=True)
    
    # Exemple de bêta glissant
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    base_beta = 1.0
    rolling_beta_example = base_beta + 0.3 * np.sin(np.linspace(0, 3*np.pi, 200)) + np.random.randn(200) * 0.1
    
    fig_rolling = go.Figure()
    fig_rolling.add_trace(go.Scatter(x=dates, y=rolling_beta_example, mode='lines',
                                     line=dict(color='#8B7355', width=2), name='Bêta glissant'))
    fig_rolling.add_hline(y=1, line_dash="dash", line_color="gray", annotation_text="β = 1")
    fig_rolling.add_hrect(y0=1.1, y1=1.5, fillcolor="rgba(239, 68, 68, 0.1)", line_width=0)
    fig_rolling.add_hrect(y0=0.5, y1=0.9, fillcolor="rgba(59, 130, 246, 0.1)", line_width=0)
    
    fig_rolling.update_layout(
        title="Exemple d'évolution du Bêta Glissant",
        xaxis_title="Date",
        yaxis_title="Bêta",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#4A3728'),
        height=350
    )
    fig_rolling.update_xaxes(gridcolor='#E8DDD4')
    fig_rolling.update_yaxes(gridcolor='#E8DDD4')
    
    st.plotly_chart(fig_rolling, use_container_width=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Utilité du bêta glissant :</strong><br><br>
        • Identifier les changements de comportement de l'action<br>
        • Détecter si l'action devient plus ou moins risquée<br>
        • Ajuster la pondération dans un portefeuille en fonction du risque
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("5. Applications Pratiques")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 📈 Gestion de Portefeuille
        
        Le bêta du portefeuille est la moyenne pondérée des bêtas :
        
        **βportefeuille = Σ (wi × βi)**
        
        où wi est le poids de chaque action.
        
        ---
        
        **Stratégies :**
        - **Marché haussier** : Surpondérer les actions à bêta élevé
        - **Marché baissier** : Surpondérer les actions à bêta faible
        - **Volatilité élevée** : Préférer les bêtas faibles
        """)
    
    with col2:
        st.markdown("""
        ### 🎯 CAPM (Capital Asset Pricing Model)
        
        Le bêta est central dans le modèle CAPM :
        
        **E(Ri) = Rf + βi × (E(Rm) - Rf)**
        
        où :
        - E(Ri) = Rendement attendu de l'action
        - Rf = Taux sans risque
        - E(Rm) = Rendement attendu du marché
        
        ---
        
        Le terme **(E(Rm) - Rf)** est appelé la **prime de risque du marché**.
        """)
    
    st.markdown("""
    <div class="warning-box">
        <strong>⚠️ Limitations du Bêta :</strong><br><br>
        • Le bêta est basé sur des données historiques et peut changer<br>
        • Il ne capture que le risque systématique (lié au marché)<br>
        • Le choix de l'indice de référence influence fortement le résultat<br>
        • La période d'estimation impacte la valeur obtenue
    </div>
    """, unsafe_allow_html=True)

# ==================== STATISTIQUES DESCRIPTIVES ====================
elif section == "📊 Statistiques Descriptives":
    st.header("📊 Statistiques Descriptives")
    
    st.subheader("1. Volatilité Annualisée")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule :</strong><br><br>
        Volatilité Annualisée = σ_journalier × √365<br><br>
        où :<br>
        • σ_journalier = Écart-type des rendements journaliers<br>
        • 365 = Nombre de jours par an
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="example-box">
        <strong>📝 Exemple :</strong><br>
        Si la volatilité journalière est de 1.5%<br>
        Volatilité annualisée = 1.5% × √365 ≈ <strong>28.7%</strong>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.subheader("2. Rendement Total")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formule :</strong><br><br>
        Rendement Total (%) = ((Prix Final / Prix Initial) - 1) × 100
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="interpretation-box">
        <strong>💡 Utilité des statistiques descriptives :</strong><br><br>
        • <strong>Volatilité</strong> : Mesure le risque d'un actif. Plus elle est élevée, plus l'actif est risqué.<br>
        • <strong>Prix Min/Max</strong> : Montre l'amplitude des variations de prix.<br>
        • <strong>Rendement Total</strong> : Performance globale sur toute la période d'observation.
    </div>
    """, unsafe_allow_html=True)

# ==================== À PROPOS DE L'APPLICATION ====================
elif section == "ℹ️ À propos de l'application":
    st.header("ℹ️ À propos de BRVM Analytics")
    
    st.markdown("""
    ### 🎯 Objectif
    
    BRVM Analytics est une application d'analyse boursière conçue pour permettre aux investisseurs et analystes 
    de suivre et analyser les performances des actions et indices.
    
    ### 📊 Fonctionnalités
    
    | Page | Description |
    |------|-------------|
    | **Accueil** | Top & Flop performers avec filtres de période |
    | **Overview** | Statistiques descriptives du portefeuille |
    | **Performances** | Performances calendaires et glissantes avec graphiques |
    | **Corrélations & Bêta** | Matrices de corrélation et analyse du bêta |
    | **Indicateurs Techniques** | RSI, SMA/EMA, MACD |
    | **Importation** | Ajouter de nouvelles données |
    | **Chatbot IA** | Assistant intelligent pour l'analyse financière |
    | **Stratégie** | Construction et optimisation de portefeuilles (Manuel, Markowitz, Risk Parity) |
    
    ### 🛠️ Technologies
    
    - **Streamlit** : Framework web Python
    - **Pandas** : Manipulation de données
    - **Plotly** : Visualisations interactives
    - **NumPy** : Calculs numériques
    
    ### 🎨 Design
    
    Cette application utilise le thème **Claude Anthropic** caractérisé par :
    - Des tons beiges et marron chaleureux
    - Une interface épurée et professionnelle
    - Une navigation intuitive
    
    ---
    
    <div style="text-align: center; padding: 20px; color: #8B7355;">
        <strong>BRVM Analytics</strong><br>
        Propulsé par Claude Anthropic<br>
        © 2026
    </div>
    """, unsafe_allow_html=True)
