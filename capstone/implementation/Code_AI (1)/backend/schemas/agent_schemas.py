from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class CodeGenerationRequest(BaseModel):
    project_id: int
    instructions: str = Field(..., description="Task description for code generation")
    code_context: Optional[str] = Field(None, description="Prior code context")
    language: str = Field(default="python", description="Target language")
    temperature: float = Field(default=0.15, ge=0.0, le=1.0, exclude=True)
    max_tokens: int = Field(default=600, ge=64, le=2048, exclude=True)


class CodeGenerationResponse(BaseModel):
    generated_code: str
    model_name: str
    prompt: str


class CodeReviewRequest(BaseModel):
    project_id: int
    code: str
    language: str = Field(default="python", description="Language of the code to review")
    review_depth: int = Field(default=2, ge=1, le=5)
    temperature: float = Field(default=0.15, ge=0.0, le=1.0, exclude=True)
    max_tokens: int = Field(default=600, ge=64, le=2048, exclude=True)


class CodeReviewResponse(BaseModel):
    summary: str
    findings: List[str]
    suggestions: List[str]
    model_name: str


class VulnerabilityRequest(BaseModel):
    project_id: int
    code: str
    security_level: int = Field(default=1, ge=1, le=3)


class VulnerabilityFinding(BaseModel):
    severity: str
    pattern: str
    description: str
    recommendation: str
    cwe_id: str
    risk_score: float


class VulnerabilityResponse(BaseModel):
    summary: str
    findings: List[VulnerabilityFinding]


class RecommendationRequest(BaseModel):
    project_id: int
    title: str
    details: str
    category: str = "resilience"
    priority: int = 1


class RecommendationResponse(BaseModel):
    id: int
    title: str
    details: str
    category: str
    priority: int

    model_config = ConfigDict(from_attributes=True)


class ReportRequest(BaseModel):
    project_id: int
    format: str = Field(
        default="pdf",
        description="Report format: pdf, csv, json"
    )


class ReportResponse(BaseModel):
    filename: str
    format: str


class SearchFilterRequest(BaseModel):
    query: Optional[str] = None
    project_id: Optional[int] = None
    severity: Optional[str] = None
    role: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

class CodeExplanationRequest(BaseModel):
    project_id: int
    code: str
    language: str = "python"
    detail_level: int = Field(default=3, ge=1, le=5)


class CodeExplanationResponse(BaseModel):
    explanation: str
    model_name: str


class AutoFixRequest(BaseModel):
    project_id: int = 1
    code: str
    language: str = "python"
    vulnerabilities: Optional[List[str]] = None
    review_feedback: Optional[str] = None


class AutoFixResponse(BaseModel):
    original_code: str
    fixed_code: str
    changes_made: List[str]
    model_name: str


class PipelineRequest(BaseModel):
    project_id: int = 1
    instructions: str
    language: str = "python"
    code_context: Optional[str] = None
    auto_fix_if_vulnerable: bool = True


class PipelineResponse(BaseModel):
    generated_code: str
    review_summary: str
    review_score: int
    findings: List[str]
    suggestions: List[str]
    vulnerabilities: List[VulnerabilityFinding]
    explanation: str
    fixed_code: Optional[str] = None
    model_name: str
    execution_time: float


class PDFExportRequest(BaseModel):
    project_id: int = 1
    title: str = "Code AI Security & Quality Audit Report"
    code: str = ""
    language: str = "python"
    review_summary: str = ""
    review_score: int = 85
    findings: List[str] = []
    suggestions: List[str] = []
    vulnerabilities: List[VulnerabilityFinding] = []
    explanation: str = ""
    fixed_code: Optional[str] = None

