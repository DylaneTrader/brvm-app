"""
Page Chatbot - Assistant IA pour l'analyse financière
"""

import streamlit as st
import pandas as pd
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Chatbot IA - BRVM Analytics", page_icon="🤖", layout="wide")

# CSS du thème Claude
st.markdown("""
<style>
    .stApp { background-color: #FAF9F6; }
    [data-testid="stSidebar"] { background-color: #E8DDD4; }
    h1, h2, h3 { color: #4A3728 !important; }
    
    .chat-container {
        background: white;
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border: 1px solid #E8DDD4;
    }
    
    .user-message {
        background: #E8DDD4;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #8B7355;
    }
    
    .assistant-message {
        background: #FAF9F6;
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        border-left: 4px solid #4A3728;
        border: 1px solid #E8DDD4;
    }
    
    .config-box {
        background: white;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #8B7355;
        margin: 15px 0;
    }
    
    .warning-box {
        background: #FEF3C7;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #F59E0B;
        margin: 10px 0;
    }
    
    .success-box {
        background: #D1FAE5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10B981;
        margin: 10px 0;
    }
    
    .model-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        border: 2px solid #E8DDD4;
        margin: 5px 0;
        cursor: pointer;
    }
    
    .model-card:hover {
        border-color: #8B7355;
    }
</style>
""", unsafe_allow_html=True)

# Chemin du fichier de données
DATA_FILE = "historical stock data.xlsx"

# Initialisation du session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'api_provider' not in st.session_state:
    st.session_state.api_provider = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = None

# Configuration des modèles disponibles
MODELS = {
    'OpenAI': {
        'models': [
            {'id': 'gpt-4o', 'name': 'GPT-4o', 'description': 'Modèle le plus avancé, multimodal'},
            {'id': 'gpt-4o-mini', 'name': 'GPT-4o Mini', 'description': 'Plus rapide et économique'},
            {'id': 'gpt-4-turbo', 'name': 'GPT-4 Turbo', 'description': 'Puissant avec contexte étendu'},
            {'id': 'gpt-3.5-turbo', 'name': 'GPT-3.5 Turbo', 'description': 'Rapide et économique'},
        ],
        'base_url': 'https://api.openai.com/v1',
        'key_prefix': 'sk-'
    },
    'Anthropic': {
        'models': [
            {'id': 'claude-sonnet-4-20250514', 'name': 'Claude Sonnet 4', 'description': 'Le plus récent et performant'},
            {'id': 'claude-3-5-sonnet-latest', 'name': 'Claude 3.5 Sonnet', 'description': 'Meilleur rapport qualité/prix'},
            {'id': 'claude-3-5-haiku-latest', 'name': 'Claude 3.5 Haiku', 'description': 'Ultra-rapide et léger'},
            {'id': 'claude-3-opus-latest', 'name': 'Claude 3 Opus', 'description': 'Puissant et détaillé'},
        ],
        'base_url': 'https://api.anthropic.com/v1',
        'key_prefix': 'sk-ant-'
    }
}

