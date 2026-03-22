"""
Page Importation - Importer de nouvelles données
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Importation - BRVM Analytics", page_icon="📥", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .import-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #8B7355;
        margin: 15px 0;
    }
    
    .success-box {
        background: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin: 10px 0;
    }
    
    .warning-box {
        background: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #F59E0B;
        margin: 10px 0;
    }
    
    .error-box {
        background: #FEE2E2;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #EF4444;
        margin: 10px 0;
    }
    
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
    }
    
    .comparison-table th, .comparison-table td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid #E8DDD4;
    }
    
    .comparison-table th {
        background-color: #E8DDD4;
        color: #4A3728;
    }
    
    .mode-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #E8DDD4;
        margin: 10px 0;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mode-card:hover {
        border-color: #8B7355;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .mode-card.selected {
        border-color: #8B7355;
        background: #FAF9F6;
    }
</style>
""", unsafe_allow_html=True)

st.title("📥 Importation de Données")

# Chemin du fichier de données principal
DATA_FILE = "historical stock data.xlsx"

def get_existing_data():
    """Charge les données existantes"""
    try:
        xl = pd.ExcelFile(DATA_FILE)
        
        historique_actions = pd.read_excel(xl, sheet_name='historique_actions')
        historique_actions['Date'] = pd.to_datetime(historique_actions['Date'])
        historique_actions = historique_actions.set_index('Date').sort_index()
        
        historique_indices = pd.read_excel(xl, sheet_name='historique_indices')
        historique_indices['Date'] = pd.to_datetime(historique_indices['Date'])
        historique_indices = historique_indices.set_index('Date').sort_index()
        
        # Charger les fiches (métadonnées)
        fiche_actions = pd.read_excel(xl, sheet_name='fiche_actions')
        fiche_indices = pd.read_excel(xl, sheet_name='fiche_indices')
        
        return {
            'historique_actions': historique_actions,
            'historique_indices': historique_indices,
            'fiche_actions': fiche_actions,
            'fiche_indices': fiche_indices,
            'excel_file': xl
        }
    except Exception as e:
        st.error(f"Erreur lors du chargement des données existantes: {e}")
        return None

def analyze_new_data(new_df, existing_df, data_type):
    """Analyse les nouvelles données par rapport aux existantes"""
    analysis = {
        'total_rows_new': len(new_df),
        'total_rows_existing': len(existing_df),
        'total_new_rows': 0,
        'duplicate_rows': 0,
        'new_columns': [],
        'missing_columns': [],
        'common_columns': [],
        'date_range_new': None,
        'date_range_existing': None,
        'new_dates': [],
        'overlapping_dates': []
    }
    
    # Convertir la colonne Date si nécessaire
    if 'Date' in new_df.columns:
        new_df['Date'] = pd.to_datetime(new_df['Date'])
        new_df = new_df.set_index('Date').sort_index()
    
    # Analyse des dates
    analysis['date_range_new'] = (new_df.index.min(), new_df.index.max())
    analysis['date_range_existing'] = (existing_df.index.min(), existing_df.index.max())
    
    # Trouver les nouvelles dates et dates en commun
    existing_dates = set(existing_df.index)
    new_dates = set(new_df.index)
    
    unique_new_dates = new_dates - existing_dates
    overlapping_dates = new_dates & existing_dates
    
    analysis['new_dates'] = sorted(list(unique_new_dates))
    analysis['overlapping_dates'] = sorted(list(overlapping_dates))
    analysis['total_new_rows'] = len(unique_new_dates)
    analysis['duplicate_rows'] = len(overlapping_dates)
    
    # Analyse des colonnes
    existing_cols = set(existing_df.columns)
    new_cols = set(new_df.columns)
    
    analysis['new_columns'] = sorted(list(new_cols - existing_cols))
    analysis['missing_columns'] = sorted(list(existing_cols - new_cols))
    analysis['common_columns'] = sorted(list(new_cols & existing_cols))
    
    return analysis, new_df

def merge_data_append(existing_df, new_df, new_dates):
    """Ajoute uniquement les nouvelles lignes (dates non existantes)"""
    # Filtrer uniquement les nouvelles dates
    new_df_filtered = new_df.loc[new_df.index.isin(new_dates)]
    
    # Trouver les colonnes communes
    common_cols = list(set(existing_df.columns) & set(new_df_filtered.columns))
    
    # Ne garder que les colonnes communes pour les nouvelles données
    new_df_filtered = new_df_filtered[common_cols]
    
    # Concaténer
    merged = pd.concat([existing_df, new_df_filtered]).sort_index()
    
    # Supprimer les doublons éventuels
    merged = merged[~merged.index.duplicated(keep='first')]
    
    return merged

