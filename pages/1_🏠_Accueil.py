"""
Page Accueil - Top & Flop Performers
"""

import streamlit as st
import pandas as pd
import sys
import os

# Ajouter le chemin parent pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import load_data, calculate_returns_for_period, get_top_flop_performers

st.set_page_config(page_title="Accueil - BRVM Analytics", page_icon="🏠", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .top-performer {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .flop-performer {
        background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .performer-symbol {
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .performer-return {
        font-size: 1.4rem;
        font-weight: bold;
    }
    
    .performer-name {
        font-size: 0.85rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏠 Accueil - Top & Flop Performers")

# Charger les données
@st.cache_data
def get_data():
    return load_data()

try:
    data = get_data()
    fiche_actions = data['fiche_actions']
    historique_actions = data['historique_actions']
    
    # Créer un mapping symbole -> nom
    symbol_to_name = dict(zip(fiche_actions['Symbol'], fiche_actions['Name']))
    
    st.markdown("---")
    
    # Filtre de période
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        period_labels = {
            '1D': '1 Jour',
            '1W': '1 Semaine',
            '1M': '1 Mois',
            '3M': '3 Mois',
            '6M': '6 Mois',
            '1Y': '1 An',
            '3Y': '3 Ans'
        }
        
        selected_period = st.selectbox(
            "📅 Sélectionnez la période",
            options=list(period_labels.keys()),
            format_func=lambda x: period_labels[x],
            index=0
        )
    
    st.markdown("---")
    
    # Calculer les rendements
    returns = calculate_returns_for_period(historique_actions, selected_period)
    performers = get_top_flop_performers(returns, n=5)
    
    # Afficher Top & Flop
    col_top, col_flop = st.columns(2)
    
    with col_top:
        st.markdown("### 🚀 Top 5 Performers")
        st.markdown(f"*Meilleures performances sur {period_labels[selected_period]}*")
        
        for i, (symbol, ret) in enumerate(performers['top'].items(), 1):
            name = symbol_to_name.get(symbol, symbol)
            st.markdown(f"""
            <div class="top-performer">
                <div>
                    <span class="performer-symbol">#{i} {symbol}</span>
                    <div class="performer-name">{name}</div>
                </div>
                <span class="performer-return">+{ret:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with col_flop:
        st.markdown("### 📉 Flop 5 Performers")
        st.markdown(f"*Pires performances sur {period_labels[selected_period]}*")
        
        for i, (symbol, ret) in enumerate(performers['flop'].items(), 1):
            name = symbol_to_name.get(symbol, symbol)
            st.markdown(f"""
            <div class="flop-performer">
                <div>
                    <span class="performer-symbol">#{i} {symbol}</span>
                    <div class="performer-name">{name}</div>
                </div>
                <span class="performer-return">{ret:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tableau complet des rendements
    with st.expander("📊 Voir tous les rendements", expanded=False):
        returns_df = pd.DataFrame({
            'Symbole': returns.index,
            'Nom': [symbol_to_name.get(s, s) for s in returns.index],
            f'Rendement {period_labels[selected_period]} (%)': returns.values
        }).dropna()
        
        returns_df = returns_df.sort_values(
            f'Rendement {period_labels[selected_period]} (%)', 
            ascending=False
        ).reset_index(drop=True)
        
        st.dataframe(
            returns_df.style.format({f'Rendement {period_labels[selected_period]} (%)': '{:.2f}%'}),
            use_container_width=True,
            height=400
        )
    
except Exception as e:
    st.error(f"❌ Erreur lors du chargement des données: {e}")
    st.info("Vérifiez que le fichier 'historical stock data.xlsx' est présent dans le dossier de l'application.")
