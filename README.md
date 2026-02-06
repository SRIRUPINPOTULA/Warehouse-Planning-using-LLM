# 🧠 Improving LLM Reasoning and Planning Using CSP and Chain-of-Thought

## Overview
This project explores whether **Large Language Models (LLMs)** can be guided to solve complex **reasoning and planning problems** by combining **Chain-of-Thought (CoT) prompting** with **symbolic verification using Answer Set Programming (ASP)**.

The system follows an **iterative generate–verify–refine loop**, where:
1. An LLM generates a CSP formulation for a planning problem.
2. The formulation is checked using a symbolic verifier (ASP / Clingo-style).
3. Feedback is used to improve subsequent reasoning iterations.

The primary evaluation domain is a **simplified automated warehouse planning scenario**.

---

## Key Ideas
- Explicit **Chain-of-Thought reasoning** through prompt design  
- **Constraint Satisfaction Problems (CSP)** for formal reasoning  
- **Symbolic verification** to ensure correctness  
- **Iterative refinement** to improve solution quality  

---

## File Structure

```text
.
├── llm_warehouse_solver_iter1.py
├── llm_warehouse_solver_iter2.py
└── README.md
```

---

## Iteration Details

### 🔹 Iteration 1 — Baseline Reasoning + CSP Generation
**File:** `llm_warehouse_solver_iter1.py`

This iteration establishes the core pipeline:
- Uses reasoning calibration prompts with well-known CSP problems (e.g., N-Queens).
- Teaches the LLM correct **ASP / CSP syntax and semantics**.
- Generates an initial CSP formulation for the warehouse planning task.
- Verification feedback is **binary** (valid / invalid).

**Goal:**  
Evaluate whether an LLM can generate *syntactically valid* CSP formulations after calibration.

---

### 🔹 Iteration 2 — Refined Reasoning + Iterative Feedback
**File:** `llm_warehouse_solver_iter2.py`

This iteration improves upon Iteration 1 by:
- Refining Chain-of-Thought prompting.
- Adding more explicit and structured constraints.
- Improving reasoning robustness and consistency.
- Preparing the system for **iterative correction using verifier feedback**.

**Goal:**  
Improve convergence toward **correct and verifiable solutions** using iterative refinement.

---

## Methodology

1. **Reasoning Calibration**  
   The LLM is exposed to small CSP problems with correct solutions and explanations to learn structured reasoning patterns.

2. **Problem Prompting**  
   A warehouse planning query is passed to the LLM, requesting a CSP-style formulation.

3. **Symbolic Verification**  
   The generated CSP program is checked using an ASP-based verifier.

4. **Iterative Refinement**  
   Failed solutions are revised using feedback and regenerated in the next iteration.

---

## Technologies Used
- **Python**
- **Google Gemini API**
- **Answer Set Programming (ASP)**
- **Constraint Satisfaction Problems (CSP)**
- **Chain-of-Thought Prompting**

---

## How to Run

### Export the API Key and then 
```bash
export GEMINI_API_KEY="your_api_key_here"
python3 filename.py
```