def replace_data(existing_df, new_df):
    """Remplace complètement les données existantes par les nouvelles"""
    # Garder la même structure de colonnes que l'existant si possible
    common_cols = list(set(existing_df.columns) & set(new_df.columns))
    
    # Utiliser les nouvelles données avec les colonnes communes
    replaced = new_df[common_cols].copy()
    replaced = replaced.sort_index()
    
    return replaced

def save_to_excel(sheet_name, new_data, has_index=True):
    """Sauvegarde les données dans le fichier Excel"""
    with pd.ExcelFile(DATA_FILE) as xl:
        all_sheets = {}
        for sheet in xl.sheet_names:
            if sheet == sheet_name:
                if has_index:
                    all_sheets[sheet] = new_data.reset_index()
                else:
                    all_sheets[sheet] = new_data
            else:
                all_sheets[sheet] = pd.read_excel(xl, sheet_name=sheet)
    
    with pd.ExcelWriter(DATA_FILE, engine='openpyxl') as writer:
        for sname, df in all_sheets.items():
            df.to_excel(writer, sheet_name=sname, index=False)

def analyze_fiche_data(new_df, existing_df, key_column='Symbol'):
    """Analyse les données de type fiche (métadonnées) par rapport aux existantes"""
    analysis = {
        'total_rows_new': len(new_df),
        'total_rows_existing': len(existing_df),
        'new_items': [],
        'existing_items': [],
        'updated_items': [],
        'new_columns': [],
        'missing_columns': [],
        'common_columns': []
    }
    
    # Colonnes
    existing_cols = set(existing_df.columns)
    new_cols = set(new_df.columns)
    
    analysis['new_columns'] = sorted(list(new_cols - existing_cols))
    analysis['missing_columns'] = sorted(list(existing_cols - new_cols))
    analysis['common_columns'] = sorted(list(new_cols & existing_cols))
    
    # Items (basé sur la clé - généralement Symbol)
    if key_column in new_df.columns and key_column in existing_df.columns:
        existing_keys = set(existing_df[key_column].dropna().unique())
        new_keys = set(new_df[key_column].dropna().unique())
        
        analysis['new_items'] = sorted(list(new_keys - existing_keys))
        analysis['existing_items'] = sorted(list(existing_keys))
        analysis['updated_items'] = sorted(list(new_keys & existing_keys))
    
    return analysis

def merge_fiche_append(existing_df, new_df, key_column='Symbol'):
    """Ajoute uniquement les nouvelles lignes (clés non existantes)"""
    if key_column not in new_df.columns or key_column not in existing_df.columns:
        return existing_df
    
    existing_keys = set(existing_df[key_column].dropna().unique())
    
    # Filtrer uniquement les nouvelles clés
    new_rows = new_df[~new_df[key_column].isin(existing_keys)]
    
    # Garder uniquement les colonnes communes
    common_cols = list(set(existing_df.columns) & set(new_rows.columns))
    new_rows = new_rows[common_cols]
    
    # Concaténer
    merged = pd.concat([existing_df, new_rows], ignore_index=True)
    
    return merged

def replace_fiche_data(existing_df, new_df):
    """Remplace complètement les données de fiche"""
    # Garder la même structure de colonnes si possible
    common_cols = list(set(existing_df.columns) & set(new_df.columns))
    
    return new_df[common_cols].copy()

st.markdown("---")

st.markdown("""
<div class="import-box">
    <h4>📌 Instructions d'importation</h4>
    <p>Cette fonctionnalité vous permet de gérer vos données avec deux modes d'importation :</p>
    <ul>
        <li><strong>🔄 Écraser :</strong> Remplace complètement les données existantes par les nouvelles</li>
        <li><strong>➕ Ajouter :</strong> Importe uniquement les nouvelles lignes (dates non existantes)</li>
    </ul>
    <p><strong>Format attendu :</strong> Fichier Excel (.xlsx) avec colonnes Date + Symboles</p>
</div>
""", unsafe_allow_html=True)

