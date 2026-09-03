import logging
from typing import Any
from backend.agents.llm_engine import LocalLLMEngine
logger=logging.getLogger(__name__)

class AgentBase:
    def __init__(self,engine=None): self.engine=engine or LocalLLMEngine()
    def run(self,payload:Any)->Any: raise NotImplementedError

class CodeGenerationAgent(AgentBase):
    def run(self,request):
        p=f"Generate concise, secure {request.language} code for this task. Return ONLY runnable code, no markdown. Task: {request.instructions}"
        if request.code_context: p+=f"\nExisting context: {request.code_context}"
        return self.engine.generate_text(p,0.1,450)

class CodeReviewAgent(AgentBase):
    def run(self,request):
        p=f"Review this {request.language} code. Be concise. List critical bugs, security issues, performance issues, and 3 fixes. End with SCORE: 0-100.\nCODE:\n{request.code}"
        return self.engine.generate_text(p,0.1,450)

class VulnerabilityAgent(AgentBase):
    def run(self,request):
        p=f"Identify security vulnerabilities in this {request.language} code. For each give severity, CWE, reason, and fix. If none, say none. Be concise.\n{request.code}"
        return self.engine.generate_text(p,0.05,350)

class ExplanationAgent(AgentBase):
    def run(self,request):
        p=f"Explain this {request.language} code briefly: purpose, flow, important functions, security risks, edge cases.\n{request.code}"
        return self.engine.generate_text(p,0.1,350)

class OptimizationAgent(AgentBase):
    def run(self,request): return self.engine.generate_text(f"Give 5 concise performance improvements for this code:\n{request.code}",0.1,300)
class UnitTestAgent(AgentBase):
    def run(self,request): return self.engine.generate_text(f"Generate concise unit tests for this code. Return only tests:\n{request.code}",0.1,350)
class RefactorAgent(AgentBase):
    def run(self, request):
        vuln_ctx = ""
        if hasattr(request, "vulnerabilities") and request.vulnerabilities:
            vuln_ctx = f"\nAddress these vulnerabilities:\n- " + "\n- ".join(request.vulnerabilities)
        if hasattr(request, "review_feedback") and request.review_feedback:
            vuln_ctx += f"\nReview feedback: {request.review_feedback}"
        prompt = (
            f"Refactor and secure this {getattr(request, 'language', 'python')} code. "
            f"Fix all security flaws, bugs, and performance issues.{vuln_ctx}\n"
            f"Return ONLY the updated runnable code, without markdown, without explanations.\n\n"
            f"CODE:\n{request.code}"
        )
        return self.engine.generate_text(prompt, 0.1, 550)
class ArchitectureAgent(AgentBase):
    def run(self,request): return self.engine.generate_text(f"Give concise architecture recommendations for:\n{request.instructions}",0.1,350)
class PerformanceAgent(AgentBase):
    def run(self,request): return self.engine.generate_text(f"Find performance bottlenecks and fixes in:\n{request.code}",0.1,450)

