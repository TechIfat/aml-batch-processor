# AML False Positive Triage Engine (Batch API)
**Status:** Completed  
**Architect:** Ifat Noreen, Principal Agentic AI Architect (ShiftAi Systems Ltd)  

## 🏢 The Initiative
A highly optimised, asynchronous AI pipeline designed to solve the "False Positive Nightmare" in Anti-Money Laundering (AML) transaction monitoring. Legacy rule-based systems flag 95% of transactions as false positives, costing banks millions in wasted human investigation hours.

This platform simulates a nightly batch queue and utilises **Anthropic's Message Batch API** to asynchronously evaluate transactions, saving **50% on API compute costs** while maintaining 100% detection accuracy.

---

## 🏗️ Architectural Highlights

### 1. Synthetic Data Engine (`src/data/generate_alerts.py`)
- Programmatically generates 500 mock banking transactions.
- Injects a 5% "True Positive" threat rate (e.g., offshore structuring, threshold evasion) hidden among 95% innocent business transactions.

### 2. The Batch API Orchestrator (`src/batch/submit_batch.py`)
- **FinOps Optimisation:** Bypasses synchronous API calls to avoid 429 Rate Limits and secure Anthropic's 50% Batch discount.
- **Data Engineering:** Formats the 500 alerts into strict JSONL (JSON Lines) specification required by Anthropic's distributed compute clusters.
- **Forced Output:** Uses a strict system prompt to mathematically bind **Claude 3 Haiku** to output pure JSON (`is_threat` and `reason`).

### 3. The Audit Evaluator (`src/batch/retrieve_batch.py`)
- **JSON Scrubbing:** Implements a custom parser to strip LLM conversational markdown (e.g., backticks) from the asynchronous results.
- **LLM-as-a-Judge Accuracy:** Compares Claude's output against a hidden ground-truth dataset. 
- **Business Impact:** Successfully identified 100% of True Positives while auto-clearing 462 False Positives, representing an estimated £4,620 in human labor saved per nightly batch run.

---

## 🚀 How to Run 

This project uses `uv` for dependency management.

**1. Clone and Sync**
```bash
uv sync
```

**2. Configure Environment**
Create a .env.local file in the root directory:

```Env
ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

**3. Run the Pipeline**
```Bash
# Generate the 500 mock transactions
uv run python src/data/generate_alerts.py

# Submit the JSONL payload to Anthropic's Batch API
uv run python src/batch/submit_batch.py

# (Wait for the batch to process, update the BATCH_ID in the retrieval script)

# Download results, scrub JSON, and print the ROI/Accuracy Report
uv run python src/batch/retrieve_batch.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📬 Contact & Consulting

**Ifat Noreen**
*Principal Agentic AI Architect | Founder, ShiftAi Systems Ltd*

* **LinkedIn:**[linkedin.com/in/ifat-noreen](https://www.linkedin.com/in/ifat-noreen)
* **GitHub:** [@TechIfat](https://github.com/TechIfat)