# Informations sur les données actuelles
existing_data = get_existing_data()
if existing_data:
    st.markdown("##### 📊 Données actuelles")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.info(f"**Historique Actions**\n{len(existing_data['historique_actions'])} lignes")
    with col2:
        st.info(f"**Historique Indices**\n{len(existing_data['historique_indices'])} lignes")
    with col3:
        st.info(f"**Fiche Actions**\n{len(existing_data['fiche_actions'])} titres")
    with col4:
        st.info(f"**Fiche Indices**\n{len(existing_data['fiche_indices'])} lignes")

st.markdown("---")

# Tabs pour tous les types de données
tab_hist_actions, tab_hist_indices, tab_fiche_actions, tab_fiche_indices = st.tabs([
    "📊 Historique Actions", 
    "📈 Historique Indices",
    "📋 Fiche Actions",
    "📑 Fiche Indices"
])

def render_import_section(uploaded_file, data_type, existing_df, sheet_name, key_prefix):
    """Rendu de la section d'importation pour actions ou indices"""
    
    if uploaded_file:
        try:
            # Charger le nouveau fichier
            new_df = pd.read_excel(uploaded_file)
            
            # Aperçu des données
            st.markdown("##### 📄 Aperçu des données importées")
            st.dataframe(new_df.head(10), use_container_width=True, height=200)
            
            # Analyser les données
            analysis, processed_new_df = analyze_new_data(new_df.copy(), existing_df, data_type)
            
            st.markdown("---")
            st.markdown("##### 🔍 Analyse comparative")
            
            # Tableau de comparaison
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Lignes existantes", analysis['total_rows_existing'])
            with col2:
                st.metric("Lignes importées", analysis['total_rows_new'])
            with col3:
                st.metric("Nouvelles dates", analysis['total_new_rows'], 
                         delta=f"+{analysis['total_new_rows']}" if analysis['total_new_rows'] > 0 else "0")
            with col4:
                st.metric("Dates en commun", analysis['duplicate_rows'])
            
            # Détails des plages de dates
            st.markdown(f"""
            <div class="import-box">
                <table class="comparison-table">
                    <tr>
                        <th>📅 Plages de dates</th>
                        <th>Données existantes</th>
                        <th>Données importées</th>
                    </tr>
                    <tr>
                        <td><strong>Date début</strong></td>
                        <td>{analysis['date_range_existing'][0].strftime('%d/%m/%Y')}</td>
                        <td>{analysis['date_range_new'][0].strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td><strong>Date fin</strong></td>
                        <td>{analysis['date_range_existing'][1].strftime('%d/%m/%Y')}</td>
                        <td>{analysis['date_range_new'][1].strftime('%d/%m/%Y')}</td>
                    </tr>
                    <tr>
                        <td><strong>Colonnes</strong></td>
                        <td>{len(existing_df.columns)} symboles</td>
                        <td>{len(processed_new_df.columns)} symboles</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Alertes sur les colonnes
            if analysis['new_columns']:
                with st.expander(f"🆕 {len(analysis['new_columns'])} nouvelles colonnes détectées", expanded=False):
                    st.write(", ".join(analysis['new_columns'][:30]))
                    if len(analysis['new_columns']) > 30:
                        st.write(f"... et {len(analysis['new_columns']) - 30} autres")
                    st.warning("Ces colonnes ne seront pas importées en mode 'Ajouter' (sauf si vous écrasez les données).")
            
            if analysis['missing_columns']:
                with st.expander(f"⚠️ {len(analysis['missing_columns'])} colonnes manquantes", expanded=False):
                    st.write(", ".join(analysis['missing_columns'][:30]))
                    if len(analysis['missing_columns']) > 30:
                        st.write(f"... et {len(analysis['missing_columns']) - 30} autres")
            
            st.markdown("---")
            st.markdown("##### 🎯 Choisissez le mode d'importation")
            
            # Choix du mode d'importation
            import_mode = st.radio(
                "Mode d'importation",
                options=['append', 'replace'],
                format_func=lambda x: "➕ Ajouter (uniquement les nouvelles dates)" if x == 'append' else "🔄 Écraser (remplacer toutes les données)",
                key=f'{key_prefix}_mode',
                horizontal=True
            )
            
            # Résumé de l'action
            if import_mode == 'append':
                if analysis['total_new_rows'] > 0:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Action prévue :</strong><br>
                        <strong>{analysis['total_new_rows']}</strong> nouvelles lignes seront ajoutées aux {analysis['total_rows_existing']} existantes.<br>
                        <em>Total après import : {analysis['total_rows_existing'] + analysis['total_new_rows']} lignes</em><br><br>
                        <strong>Nouvelles dates :</strong> {', '.join([d.strftime('%d/%m/%Y') for d in analysis['new_dates'][:5]])}{'...' if len(analysis['new_dates']) > 5 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <strong>⚠️ Aucune nouvelle date détectée</strong><br>
                        Toutes les dates du fichier importé existent déjà. Aucune ligne ne sera ajoutée.<br>
                        <em>Utilisez le mode "Écraser" si vous voulez remplacer les données existantes.</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:  # replace
                st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ Attention - Écrasement des données</strong><br>
                    Les <strong>{analysis['total_rows_existing']}</strong> lignes existantes seront <strong>supprimées</strong> et remplacées par les <strong>{analysis['total_rows_new']}</strong> lignes du fichier importé.<br><br>
                    <strong>Colonnes conservées :</strong> {len(analysis['common_columns'])} colonnes communes
                </div>
                """, unsafe_allow_html=True)
                
                # Confirmation supplémentaire pour l'écrasement
                confirm_replace = st.checkbox(
                    "Je confirme vouloir écraser les données existantes",
                    key=f'{key_prefix}_confirm_replace'
                )
            
            st.markdown("---")
            
            # Boutons de validation
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                can_proceed = True
                if import_mode == 'append' and analysis['total_new_rows'] == 0:
                    can_proceed = False
                if import_mode == 'replace' and not st.session_state.get(f'{key_prefix}_confirm_replace', False):
                    can_proceed = False
                
                if st.button(
                    "✅ Valider l'importation" if import_mode == 'append' else "🔄 Confirmer l'écrasement",
                    key=f'{key_prefix}_validate',
                    disabled=not can_proceed,
                    use_container_width=True
                ):
                    try:
                        if import_mode == 'append':
                            # Ajouter les nouvelles lignes
                            merged_data = merge_data_append(existing_df, processed_new_df, analysis['new_dates'])
                            save_to_excel(sheet_name, merged_data)
                            st.success(f"✅ {analysis['total_new_rows']} nouvelles lignes ajoutées avec succès !")
                        else:
                            # Écraser les données
                            replaced_data = replace_data(existing_df, processed_new_df)
                            save_to_excel(sheet_name, replaced_data)
                            st.success(f"✅ Données écrasées avec succès ! {len(replaced_data)} lignes importées.")
                        
                        st.balloons()
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'importation : {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

