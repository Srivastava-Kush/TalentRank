import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.append(str(SRC))

from app.schemas import CandidateInput
from app.services.resume_parser import parse_resume_bytes, extract_candidate_profile
from app.services.scoring import build_skill_context, rank_candidates


st.set_page_config(page_title="TalentRank Studio", page_icon="📄", layout="wide")


def analyze_uploaded_resumes(
    job_title: str,
    job_description: str,
    role_family: str | None,
    must_have_skills: list[str],
    nice_to_have_skills: list[str],
    resumes: list[tuple[str, bytes]],
) -> dict[str, Any]:
    candidates: list[CandidateInput] = []

    for file_name, content in resumes:
        resume_text = parse_resume_bytes(file_name, content)
        candidate_name, years = extract_candidate_profile(resume_text, file_name)
        candidates.append(
            CandidateInput(
                name=candidate_name,
                resume_text=resume_text,
                years_experience=years,
            )
        )

    role, required, must_have, nice_to_have = build_skill_context(
        job_title,
        job_description,
        role_family,
        must_have_skills,
        nice_to_have_skills,
    )

    ranked = rank_candidates(candidates, role, required, must_have, nice_to_have)

    return {
        "job_title": job_title,
        "role_family": role,
        "required_skills": required,
        "must_have_skills": must_have,
        "nice_to_have_skills": nice_to_have,
        "ranked_candidates": [candidate.model_dump() for candidate in ranked[:5]],
    }


def main() -> None:
    st.title("TalentRank Studio")
    st.caption("Upload resumes and score them against a job description in Streamlit.")

    with st.sidebar:
        st.header("Job details")
        job_title = st.text_input("Job title", value="Backend Python Engineer")
        job_description = st.text_area(
            "Job description",
            value="Need strong Python, FastAPI, Docker, and PostgreSQL experience.",
            height=180,
        )
        role_family = st.selectbox(
            "Role family",
            options=["backend", "frontend", "data_ai", "devops", "fullstack"],
            index=0,
        )
        must_have_skills = st.text_input(
            "Must-have skills (comma separated)",
            value="python, fastapi",
        ).split(",")
        nice_to_have_skills = st.text_input(
            "Nice-to-have skills (comma separated)",
            value="docker, postgres",
        ).split(",")

        uploaded_files = st.file_uploader(
            "Upload resumes",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
        )

    if st.button("Analyze candidates", type="primary") and uploaded_files:
        resumes = [
            (file.name, file.getvalue())
            for file in uploaded_files
        ]
        result = analyze_uploaded_resumes(
            job_title=job_title,
            job_description=job_description,
            role_family=role_family,
            must_have_skills=[item.strip() for item in must_have_skills if item.strip()],
            nice_to_have_skills=[item.strip() for item in nice_to_have_skills if item.strip()],
            resumes=resumes,
        )

        st.success(f"Analyzed {len(result['ranked_candidates'])} candidates")

        st.subheader("Required skills")
        st.write(", ".join(result["required_skills"]))

        st.subheader("Ranked candidates")
        for candidate in result["ranked_candidates"]:
            with st.expander(f"{candidate['name']} — {candidate['total_score']} points"):
                st.write(f"Role family: {candidate['role_family']}")
                st.write(f"Matched skills: {', '.join(candidate['matched_skills']) or 'None'}")
                st.write(f"Missing skills: {', '.join(candidate['missing_skills']) or 'None'}")
                st.write(f"Strengths: {', '.join(candidate['strengths'])}")
                st.write(f"Concerns: {', '.join(candidate['concerns'])}")


if __name__ == "__main__":
    main()
