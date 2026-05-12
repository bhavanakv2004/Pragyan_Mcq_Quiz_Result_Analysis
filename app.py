import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import *
from auth import *

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Secure MCQ Analytics",
    layout="wide"
)

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN SYSTEM ---------------- #
if not st.session_state.logged_in:

    menu = st.sidebar.selectbox(
        "Select Option",
        ["Login", "Register"]
    )

    # -------- REGISTER -------- #
    if menu == "Register":

        st.title("📝 Create Account")

        new_user = st.text_input(
            "Username"
        )

        new_pass = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Register"):

            success, msg = register_user(
                new_user,
                new_pass
            )

            if success:
                st.success(msg)

            else:
                st.error(msg)

    # -------- LOGIN -------- #
    elif menu == "Login":

        st.title("🔐 Login")

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            valid = login_user(
                username,
                password
            )

            if valid:

                st.session_state.logged_in = True
                st.session_state.username = username

                st.success(
                    "✅ Login Successful"
                )

                st.rerun()

            else:
                st.error(
                    "❌ Invalid Username or Password"
                )

    st.stop()

# ---------------- LOGOUT ---------------- #
st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()

# ---------------- TITLE ---------------- #
st.title("📊 Secure Multi-Subject MCQ Analytics")

st.markdown(
    """
Analyze:
- Multiple Subjects
- Randomized Questions
- Department Performance
- College Ranking
- Weak Questions
- Attempt Rate
"""
)

# ---------------- FILE UPLOAD ---------------- #
data_file = st.file_uploader(
    "Upload Student Response CSV",
    type=["csv"]
)

answer_file = st.file_uploader(
    "Upload Answer Key CSV",
    type=["csv"]
)

# ---------------- PROCESS FILES ---------------- #
if data_file and answer_file:

    df, answer_df = load_data(
        data_file,
        answer_file
    )

    valid, message = validate_files(
        df,
        answer_df
    )

    if not valid:

        st.error(message)
        st.stop()

    st.success(message)

    df = calculate_score(
        df,
        answer_df
    )

    # ---------------- SIDEBAR FILTERS ---------------- #
    st.sidebar.header("🔍 Filters")

    colleges = st.sidebar.multiselect(
        "Select College",
        df["College"].unique()
    )

    departments = st.sidebar.multiselect(
        "Select Department",
        df["Department"].unique()
    )

    subjects = st.sidebar.multiselect(
        "Select Subject",
        df["Subject"].unique()
    )

    students = st.sidebar.multiselect(
        "Select Student",
        df["Name"].unique()
    )

    filtered_df = df.copy()

    if colleges:
        filtered_df = filtered_df[
            filtered_df["College"].isin(colleges)
        ]

    if departments:
        filtered_df = filtered_df[
            filtered_df["Department"].isin(departments)
        ]

    if subjects:
        filtered_df = filtered_df[
            filtered_df["Subject"].isin(subjects)
        ]

    if students:
        filtered_df = filtered_df[
            filtered_df["Name"].isin(students)
        ]

    if filtered_df.empty:

        st.warning(
            "⚠️ No data found for selected filters"
        )

        st.stop()

    # ---------------- KPIs ---------------- #
    st.header("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Students",
        len(filtered_df)
    )

    col2.metric(
        "Average Score",
        round(filtered_df["Score"].mean(), 2)
    )

    col3.metric(
        "Highest Score",
        filtered_df["Score"].max()
    )

    col4.metric(
        "Lowest Score",
        filtered_df["Score"].min()
    )

    # ---------------- SCORE DISTRIBUTION ---------------- #
    st.header("📈 Score Distribution")

    fig, ax = plt.subplots()

    sns.histplot(
        filtered_df["Score"],
        bins=10,
        kde=True,
        ax=ax
    )

    st.pyplot(fig)

    # ---------------- LEADERBOARD ---------------- #
    st.header("🏆 Leaderboard")

    leaderboard_df = leaderboard(filtered_df)

    st.dataframe(
        leaderboard_df
    )

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    q_analysis = question_analysis(
        filtered_df,
        answer_df
    )

    st.dataframe(q_analysis)

    fig, ax = plt.subplots()

    sns.barplot(
        x="Question_ID",
        y="Accuracy",
        data=q_analysis,
        ax=ax
    )

    plt.xticks(rotation=45)

    st.pyplot(fig)

    # ---------------- ATTEMPT RATE ---------------- #
    st.header("📌 Attempt Rate")

    attempt_df = attempt_rate(
        filtered_df,
        answer_df
    )

    st.dataframe(attempt_df)

    # ---------------- DEPARTMENT PERFORMANCE ---------------- #
    st.header("🏢 Department Performance")

    dept_df = department_performance(
        filtered_df
    )

    fig, ax = plt.subplots()

    dept_df.plot(
        kind="bar",
        ax=ax
    )

    st.pyplot(fig)

    # ---------------- HEATMAP ---------------- #
    st.header("🔥 Heatmap")

    heatmap_df = heatmap_data(
        filtered_df
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    sns.heatmap(
        heatmap_df,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)

    # ---------------- SUSPICIOUS DETECTION ---------------- #
    st.header("🚨 Suspicious Pattern Detection")

    suspicious = filtered_df.groupby(
        "Score"
    ).size()

    suspicious = suspicious[
        suspicious > 5
    ]

    st.write(suspicious)

    # ---------------- DOWNLOAD REPORT ---------------- #
    st.header("📥 Download Report")

    report_csv = leaderboard_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download Leaderboard",
        data=report_csv,
        file_name="leaderboard.csv",
        mime="text/csv"
    )
