import logging
import time
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import BASE_DIR
from backend.database.db import get_db
from backend.models import GeneratedCode, ReviewHistory
from backend.schemas.agent_schemas import (
    CodeGenerationRequest,
    CodeReviewRequest,
    VulnerabilityRequest,
    RecommendationRequest,
    ReportRequest,
    CodeExplanationRequest,
    AutoFixRequest,
    PipelineRequest,
    PDFExportRequest,
)
from backend.services.agent_service import AgentService, orchestrator


class SaveGeneratedRequest(BaseModel):
    project_id: int
    prompt: str
    code: str
    model_name: str

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/agents",
    tags=["AI Multi-Agent System"],
)


class ModelSelectRequest(BaseModel):
    model: str
    source: str = "remote"  # 'local' or 'remote'


@router.get("/models", summary="List available models")
def list_models():
    try:
        models = orchestrator.available_models()
        return {"success": True, "models": models}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-generated", summary="Persist generated code to DB")
async def save_generated(request: SaveGeneratedRequest, db: AsyncSession = Depends(get_db)):
    try:
        stmt = insert(GeneratedCode).values(
            project_id=request.project_id,
            code=request.code,
            prompt=request.prompt,
            model_name=request.model_name,
            created_at=datetime.utcnow(),
        )
        await db.execute(stmt)
        await db.commit()
        return {"success": True}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-model", summary="Get current active model")
def active_model():
    try:
        model = orchestrator.current_model()
        return {"success": True, "model": model}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", summary="Local LLM status")
def llm_status():
    try:
        return {"success": True, "data": orchestrator.llm_engine.status()}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/history/generated", summary="List generated code for a project")
