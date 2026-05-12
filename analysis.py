import pandas as pd
import numpy as np

# ---------------- LOAD DATA ---------------- #
def load_data(data_file, answer_file):

    df = pd.read_csv(data_file)
    answer_df = pd.read_csv(answer_file)

    df.fillna("Not Answered", inplace=True)

    df.columns = df.columns.str.strip()
    answer_df.columns = answer_df.columns.str.strip()

    return df, answer_df


# ---------------- VALIDATION ---------------- #
def validate_files(df, answer_df):

    required_cols = ["Name", "Department", "College", "Subject"]

    for col in required_cols:

        if col not in df.columns:
            return False, f"❌ Missing column: {col}"

    # Answer file validation
    required_answer_cols = [
        "Subject",
        "Question_ID",
        "Answer"
    ]

    for col in required_answer_cols:

        if col not in answer_df.columns:
            return False, f"❌ Missing answer key column: {col}"

    # Duplicate check
    if df.duplicated().sum() > 0:
        return False, "❌ Duplicate student records found"

    # Missing values
    if df.isnull().sum().sum() > 0:
        return False, "❌ Missing values detected"

    # Valid options
    valid_options = [
        "A",
        "B",
        "C",
        "D",
        "Not Answered"
    ]

    # Validate answers
    qids = answer_df["Question_ID"].unique()

    for qid in qids:

        if qid not in df.columns:
            return False, f"❌ Missing question column: {qid}"

        invalid = ~df[qid].isin(valid_options)

        if invalid.any():
            return False, f"❌ Invalid answers in {qid}"

    return True, "✅ Files Valid"


# ---------------- SCORE CALCULATION ---------------- #
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

            correct = df[
                df[qid] == correct_ans
            ].shape[0]

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
        columns=["Question_ID", "Accuracy", "Difficulty"]
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
        columns=["Question_ID", "Attempt Rate"]
    )


# ---------------- SCORE STATS ---------------- #
def score_statistics(df):

    return {
        "Mean": round(df["Score"].mean(), 2),
        "Median": round(df["Score"].median(), 2),
        "Std Dev": round(df["Score"].std(), 2)
    }


# ---------------- LEADERBOARD ---------------- #
def leaderboard(df):

    rank_df = df.sort_values(
        "Score",
        ascending=False
    )

    rank_df["Rank"] = rank_df["Score"].rank(
        ascending=False,
        method="dense"
    )

    return rank_df[
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

    return df.groupby(
        "Department"
    )["Score"].mean()


# ---------------- COLLEGE PERFORMANCE ---------------- #
def college_performance(df):

    return df.groupby(
        "College"
    )["Score"].mean()


# ---------------- HEATMAP ---------------- #
def heatmap_data(df):

    pivot = df.pivot_table(
        values="Score",
        index="Department",
        columns="College",
        aggfunc="mean",
        fill_value=0
    )

    return pivot
