import asyncio
import logging
from sqlalchemy.exc import SQLAlchemyError

from backend.agents.orchestrator import AgentOrchestrator
from backend.models import (
    GeneratedCode,
    Recommendation,
    Report,
    ReviewHistory,
    Vulnerability,
)
from backend.schemas.agent_schemas import (
    CodeGenerationRequest,
    CodeReviewRequest,
    RecommendationRequest,
    ReportRequest,
    VulnerabilityRequest,
    CodeExplanationRequest,
)

logger = logging.getLogger(__name__)

orchestrator = AgentOrchestrator()


class AgentService:
    """
    Service Layer

    Responsibilities
    ----------------
    • Calls AI Orchestrator
    • Saves AI results
    • Handles database transactions
    • Handles rollback on failures
    """

    # ==========================================================
    # Code Generation
    # ==========================================================

    @staticmethod
    async def generate_code(db, request: CodeGenerationRequest):

        try:

            logger.info("Generating Code")

            response = await asyncio.to_thread(orchestrator.generate_code, request)

            generated = GeneratedCode(
                project_id=request.project_id,
                code=response.generated_code,
                prompt=response.prompt,
                model_name=response.model_name,
            )

            db.add(generated)

            await db.commit()
            await db.refresh(generated)

            logger.info("Generated code saved successfully")

            return response

        except SQLAlchemyError as e:

            await db.rollback()

            logger.exception(e)

            raise

    # ==========================================================
    # Code Review
    # ==========================================================

    @staticmethod
    async def review_code(db, request: CodeReviewRequest):

        try:

            logger.info("Reviewing Code")

            response = await asyncio.to_thread(orchestrator.review_code, request)

            review = ReviewHistory(
                project_id=request.project_id,
                summary=response.summary,
                findings="\n".join(response.findings),
                suggestions="\n".join(response.suggestions),
                model_name=response.model_name,
            )

            db.add(review)

            await db.commit()
            await db.refresh(review)

            logger.info("Review saved")

            return response

        except SQLAlchemyError as e:

            await db.rollback()

            logger.exception(e)

            raise

    # ==========================================================
    # Vulnerability Analysis
    # ==========================================================

    @staticmethod
    async def analyze_vulnerabilities(db, request: VulnerabilityRequest):

        try:

            logger.info("Running Security Scan")

            response = await asyncio.to_thread(orchestrator.analyze_vulnerabilities, request)

            for finding in response.findings:

                vulnerability = Vulnerability(
                    project_id=request.project_id,
                    severity=finding.severity,
                    pattern=finding.pattern,
                    description=finding.description,
                    recommendation=finding.recommendation,
                    cwe_id=finding.cwe_id,
                    risk_score=finding.risk_score,
                )

                db.add(vulnerability)

            await db.commit()

            logger.info("Security findings saved")

            return response

        except SQLAlchemyError as e:

            await db.rollback()

            logger.exception(e)

            raise

    # ==========================================================
    # Code Explanation
    # ==========================================================

    @staticmethod
    async def explain_code(db, request: CodeExplanationRequest):
        return await asyncio.to_thread(orchestrator.explain_code, request)

    # ==========================================================
    # Recommendation
    # ==========================================================

    @staticmethod
    async def create_recommendation(
        db,
        request: RecommendationRequest,
    ):

        try:

            logger.info("Saving Recommendation")

            recommendation = Recommendation(
                project_id=request.project_id,
                title=request.title,
                details=request.details,
                category=request.category,
                priority=request.priority,
            )

            db.add(recommendation)

            await db.commit()
            await db.refresh(recommendation)

            logger.info("Recommendation saved")

            return recommendation

        except SQLAlchemyError as e:

            await db.rollback()

            logger.exception(e)

            raise

    # ==========================================================
    # Auto-Fix Code
    # ==========================================================

    @staticmethod
    async def auto_fix_code(db, request):
        try:
            logger.info("Auto-Fixing Code Flaws")
            response = await asyncio.to_thread(orchestrator.auto_fix_code, request)
            if response.fixed_code:
                generated = GeneratedCode(
                    project_id=request.project_id,
                    code=response.fixed_code,
                    prompt=f"[AUTO-FIXED] {getattr(request, 'language', 'code')}",
                    model_name=response.model_name,
                )
                db.add(generated)
                await db.commit()
            return response
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(e)
            raise

    # ==========================================================
    # Full Unified Pipeline
    # ==========================================================

    @staticmethod
    async def run_full_pipeline(db, request):
        try:
            logger.info("Running 1-Click Multi-Agent Pipeline")
            response = await asyncio.to_thread(orchestrator.run_full_pipeline, request)
            if response.generated_code:
                generated = GeneratedCode(
                    project_id=request.project_id,
                    code=response.generated_code,
                    prompt=request.instructions,
                    model_name=response.model_name,
                )
                db.add(generated)

                review = ReviewHistory(
                    project_id=request.project_id,
                    summary=response.review_summary,
                    findings="\n".join(response.findings),
                    suggestions="\n".join(response.suggestions),
                    model_name=response.model_name,
                )
                db.add(review)

                for finding in response.vulnerabilities:
                    if finding.cwe_id != "CWE-0":
                        vuln = Vulnerability(
                            project_id=request.project_id,
                            severity=finding.severity,
                            pattern=finding.pattern,
                            description=finding.description,
                            recommendation=finding.recommendation,
                            cwe_id=finding.cwe_id,
                            risk_score=finding.risk_score,
                        )
                        db.add(vuln)

                await db.commit()
            return response
        except SQLAlchemyError as e:
            await db.rollback()
            logger.exception(e)
            raise

    # ==========================================================
    # PDF Audit Report Export
    # ==========================================================

    @staticmethod
    def export_pdf_report(request):
        return orchestrator.report_builder.generate_audit_pdf(request)