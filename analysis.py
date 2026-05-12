import pandas as pd
import numpy as np

# ---------------- LOAD FILE ---------------- #
def load_file(file):

    # CSV
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)

    # EXCEL
    else:
        df = pd.read_excel(file)

    # Remove spaces
    df.columns = df.columns.str.strip()

    # Fill empty values
    df.fillna("Not Answered", inplace=True)

    return df


# ---------------- VALIDATE FILES ---------------- #
def validate_files(df, answer_df):

    # Required columns
    required_cols = [
        "Name",
        "Department",
        "College",
        "Subject"
    ]

    for col in required_cols:

        if col not in df.columns:

            return False, f"❌ Missing column: {col}"

    # Answer key columns
    answer_required = [
        "Question_ID",
        "Answer",
        "Subject"
    ]

    for col in answer_required:

        if col not in answer_df.columns:

            return False, f"❌ Missing answer key column: {col}"

    # Duplicate records
    if df.duplicated().sum() > 0:

        return False, "❌ Duplicate student records found"

    # Valid options
    valid_options = [
        "A",
        "B",
        "C",
        "D",
        "Not Answered"
    ]

    qids = answer_df["Question_ID"].unique()

    for qid in qids:

        if qid not in df.columns:

            return False, f"❌ Missing question column: {qid}"

        invalid = ~df[qid].isin(valid_options)

        if invalid.any():

            return False, f"❌ Invalid values detected in {qid}"

    return True, "✅ Files validated successfully"


# ---------------- CALCULATE SCORE ---------------- #
def calculate_score(df, answer_df):

    scores = []

    for _, row in df.iterrows():

        subject_answers = answer_df[
            answer_df["Subject"] == row["Subject"]
        ]

        answer_key = dict(
            zip(
                subject_answers["Question_ID"],
                subject_answers["Answer"]
            )
        )

        score = 0

        for qid, correct_ans in answer_key.items():

            if qid in row.index:

                if row[qid] == correct_ans:

                    score += 1

        scores.append(score)

    df["Score"] = scores

    return df


# ---------------- QUESTION ANALYSIS ---------------- #
def question_analysis(df, answer_df):

    result = []

    for _, ans_row in answer_df.iterrows():

        qid = ans_row["Question_ID"]

        correct_ans = ans_row["Answer"]

        if qid in df.columns:

            correct = (
                df[qid] == correct_ans
            ).sum()

            accuracy = correct / len(df)

            # Difficulty
            if accuracy > 0.8:

                difficulty = "Easy"

            elif accuracy >= 0.5:

                difficulty = "Medium"

            else:

                difficulty = "Hard"

            result.append([
                qid,
                round(accuracy, 2),
                difficulty
            ])

    return pd.DataFrame(
        result,
        columns=[
            "Question_ID",
            "Accuracy",
            "Difficulty"
        ]
    )


# ---------------- ATTEMPT RATE ---------------- #
def attempt_rate(df, answer_df):

    result = []

    qids = answer_df["Question_ID"].unique()

    for qid in qids:

        if qid in df.columns:

            rate = (
                df[qid] != "Not Answered"
            ).mean()

            result.append([
                qid,
                round(rate, 2)
            ])

    return pd.DataFrame(
        result,
        columns=[
            "Question_ID",
            "Attempt Rate"
        ]
    )


# ---------------- LEADERBOARD ---------------- #
def leaderboard(df):

    leaderboard_df = df.sort_values(
        "Score",
        ascending=False
    )

    leaderboard_df["Rank"] = (
        leaderboard_df["Score"]
        .rank(
            ascending=False,
            method="dense"
        )
    )

    return leaderboard_df[
        [
            "Name",
            "Department",
            "College",
            "Subject",
            "Score",
            "Rank"
        ]
    ]


# ---------------- DEPARTMENT PERFORMANCE ---------------- #
def department_performance(df):

    return (
        df.groupby("Department")["Score"]
        .mean()
        .sort_values(ascending=False)
    )


# ---------------- COLLEGE PERFORMANCE ---------------- #
def college_performance(df):

    return (
        df.groupby("College")["Score"]
        .mean()
        .sort_values(ascending=False)
    )


# ---------------- HEATMAP ---------------- #
def heatmap_data(df):

    return df.pivot_table(
        values="Score",
        index="Department",
        columns="College",
        aggfunc="mean",
        fill_value=0
    )
