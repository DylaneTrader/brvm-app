"""
Utils - Fonctions utilitaires pour l'application BRVM Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Chemin du fichier de données
DATA_FILE = "historical stock data.xlsx"

def get_data_path():
    """Retourne le chemin vers le fichier de données"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), DATA_FILE)

@pd.api.extensions.register_dataframe_accessor("cache")
class CacheAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj

def load_data():
    """Charge toutes les données depuis le fichier Excel"""
    try:
        path = DATA_FILE
        if not os.path.exists(path):
            path = os.path.join(os.path.dirname(__file__), "..", DATA_FILE)
        
        xl = pd.ExcelFile(path)
        
        # Charger les données
        fiche_actions = pd.read_excel(xl, sheet_name='fiche_actions')
        historique_actions = pd.read_excel(xl, sheet_name='historique_actions')
        historique_actions['Date'] = pd.to_datetime(historique_actions['Date'])
        historique_actions = historique_actions.set_index('Date').sort_index()
        
        indices_info = pd.read_excel(xl, sheet_name='indices')
        historique_indices = pd.read_excel(xl, sheet_name='historique_indices')
        historique_indices['Date'] = pd.to_datetime(historique_indices['Date'])
        historique_indices = historique_indices.set_index('Date').sort_index()
        
        return {
            'fiche_actions': fiche_actions,
            'historique_actions': historique_actions,
            'indices_info': indices_info,
            'historique_indices': historique_indices
        }
    except Exception as e:
        raise Exception(f"Erreur lors du chargement des données: {e}")


# ==================== CALCULS DE PERFORMANCE ====================

def calculate_return(prices: pd.Series, periods: int = 1) -> float:
    """
    Calcule le rendement sur une période donnée
    
    Args:
        prices: Série de prix
        periods: Nombre de périodes
    
    Returns:
        Rendement en pourcentage
    """
    if len(prices) < periods + 1:
        return np.nan
    
    current_price = prices.iloc[-1]
    past_price = prices.iloc[-(periods + 1)]
    
    if past_price == 0 or pd.isna(past_price):
        return np.nan
    
    return ((current_price / past_price) - 1) * 100


def calculate_returns_for_period(df: pd.DataFrame, period: str) -> pd.Series:
    """
    Calcule les rendements pour toutes les colonnes sur une période donnée
    
    Périodes supportées: 1D, 1W, 1M, 3M, 6M, 1Y, 3Y
    """
    period_days = {
        '1D': 1,
        '1W': 7,     # 7 jours
        '1M': 30,    # ~30 jours par mois
        '3M': 91,
        '6M': 182,
        '1Y': 365,
        '3Y': 1095
    }
    
    days = period_days.get(period, 1)
    returns = {}
    
    for col in df.columns:
        returns[col] = calculate_return(df[col].dropna(), days)
    
    return pd.Series(returns)