def load_data_context():
    """Charge le contexte des données pour le chatbot"""
    try:
        xl = pd.ExcelFile(DATA_FILE)
        
        # Charger les données
        hist_actions = pd.read_excel(xl, sheet_name='historique_actions')
        hist_indices = pd.read_excel(xl, sheet_name='historique_indices')
        fiche_actions = pd.read_excel(xl, sheet_name='fiche_actions')
        
        # Convertir les dates
        hist_actions['Date'] = pd.to_datetime(hist_actions['Date'])
        hist_indices['Date'] = pd.to_datetime(hist_indices['Date'])
        
        # Formater les dates pour l'affichage
        date_debut_actions = hist_actions['Date'].min().strftime('%d/%m/%Y')
        date_fin_actions = hist_actions['Date'].max().strftime('%d/%m/%Y')
        date_debut_indices = hist_indices['Date'].min().strftime('%d/%m/%Y')
        date_fin_indices = hist_indices['Date'].max().strftime('%d/%m/%Y')
        
        # Créer un résumé des données
        context = f"""
Contexte des données financières disponibles :

📊 **Actions disponibles** : {len(fiche_actions)} titres
- Secteurs : {', '.join(fiche_actions['Sector'].dropna().unique()[:10]) if 'Sector' in fiche_actions.columns else 'N/A'}
- Exemples de symboles : {', '.join(fiche_actions['Symbol'].head(10).tolist()) if 'Symbol' in fiche_actions.columns else 'N/A'}

📅 **Période des données** (IMPORTANT - toujours mentionner dans tes réponses) :
- Actions : du {date_debut_actions} au {date_fin_actions} ({len(hist_actions)} jours de données)
- Indices : du {date_debut_indices} au {date_fin_indices} ({len(hist_indices)} jours de données)

📋 **Colonnes actions** : {', '.join(hist_actions.columns[:15].tolist())}...

⚠️ RAPPEL : Dans toutes tes réponses, tu DOIS préciser l'intervalle de temps concerné.
"""
        return context
    except Exception as e:
        return f"Erreur lors du chargement des données : {e}"

def call_openai_api(messages, model, api_key):
    """Appelle l'API OpenAI"""
    try:
        import requests
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': model,
            'messages': messages,
            'max_tokens': 2000,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            error_msg = response.json().get('error', {}).get('message', response.text)
            return f"❌ Erreur API OpenAI : {error_msg}"
            
    except ImportError:
        return "❌ Le module 'requests' n'est pas installé. Installez-le avec : pip install requests"
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def call_anthropic_api(messages, model, api_key):
    """Appelle l'API Anthropic"""
    try:
        import requests
        
        headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }
        
        # Convertir le format des messages pour Anthropic
        anthropic_messages = []
        system_content = ""
        
        for msg in messages:
            if msg['role'] == 'system':
                system_content = msg['content']
            else:
                anthropic_messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        data = {
            'model': model,
            'max_tokens': 2000,
            'messages': anthropic_messages
        }
        
        if system_content:
            data['system'] = system_content
        
        response = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()['content'][0]['text']
        else:
            # Améliorer le parsing de l'erreur
            try:
                error_data = response.json()
                if 'error' in error_data:
                    error_type = error_data['error'].get('type', 'unknown')
                    error_msg = error_data['error'].get('message', str(error_data))
                    return f"❌ Erreur API Anthropic ({error_type}): {error_msg}"
                else:
                    return f"❌ Erreur API Anthropic: {error_data}"
            except:
                return f"❌ Erreur API Anthropic (HTTP {response.status_code}): {response.text}"
            
    except ImportError:
        return "❌ Le module 'requests' n'est pas installé. Installez-le avec : pip install requests"
    except Exception as e:
        return f"❌ Erreur : {str(e)}"

def get_ai_response(user_message, data_context):
    """Obtient une réponse de l'IA"""
    if not st.session_state.api_key or not st.session_state.selected_model:
        return "⚠️ Veuillez configurer votre clé API et sélectionner un modèle dans la barre latérale."
    
    # Construire les messages
    system_message = f"""Tu es un assistant financier expert spécialisé dans l'analyse des marchés boursiers, particulièrement le marché BRVM (Bourse Régionale des Valeurs Mobilières).

{data_context}

Tu dois :
- Répondre en français
- Être précis et factuel dans tes analyses
- **TOUJOURS préciser les intervalles de temps** dans tes réponses (dates de début/fin, période analysée)
- Quand tu cites des données ou analyses, TOUJOURS indiquer la période concernée (ex: "Sur la période du 01/01/2024 au 31/12/2024...")
- Citer les données disponibles quand c'est pertinent
- Expliquer les concepts financiers de manière accessible
- Suggérer des analyses ou visualisations pertinentes disponibles dans l'application
- Mentionner explicitement si les données sont limitées à une certaine période
"""
    
    messages = [
        {'role': 'system', 'content': system_message}
    ]
    
    # Ajouter l'historique de conversation (limité aux 10 derniers messages)
    for msg in st.session_state.messages[-10:]:
        messages.append({'role': msg['role'], 'content': msg['content']})
    
    # Ajouter le nouveau message
    messages.append({'role': 'user', 'content': user_message})
    
    # Appeler l'API appropriée
    if st.session_state.api_provider == 'OpenAI':
        return call_openai_api(messages, st.session_state.selected_model, st.session_state.api_key)
    else:
        return call_anthropic_api(messages, st.session_state.selected_model, st.session_state.api_key)

