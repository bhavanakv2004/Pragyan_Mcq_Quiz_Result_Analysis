import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from analysis import *
from auth import *

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="MCQ Analytics Dashboard",
    layout="wide"
)

# ---------------- SESSION ---------------- #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- LOGIN PAGE ---------------- #
if not st.session_state.logged_in:

    st.markdown("""
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
        margin-top: 30px;
    }

    .sub-title {
        text-align: center;
        color: #dddddd;
        font-size: 18px;
        margin-bottom: 30px;
    }

    div.stButton > button {
        width: 100%;
        height: 45px;
        border-radius: 10px;
        font-size: 18px;
    }

    </style>
    """, unsafe_allow_html=True)

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

        # ---------------- REGISTER ---------------- #
        if option == "Register":

            st.subheader("📝 Register")

            new_user = st.text_input("Username")

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

                    st.error("❌ Passwords do not match")

                else:

                    success, msg = register_user(
                        new_user,
                        new_pass
                    )

                    if success:
                        st.success(msg)

                    else:
                        st.error(msg)

        # ---------------- LOGIN ---------------- #
        else:

            st.subheader("🔐 Login")

            username = st.text_input("Username")

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

    st.stop()

# ---------------- TITLE ---------------- #
st.title("📊 MCQ Analytics Dashboard")

# ---------------- UPLOAD TYPE ---------------- #
upload_mode = st.radio(
    "📂 Select Upload Type",
    ["Single Subject", "Multiple Subjects"],
    horizontal=True
)

# ---------------- SINGLE SUBJECT ---------------- #
if upload_mode == "Single Subject":

    response_files = [
        st.file_uploader(
            "Upload Student Response File",
            type=["csv", "xlsx"],
            key="single_response"
        )
    ]

    answer_files = [
        st.file_uploader(
            "Upload Answer Key File",
            type=["csv", "xlsx"],
            key="single_answer"
        )
    ]

# ---------------- MULTIPLE SUBJECT ---------------- #
else:

    response_files = st.file_uploader(
        "Upload Multiple Student Response Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="multi_response"
    )

    answer_files = st.file_uploader(
        "Upload Multiple Answer Key Files",
        type=["csv", "xlsx"],
        accept_multiple_files=True,
        key="multi_answer"
    )

# ---------------- REMOVE EMPTY ---------------- #
response_files = [
    file for file in response_files
    if file is not None
]

answer_files = [
    file for file in answer_files
    if file is not None
]

# ---------------- PROCESS FILES ---------------- #
if response_files and answer_files:

    all_students = []
    all_answers = []

    # ---------------- RESPONSE FILES ---------------- #
    for file in response_files:

        try:

            temp_df = load_file(file)

            subject_name = (
                file.name
                .split(".")[0]
                .replace("_student", "")
                .replace("_answers", "")
                .replace(" student", "")
                .replace(" answers", "")
                .replace(" (1)", "")
                .replace(" (2)", "")
                .replace(" (3)", "")
                .strip()
                .upper()
            )

            temp_df["Subject"] = subject_name

            all_students.append(temp_df)

        except Exception as e:

            st.error(
                f"❌ Error reading {file.name}: {e}"
            )

    # ---------------- ANSWER FILES ---------------- #
    for file in answer_files:

        try:

            ans_df = load_file(file)

            subject_name = (
                file.name
                .split(".")[0]
                .replace("_student", "")
                .replace("_answers", "")
                .replace(" student", "")
                .replace(" answers", "")
                .replace(" (1)", "")
                .replace(" (2)", "")
                .replace(" (3)", "")
                .strip()
                .upper()
            )

            ans_df["Subject"] = subject_name

            all_answers.append(ans_df)

        except Exception as e:

            st.error(
                f"❌ Error reading {file.name}: {e}"
            )

    # ---------------- EMPTY CHECK ---------------- #
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

    # ---------------- MERGE ---------------- #
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
    raw_df, df = calculate_score(
        df,
        answer_df
    )

    # ---------------- EMPTY CHECK ---------------- #
    if df.empty:

        st.error(
            "❌ No matching subject data found"
        )

        st.stop()

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

    all_subjects = []

    for item in df["Subject"]:
    
        split_subjects = str(item).split(",")
    
        for sub in split_subjects:
    
            all_subjects.append(
                sub.strip().upper()
            )
    
    subjects = st.sidebar.multiselect(
        "Select Subject",
        sorted(set(all_subjects))
    )

    # ---------------- FILTER DATA ---------------- #
    filtered_df = df.copy()

    if colleges:

        filtered_df = filtered_df[
            filtered_df["College"].isin(colleges)
        ]

    if departments:

        filtered_df = filtered_df[
            filtered_df["Department"].isin(departments)
        ]

   # ---------------- SUBJECT FILTER ---------------- #
    if subjects:

        def subject_match(subject_text):
    
            # Convert:
            # "PYTHON, JAVA"
            # into list
    
            student_subjects = [
                s.strip().upper()
                for s in str(subject_text).split(",")
            ]
    
            selected_subjects = [
                s.strip().upper()
                for s in subjects
            ]
    
            # Check at least one match
            return any(
                sub in student_subjects
                for sub in selected_subjects
            )
    
        filtered_df = filtered_df[
            filtered_df["Subject"].apply(
                subject_match
            )
        ]

    # ---------------- KPI ---------------- #
    st.header("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Students",
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

    # ---------------- LEADERBOARD ---------------- #
    st.header("🏆 Leaderboard")

    leaderboard_df = leaderboard(filtered_df)

    st.dataframe(leaderboard_df)

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    q_analysis = question_analysis(
        raw_df,
        answer_df
    )

    st.dataframe(q_analysis)

    # ---------------- ATTEMPT RATE ---------------- #
    st.header("📌 Attempt Rate")

    attempt_df = attempt_rate(
        raw_df,
        answer_df
    )

    st.dataframe(attempt_df)

    # ---------------- DEPARTMENT PERFORMANCE ---------------- #
    st.header("🏢 Department Performance")

    dept_df = department_performance(
        filtered_df
    )

    st.bar_chart(dept_df)

    # ---------------- HEATMAP ---------------- #
    st.header("🔥 Department Heatmap")

    heatmap_df = heatmap_data(
        filtered_df
    )

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
