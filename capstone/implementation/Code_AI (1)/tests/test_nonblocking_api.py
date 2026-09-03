from pathlib import Path


def test_llm_calls_are_offloaded_from_fastapi_event_loop():
    root = Path(__file__).resolve().parents[1]
    service = (root / "backend" / "services" / "agent_service.py").read_text(encoding="utf-8")
    assert "asyncio.to_thread(orchestrator.generate_code, request)" in service
    assert "asyncio.to_thread(orchestrator.review_code, request)" in service
    assert "asyncio.to_thread(orchestrator.analyze_vulnerabilities, request)" in service
