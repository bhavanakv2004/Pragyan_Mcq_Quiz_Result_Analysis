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
    page_title="Secure Quiz Analytics",
    layout="wide"
)

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ==========================================
# REGISTER USER
# ==========================================

def register_user(username, password, role, college_id):

    users = load_users()

    if username in users:
        return False, "Username already exists"

    users[username] = {
        "password": password,
        "role": role,
        "college_id": college_id
    }

    save_users(users)

    return True, "Registration Successful"

# ==========================================
# LOGIN AUTHENTICATION
# ==========================================

def authenticate(username, password):

    users = load_users()

    if username in users:

        user = users[username]

        if user["password"] == password:
            return True, user

    return False, None

# ==========================================
# AUDIT LOG
# ==========================================

def log_activity(user, action):

    with open("logs/audit_log.txt", "a") as f:
        f.write(
            f"{datetime.now()} | {user} | {action}\n"
        )

# ==========================================
# FILE HASHING
# ==========================================

def generate_file_hash(file_bytes):

    return hashlib.sha256(file_bytes).hexdigest()

# ==========================================
# VALIDATION
# ==========================================

required_response_columns = [
    "Student_ID",
    "College_ID",
    "Question_ID",
    "Student_Answer"
]

required_answer_columns = [
    "Question_ID",
    "Correct_Answer",
    "Subject"
]

def validate_columns(df, required_columns):

    missing = []

    for col in required_columns:
        if col not in df.columns:
            missing.append(col)

    return missing

# ==========================================
# ANALYTICS FUNCTIONS
# ==========================================

def evaluate_answers(response_df, answer_df):

    merged = pd.merge(
        response_df,
        answer_df,
        on="Question_ID",
        how="left"
    )

    merged["Result"] = (
        merged["Student_Answer"] ==
        merged["Correct_Answer"]
    )

    merged["Score"] = merged["Result"].astype(int)

    return merged

# ==========================================
# STUDENT PERFORMANCE
# ==========================================

def student_performance(result_df):

    performance = (
        result_df.groupby(
            ["Student_ID", "Subject"]
        )["Score"]
        .sum()
        .reset_index()
    )

    return performance

# ==========================================
# DIFFICULT QUESTIONS
# ==========================================

def difficult_questions(result_df):

    difficulty = (
        result_df.groupby("Question_ID")["Score"]
        .mean()
        .reset_index()
    )

    difficulty.columns = [
        "Question_ID",
        "Accuracy"
    ]

    difficult = difficulty[
        difficulty["Accuracy"] < 0.4
    ]

    return difficult

# ==========================================
# READ FILES
# ==========================================

def read_file(file):

    if file.name.endswith(".csv"):
        return pd.read_csv(file)

    return pd.read_excel(file)

# ==========================================
# MAIN APP
# ==========================================

try:

    st.title(
        "Secure Multi-Subject Quiz Analytics System"
    )

    # ======================================
    # AUTHENTICATION
    # ======================================

    st.sidebar.title("Authentication")

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    # ======================================
    # REGISTER
    # ======================================

    if menu == "Register":

        st.subheader("Create Account")

        new_user = st.text_input(
            "Username"
        )

        new_password = st.text_input(
            "Password",
            type="password"
        )

        role = st.selectbox(
            "Role",
            ["faculty", "student"]
        )

        college_id = st.text_input(
            "College ID"
        )

        register_btn = st.button(
            "Register"
        )

        if register_btn:

            status, message = register_user(
                new_user,
                new_password,
                role,
                college_id
            )

            if status:
                st.success(message)

                log_activity(
                    new_user,
                    "Registered Account"
                )

            else:
                st.error(message)

    # ======================================
    # LOGIN
    # ======================================

    elif menu == "Login":

        st.subheader("Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login_btn = st.button(
            "Login"
        )

        if login_btn:

            status, user = authenticate(
                username,
                password
            )

            if status:

                st.session_state["user"] = user
                st.session_state["username"] = username

                st.success(
                    "Login Successful"
                )

                log_activity(
                    username,
                    "Logged In"
                )

            else:
                st.error(
                    "Invalid Credentials"
                )

    # ======================================
    # DASHBOARD
    # ======================================

    if "user" in st.session_state:

        user = st.session_state["user"]
        username = st.session_state["username"]

        st.success(
            f"Welcome {username}"
        )

        st.sidebar.header("Upload Files")

        answer_files = st.sidebar.file_uploader(
            "Upload Answer Keys",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )

        response_files = st.sidebar.file_uploader(
            "Upload Response Files",
            type=["csv", "xlsx"],
            accept_multiple_files=True
        )

        # ==================================
        # PROCESS FILES
        # ==================================

        if answer_files and response_files:

            all_answers = []
            all_responses = []

            # ==============================
            # ANSWER KEYS
            # ==============================

            for file in answer_files:

                file_hash = generate_file_hash(
                    file.getvalue()
                )

                st.sidebar.write(
                    f"Hash: {file_hash[:10]}..."
                )

                df = read_file(file)

                missing = validate_columns(
                    df,
                    required_answer_columns
                )

                if missing:
                    st.error(
                        f"Missing columns in {file.name}: {missing}"
                    )

                else:
                    all_answers.append(df)

            # ==============================
            # RESPONSE FILES
            # ==============================

            for file in response_files:

                df = read_file(file)

                missing = validate_columns(
                    df,
                    required_response_columns
                )

                if missing:

                    st.error(
                        f"Missing columns in {file.name}: {missing}"
                    )

                else:

                    # ======================
                    # SECURITY CHECK
                    # ======================

                    if user["role"] != "admin":

                        allowed_college = (
                            user["college_id"]
                        )

                        invalid = df[
                            df["College_ID"]
                            != allowed_college
                        ]

                        if len(invalid) > 0:

                            st.error(
                                "Unauthorized College Data Detected"
                            )

                        else:
                            all_responses.append(df)

                    else:
                        all_responses.append(df)

            # ==============================
            # COMBINE FILES
            # ==============================

            if all_answers and all_responses:

                answer_df = pd.concat(
                    all_answers
                )

                response_df = pd.concat(
                    all_responses
                )

                # ==========================
                # EVALUATE
                # ==========================

                result_df = evaluate_answers(
                    response_df,
                    answer_df
                )

                performance_df = student_performance(
                    result_df
                )

                difficult_df = difficult_questions(
                    result_df
                )

                # ==========================
                # DISPLAY RESULTS
                # ==========================

                st.subheader(
                    "Student Performance"
                )

                st.dataframe(
                    performance_df
                )

                # ==========================
                # CHART
                # ==========================

                fig = px.bar(
                    performance_df,
                    x="Student_ID",
                    y="Score",
                    color="Subject",
                    title="Student Scores"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                # ==========================
                # DIFFICULT QUESTIONS
                # ==========================

                st.subheader(
                    "Difficult Questions"
                )

                st.dataframe(
                    difficult_df
                )

                # ==========================
                # WEAK STUDENTS
                # ==========================

                st.subheader(
                    "Weak Students"
                )

                weak_students = performance_df[
                    performance_df["Score"] < 3
                ]

                st.dataframe(
                    weak_students
                )

                # ==========================
                # DOWNLOAD REPORT
                # ==========================

                csv = performance_df.to_csv(
                    index=False
                )

                st.download_button(
                    label="Download Report",
                    data=csv,
                    file_name="performance_report.csv",
                    mime="text/csv"
                )

                # ==========================
                # LOGGING
                # ==========================

                log_activity(
                    username,
                    "Processed Analytics"
                )

except Exception as e:

    st.error(f"Error: {e}")

    st.code(traceback.format_exc())
