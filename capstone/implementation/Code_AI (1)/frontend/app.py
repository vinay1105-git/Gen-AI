import os
import sys
import time
import requests
import pandas as pd
import streamlit as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

API = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/api/v1/agents")
HEALTH = os.getenv("HEALTH_URL", "http://127.0.0.1:8000/api/v1/health")

st.set_page_config(
    page_title="Code AI — Multi-Agent Engineering & Security Studio",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Enterprise CSS Design System
st.markdown(
    """
    <style>
    /* Main Layout & Typography */
    .block-container { max-width: 1400px; padding-top: 1.2rem; padding-bottom: 3rem; }
    
    /* Sleek Cards */
    .feature-card {
        background: linear-gradient(145deg, #ffffff, #f8fafc);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* Status Badges */
    .badge-critical { background-color: #fee2e2; color: #991b1b; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.78rem; border: 1px solid #f87171; }
    .badge-high { background-color: #ffedd5; color: #9a3412; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.78rem; border: 1px solid #fb923c; }
    .badge-medium { background-color: #fef9c3; color: #854d0e; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.78rem; border: 1px solid #facc15; }
    .badge-low { background-color: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 6px; font-weight: 600; font-size: 0.78rem; border: 1px solid #4ade80; }
    
    /* Metrics Header */
    .metric-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
    }
    
    /* Buttons Styling */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def call(url, method="get", timeout=120, **kwargs):
    try:
        t = time.perf_counter()
        r = getattr(requests, method)(url, timeout=timeout, **kwargs)
        dt = round(time.perf_counter() - t, 2)
        if r.ok:
            if "application/pdf" in r.headers.get("Content-Type", ""):
                return r.content, None, dt
            return r.json(), None, dt
        return None, f"HTTP {r.status_code}: {r.text[:600]}", dt
    except requests.RequestException as e:
        return None, f"Backend connection failed: {e}", 0


def health():
    return call(HEALTH, timeout=3)


def status():
    return call(f"{API}/status", timeout=3)


# Initialize Session State
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Dashboard"
if "generated" not in st.session_state:
    st.session_state.generated = ""
if "review" not in st.session_state:
    st.session_state.review = None
if "vulnerability" not in st.session_state:
    st.session_state.vulnerability = None
if "explanation" not in st.session_state:
    st.session_state.explanation = ""
if "fixed_code" not in st.session_state:
    st.session_state.fixed_code = ""
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None


ok, herr, _ = health()
stdata, serr, _ = status() if ok else ({}, "Backend offline", 0)
stdata = (stdata or {}).get("data", {})
models = stdata.get("installed_models", [])
active = stdata.get("model", "auto")

NAV_OPTIONS = [
    "🏠 Dashboard",
    "🚀 1-Click Full Audit",
    "🧑‍💻 Code Generation",
    "🔍 Code Review",
    "🛡️ Vulnerability Scanner",
    "📖 Code Explanation",
    "⚡ Auto-Fix Studio",
    "🏆 Model Comparison",
    "📜 Activity History",
    "⚙️ System Diagnostics",
]

# Sidebar
with st.sidebar:
    st.markdown("## 🛡️ **Code AI Studio**")
    st.caption("Multi-Agent Code Engineering, Review & Security")

    current_idx = NAV_OPTIONS.index(st.session_state.menu) if st.session_state.menu in NAV_OPTIONS else 0
    menu = st.radio(
        "Workspace Navigation",
        NAV_OPTIONS,
        index=current_idx,
        label_visibility="collapsed",
        key="nav_selection",
    )
    st.session_state.menu = menu

    st.divider()


    # System Status Indicators
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Backend", "🟢 Online" if ok else "🔴 Offline")
    with c2:
        st.metric("Ollama", "🟢 Ready" if stdata.get("reachable") else "🔴 Offline")

    if models:
        st.caption("Active Model Selection:")
        selected_m = st.selectbox(
            "Active Model",
            models,
            index=models.index(active) if active in models else 0,
            label_visibility="collapsed",
        )
        if selected_m != active and st.button("Apply Model", use_container_width=True):
            call(f"{API}/select-model", "post", json={"model": selected_m, "source": "local"})
            st.rerun()
    else:
        st.caption(f"Active Model: `{active}`")

if not ok:
    st.error("⚠️ Backend is not reachable. Run `run.bat` from the project directory.")
    if herr:
        st.code(herr)
    st.stop()


LANGUAGES = ["python", "javascript", "typescript", "java", "go", "rust", "cpp", "c", "sql"]


# ==========================================================
# 0. 🏠 Executive Dashboard
# ==========================================================
if menu == "🏠 Dashboard":
    st.markdown(
        """
        <div style="padding: 1.2rem 0 0.5rem 0;">
            <span style="background: #e0f2fe; color: #0369a1; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; margin-right: 6px;">🔒 100% Local & Private</span>
            <span style="background: #f3e8ff; color: #7e22ce; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; margin-right: 6px;">🤖 Multi-Agent AI</span>
            <span style="background: #dcfce7; color: #15803d; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem; margin-right: 6px;">⚡ Ollama Powered</span>
            <span style="background: #fee2e2; color: #b91c1c; padding: 4px 10px; border-radius: 20px; font-weight: 600; font-size: 0.8rem;">🛡️ CWE & CVSS Scanner</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.title("LLM-Based Multi-Agent Code Generation, Review & Vulnerability Explanation System")
    st.markdown("##### *Local LLM deployment with multi-agent orchestration for automated code synthesis, review, security analysis, explanation, and self-healing fixes.*")
    
    st.divider()

    # Executive Status Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">BACKEND ENGINE</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #16a34a; margin-top: 4px;">FastAPI Online</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">Port 8000 • Healthy</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">LOCAL INFERENCE</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #2563eb; margin-top: 4px;">Ollama Ready</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">Port 11434 • Warm</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">ACTIVE MODEL</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #0f172a; margin-top: 4px;">{active}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">{len(models)} model(s) available</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div style="font-size: 0.8rem; color: #64748b; font-weight: 600;">SECURITY ENGINE</div>
                <div style="font-size: 1.4rem; font-weight: 700; color: #d97706; margin-top: 4px;">CWE / CVSS Active</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">Multi-Language Support</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("🤖 Multi-Agent Architecture & Capabilities")

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🧑‍💻</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">Code Generator Agent</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 6px;">
                    Synthesizes runnable, secure source code across 9 languages from natural language prompts.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🔍</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">Code Review Agent</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 6px;">
                    Performs automated code reviews checking syntax, anti-patterns, performance, and scores 0-100.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">🛡️</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">Vulnerability Agent</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 6px;">
                    Detects injection, deserialization, and secret leaks mapped to CWE IDs and CVSS risk scores.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_d:
        st.markdown(
            """
            <div class="feature-card">
                <div style="font-size: 1.6rem; margin-bottom: 6px;">⚡</div>
                <div style="font-weight: 700; font-size: 1.05rem; color: #1e293b;">Auto-Fix & Explainer</div>
                <div style="font-size: 0.82rem; color: #475569; margin-top: 6px;">
                    Generates architectural breakdowns and self-heals code by patching security flaws automatically.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
                # Quick Launchpad & Database Stats
    c_lp, c_st = st.columns([2, 1])
    with c_lp:
        st.subheader("⚡ Quick Launchpad")
        st.info("💡 **Tip:** Use **1-Click Full Audit** to run Generation, Review, Security Scanning, and Explanation in a single automated pass.")
        lp1, lp2, lp3 = st.columns(3)
        with lp1:
            if st.button("🚀 1-Click Full Audit", use_container_width=True, type="primary"):
                st.session_state.menu = "🚀 1-Click Full Audit"
                st.rerun()
        with lp2:
            if st.button("🧑‍💻 Generate Code", use_container_width=True):
                st.session_state.menu = "🧑‍💻 Code Generation"
                st.rerun()
        with lp3:
            if st.button("🛡️ Vulnerability Scan", use_container_width=True):
                st.session_state.menu = "🛡️ Vulnerability Scanner"
                st.rerun()

    with c_st:
        st.subheader("📊 Recent System Activity")
        g_data, _, _ = call(f"{API}/history/generated", timeout=3)
        r_data, _, _ = call(f"{API}/history/reviews", timeout=3)
        g_count = len((g_data or {}).get("items", []))
        r_count = len((r_data or {}).get("items", []))
        st.write(f"• **Code Generations:** `{g_count}` records")
        st.write(f"• **Code Reviews:** `{r_count}` records")
        st.write(f"• **Persistence Engine:** SQLite + SQLAlchemy")


# ==========================================================
# 1. 🚀 1-Click Full Audit (Unified Multi-Agent Pipeline)
# ==========================================================
elif menu == "🚀 1-Click Full Audit":
    st.title("🚀 1-Click Full Multi-Agent Audit Pipeline")
    st.markdown("Execute **Code Generation $\\rightarrow$ Review $\\rightarrow$ Security Scan $\\rightarrow$ Explanation $\\rightarrow$ Auto-Fix** in a single end-to-end workflow.")

    col1, col2 = st.columns([3, 1])
    with col1:
        instructions = st.text_area(
            "What should be generated and audited?",
            height=130,
            placeholder="Example: Build a Python REST API endpoint that validates user email and hashes passwords securely with bcrypt.",
        )
    with col2:
        language = st.selectbox("Language", LANGUAGES, index=0)
        auto_fix_toggle = st.checkbox("Auto-Fix security issues if found", value=True)
        context = st.text_area("Existing context / constraints", height=65, placeholder="Optional context...")

    if st.button("⚡ Run Full Multi-Agent Audit", type="primary", use_container_width=True):
        if not instructions.strip():
            st.warning("Please provide task instructions.")
        else:
            with st.spinner("🤖 Orchestrating multi-agent pipeline (Generation, Review, Security Scan, Explanation, Auto-Fix)..."):
                payload = {
                    "project_id": 1,
                    "instructions": instructions,
                    "language": language,
                    "code_context": context,
                    "auto_fix_if_vulnerable": auto_fix_toggle,
                }
                res, err, dt = call(f"{API}/pipeline", "post", timeout=180, json=payload)
                if err:
                    st.error(f"Pipeline execution failed: {err}")
                else:
                    st.session_state.pipeline_result = (res or {}).get("data")
                    st.session_state.generated = st.session_state.pipeline_result.get("generated_code", "")
                    st.success(f"Audit completed in {dt:.2f}s using `{st.session_state.pipeline_result.get('model_name')}`")


    pdata = st.session_state.pipeline_result
    if pdata:
        st.divider()
        # Top Metrics Row
        m1, m2, m3, m4 = st.columns(4)
        score = pdata.get("review_score", 85)
        score_color = "🟢" if score >= 80 else ("🟠" if score >= 60 else "🔴")
        vulns = pdata.get("vulnerabilities", [])
        m1.metric("Quality Score", f"{score}/100 {score_color}")
        m2.metric("Vulnerabilities Detected", len(vulns))
        m3.metric("Execution Time", f"{pdata.get('execution_time', 0)}s")
        m4.metric("Auto-Fix Applied", "✅ Yes" if pdata.get("fixed_code") else "✨ Code Secure")

        # Multi-tab inspection
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🧑‍💻 Generated Code",
            "🔍 Code Review",
            "🛡️ Security Vulnerabilities",
            "📖 Architecture & Explanation",
            "⚡ Auto-Fixed Output",
        ])

        with tab1:
            st.subheader("Generated Source Code")
            st.code(pdata.get("generated_code", ""), language=language)
            st.download_button(
                "📥 Download Generated Code",
                pdata.get("generated_code", ""),
                file_name=f"generated_code.{language}",
                mime="text/plain",
            )

        with tab2:
            st.subheader("AI Code Review & Quality Assessment")
            st.markdown(pdata.get("review_summary", ""))
            c_f, c_s = st.columns(2)
            with c_f:
                st.markdown("#### ⚠️ Findings")
                for f in pdata.get("findings", []):
                    st.warning(f)
            with c_s:
                st.markdown("#### 💡 Actionable Suggestions")
                for s in pdata.get("suggestions", []):
                    st.info(s)

        with tab3:
            st.subheader("Vulnerability Findings Matrix")
            if vulns:
                df = pd.DataFrame(vulns)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ No common security vulnerabilities detected.")

        with tab4:
            st.subheader("Architecture & Logic Explanation")
            st.markdown(pdata.get("explanation", ""))

        with tab5:
            st.subheader("Auto-Fixed & Hardened Code")
            if pdata.get("fixed_code"):
                st.code(pdata.get("fixed_code", ""), language=language)
                st.download_button(
                    "📥 Download Hardened Code",
                    pdata.get("fixed_code", ""),
                    file_name=f"hardened_code.{language}",
                    mime="text/plain",
                )
            else:
                st.info("The generated code met quality and security thresholds. No auto-fix was required.")

        st.divider()
        # PDF Export Action
        st.subheader("📄 Export Executive Security Audit Report")
        st.caption("Generate an official, executive-ready PDF audit report containing quality scores, CWE vulnerability matrices, and source code.")
        col_pdf1, col_pdf2 = st.columns([1, 1])
        with col_pdf1:
            if st.button("📄 Generate Audit PDF Report", type="secondary", use_container_width=True):
                with st.spinner("Compiling PDF document with ReportLab..."):
                    pdf_payload = {
                        "project_id": 1,
                        "title": f"Code AI Security & Quality Audit ({language.upper()})",
                        "code": pdata.get("generated_code", ""),
                        "language": language,
                        "review_summary": pdata.get("review_summary", ""),
                        "review_score": score,
                        "findings": pdata.get("findings", []),
                        "suggestions": pdata.get("suggestions", []),
                        "vulnerabilities": vulns,
                        "explanation": pdata.get("explanation", ""),
                        "fixed_code": pdata.get("fixed_code"),
                    }
                    pdf_bytes, pdf_err, _ = call(f"{API}/export-pdf", "post", json=pdf_payload)
                    if pdf_err:
                        st.error(f"Failed to generate PDF: {pdf_err}")
                    elif pdf_bytes:
                        st.session_state.pdf_bytes = pdf_bytes
                        st.session_state.pdf_name = f"security_audit_{language}_{int(time.time())}.pdf"
                        st.success("✅ Audit PDF generated successfully! Click download on the right.")

        with col_pdf2:
            if st.session_state.get("pdf_bytes"):
                st.download_button(
                    label=f"⬇️ Download {st.session_state.get('pdf_name', 'audit_report.pdf')}",
                    data=st.session_state.pdf_bytes,
                    file_name=st.session_state.get("pdf_name", "security_audit_report.pdf"),
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )



# ==========================================================
# 2. 🧑‍💻 Code Generation
# ==========================================================
elif menu == "🧑‍💻 Code Generation":
    st.title("🧑‍💻 AI Code Generation Agent")
    st.markdown("Generate clean, structured, and secure code using your local LLM.")

    c1, c2 = st.columns([3, 1])
    with c1:
        instructions = st.text_area(
            "Instructions",
            height=150,
            placeholder="Example: Write a Python function to validate and parse JWT tokens with expiration verification.",
        )
    with c2:
        language = st.selectbox("Language", LANGUAGES, key="gen_lang")
        context = st.text_area("Optional Constraints", height=85)

    if st.button("⚡ Generate Code", type="primary", use_container_width=True):
        if not instructions.strip():
            st.warning("Please enter task instructions.")
        else:
            with st.spinner("Generating code with local LLM..."):
                payload = {
                    "project_id": 1,
                    "instructions": instructions,
                    "code_context": context,
                    "language": language,
                }
                data, err, dt = call(f"{API}/generate", "post", timeout=60, json=payload)
                if err:
                    st.error(err)
                else:
                    st.session_state.generated = data["data"]["generated_code"]
                    st.success(f"Generated in {dt:.2f}s • {data['data']['model_name']}")

    if st.session_state.generated:
        st.subheader("Generated Output")
        st.code(st.session_state.generated, language=language)
        c_d, c_r, c_v, c_e = st.columns(4)
        with c_d:
            st.download_button("📥 Download Code", st.session_state.generated, "generated_code.txt", use_container_width=True)
        with c_r:
            if st.button("🔍 Send to Review", use_container_width=True):
                st.session_state.menu = "🔍 Code Review"
                st.rerun()
        with c_v:
            if st.button("🛡️ Send to Scanner", use_container_width=True):
                st.session_state.menu = "🛡️ Vulnerability Scanner"
                st.rerun()
        with c_e:
            if st.button("📖 Explain Code", use_container_width=True):
                st.session_state.menu = "📖 Code Explanation"
                st.rerun()


# ==========================================================
# 3. 🔍 Code Review
# ==========================================================
elif menu == "🔍 Code Review":
    st.title("🔍 AI Code Review Agent")
    st.markdown("Perform comprehensive static and architectural code reviews checking for bugs, security, and performance.")

    c_code, c_side = st.columns([3, 1])
    with c_code:
        code = st.text_area("Source Code", value=st.session_state.generated, height=360, key="rev_code")
    with c_side:
        language = st.selectbox("Language", LANGUAGES, key="rev_lang")
        depth = st.slider("Review Depth", 1, 5, 3)

    if st.button("⚡ Run AI Code Review", type="primary", use_container_width=True):
        if not code.strip():
            st.warning("Please paste or generate code first.")
        else:
            with st.spinner("Analyzing code quality and vulnerabilities..."):
                payload = {"project_id": 1, "code": code, "language": language, "review_depth": depth}
                data, err, dt = call(f"{API}/review", "post", timeout=60, json=payload)
                if err:
                    st.error(err)
                else:
                    st.session_state.review = data["data"]
                    st.success(f"Review completed in {dt:.2f}s • {data['data']['model_name']}")

    if st.session_state.review:
        r = st.session_state.review
        st.subheader("Review Summary")
        st.markdown(r.get("summary", ""))

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("⚠️ Critical Issues & Findings")
            for f in r.get("findings", []):
                st.warning(f)
        with c2:
            st.subheader("💡 Actionable Suggestions")
            for s in r.get("suggestions", []):
                st.info(s)


# ==========================================================
# 4. 🛡️ Vulnerability Scanner
# ==========================================================
elif menu == "🛡️ Vulnerability Scanner":
    st.title("🛡️ Vulnerability Detection & CWE Engine")
    st.markdown("Scan code for security flaws, CWE identifiers, CVSS risk scores, and remediations.")

    code = st.text_area("Source Code to Scan", value=st.session_state.generated, height=340, key="vuln_code")

    c1, c2 = st.columns([1, 1])
    with c1:
        run_scan = st.button("⚡ Scan for Security Vulnerabilities", type="primary", use_container_width=True)
    with c2:
        auto_fix_btn = st.button("⚡ Auto-Fix Security Flaws", type="secondary", use_container_width=True)

    if run_scan:
        if not code.strip():
            st.warning("Please paste or generate code first.")
        else:
            with st.spinner("Running security vulnerability analysis..."):
                data, err, dt = call(f"{API}/vulnerabilities", "post", timeout=60, json={"project_id": 1, "code": code, "security_level": 3})
                if err:
                    st.error(err)
                else:
                    st.session_state.vulnerability = data["data"]
                    st.success(f"Security scan completed in {dt:.2f}s")

    if auto_fix_btn:
        if not code.strip():
            st.warning("Please paste or generate code first.")
        else:
            with st.spinner("Auto-patching vulnerabilities with Refactor Agent..."):
                fix_payload = {"project_id": 1, "code": code, "language": "python"}
                fdata, ferr, fdt = call(f"{API}/auto-fix", "post", timeout=60, json=fix_payload)
                if ferr:
                    st.error(ferr)
                else:
                    st.session_state.fixed_code = fdata["data"]["fixed_code"]
                    st.success(f"Patched successfully in {fdt:.2f}s")

    if st.session_state.vulnerability:
        v = st.session_state.vulnerability
        st.info(v.get("summary", ""))
        findings = v.get("findings", [])
        if findings:
            df = pd.DataFrame(findings)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No common static vulnerabilities detected.")

    if st.session_state.fixed_code:
        st.subheader("⚡ Auto-Fixed Secure Code")
        st.code(st.session_state.fixed_code, language="python")
        st.download_button("📥 Download Fixed Code", st.session_state.fixed_code, "fixed_code.py")


# ==========================================================
# 5. 📖 Code Explanation
# ==========================================================
elif menu == "📖 Code Explanation":
    st.title("📖 Code Architecture & Logic Explanation")
    st.markdown("Break down purpose, execution flow, key functions, security risks, and edge cases.")

    c_code, c_lang = st.columns([3, 1])
    with c_code:
        code = st.text_area("Code", value=st.session_state.generated, height=340, key="exp_code")
    with c_lang:
        language = st.selectbox("Language", LANGUAGES, key="exp_lang")

    if st.button("⚡ Explain Code", type="primary", use_container_width=True):
        if not code.strip():
            st.warning("Please paste or generate code first.")
        else:
            with st.spinner("Generating architectural explanation..."):
                data, err, dt = call(f"{API}/explain", "post", timeout=15, json={"project_id": 1, "code": code, "language": language, "detail_level": 3})
                if err:
                    st.error(err)
                else:
                    result = (data or {}).get("data") or {}
                    st.session_state.explanation = result.get("explanation", "")
                    st.success(f"Explanation ready in {dt:.2f}s • {result.get('model_name')}")

    if st.session_state.explanation:
        st.subheader("Explanation")
        st.markdown(st.session_state.explanation)


# ==========================================================
# 6. ⚡ Auto-Fix Studio
# ==========================================================
elif menu == "⚡ Auto-Fix Studio":
    st.title("⚡ Auto-Fix & Refactoring Studio")
    st.markdown("Provide flawed or vulnerable code and let the **Refactor Agent** produce an optimized, hardened version with side-by-side diff.")

    c1, c2 = st.columns([3, 1])
    with c1:
        code = st.text_area("Code to Refactor / Patch", value=st.session_state.generated, height=280, key="af_code")
    with c2:
        language = st.selectbox("Language", LANGUAGES, key="af_lang")
        feedback = st.text_area("Specific Fix Instructions (Optional)", height=150, placeholder="e.g., Replace MD5 with SHA-256 and remove eval().")

    if st.button("⚡ Auto-Fix & Harden Code", type="primary", use_container_width=True):
        if not code.strip():
            st.warning("Please enter code to fix.")
        else:
            with st.spinner("Refactoring and securing code..."):
                payload = {"project_id": 1, "code": code, "language": language, "review_feedback": feedback}
                data, err, dt = call(f"{API}/auto-fix", "post", timeout=60, json=payload)
                if err:
                    st.error(err)
                else:
                    res = (data or {}).get("data") or {}
                    st.session_state.fixed_code = res.get("fixed_code", "")
                    st.success(f"Refactored in {dt:.2f}s • {res.get('model_name')}")
                    if res.get("changes_made"):
                        st.subheader("Changes Applied:")
                        for ch in res.get("changes_made", []):
                            st.write(f"• {ch}")

    if st.session_state.fixed_code:
        st.subheader("Comparison: Original vs. Fixed")
        col_orig, col_fixed = st.columns(2)
        with col_orig:
            st.caption("Original Code:")
            st.code(code, language=language)
        with col_fixed:
            st.caption("Hardened / Fixed Code:")
            st.code(st.session_state.fixed_code, language=language)
            st.download_button("📥 Download Hardened Code", st.session_state.fixed_code, f"fixed_code.{language}")


# ==========================================================
# 7. 🏆 Model Comparison
# ==========================================================
elif menu == "🏆 Model Comparison":
    st.title("🏆 Two-Model Local Benchmarking")
    st.markdown("Run the same coding task concurrently on two local Ollama models and rank them by speed and quality.")

    if len(models) < 2:
        st.warning(f"Install at least two models to run comparison. Currently detected: {models}")
        st.info("Example: Run `ollama pull llama3.2` and `ollama pull qwen2.5-coder:1.5b` in your terminal.")
    else:
        m1 = st.selectbox("Model 1", models, index=0)
        remaining = [m for m in models if m != m1]
        m2 = st.selectbox("Model 2", remaining, index=0 if remaining else None)
        language = st.selectbox("Language", LANGUAGES, key="cmp_lang")
        task = st.text_area("Coding Task", height=120, placeholder="Example: Write a thread-safe singleton in Python with unit tests.")

        if st.button("🏁 Run Benchmark", type="primary", use_container_width=True):
            if not task.strip():
                st.warning("Please enter a coding task.")
            else:
                with st.spinner("Benchmarking both models concurrently..."):
                    param_models = requests.utils.quote(f"{m1},{m2}")
                    data, err, dt = call(
                        f"{API}/generate-multi?models={param_models}",
                        "post",
                        timeout=90,
                        json={"project_id": 1, "instructions": task, "language": language},
                    )
                    if err:
                        st.error(err)
                    else:
                        st.session_state["comparison"] = data.get("results", [])
                        st.success(f"Benchmark completed in {dt:.2f}s total")

        rows = st.session_state.get("comparison", [])
        if rows:
            table = [
                {
                    "Rank": r.get("rank"),
                    "Model": r.get("model"),
                    "Time (s)": r.get("response_time"),
                    "Quality Score": r.get("quality_score"),
                    "Overall Score": r.get("overall_score"),
                }
                for r in rows
            ]
            st.dataframe(pd.DataFrame(table), use_container_width=True, hide_index=True)
            winner = rows[0]
            st.success(f"🥇 Winner: **{winner['model']}** (Overall Score: {winner.get('overall_score')}, Time: {winner.get('response_time')}s)")
            for r in rows:
                with st.expander(f"#{r.get('rank')} {r.get('model')} — {r.get('response_time')}s"):
                    if r.get("error"):
                        st.error(r["error"])
                    else:
                        st.code(r.get("generated_code", ""), language=language)


# ==========================================================
# 8. 📜 Activity History
# ==========================================================
elif menu == "📜 Activity History":
    st.title("📜 Activity History & Search")
    st.markdown("Search and inspect past code generations and AI reviews.")

    search_query = st.text_input("🔍 Search History by Keyword", placeholder="Search prompts or summaries...")

    if search_query.strip():
        sdata, serr, _ = call(f"{API}/history/search?q={requests.utils.quote(search_query)}")
        items_dict = (sdata or {}).get("items", {})
        gen_items = items_dict.get("generated", [])
        rev_items = items_dict.get("reviews", [])
    else:
        gdata, _, _ = call(f"{API}/history/generated", timeout=5)
        rdata, _, _ = call(f"{API}/history/reviews", timeout=5)
        gen_items = (gdata or {}).get("items", [])
        rev_items = (rdata or {}).get("items", [])

    h_tab1, h_tab2 = st.tabs([f"🧑‍💻 Generated Code ({len(gen_items)})", f"🔍 Code Reviews ({len(rev_items)})"])

    with h_tab1:
        if gen_items:
            for item in reversed(gen_items[-15:]):
                with st.expander(f"📌 [{item.get('created_at', '')[:19]}] {item.get('prompt', '')[:80]}... ({item.get('model_name')})"):
                    code_content = item.get("code", "")
                    if code_content:
                        st.code(code_content)
                        st.download_button("📥 Download", code_content, file_name=f"history_code_{item.get('id')}.txt", key=f"dl_g_{item.get('id')}")
                    else:
                        st.write("Prompt:", item.get("prompt"))
        else:
            st.info("No generated code records found.")

    with h_tab2:
        if rev_items:
            for item in reversed(rev_items[-15:]):
                with st.expander(f"🔍 [{item.get('created_at', '')[:19]}] {item.get('summary', '')[:80]}... ({item.get('model_name')})"):
                    st.markdown(item.get("summary", ""))
                    if item.get("findings"):
                        st.markdown("**Findings:**")
                        st.warning(item.get("findings"))
                    if item.get("suggestions"):
                        st.markdown("**Suggestions:**")
                        st.info(item.get("suggestions"))
        else:
            st.info("No review records found.")


# ==========================================================
# 9. ⚙️ System Diagnostics
# ==========================================================
elif menu == "⚙️ System Diagnostics":
    st.title("⚙️ System Health & Diagnostics")
    st.markdown("Check local LLM connection status, installed models, and endpoint latency.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Backend Service", "Online" if ok else "Offline")
    c2.metric("Ollama Engine", "Connected" if stdata.get("reachable") else "Offline")
    c3.metric("Installed Models", len(models))

    st.subheader("Model Configuration")
    st.json(stdata)

    st.subheader("Model Setup Assistant")
    st.info("Run these commands in your Windows terminal to pull recommended local models:")
    st.code("ollama pull llama3.2\nollama pull qwen2.5-coder:1.5b\nollama pull codellama", language="bash")
