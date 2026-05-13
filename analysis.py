import pandas as pd
import numpy as np


# ---------------- LOAD FILE ---------------- #
def load_file(file):

    # ---------------- CSV ---------------- #
    if file.name.endswith(".csv"):

        df = pd.read_csv(file)

    # ---------------- EXCEL ---------------- #
    else:

        df = pd.read_excel(file)

    # ---------------- CLEAN COLUMN NAMES ---------------- #
    df.columns = df.columns.str.strip()

    # ---------------- FILL EMPTY VALUES ---------------- #
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

    # ---------------- REQUIRED STUDENT COLUMNS ---------------- #
    required_cols = [
        "Name",
        "Department",
        "College",
        "Subject"
    ]

    for col in required_cols:

        if col not in df.columns:

            return False, f"❌ Missing column: {col}"

    # ---------------- REQUIRED ANSWER COLUMNS ---------------- #
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

    # ---------------- SUBJECT CLEANING ---------------- #
    df["Subject"] = (
        df["Subject"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    answer_df["Subject"] = (
        answer_df["Subject"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ---------------- VALID ANSWERS ---------------- #
    valid_options = [
        "A",
        "B",
        "C",
        "D",
        "NOT ANSWERED"
    ]

    subjects = answer_df["Subject"].unique()

    for subject in subjects:

        subject_students = df[
            df["Subject"] == subject
        ].copy()

        subject_answers = answer_df[
            answer_df["Subject"] == subject
        ]

        # Skip if no student data
        if subject_students.empty:

            continue

        qids = subject_answers[
            "Question_ID"
        ].tolist()

        for qid in qids:

            if qid not in subject_students.columns:

                continue

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

    subject_results = []

    # ---------------- CLEAN SUBJECT NAMES ---------------- #
    df["Subject"] = (
        df["Subject"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    answer_df["Subject"] = (
        answer_df["Subject"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    subjects = df["Subject"].unique()

    for subject in subjects:

        # ---------------- FILTER SUBJECT ---------------- #
        subject_students = df[
            df["Subject"] == subject
        ].copy()

        subject_answers = answer_df[
            answer_df["Subject"] == subject
        ].copy()

        # ---------------- SKIP EMPTY ---------------- #
        if subject_students.empty:

            continue

        if subject_answers.empty:

            continue

        # ---------------- ANSWER KEY ---------------- #
        answer_key = dict(
            zip(
                subject_answers["Question_ID"],
                subject_answers["Answer"]
            )
        )

        scores = []

        # ---------------- SCORE CALCULATION ---------------- #
        for _, row in subject_students.iterrows():

            score = 0

            for qid, correct_ans in answer_key.items():

                if qid in row.index:

                    student_ans = (
                        str(row[qid])
                        .strip()
                        .upper()
                    )

                    correct_ans = (
                        str(correct_ans)
                        .strip()
                        .upper()
                    )

                    if student_ans == correct_ans:

                        score += 1

            scores.append(score)

        # ---------------- ADD SCORE ---------------- #
        subject_students["Score"] = scores

        subject_results.append(subject_students)

    # ---------------- EMPTY CHECK ---------------- #
    if len(subject_results) == 0:

        empty_df = pd.DataFrame()

        return empty_df, empty_df

    # ---------------- MERGE ALL SUBJECTS ---------------- #
    merged_df = pd.concat(
        subject_results,
        ignore_index=True
    )

    # ---------------- FINAL LEADERBOARD ---------------- #
    final_df = merged_df.groupby(
        ["Name", "Department", "College"],
        as_index=False
    ).agg({

        # SUM MULTIPLE SUBJECT SCORES
        "Score": "sum",

        # COMBINE SUBJECT NAMES
        "Subject": lambda x:
            ", ".join(sorted(set(x)))

    })

    # ---------------- SORT ---------------- #
    final_df = final_df.sort_values(
        "Score",
        ascending=False
    )

    return merged_df, final_df


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
