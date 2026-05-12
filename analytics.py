import pandas as pd


# ==========================================
# Evaluate Student Responses
# ==========================================
def evaluate_answers(response_df, answer_df):

    merged = pd.merge(
        response_df,
        answer_df,
        on="Question_ID",
        how="left"
    )

    merged["Result"] = (
        merged["Student_Answer"] == merged["Correct_Answer"]
    )

    merged["Score"] = merged["Result"].astype(int)

    return merged


# ==========================================
# Student Performance
# ==========================================
def student_performance(result_df):

    performance = (
        result_df.groupby(["Student_ID", "Subject"])["Score"]
        .sum()
        .reset_index()
    )

    return performance


# ==========================================
# Weak Question Analysis
# ==========================================
def difficult_questions(result_df):

    difficulty = (
        result_df.groupby("Question_ID")["Score"]
        .mean()
        .reset_index()
    )

    difficulty.columns = ["Question_ID", "Accuracy"]

    difficult = difficulty[difficulty["Accuracy"] < 0.4]

    return difficult
