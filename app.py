import os
import streamlit as st

# Installation automatique de Chromium pour Playwright sur le cloud Streamlit
@st.cache_resource
def install_playwright():
    os.system("playwright install chromium")

install_playwright()

# (Le reste de votre code app.py...)
