required_response_columns = [
    "Student_ID",
    "College_ID",
    "Question_ID",
    "Student_Answer"
]

required_answer_columns = [
    "Question_ID",
    "Correct_Answer",
    "Subject"
]


def validate_columns(df, required_columns):
    missing = []

    for col in required_columns:
        if col not in df.columns:
            missing.append(col)

    return missing
