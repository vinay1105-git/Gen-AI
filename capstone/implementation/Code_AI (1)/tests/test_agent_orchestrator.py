import pytest

from backend.agents.orchestrator import AgentOrchestrator
from backend.schemas.agent_schemas import CodeGenerationRequest, CodeReviewRequest, VulnerabilityRequest


@pytest.mark.asyncio
async def test_agent_orchestrator_generate_code():
    orchestrator = AgentOrchestrator()
    request = CodeGenerationRequest(project_id=1, instructions="Create a Python function that adds two numbers.")
    response = orchestrator.generate_code(request)
    assert "function" in response.generated_code.lower() or response.generated_code.startswith("[fallback]")


@pytest.mark.asyncio
async def test_agent_orchestrator_review_code():
    orchestrator = AgentOrchestrator()
    request = CodeReviewRequest(project_id=1, code="print('Hello')")
    response = orchestrator.review_code(request)
    assert response.model_name is not None


@pytest.mark.asyncio
async def test_agent_orchestrator_analyze_vulnerabilities():
    orchestrator = AgentOrchestrator()
    request = VulnerabilityRequest(project_id=1, code="eval('2+2')", security_level=3)
    response = orchestrator.analyze_vulnerabilities(request)
    assert len(response.findings) >= 1


def test_quick_code_explanation_fallback_is_available():
    text = AgentOrchestrator._quick_code_explanation(
        'def is_palindrome(s):\n    return s == s[::-1]', 'python'
    )
    assert 'PURPOSE' in text and 'FLOW' in text and 'KEY FUNCTIONS' in text


def test_deterministic_fix_patches_vulnerabilities():
    orchestrator = AgentOrchestrator()
    vulnerable_code = "eval('user_input')\nshell=True\npickle.load(f)"
    fixed, changes = orchestrator._deterministic_fix(vulnerable_code, "python")
    assert "ast.literal_eval" in fixed
    assert "shell=False" in fixed
    assert "json.loads" in fixed
    assert len(changes) >= 3


def test_pdf_export_generation():
    from backend.reports.report_builder import ReportBuilder
    from backend.schemas.agent_schemas import PDFExportRequest, VulnerabilityFinding

    builder = ReportBuilder()
    req = PDFExportRequest(
        project_id=1,
        title="Test Security Audit",
        code="def hello(): return 'world'",
        review_score=92,
        review_summary="Code is clean and concise.",
        vulnerabilities=[
            VulnerabilityFinding(
                severity="low",
                pattern="None",
                description="No vulnerabilities",
                recommendation="Keep code clean",
                cwe_id="CWE-0",
                risk_score=1.0,
            )
        ],
    )
    pdf_bytes = builder.generate_audit_pdf(req)
    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 500

