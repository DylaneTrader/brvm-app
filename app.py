"""
Application BRVM - Analyse de données boursières
Thème: Claude Anthropic
"""

import streamlit as st

# Configuration de la page - Thème Claude Anthropic
st.set_page_config(
    page_title="BRVM Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé - Thème Claude Anthropic (beige/marron)
st.markdown("""
<style>
    /* Thème Claude Anthropic */
    :root {
        --claude-beige: #FAF9F6;
        --claude-tan: #E8DDD4;
        --claude-brown: #8B7355;
        --claude-dark: #4A3728;
        --claude-accent: #C4A77D;
        --claude-orange: #D97706;
    }
    
    /* Background principal */
    .stApp {
        background-color: var(--claude-beige);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: var(--claude-tan);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--claude-dark);
    }
    
    /* Titres */
    h1, h2, h3, h4, h5, h6 {
        color: var(--claude-dark) !important;
    }
    
    /* Métriques */
    [data-testid="stMetric"] {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid var(--claude-brown);
    }
    
    [data-testid="stMetricLabel"] {
        color: var(--claude-brown) !important;
    }
    
    [data-testid="stMetricValue"] {
        color: var(--claude-dark) !important;
    }
    
    /* Boutons */
    .stButton > button {
        background-color: var(--claude-brown);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: var(--claude-dark);
        transform: translateY(-2px);
    }
    
    /* Selectbox et inputs */
    .stSelectbox > div > div {
        background-color: white;
        border: 1px solid var(--claude-tan);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--claude-tan);
        padding: 5px;
        border-radius: 10px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--claude-dark);
        border-radius: 8px;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--claude-brown) !important;
        color: white !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        border: 1px solid var(--claude-tan);
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: var(--claude-tan);
        border-radius: 8px;
    }
    
    /* Cards personnalisées */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid var(--claude-brown);
        margin-bottom: 10px;
    }
    
    .metric-card-positive {
        border-left-color: #10B981;
    }
    
    .metric-card-negative {
        border-left-color: #EF4444;
    }
    
    /* Logo et branding */
    .claude-logo {
        font-size: 2rem;
        font-weight: bold;
        color: var(--claude-dark);
        text-align: center;
        padding: 20px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px;
        color: var(--claude-brown);
        font-size: 0.8rem;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: #D1FAE5;
        border: 1px solid #10B981;
    }
    
    .stError {
        background-color: #FEE2E2;
        border: 1px solid #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.sidebar.markdown("""
<div class="claude-logo">
    📊 BRVM Analytics
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# Navigation
pages = {
    "🏠 Accueil": "pages/1_🏠_Accueil.py",
    "📋 Overview": "pages/2_📋_Overview.py",
    "📈 Performances": "pages/3_📈_Performances.py",
    "🔗 Corrélations": "pages/4_🔗_Corrélations.py",
    "📐 Indicateurs Techniques": "pages/5_📐_Indicateurs_Techniques.py",
    "📥 Importation": "pages/6_📥_Importation.py",
    "ℹ️ À propos": "pages/7_ℹ️_À_propos.py"
}

# Page d'accueil par défaut
st.markdown("""
# 📊 BRVM Analytics

### Bienvenue dans votre application d'analyse boursière

Utilisez le menu de navigation à gauche pour accéder aux différentes fonctionnalités :

- **🏠 Accueil** : Top & Flop performers avec filtres de période
- **📋 Overview** : Statistiques descriptives du portefeuille
- **📈 Performances** : Performances calendaires et glissantes avec graphiques comparatifs
- **🔗 Corrélations** : Matrices de corrélation pour actions et indices
- **📐 Indicateurs Techniques** : RSI, SMA/EMA, MACD pour les actions
- **📥 Importation** : Importer de nouvelles données
- **ℹ️ À propos** : Documentation des formules et indicateurs

---

<div class="footer">
    Propulsé par Claude Anthropic • BRVM Analytics 2026
</div>
""", unsafe_allow_html=True)