# ==================== IMPORTATION HISTORIQUE ACTIONS ====================
with tab_hist_actions:
    st.subheader("Importer des données historiques d'actions")
    
    uploaded_hist_actions = st.file_uploader(
        "📁 Sélectionnez votre fichier Excel contenant les données historiques d'actions",
        type=['xlsx', 'xls'],
        key='upload_hist_actions'
    )
    
    if existing_data:
        render_import_section(
            uploaded_hist_actions, 
            'actions', 
            existing_data['historique_actions'],
            'historique_actions',
            'hist_actions'
        )

# ==================== IMPORTATION HISTORIQUE INDICES ====================
with tab_hist_indices:
    st.subheader("Importer des données historiques d'indices")
    
    uploaded_hist_indices = st.file_uploader(
        "📁 Sélectionnez votre fichier Excel contenant les données historiques d'indices",
        type=['xlsx', 'xls'],
        key='upload_hist_indices'
    )
    
    if existing_data:
        render_import_section(
            uploaded_hist_indices, 
            'indices', 
            existing_data['historique_indices'],
            'historique_indices',
            'hist_indices'
        )

# ==================== IMPORTATION FICHE ACTIONS ====================
def render_fiche_import_section(uploaded_file, existing_df, sheet_name, key_prefix, key_column='Symbol'):
    """Rendu de la section d'importation pour les fiches (métadonnées)"""
    
    if uploaded_file:
        try:
            # Charger le nouveau fichier
            new_df = pd.read_excel(uploaded_file)
            
            # Aperçu des données
            st.markdown("##### 📄 Aperçu des données importées")
            st.dataframe(new_df.head(10), use_container_width=True, height=200)
            
            # Analyser les données
            analysis = analyze_fiche_data(new_df.copy(), existing_df, key_column)
            
            st.markdown("---")
            st.markdown("##### 🔍 Analyse comparative")
            
            # Tableau de comparaison
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Éléments existants", analysis['total_rows_existing'])
            with col2:
                st.metric("Éléments importés", analysis['total_rows_new'])
            with col3:
                st.metric("Nouveaux éléments", len(analysis['new_items']), 
                         delta=f"+{len(analysis['new_items'])}" if analysis['new_items'] else "0")
            with col4:
                st.metric("En commun", len(analysis['updated_items']))
            
            # Détails
            st.markdown(f"""
            <div class="import-box">
                <table class="comparison-table">
                    <tr>
                        <th>📋 Détails</th>
                        <th>Données existantes</th>
                        <th>Données importées</th>
                    </tr>
                    <tr>
                        <td><strong>Nombre de lignes</strong></td>
                        <td>{analysis['total_rows_existing']}</td>
                        <td>{analysis['total_rows_new']}</td>
                    </tr>
                    <tr>
                        <td><strong>Colonnes</strong></td>
                        <td>{len(existing_df.columns)}</td>
                        <td>{len(new_df.columns)}</td>
                    </tr>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # Nouveaux éléments
            if analysis['new_items']:
                with st.expander(f"🆕 {len(analysis['new_items'])} nouveaux éléments détectés", expanded=True):
                    st.write(", ".join(analysis['new_items'][:30]))
                    if len(analysis['new_items']) > 30:
                        st.write(f"... et {len(analysis['new_items']) - 30} autres")
            
            # Alertes sur les colonnes
            if analysis['new_columns']:
                with st.expander(f"🆕 {len(analysis['new_columns'])} nouvelles colonnes détectées", expanded=False):
                    st.write(", ".join(analysis['new_columns']))
                    st.warning("Ces colonnes ne seront pas importées en mode 'Ajouter'.")
            
            if analysis['missing_columns']:
                with st.expander(f"⚠️ {len(analysis['missing_columns'])} colonnes manquantes", expanded=False):
                    st.write(", ".join(analysis['missing_columns']))
            
            st.markdown("---")
            st.markdown("##### 🎯 Choisissez le mode d'importation")
            
            # Choix du mode d'importation
            import_mode = st.radio(
                "Mode d'importation",
                options=['append', 'replace'],
                format_func=lambda x: "➕ Ajouter (uniquement les nouveaux éléments)" if x == 'append' else "🔄 Écraser (remplacer toutes les données)",
                key=f'{key_prefix}_mode',
                horizontal=True
            )
            
            # Résumé de l'action
            if import_mode == 'append':
                if analysis['new_items']:
                    st.markdown(f"""
                    <div class="success-box">
                        <strong>✅ Action prévue :</strong><br>
                        <strong>{len(analysis['new_items'])}</strong> nouveaux éléments seront ajoutés aux {analysis['total_rows_existing']} existants.<br>
                        <em>Total après import : {analysis['total_rows_existing'] + len(analysis['new_items'])} éléments</em><br><br>
                        <strong>Nouveaux symboles :</strong> {', '.join(analysis['new_items'][:10])}{'...' if len(analysis['new_items']) > 10 else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="warning-box">
                        <strong>⚠️ Aucun nouvel élément détecté</strong><br>
                        Tous les éléments du fichier importé existent déjà. Aucune ligne ne sera ajoutée.<br>
                        <em>Utilisez le mode "Écraser" si vous voulez remplacer les données existantes.</em>
                    </div>
                    """, unsafe_allow_html=True)
            
            else:  # replace
                st.markdown(f"""
                <div class="warning-box">
                    <strong>⚠️ Attention - Écrasement des données</strong><br>
                    Les <strong>{analysis['total_rows_existing']}</strong> éléments existants seront <strong>supprimés</strong> et remplacés par les <strong>{analysis['total_rows_new']}</strong> éléments du fichier importé.<br><br>
                    <strong>Colonnes conservées :</strong> {len(analysis['common_columns'])} colonnes communes
                </div>
                """, unsafe_allow_html=True)
                
                # Confirmation supplémentaire pour l'écrasement
                confirm_replace = st.checkbox(
                    "Je confirme vouloir écraser les données existantes",
                    key=f'{key_prefix}_confirm_replace'
                )
            
            st.markdown("---")
            
            # Boutons de validation
            col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
            
            with col_btn2:
                can_proceed = True
                if import_mode == 'append' and not analysis['new_items']:
                    can_proceed = False
                if import_mode == 'replace' and not st.session_state.get(f'{key_prefix}_confirm_replace', False):
                    can_proceed = False
                
                if st.button(
                    "✅ Valider l'importation" if import_mode == 'append' else "🔄 Confirmer l'écrasement",
                    key=f'{key_prefix}_validate',
                    disabled=not can_proceed,
                    use_container_width=True
                ):
                    try:
                        if import_mode == 'append':
                            # Ajouter les nouveaux éléments
                            merged_data = merge_fiche_append(existing_df, new_df, key_column)
                            save_to_excel(sheet_name, merged_data, has_index=False)
                            st.success(f"✅ {len(analysis['new_items'])} nouveaux éléments ajoutés avec succès !")
                        else:
                            # Écraser les données
                            replaced_data = replace_fiche_data(existing_df, new_df)
                            save_to_excel(sheet_name, replaced_data, has_index=False)
                            st.success(f"✅ Données écrasées avec succès ! {len(replaced_data)} éléments importés.")
                        
                        st.balloons()
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de l'importation : {e}")
        
        except Exception as e:
            st.error(f"❌ Erreur lors de la lecture du fichier : {e}")

with tab_fiche_actions:
    st.subheader("Importer la fiche des actions (métadonnées)")
    
    st.markdown("""
    <div class="import-box">
        <strong>📋 Format attendu :</strong><br>
        Colonnes : Symbol, Name, Sector, Category, Description
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_fiche_actions = st.file_uploader(
        "📁 Sélectionnez votre fichier Excel contenant les métadonnées des actions",
        type=['xlsx', 'xls'],
        key='upload_fiche_actions'
    )
    
    if existing_data:
        render_fiche_import_section(
            uploaded_fiche_actions, 
            existing_data['fiche_actions'],
            'fiche_actions',
            'fiche_actions',
            'Symbol'
        )

# ==================== IMPORTATION FICHE INDICES ====================
with tab_fiche_indices:
    st.subheader("Importer la fiche des indices (métadonnées)")
    
    st.markdown("""
    <div class="import-box">
        <strong>📋 Format attendu :</strong><br>
        Colonnes : Symbol, Name, Region, Description (ou format personnalisé)
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_fiche_indices = st.file_uploader(
        "📁 Sélectionnez votre fichier Excel contenant les métadonnées des indices",
        type=['xlsx', 'xls'],
        key='upload_fiche_indices'
    )
    
    if existing_data:
        render_fiche_import_section(
            uploaded_fiche_indices, 
            existing_data['fiche_indices'],
            'fiche_indices',
            'fiche_indices',
            'Symbol'
        )

# Section d'aide
with st.expander("❓ Aide et format des données", expanded=False):
    st.markdown("""
    ### Format attendu des fichiers
    
    #### 📊 Historique des actions :
    | Date | AAPL | MSFT | GOOGL | ... |
    |------|------|------|-------|-----|
    | 2024-01-01 | 185.50 | 375.20 | 140.30 | ... |
    | 2024-01-02 | 186.10 | 376.80 | 141.00 | ... |
    
    #### 📈 Historique des indices :
    | Date | ^GSPC | BTC-USD | ETH-USD | ... |
    |------|-------|---------|---------|-----|
    | 2024-01-01 | 4750.00 | 42000.00 | 2300.00 | ... |
    | 2024-01-02 | 4760.50 | 42500.00 | 2350.00 | ... |
    
    #### 📋 Fiche des actions (métadonnées) :
    | Symbol | Name | Sector | Category | Description |
    |--------|------|--------|----------|-------------|
    | AAPL | Apple Inc. | Technology | Large Cap | Fabricant de smartphones... |
    | MSFT | Microsoft | Technology | Large Cap | Éditeur de logiciels... |
    
    #### 📑 Fiche des indices (métadonnées) :
    | Symbol | Name | Region | Description |
    |--------|------|--------|-------------|
    | ^GSPC | S&P 500 | USA | Indice des 500 plus grandes... |
    | BTC-USD | Bitcoin | Global | Cryptomonnaie décentralisée... |
    
    ### Modes d'importation :
    
    #### ➕ Mode "Ajouter"
    - Conserve toutes les données existantes
    - Pour les historiques : ajoute uniquement les nouvelles dates
    - Pour les fiches : ajoute uniquement les nouveaux symboles
    - Les colonnes doivent correspondre aux colonnes existantes
    
    #### 🔄 Mode "Écraser"
    - Remplace TOUTES les données existantes
    - Nécessite une confirmation explicite
    - Utilise uniquement les colonnes communes
    
    ### Notes importantes :
    - La colonne **Date** est obligatoire pour les historiques
    - La colonne **Symbol** est obligatoire pour les fiches
    - Les formats de date acceptés : YYYY-MM-DD, DD/MM/YYYY, etc.
    - Toujours vérifier l'analyse comparative avant de valider
    """)
