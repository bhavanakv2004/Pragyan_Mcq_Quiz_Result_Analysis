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

    # ---------- CUSTOM CSS ---------- #
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
            box-shadow: 0px 0px 25px rgba(0,0,0,0.3);
        }

        div.stButton > button {
            width: 100%;
            height: 50px;
            border-radius: 10px;
            font-size: 18px;
            background: linear-gradient(
                to right,
                #00c6ff,
                #0072ff
            );
            color: white;
            border: none;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="main-title">📊 Secure MCQ Analytics Dashboard</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">Login or Register to Continue</div>',
        unsafe_allow_html=True
    )

    option = st.radio(
        "Choose Option",
        ["Login", "Register"],
        horizontal=True
    )

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown(
            '<div class="login-box">',
            unsafe_allow_html=True
        )

        # -------- REGISTER -------- #
        if option == "Register":

            st.subheader("📝 Create Account")

            new_user = st.text_input(
                "Create Username"
            )

            new_pass = st.text_input(
                "Create Password",
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

                elif len(new_pass) < 4:

                    st.warning(
                        "⚠️ Password should contain minimum 4 characters"
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

                    st.success(
                        "✅ Login Successful"
                    )

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
st.title("📊 Secure Multi-Subject MCQ Analytics")

st.markdown("""
Analyze:
- Multiple Quiz Files
- Randomized Questions
- Department Performance
- College Ranking
- Weak Questions
- Attempt Rate
""")

# ---------------- MULTIPLE FILE UPLOAD ---------------- #
response_files = st.file_uploader(
    "📂 Upload Multiple Student Response Files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

answer_files = st.file_uploader(
    "📂 Upload Multiple Answer Key Files",
    type=["csv", "xlsx"],
    accept_multiple_files=True
)

# ---------------- PROCESS FILES ---------------- #
if response_files and answer_files:

    all_students = []
    all_answers = []

    # -------- LOAD RESPONSE FILES -------- #
    for file in response_files:

        try:

            temp_df = load_file(file)

            subject_name = (
                file.name.split(".")[0]
            )

            temp_df["Subject"] = subject_name

            all_students.append(temp_df)

        except Exception as e:

            st.error(
                f"❌ Error reading {file.name}: {e}"
            )

    # -------- LOAD ANSWER FILES -------- #
    for file in answer_files:

        try:

            ans_df = load_file(file)

            subject_name = (
                file.name.split("_")[0]
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

    # ---------------- KPI ---------------- #
    st.header("📌 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Students",
        len(df)
    )

    col2.metric(
        "Average Score",
        round(df["Score"].mean(), 2)
    )

    col3.metric(
        "Highest Score",
        df["Score"].max()
    )

    col4.metric(
        "Lowest Score",
        df["Score"].min()
    )

    # ---------------- SUBJECT PERFORMANCE ---------------- #
    st.header("📚 Subject-wise Performance")

    subject_perf = (
        df.groupby("Subject")["Score"]
        .mean()
        .sort_values(ascending=False)
    )

    st.dataframe(subject_perf)

    fig, ax = plt.subplots()

    subject_perf.plot(
        kind="bar",
        ax=ax
    )

    ax.set_title(
        "Average Score by Subject"
    )

    st.pyplot(fig)

    # ---------------- LEADERBOARD ---------------- #
    st.header("🏆 Leaderboard")

    leaderboard_df = leaderboard(df)

    st.dataframe(
        leaderboard_df
    )

    # ---------------- QUESTION ANALYSIS ---------------- #
    st.header("❓ Question Analysis")

    q_analysis = question_analysis(
        df,
        answer_df
    )

    st.dataframe(q_analysis)

    # ---------------- ATTEMPT RATE ---------------- #
    st.header("📌 Attempt Rate")

    attempt_df = attempt_rate(
        df,
        answer_df
    )

    st.dataframe(attempt_df)

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

    # ---------------- DOWNLOAD REPORT ---------------- #
    st.header("📥 Download Leaderboard")

    csv = leaderboard_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="leaderboard.csv",
        mime="text/csv"
    )
