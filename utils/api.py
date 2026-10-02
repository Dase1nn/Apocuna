import requests
from requests.exceptions import Timeout, RequestException
import config
import streamlit as st

def fetch_data_safe(url: str, fallback_data=None):
    """
    Realiza una llamada de red de forma segura.
    Si falla, retorna fallback_data y no rompe la app, tal como exige la regla.
    """
    try:
        response = requests.get(url, timeout=config.TIMEOUT_RED)
        response.raise_for_status()
        return response.json()
    except Timeout:
        st.warning(f"La conexión a {url} ha tardado demasiado (Timeout). Usando datos locales de respaldo.")
        return fallback_data
    except RequestException as e:
        st.warning(f"Error de red al conectar con {url}. Usando datos locales de respaldo.")
        return fallback_data