def calculate_calendar_performance(df: pd.DataFrame, perf_type: str) -> pd.Series:
    """
    Calcule les performances calendaires
    
    Types supportés: WTD, MTD, QTD, STD, YTD
    """
    if df.empty:
        return pd.Series()
    
    last_date = df.index[-1]
    year = last_date.year
    month = last_date.month
    
    if perf_type == 'WTD':  # Week-to-date
        # Lundi de la semaine en cours
        start_date = last_date - timedelta(days=last_date.weekday())
    
    elif perf_type == 'MTD':  # Month-to-date
        start_date = datetime(year, month, 1)
    
    elif perf_type == 'QTD':  # Quarter-to-date
        quarter_start_month = ((month - 1) // 3) * 3 + 1
        start_date = datetime(year, quarter_start_month, 1)
    
    elif perf_type == 'STD':  # Semester-to-date
        semester_start_month = 1 if month <= 6 else 7
        start_date = datetime(year, semester_start_month, 1)
    
    elif perf_type == 'YTD':  # Year-to-date
        start_date = datetime(year, 1, 1)
    
    else:
        return pd.Series()
    
    # Trouver la première date disponible >= start_date
    mask = df.index >= pd.Timestamp(start_date)
    if not mask.any():
        return pd.Series()
    
    period_data = df.loc[mask]
    if len(period_data) < 2:
        return pd.Series()
    
    returns = {}
    for col in df.columns:
        first_price = period_data[col].dropna().iloc[0] if not period_data[col].dropna().empty else np.nan
        last_price = period_data[col].dropna().iloc[-1] if not period_data[col].dropna().empty else np.nan
        
        if pd.notna(first_price) and first_price != 0:
            returns[col] = ((last_price / first_price) - 1) * 100
        else:
            returns[col] = np.nan
    
    return pd.Series(returns)


def calculate_cumulative_returns(df: pd.DataFrame, start_date=None) -> pd.DataFrame:
    """
    Calcule les rendements cumulés normalisés à 100
    
    Args:
        df: DataFrame avec les prix
        start_date: Date de début (optionnel)
    
    Returns:
        DataFrame avec les rendements cumulés
    """
    if start_date:
        df = df.loc[df.index >= pd.Timestamp(start_date)]
    
    if df.empty:
        return df
    
    # Normaliser à 100 au premier point
    return (df / df.iloc[0]) * 100


# ==================== INDICATEURS TECHNIQUES ====================

def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """
    Calcule le RSI (Relative Strength Index)
    
    RSI = 100 - (100 / (1 + RS))
    RS = Moyenne des gains / Moyenne des pertes
    """
    delta = prices.diff()
    
    gains = delta.where(delta > 0, 0)
    losses = (-delta).where(delta < 0, 0)
    
    avg_gains = gains.rolling(window=period, min_periods=period).mean()
    avg_losses = losses.rolling(window=period, min_periods=period).mean()
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_sma(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    Calcule la SMA (Simple Moving Average)
    
    SMA = Somme des prix / Nombre de périodes
    """
    return prices.rolling(window=period, min_periods=period).mean()


def calculate_ema(prices: pd.Series, period: int = 20) -> pd.Series:
    """
    Calcule l'EMA (Exponential Moving Average)
    
    EMA = Prix × k + EMA_précédent × (1 - k)
    k = 2 / (période + 1)
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> dict:
    """
    Calcule le MACD (Moving Average Convergence Divergence)
    
    MACD Line = EMA(12) - EMA(26)
    Signal Line = EMA(9) de MACD Line
    Histogram = MACD Line - Signal Line
    """
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }


# ==================== CORRÉLATIONS ====================

def calculate_correlation_matrix(df: pd.DataFrame, method: str = 'pearson') -> pd.DataFrame:
    """
    Calcule la matrice de corrélation
    
    Args:
        df: DataFrame avec les prix
        method: 'pearson' ou 'spearman'
    
    Returns:
        Matrice de corrélation
    """
    # Calculer les rendements journaliers
    returns = df.pct_change().dropna()
    
    # Calculer la corrélation
    return returns.corr(method=method)


# ==================== STATISTIQUES DESCRIPTIVES ====================

def calculate_descriptive_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcule les statistiques descriptives pour chaque actif
    """
    stats = {}
    
    for col in df.columns:
        series = df[col].dropna()
        returns = series.pct_change().dropna()
        
        stats[col] = {
            'Dernier Prix': series.iloc[-1] if len(series) > 0 else np.nan,
            'Prix Min': series.min(),
            'Prix Max': series.max(),
            'Prix Moyen': series.mean(),
            'Volatilité (annualisée)': returns.std() * np.sqrt(365) * 100 if len(returns) > 0 else np.nan,
            'Rendement Total (%)': ((series.iloc[-1] / series.iloc[0]) - 1) * 100 if len(series) > 1 else np.nan,
            'Nb Observations': len(series)
        }
    
    return pd.DataFrame(stats).T


def get_top_flop_performers(returns: pd.Series, n: int = 5) -> dict:
    """
    Retourne les n meilleures et pires performances
    """
    sorted_returns = returns.dropna().sort_values(ascending=False)
    
    return {
        'top': sorted_returns.head(n),
        'flop': sorted_returns.tail(n).sort_values()
    }


# ==================== BÊTA ====================

def calculate_beta(stock_prices: pd.Series, index_prices: pd.Series, period: int = None) -> float:
    """
    Calcule le bêta d'une action par rapport à un indice
    
    Bêta = Cov(Rstock, Rindex) / Var(Rindex)
    
    Args:
        stock_prices: Série des prix de l'action
        index_prices: Série des prix de l'indice de référence
        period: Nombre de jours à considérer (None = toute la période)
    
    Returns:
        Valeur du bêta
    """
    # Aligner les séries sur les mêmes dates
    aligned = pd.DataFrame({
        'stock': stock_prices,
        'index': index_prices
    }).dropna()
    
    if period:
        aligned = aligned.tail(period)
    
    if len(aligned) < 20:  # Minimum de données requis
        return np.nan
    
    # Calculer les rendements
    stock_returns = aligned['stock'].pct_change().dropna()
    index_returns = aligned['index'].pct_change().dropna()
    
    # Calculer le bêta
    covariance = np.cov(stock_returns, index_returns)[0, 1]
    variance = np.var(index_returns)
    
    if variance == 0:
        return np.nan
    
    return covariance / variance


def calculate_rolling_beta(stock_prices: pd.Series, index_prices: pd.Series, window: int = 60) -> pd.Series:
    """
    Calcule le bêta glissant d'une action par rapport à un indice
    
    Args:
        stock_prices: Série des prix de l'action
        index_prices: Série des prix de l'indice de référence
        window: Taille de la fenêtre glissante (en jours)
    
    Returns:
        Série du bêta glissant
    """
    # Aligner les séries sur les mêmes dates
    aligned = pd.DataFrame({
        'stock': stock_prices,
        'index': index_prices
    }).dropna()
    
    if len(aligned) < window:
        return pd.Series()
    
    # Calculer les rendements
    stock_returns = aligned['stock'].pct_change()
    index_returns = aligned['index'].pct_change()
    
    # Calculer le bêta glissant
    rolling_cov = stock_returns.rolling(window=window).cov(index_returns)
    rolling_var = index_returns.rolling(window=window).var()
    
    rolling_beta = rolling_cov / rolling_var
    
    return rolling_beta


def calculate_alpha(stock_returns: pd.Series, index_returns: pd.Series, beta: float, risk_free_rate: float = 0.02) -> float:
    """
    Calcule l'alpha (Jensen's Alpha)
    
    Alpha = Rstock - [Rf + Beta × (Rindex - Rf)]
    
    Args:
        stock_returns: Rendement annualisé de l'action
        index_returns: Rendement annualisé de l'indice
        beta: Bêta de l'action
        risk_free_rate: Taux sans risque annuel (par défaut 2%)
    
    Returns:
        Alpha en pourcentage
    """
    expected_return = risk_free_rate + beta * (index_returns - risk_free_rate)
    alpha = stock_returns - expected_return
    return alpha * 100  # En pourcentage
