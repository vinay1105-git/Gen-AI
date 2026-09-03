import html
import io
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.config import REPORT_DIR
from backend.models import Report
from backend.schemas.agent_schemas import PDFExportRequest, ReportRequest

logger = logging.getLogger(__name__)


def _clean_text_for_pdf(text: Any) -> str:
    """Safely escape text for ReportLab Paragraphs and preserve linebreaks."""
    if not text:
        return ""
    # Convert to string and escape HTML
    s = html.escape(str(text).strip())
    # Convert markdown headings ### to bold
    s = re.sub(r"#{1,6}\s*(.*?)(?:<br/>|\n|$)", r"<b>\1</b><br/>", s)
    # Convert bold **text** to <b>text</b>
    s = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", s)
    # Convert backticks `code` to <code>code</code>
    s = re.sub(r"`(.*?)`", r"<code>\1</code>", s)
    # Convert newlines to <br/>
    s = s.replace("\r\n", "<br/>").replace("\n", "<br/>")
    return s


class ReportBuilder:
    """Builds professional multi-page PDF code quality and security audit reports."""

    async def build_report(self, db, request: ReportRequest) -> dict:
        filename = f"project_{request.project_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.{request.format}"
        filepath = REPORT_DIR / filename
        if request.format.lower() == "pdf":
            req_export = PDFExportRequest(
                project_id=request.project_id,
                title=f"Security & Code Audit Report (Project #{request.project_id})",
            )
            pdf_bytes = self.generate_audit_pdf(req_export)
            with open(filepath, "wb") as f:
                f.write(pdf_bytes)
        else:
            with open(filepath, "w", encoding="utf-8") as fp:
                fp.write(f"Report for project {request.project_id}\nFormat: {request.format}\n")

        report = Report(project_id=request.project_id, filename=filename, format=request.format)
        db.add(report)
        await db.commit()
        await db.refresh(report)
        return {"filename": filename, "format": request.format}

    def generate_audit_pdf(self, request: PDFExportRequest) -> bytes:
        """Generate a complete, polished PDF audit report and return as bytes."""
        try:
            return self._build_pdf_document(request)
        except Exception as exc:
            logger.warning("Primary PDF generation encountered error: %s. Building safe fallback PDF.", exc)
            return self._build_fallback_pdf(request)

    def _build_pdf_document(self, request: PDFExportRequest) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        primary_color = colors.HexColor("#1e293b")
        accent_color = colors.HexColor("#2563eb")
        dark_gray = colors.HexColor("#475569")
        light_bg = colors.HexColor("#f8fafc")

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=primary_color,
            spaceAfter=4,
        )
        subtitle_style = ParagraphStyle(
            "DocSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=dark_gray,
            spaceAfter=6,
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=11.5,
            leading=15,
            textColor=accent_color,
            spaceBefore=8,
            spaceAfter=4,
        )
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["BodyText"],
            fontSize=8.5,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        code_style = ParagraphStyle(
            "CodeBlock",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=7.5,
            leading=9.5,
            textColor=colors.HexColor("#0f172a"),
            backColor=colors.HexColor("#f1f5f9"),
            borderPadding=4,
            spaceBefore=3,
            spaceAfter=4,
        )

        elements = []

        # Header Block
        elements.append(Paragraph(_clean_text_for_pdf(request.title or "Code AI Security & Quality Audit Report"), title_style))
        elements.append(
            Paragraph(
                f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} • "
                f"Project: #{request.project_id} • Language: {request.language.upper()} • "
                f"Engine: Code AI Local LLM",
                subtitle_style,
            )
        )
        elements.append(HRFlowable(width="100%", thickness=1.5, color=accent_color, spaceBefore=2, spaceAfter=8))

        # Executive Metrics Table
        score = request.review_score
        score_hex = "#16a34a" if score >= 80 else ("#ea580c" if score >= 60 else "#dc2626")
        raw_vulns = request.vulnerabilities or []
        vuln_count = len(raw_vulns)

        crit_count = 0
        for v in raw_vulns:
            sev = (v.severity if hasattr(v, "severity") else v.get("severity", "")).lower()
            if sev in ["high", "critical"]:
                crit_count += 1

        metrics_data = [
            [
                Paragraph("<b>Quality Score</b>", body_style),
                Paragraph("<b>Vulnerabilities</b>", body_style),
                Paragraph("<b>Critical / High</b>", body_style),
                Paragraph("<b>Status</b>", body_style),
            ],
            [
                Paragraph(f"<font color='{score_hex}'><b>{score}/100</b></font>", title_style),
                Paragraph(f"<b>{vuln_count}</b> finding(s)", title_style),
                Paragraph(f"<font color='{'#dc2626' if crit_count > 0 else '#16a34a'}'><b>{crit_count}</b></font>", title_style),
                Paragraph(
                    "<b>SECURE</b>" if vuln_count == 0 and score >= 80 else "<b>ACTION RECOMMENDED</b>",
                    body_style,
                ),
            ],
        ]
        metrics_table = Table(metrics_data, colWidths=[130, 130, 130, 150])
        metrics_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                    ("BACKGROUND", (0, 1), (-1, 1), light_bg),
                    ("TEXTCOLOR", (0, 0), (-1, -1), primary_color),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#94a3b8")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        elements.append(metrics_table)
        elements.append(Spacer(1, 8))

        # Vulnerabilities Section
        elements.append(Paragraph("🛡️ Security Vulnerability Assessment", heading_style))
        if raw_vulns:
            v_rows = [
                [
                    Paragraph("<b>Severity</b>", body_style),
                    Paragraph("<b>CWE ID</b>", body_style),
                    Paragraph("<b>Pattern / Finding</b>", body_style),
                    Paragraph("<b>Description & Remediation</b>", body_style),
                ]
            ]
            for v in raw_vulns:
                sev = (v.severity if hasattr(v, "severity") else v.get("severity", "LOW")).upper()
                cwe = v.cwe_id if hasattr(v, "cwe_id") else v.get("cwe_id", "CWE-0")
                pat = v.pattern if hasattr(v, "pattern") else v.get("pattern", "")
                desc = v.description if hasattr(v, "description") else v.get("description", "")
                rec = v.recommendation if hasattr(v, "recommendation") else v.get("recommendation", "")
                risk = v.risk_score if hasattr(v, "risk_score") else v.get("risk_score", 0.0)

                sev_color = "#dc2626" if sev in ["HIGH", "CRITICAL"] else ("#ea580c" if sev == "MEDIUM" else "#16a34a")
                v_rows.append(
                    [
                        Paragraph(f"<font color='{sev_color}'><b>{sev}</b><br/>Score: {risk}</font>", body_style),
                        Paragraph(f"<b>{_clean_text_for_pdf(cwe)}</b>", body_style),
                        Paragraph(f"<code>{_clean_text_for_pdf(pat)}</code>", body_style),
                        Paragraph(f"<b>{_clean_text_for_pdf(desc)}</b><br/><i>Fix: {_clean_text_for_pdf(rec)}</i>", body_style),
                    ]
                )
            v_table = Table(v_rows, colWidths=[70, 75, 115, 280])
            v_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            elements.append(v_table)
        else:
            elements.append(Paragraph("✅ <b>No known security vulnerabilities detected.</b>", body_style))

        elements.append(Spacer(1, 8))

        # Code Review & Findings
        elements.append(Paragraph("🔍 AI Code Review & Best Practice Suggestions", heading_style))
        if request.review_summary:
            elements.append(Paragraph(_clean_text_for_pdf(request.review_summary), body_style))
            elements.append(Spacer(1, 4))

        if request.suggestions:
            s_text = "<b>Actionable Recommendations:</b><br/>" + "<br/>".join([f"• {_clean_text_for_pdf(s)}" for s in request.suggestions])
            elements.append(Paragraph(s_text, body_style))
            elements.append(Spacer(1, 6))

        # Code Explanation
        if request.explanation:
            elements.append(Paragraph("📖 Code Architecture & Logic Breakdown", heading_style))
            elements.append(Paragraph(_clean_text_for_pdf(request.explanation), body_style))
            elements.append(Spacer(1, 8))

        # Source Code Snippet (Using Preformatted for zero XML parsing issues)
        if request.code:
            elements.append(Paragraph("💻 Analyzed Source Code", heading_style))
            code_snippet = request.code[:2800] if len(request.code) <= 2800 else request.code[:2600] + "\n# [...truncated for PDF...]"
            elements.append(Preformatted(code_snippet, code_style))

        # Auto-Fixed Code (if present)
        if request.fixed_code:
            elements.append(Paragraph("⚡ Auto-Fixed / Hardened Code Output", heading_style))
            fix_snippet = request.fixed_code[:2800] if len(request.fixed_code) <= 2800 else request.fixed_code[:2600] + "\n# [...truncated for PDF...]"
            elements.append(Preformatted(fix_snippet, code_style))

        doc.build(elements)
        return buffer.getvalue()

    def _build_fallback_pdf(self, request: PDFExportRequest) -> bytes:
        """Lightweight guaranteed PDF fallback in case complex layout encounters formatting errors."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(html.escape(request.title or "Security & Code Quality Audit"), styles["Heading1"]),
            Paragraph(f"Project: #{request.project_id} | Language: {html.escape(request.language)}", styles["Normal"]),
            Paragraph(f"Review Score: {request.review_score}/100", styles["Heading2"]),
            Spacer(1, 10),
            Paragraph("<b>Code Snippet:</b>", styles["Heading3"]),
            Preformatted(request.code[:2000] if request.code else "No code provided", styles["Code"]),
        ]
        doc.build(elements)
        return buffer.getvalue()