# ==================== INTERFACE ====================

st.title("🤖 Assistant IA - Analyse Financière")

# Sidebar pour la configuration
with st.sidebar:
    st.markdown("### ⚙️ Configuration de l'IA")
    
    # Sélection du fournisseur
    st.markdown("#### 1. Choisir le fournisseur")
    provider = st.radio(
        "Fournisseur d'IA",
        options=['OpenAI', 'Anthropic'],
        index=0 if st.session_state.api_provider != 'Anthropic' else 1,
        horizontal=True,
        key='provider_select'
    )
    st.session_state.api_provider = provider
    
    # Logo du fournisseur
    if provider == 'OpenAI':
        st.markdown("🟢 **OpenAI** - GPT-4, GPT-3.5")
    else:
        st.markdown("🟠 **Anthropic** - Claude 3")
    
    st.markdown("---")
    
    # Clé API
    st.markdown("#### 2. Entrer la clé API")
    api_key = st.text_input(
        f"Clé API {provider}",
        type="password",
        value=st.session_state.api_key if st.session_state.api_key else "",
        placeholder=f"Commence par {MODELS[provider]['key_prefix']}...",
        key='api_key_input'
    )
    
    if api_key:
        st.session_state.api_key = api_key
        if api_key.startswith(MODELS[provider]['key_prefix'][:5]):
            st.success("✅ Clé API valide")
        else:
            st.warning(f"⚠️ La clé devrait commencer par {MODELS[provider]['key_prefix'][:8]}...")
    
    st.markdown("---")
    
    # Sélection du modèle
    st.markdown("#### 3. Sélectionner le modèle")
    
    models = MODELS[provider]['models']
    model_options = [m['id'] for m in models]
    model_names = {m['id']: f"{m['name']} - {m['description']}" for m in models}
    
    selected_model = st.selectbox(
        "Modèle",
        options=model_options,
        format_func=lambda x: model_names[x],
        index=0,
        key='model_select'
    )
    st.session_state.selected_model = selected_model
    
    st.markdown("---")
    
    # Bouton pour effacer l'historique
    if st.button("🗑️ Effacer l'historique", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    # Informations sur le modèle sélectionné
    selected_model_info = next((m for m in models if m['id'] == selected_model), None)
    if selected_model_info:
        st.markdown(f"""
        <div class="config-box">
            <strong>Modèle actif :</strong><br>
            {selected_model_info['name']}<br>
            <small>{selected_model_info['description']}</small>
        </div>
        """, unsafe_allow_html=True)

# Contenu principal
col1, col2 = st.columns([2, 1])

with col2:
    # Statut de la configuration
    st.markdown("### 📊 Statut")
    
    config_status = []
    if st.session_state.api_provider:
        config_status.append(f"✅ Fournisseur : {st.session_state.api_provider}")
    else:
        config_status.append("❌ Fournisseur non sélectionné")
    
    if st.session_state.api_key:
        config_status.append(f"✅ Clé API : ****{st.session_state.api_key[-4:]}")
    else:
        config_status.append("❌ Clé API manquante")
    
    if st.session_state.selected_model:
        config_status.append(f"✅ Modèle : {st.session_state.selected_model}")
    else:
        config_status.append("❌ Modèle non sélectionné")
    
    for status in config_status:
        st.markdown(status)
    
    st.markdown("---")
    
    # Suggestions de questions
    st.markdown("### 💡 Suggestions")
    
    suggestions = [
        "Quelles sont les actions les plus performantes ?",
        "Explique-moi le RSI et comment l'interpréter",
        "Quelle est la corrélation entre les secteurs ?",
        "Comment analyser les tendances du marché ?",
        "Quels indicateurs techniques utiliser ?"
    ]
    
    for suggestion in suggestions:
        if st.button(suggestion, key=f"sug_{suggestion[:20]}", use_container_width=True):
            st.session_state.pending_question = suggestion

with col1:
    # Zone de chat
    st.markdown("### 💬 Conversation")
    
    # Vérifier si une question suggérée a été cliquée
    if 'pending_question' in st.session_state:
        pending = st.session_state.pending_question
        del st.session_state.pending_question
        
        # Simuler une soumission
        st.session_state.messages.append({'role': 'user', 'content': pending})
        
        # Obtenir la réponse
        data_context = load_data_context()
        response = get_ai_response(pending, data_context)
        st.session_state.messages.append({'role': 'assistant', 'content': response})
        st.rerun()
    
    # Afficher l'historique des messages
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            st.markdown("""
            <div class="chat-container">
                <h4>👋 Bienvenue !</h4>
                <p>Je suis votre assistant IA pour l'analyse financière. Je peux vous aider à :</p>
                <ul>
                    <li>📊 Analyser les performances des actions et indices</li>
                    <li>📈 Expliquer les indicateurs techniques (RSI, MACD, SMA...)</li>
                    <li>🔗 Comprendre les corrélations entre actifs</li>
                    <li>💡 Suggérer des stratégies d'analyse</li>
                </ul>
                <p><strong>Commencez par configurer votre clé API dans la barre latérale</strong>, puis posez-moi vos questions !</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            for message in st.session_state.messages:
                if message['role'] == 'user':
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>🧑 Vous :</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>🤖 Assistant :</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Zone de saisie
    st.markdown("---")
    
    # Vérifier si la configuration est complète
    is_configured = bool(st.session_state.api_key and st.session_state.selected_model)
    
    if not is_configured:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ Configuration requise</strong><br>
            Veuillez configurer votre clé API et sélectionner un modèle dans la barre latérale pour commencer à discuter.
        </div>
        """, unsafe_allow_html=True)
    
    # Formulaire de saisie
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_area(
            "Votre message",
            placeholder="Posez votre question sur les données financières...",
            height=100,
            disabled=not is_configured
        )
        
        col_submit, col_clear = st.columns([3, 1])
        
        with col_submit:
            submit = st.form_submit_button(
                "📤 Envoyer",
                use_container_width=True,
                disabled=not is_configured
            )
        
        with col_clear:
            if st.form_submit_button("🔄", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        
        if submit and user_input.strip():
            # Ajouter le message utilisateur
            st.session_state.messages.append({'role': 'user', 'content': user_input.strip()})
            
            # Obtenir la réponse
            with st.spinner("🔄 Réflexion en cours..."):
                data_context = load_data_context()
                response = get_ai_response(user_input.strip(), data_context)
            
            # Ajouter la réponse
            st.session_state.messages.append({'role': 'assistant', 'content': response})
            
            st.rerun()

# Footer avec instructions
st.markdown("---")
with st.expander("ℹ️ Comment obtenir une clé API ?"):
    st.markdown("""
    ### OpenAI
    1. Créez un compte sur [platform.openai.com](https://platform.openai.com)
    2. Allez dans **API Keys** dans les paramètres
    3. Cliquez sur **Create new secret key**
    4. Copiez la clé qui commence par `sk-`
    
    ### Anthropic
    1. Créez un compte sur [console.anthropic.com](https://console.anthropic.com)
    2. Allez dans **API Keys**
    3. Cliquez sur **Create Key**
    4. Copiez la clé qui commence par `sk-ant-`
    
    ### 🔒 Sécurité
    - Votre clé API n'est jamais stockée de manière permanente
    - Elle reste uniquement dans la session en cours
    - Fermez la fenêtre pour effacer la clé
    """)
