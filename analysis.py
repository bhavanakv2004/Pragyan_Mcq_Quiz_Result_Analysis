# ---------------- CALCULATE SCORE ---------------- #
def calculate_score(df, answer_df):

    subject_results = []

    # CLEAN SUBJECT NAMES
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

    # LOOP SUBJECTS
    for subject in subjects:

        subject_students = df[
            df["Subject"] == subject
        ].copy()

        subject_answers = answer_df[
            answer_df["Subject"] == subject
        ].copy()

        # SKIP EMPTY SUBJECTS
        if len(subject_students) == 0:
            continue

        if len(subject_answers) == 0:
            continue

        # ANSWER KEY
        answer_key = dict(
            zip(
                subject_answers["Question_ID"],
                subject_answers["Answer"]
            )
        )

        scores = []

        # SCORE EACH STUDENT
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

        # ADD SCORE COLUMN
        subject_students["Score"] = scores

        # STORE SUBJECT RESULT
        subject_results.append(subject_students)

    # EMPTY CHECK
    if len(subject_results) == 0:

        empty_df = pd.DataFrame()

        return empty_df, empty_df

    # MERGE ALL SUBJECTS
    merged_df = pd.concat(
        subject_results,
        ignore_index=True
    )

    # COMBINE SAME STUDENT
    final_df = merged_df.groupby(
        ["Name", "Department", "College"],
        as_index=False
    ).agg({

        "Score": "sum",

        "Subject": lambda x:
            ", ".join(sorted(set(x)))

    })

    # SORT SCORE
    final_df = final_df.sort_values(
        "Score",
        ascending=False
    )

    return merged_df, final_df
