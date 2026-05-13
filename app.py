import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import *
from auth import *

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title=" Smart MCQ Quiz Analytics Dashboard",
    layout="wide",
    )
# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN SYSTEM ---------------- #
if not st.session_state.logged_in:

    st.markdown(
        """
        <style>

        .stApp {
            background: linear-gradient(
                to right,
                #0f2027,
                #203a43,
                #2c5364
            );
        }

        .main-title {
            text-align: center;
            color: white;
            font-size: 42px;
            font-weight: bold;
            margin-top: 20px;
        }

        .sub-title {
            text-align: center;
            color: #dddddd;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .login-box {
            background-color: rgba(255,255,255,0.08);
            padding: 35px;
            border-radius: 20px;
        }

        div.stButton > button {
            width: 100%;
            height: 50px;
            border-radius: 10px;
            font-size: 18px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">📊 Smart MCQ Quiz Analytics Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Login or Register</div>',
        unsafe_allow_html=True
    )

    option = st.radio(
        "Choose Option",
        ["Login", "Register"],
        horizontal=True
    )

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        
        # -------- REGISTER -------- #
        if option == "Register":

            st.subheader("📝 Register")

            new_user = st.text_input(
                "Username"
            )

            new_pass = st.text_input(
                "Password",
                type="password"
            )

            confirm_pass = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button("Register"):

                if new_pass != confirm_pass:

                    st.error(
                        "❌ Passwords do not match"
                    )

                else:

                    success, msg = register_user(
                        new_user,
                        new_pass
                    )

                    if success:
                        st.success(msg)

                    else:
                        st.error(msg)

        # -------- LOGIN -------- #
        else:

            st.subheader("🔐 Login")

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

                    st.rerun()

                else:

                    st.error(
                        "❌ Invalid Username or Password"
                    )

        st.markdown(
            '</div>',
            unsafe_allow_html=True
        )

    st.stop()

# ---------------- SIDEBAR ---------------- #
st.sidebar.success(
    f"Logged in as: {st.session_state.username}"
)

if st.sidebar.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.username = ""

    st.rerun()

# ---------------- TITLE ---------------- #
st.title("📊  MCQ Analytics")

# ---------------- MULTIPLE FILE UPLOAD ---------------- #
response_files = st.file_uploader(
    "📂 Upload Student Response Files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

answer_files = st.file_uploader(
    "📂 Upload Answer Key Files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# ---------------- PROCESS FILES ---------------- #
if response_files and answer_files:

    all_students = []
    all_answers = []

    # -------- RESPONSE FILES -------- #
    for file in response_files:

        try:

            temp_df = load_file(file)

            subject_name = (
                file.name
                .split(".")[0]
                .replace(" (2)", "")
                .replace(" (3)", "")
                .replace("_answers", "")
                .strip()
            )

            temp_df["Subject"] = subject_name

            all_students.append(temp_df)

        except Exception as e:

            st.error(
                f"❌ Error reading {file.name}: {e}"
            )

    # -------- ANSWER FILES -------- #
    for file in answer_files:

        try:

            ans_df = load_file(file)

            subject_name = (
                file.name
                .split(".")[0]
                .replace(" (2)", "")
                .replace(" (3)", "")
                .replace("_answers", "")
                .strip()
            )

            ans_df["Subject"] = subject_name

            all_answers.append(ans_df)

        except Exception as e:

            st.error(
                f"❌ Error reading {file.name}: {e}"
            )

    # -------- EMPTY CHECK -------- #
    if len(all_students) == 0:

        st.warning(
            "⚠️ No valid student files uploaded"
        )

        st.stop()

    if len(all_answers) == 0:

        st.warning(
            "⚠️ No valid answer files uploaded"
        )

        st.stop()

    # -------- MERGE FILES -------- #
    df = pd.concat(
        all_students,
        ignore_index=True
    )

    answer_df = pd.concat(
        all_answers,
        ignore_index=True
    )

    # ---------------- VALIDATION ---------------- #
    valid, message = validate_files(
        df,
        answer_df
    )

    if not valid:

        st.error(message)

        st.stop()

    st.success(message)

    # ---------------- SCORE ---------------- #
    df = calculate_score(
        df,
        answer_df
    )
     # ---------------- SIDEBAR FILTERS ---------------- #
    st.sidebar.header("🔍 Filters")

    colleges = st.sidebar.multiselect("Select College", df["College"].unique())
    departments = st.sidebar.multiselect("Select Department", df["Department"].unique())
    students = st.sidebar.multiselect("Select Student", df["Name"].unique())
    subject = st.sidebar.multiselect("Select Subject", df["Subject"].unique())
                                     
    filtered_df = df.copy()

    if colleges:
        filtered_df = filtered_df[filtered_df["College"].isin(colleges)]
    if departments:
        filtered_df = filtered_df[filtered_df["Department"].isin(departments)]
    if students:
        filtered_df = filtered_df[filtered_df["Name"].isin(students)]


    # ---------------- KPI ---------------- #
    st.header("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Students",len(df))
    col2.metric("Average Score",round(df["Score"].mean(), 2))
    col3.metric("Highest Score",df["Score"].max())
    col4.metric("Lowest Score",df["Score"].min())

    # ---------------- LEADERBOARD ---------------- #
    st.header("🏆 Leaderboard")

    leaderboard_df = leaderboard(df)

    st.dataframe(leaderboard_df)

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    q_analysis = question_analysis(df,answer_df)
    st.dataframe(q_analysis)

    # ---------------- ATTEMPT RATE ---------------- #
    st.header("📌 Attempt Rate")

    attempt_df = attempt_rate(
        df,
        answer_df
    )
    st.dataframe(attempt_df)
      # ---------------- DEPARTMENT PERFORMANCE ---------------- #
    st.header("🏢 Department Performance")

    col1, col2 = st.columns(2)

    with col1:
        dept = department_performance(filtered_df)
        fig, ax = plt.subplots()
        dept.plot(kind="bar", ax=ax)
        ax.set_title("Department Performance")
        st.pyplot(fig)

    with col2:
        pivot = heatmap_data(filtered_df)
        fig, ax = plt.subplots()
        sns.heatmap(pivot, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)

    # Department Insights Table
    st.subheader("📊 Department Insights")
    dept_df = filtered_df.groupby("Department")["Score"].agg(["mean", "count"])
    st.dataframe(dept_df)

    # ---------------- COLLEGE PERFORMANCE ---------------- #
    st.header("🏫 College Ranking")

    college_df = filtered_df.groupby("College")["Score"].mean().sort_values(ascending=False)

    fig, ax = plt.subplots()
    college_df.plot(kind="barh", ax=ax)
    ax.set_title("College Performance")
    st.pyplot(fig)

    # ---------------- HEATMAP ---------------- #
    st.header("🔥 Department Heatmap")

    heatmap_df = heatmap_data(df)

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    sns.heatmap(
        heatmap_df,
        annot=True,
        cmap="coolwarm",
        ax=ax
    )

    st.pyplot(fig)
