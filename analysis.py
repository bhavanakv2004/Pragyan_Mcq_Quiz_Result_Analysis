import pandas as pd
import numpy as np

# ---------------- LOAD FILE ---------------- #
def load_file(file):

    # CSV FILE
    if file.name.endswith(".csv"):

        df = pd.read_csv(file)

    # EXCEL FILE
    else:

        df = pd.read_excel(file)

    # Remove spaces from columns
    df.columns = df.columns.str.strip()

    # Fill empty values
    df.fillna("NOT ANSWERED", inplace=True)

    # ---------------- AUTO UPPERCASE ---------------- #
    for col in df.columns:

        if col not in [
            "Name",
            "Department",
            "College",
            "Subject"
        ]:

            df[col] = (
                df[col]
                .astype(str)
                .str.strip()
                .str.upper()
            )

    return df


# ---------------- VALIDATE FILES ---------------- #
def validate_files(df, answer_df):

    required_cols = [
        "Name",
        "Department",
        "College",
        "Subject"
    ]

    for col in required_cols:

        if col not in df.columns:

            return False, f"❌ Missing column: {col}"

    answer_required = [
        "Question_ID",
        "Answer",
        "Subject"
    ]

    for col in answer_required:

        if col not in answer_df.columns:

            return False, (
                f"❌ Missing answer key column: {col}"
            )

    valid_options = [
        "A",
        "B",
        "C",
        "D",
        "NOT ANSWERED"
    ]

    # ---------------- SUBJECT-WISE VALIDATION ---------------- #
    subjects = answer_df["Subject"].unique()

    for subject in subjects:

        # Filter subject data
        subject_students = df[
            df["Subject"] == subject
        ].copy()

        subject_answers = answer_df[
            answer_df["Subject"] == subject
        ]

        qids = subject_answers[
            "Question_ID"
        ].tolist()

        for qid in qids:

            # Skip if question column missing
            if qid not in subject_students.columns:

                continue

            # Fill NaN values
            subject_students[qid] = (
                subject_students[qid]
                .fillna("NOT ANSWERED")
                .astype(str)
                .str.strip()
                .str.upper()
            )

            invalid = ~subject_students[qid].isin(
                valid_options
            )

            if invalid.any():

                return False, (
                    f"❌ Invalid values in "
                    f"{qid} ({subject})"
                )

    return True, "✅ Files validated successfully"
# ---------------- CALCULATE SCORE ---------------- #
def calculate_score(df, answer_df):

    scores = []

    # Get answer list
    correct_answers = (
        answer_df["Answer"]
        .astype(str)
        .str.strip()
        .str.upper()
        .tolist()
    )

    # Detect question columns automatically
    question_cols = [
        col for col in df.columns
        if col not in [
            "Name",
            "Department",
            "College",
            "Subject"
        ]
    ]

    # Sort columns
    question_cols = sorted(question_cols)

    for _, row in df.iterrows():

        score = 0

        for i, col in enumerate(question_cols):

            if i < len(correct_answers):

                student_ans = (
                    str(row[col])
                    .strip()
                    .upper()
                )

                correct_ans = correct_answers[i]

                if student_ans == correct_ans:

                    score += 1

        scores.append(score)

    df["Score"] = scores

    return df
# ---------------- QUESTION ANALYSIS ---------------- #
def question_analysis(df, answer_df):

    result = []

    for _, ans_row in answer_df.iterrows():

        qid = ans_row["Question_ID"]

        correct_ans = (
            str(ans_row["Answer"])
            .strip()
            .upper()
        )

        if qid in df.columns:

            correct = (
                df[qid]
                .astype(str)
                .str.strip()
                .str.upper()
                == correct_ans
            ).sum()

            accuracy = correct / len(df)

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
                df[qid]
                .astype(str)
                .str.upper()
                != "NOT ANSWERED"
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


# ---------------- HEATMAP ---------------- #
def heatmap_data(df):

    return df.pivot_table(
        values="Score",
        index="Department",
        columns="College",
        aggfunc="mean",
        fill_value=0
    )
