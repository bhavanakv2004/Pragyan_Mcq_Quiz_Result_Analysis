# ==========================================
# app.py
# Secure Multi-Subject Quiz Analytics System
# ==========================================
import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
import json
import os
import traceback
from datetime import datetime

# ==========================================
# CREATE REQUIRED FOLDERS
# ==========================================

folders = ["logs", "database", "uploads"]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

# ==========================================
# USERS FILE
# ==========================================

USERS_FILE = "database/users.json"

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title=" Quiz Analytics",
    layout="wide"
)




