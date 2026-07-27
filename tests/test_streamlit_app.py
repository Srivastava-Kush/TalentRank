from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from streamlit_app import analyze_uploaded_resumes


def test_analyze_uploaded_resumes_ranks_candidates() -> None:
    resumes = [
        ("alice.txt", b"Alice Smith, 6 years of experience in Python, FastAPI, Docker."),
        ("bob.txt", b"Bob Jones, 2 years of experience in HTML and CSS."),
    ]

    result = analyze_uploaded_resumes(
        job_title="Backend Python Engineer",
        job_description="Need Python, FastAPI, Docker, PostgreSQL experience.",
        role_family="backend",
        must_have_skills=["python", "fastapi"],
        nice_to_have_skills=["docker"],
        resumes=resumes,
    )

    assert result["job_title"] == "Backend Python Engineer"
    assert result["role_family"] == "backend"
    assert result["ranked_candidates"][0]["name"] == "Alice Smith"
    assert result["ranked_candidates"][0]["hard_constraint_passed"] is True
    assert result["ranked_candidates"][1]["name"] == "Bob Jones"
