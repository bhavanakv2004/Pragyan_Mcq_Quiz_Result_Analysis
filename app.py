import streamlit as st
import pandas as pd
import plotly.express as px

from auth import authenticate
from validator import *
from analytics import *
from audit import log_activity
from security import generate_file_hash


# ==========================================
# Streamlit Config
# ==========================================
st.set_page_config(
    page_title="Secure Quiz Analytics",
    layout="wide"
)


# ==========================================
# Authentication Section
# ==========================================
st.sidebar.title("Authentication")

menu = st.sidebar.selectbox(
    "Select Option",
    ["Login", "Register"]
)
# ==========================================
# Register
# ==========================================
if menu == "Register":

    st.sidebar.subheader("Create Account")

    new_user = st.sidebar.text_input("Username")
    new_password = st.sidebar.text_input(
        "Password",
        type="password"
    )

    role = st.sidebar.selectbox(
        "Role",
        ["faculty", "student"]
    )

    college_id = st.sidebar.text_input("College ID")

    register_btn = st.sidebar.button("Register")

    if register_btn:

        from auth import register_user

        status, message = register_user(
            new_user,
            new_password,
            role,
            college_id
        )

        if status:
            st.success(message)
            log_activity(new_user, "Registered Account")
        else:
            st.error(message)

    st.stop()
  # ==========================================
# Login
# ==========================================
st.sidebar.subheader("Login")

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input(
    "Password",
    type="password"
)

login = st.sidebar.button("Login")

if login:

    status, user = authenticate(username, password)

    if status:
        st.session_state["user"] = user
        st.session_state["username"] = username
        st.success("Login Successful")
        log_activity(username, "Logged In")

    else:
        st.error("Invalid Credentials")
        st.stop()


if "user" not in st.session_state:
    st.warning("Please login")
    st.stop()


user = st.session_state["user"]
username = st.session_state["username"]
# ==========================================
# Dashboard Title
# ==========================================
st.title("Secure Multi-Subject Quiz Analytics System")


# ==========================================
# Upload Files
# ==========================================
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


# ==========================================
# Read Uploaded Files
# ==========================================
def read_file(file):

    if file.name.endswith("csv"):
        return pd.read_csv(file)

    return pd.read_excel(file)
# ==========================================

        if missing:
            st.error(f"Missing columns in {file.name}: {missing}")
            st.stop()

        # ====================================
        # College Access Protection
        # ====================================
        if user["role"] != "admin":

            allowed_college = user["college_id"]

            invalid = df[
                df["College_ID"] != allowed_college
            ]

            if len(invalid) > 0:
                st.error(
                    "Unauthorized College Data Detected"
                )
                st.stop()

        all_responses.append(df)


    # ====================================
    # Combine Multiple Subjects
    # ====================================
    answer_df = pd.concat(all_answers)
    response_df = pd.concat(all_responses)


    # ====================================
    # Randomized Question Handling
    # ====================================
    result_df = evaluate_answers(
        response_df,
        answer_df
    )


    # ====================================
    # Performance Analytics
    # ====================================
    performance_df = student_performance(result_df)


    # ====================================
    # Display Results
    # ====================================
    st.subheader("Student Performance")
    st.dataframe(performance_df)


    # ====================================
    # Charts
    # ====================================
    fig = px.bar(
        performance_df,
        x="Student_ID",
        y="Score",
        color="Subject",
        title="Student Scores"
    )

    st.plotly_chart(fig, use_container_width=True)


    # ====================================
    # Difficult Questions
    # ====================================
    st.subheader("Difficult Questions")

    difficult_df = difficult_questions(result_df)

    st.dataframe(difficult_df)


    # ====================================
    # Weak Students
    # ====================================
    st.subheader("Weak Students")

    weak_students = performance_df[
        performance_df["Score"] < 3
    ]

    st.dataframe(weak_students)


    # ====================================
    # Download Reports
    # ====================================
    csv = performance_df.to_csv(index=False)

    st.download_button(
        label="Download Performance Report",
        data=csv,
        file_name="performance_report.csv",
        mime="text/csv"
    )


    # ====================================
    # Audit Log
    # ====================================
    log_activity(username, "Processed Quiz Analytics")