async def list_generated(project_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    try:
        q = await db.execute(GeneratedCode.__table__.select() if project_id is None else GeneratedCode.__table__.select().where(GeneratedCode.project_id == project_id))
        rows = q.fetchall()
        items = [
            {
                "id": r.id,
                "project_id": r.project_id,
                "prompt": r.prompt,
                "code": r.code,
                "model_name": r.model_name,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        return {"success": True, "items": items}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/reviews", summary="List code reviews for a project")
async def list_reviews(project_id: Optional[int] = None, db: AsyncSession = Depends(get_db)):
    try:
        q = await db.execute(ReviewHistory.__table__.select() if project_id is None else ReviewHistory.__table__.select().where(ReviewHistory.project_id == project_id))
        rows = q.fetchall()
        items = [
            {
                "id": r.id,
                "project_id": r.project_id,
                "summary": r.summary,
                "findings": r.findings,
                "suggestions": r.suggestions,
                "model_name": r.model_name,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
        return {"success": True, "items": items}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/search", summary="Search history by text")
async def search_history(q: str, db: AsyncSession = Depends(get_db)):
    try:
        sql = GeneratedCode.__table__.select().where(GeneratedCode.prompt.ilike(f"%{q}%"))
        res = await db.execute(sql)
        gen = res.fetchall()

        sql2 = ReviewHistory.__table__.select().where(ReviewHistory.summary.ilike(f"%{q}%"))
        res2 = await db.execute(sql2)
        rev = res2.fetchall()

        items = {
            "generated": [
                {"id": r.id, "project_id": r.project_id, "prompt": r.prompt, "code": r.code, "model_name": r.model_name, "created_at": r.created_at.isoformat()} for r in gen
            ],
            "reviews": [
                {"id": r.id, "project_id": r.project_id, "summary": r.summary, "findings": r.findings, "suggestions": r.suggestions, "model_name": r.model_name, "created_at": r.created_at.isoformat()} for r in rev
            ],
        }

        return {"success": True, "items": items}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# 1-Click Unified Multi-Agent Pipeline
# ==========================================================

@router.post(
    "/pipeline",
    summary="1-Click Unified Multi-Agent Pipeline",
    description="Runs Generation, Review, Security Scanning, Explanation, and Auto-Fix in one workflow.",
)
async def run_pipeline(
    request: PipelineRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info("POST /pipeline - Running Unified Audit")
        result = await AgentService.run_full_pipeline(db, request)
        return {
            "success": True,
            "message": "Full multi-agent audit completed successfully.",
            "data": result,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# Auto-Fix Code Flaws
# ==========================================================

@router.post(
    "/auto-fix",
    summary="Auto-Fix & Refactor Code",
    description="Automatically patch vulnerabilities and apply quality improvements using the Refactor Agent.",
)
async def auto_fix_code(
    request: AutoFixRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        logger.info("POST /auto-fix - Refactoring Code")
        result = await AgentService.auto_fix_code(db, request)
        return {
            "success": True,
            "message": "Code auto-fixed successfully.",
            "data": result,
        }
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# PDF Export
# ==========================================================

@router.post(
    "/export-pdf",
    summary="Export PDF Security & Quality Audit Report",
    description="Generate and return binary PDF audit report.",
)
def export_pdf(request: PDFExportRequest):
    try:
        logger.info("POST /export-pdf - Generating PDF Report")
        pdf_bytes = AgentService.export_pdf_report(request)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=code_ai_audit_project_{request.project_id}.pdf"
            },
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))




@router.post("/generate-stream", summary="Generate Source Code (stream)")
def generate_code_stream(request: CodeGenerationRequest):
    """Simple streaming endpoint that yields generated code in chunks.

    This is a simulated streaming endpoint: it generates the full code
    synchronously via the orchestrator and then streams it in chunks to
    the client. It's useful for frontends that want incremental updates
    even if the underlying LLM doesn't support true streaming.
    """

    try:
        # Generate synchronously (no DB write) to keep streaming simple
        result = orchestrator.generate_code(request)
        code = result.generated_code or ""

        def streamer():
            chunk_size = 128
            for i in range(0, len(code), chunk_size):
                yield code[i : i + chunk_size]
                time.sleep(0.03)

        return StreamingResponse(streamer(), media_type="text/plain")

    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-multi", summary="Compare two local Ollama models")
async def generate_code_multi(request: CodeGenerationRequest, models: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    try:
        selected=[m.strip() for m in (models or "").split(",") if m.strip()] or None
        if selected and len(selected)!=2:
            raise HTTPException(status_code=400, detail="Select exactly two models.")
        results=await run_in_threadpool(orchestrator.generate_code_multi, request, selected)
        await db.commit()
        return {"success":True,"results":results}
    except HTTPException: raise
    except Exception as e:
        logger.exception(e); raise HTTPException(status_code=500, detail=str(e))


@router.post("/select-model", summary="Select model for inference")
def select_model(request: ModelSelectRequest):
    try:
        model = request.model
        source = request.source.lower()
        # Set model on orchestrator's engine
        orchestrator.llm_engine.model_name = model
        # If selecting local, also update settings
        if source == "local":
            from backend.config import settings

            settings.LOCAL_LLM_MODEL = model

        # Persist selection so it survives restarts
        try:
            (BASE_DIR / ".selected_model").write_text(model, encoding="utf-8")
        except Exception:
            logger.exception("Failed to persist model selection to disk")

        return {"success": True, "selected": model, "source": source}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================================
# Code Generation
# ==========================================================

@router.post(
    "/generate",
    summary="Generate Source Code",
    description="Generate secure production-ready code using the AI Generator Agent.",
)
async def generate_code(
    request: CodeGenerationRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        logger.info("POST /generate")

        result = await AgentService.generate_code(
            db,
            request,
        )

        return {
            "success": True,
            "message": "Code generated successfully.",
            "data": result,
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# Code Review
# ==========================================================

@router.post("/explain", summary="Explain Source Code")
async def explain_code(request: CodeExplanationRequest):
    try:
        result = await run_in_threadpool(orchestrator.explain_code, request)
        return {"success": True, "message": "Code explanation generated.", "data": result.model_dump()}
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=503, detail=str(e))


@router.post(
    "/review",
    summary="Review Source Code",
    description="AI reviews source code for quality, bugs and best practices.",
)
async def review_code(
    request: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        logger.info("POST /review")

        result = await AgentService.review_code(
            db,
            request,
        )

        return {
            "success": True,
            "message": "Review completed successfully.",
            "data": result,
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# Security Analysis
# ==========================================================

@router.post(
    "/vulnerabilities",
    summary="Analyze Vulnerabilities",
    description="Scan code for security vulnerabilities.",
)
async def analyze_vulnerabilities(
    request: VulnerabilityRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        logger.info("POST /vulnerabilities")

        result = await AgentService.analyze_vulnerabilities(
            db,
            request,
        )

        return {
            "success": True,
            "message": "Security scan completed.",
            "data": result,
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# Recommendations
# ==========================================================

@router.post(
    "/recommendations",
    summary="Create Recommendation",
    description="Store AI recommendations for the selected project.",
)
async def create_recommendation(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        logger.info("POST /recommendations")

        result = await AgentService.create_recommendation(
            db,
            request,
        )

        return {
            "success": True,
            "message": "Recommendation created successfully.",
            "data": result,
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# ==========================================================
# Report Generation
# ==========================================================

@router.post(
    "/reports",
    summary="Generate AI Report",
    description="Generate a complete project report using AI.",
)
async def generate_report(
    request: ReportRequest,
    db: AsyncSession = Depends(get_db),
):

    try:

        logger.info("POST /reports")

        result = await AgentService.generate_report(
            db,
            request,
        )

        return {
            "success": True,
            "message": "Report generated successfully.",
            "data": result,
        }

    except Exception as e:

        logger.exception(e)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )