# 🩺 MedCheck — Stressed Medical Student Simulation & Counselor Training LLM

An interactive, locally deployed LLM roleplay simulator engineered for medical counselors, trainers, and mentors. MedCheck simulates **Alex Miller**, a 3rd-year medical student undergoing intense clinical rotation burnout and personal stress who is psychologically guarded and deflecting.

Built using **Open-source Local LLM (GGUF / Ollama)**, custom **Modelfile prompt engineering**, **Few-Shot Conditioning**, **Server-Sent Events (SSE) streaming**, and an automated **LLM Output Evaluation Suite**.

---

## 🌟 Key Architecture & Capabilities

1. **Local Open-Source LLM Orchestration:**
   - Runs locally via **Ollama** utilizing a quantized base model (`chat.gguf`).
   - Configured through a custom `Modelfile` with strict parameter tuning (`temperature`, `num_predict`, custom stop sequences).

2. **4-Stage Trust-Building Behavioral Dynamics:**
   - **Stage 1 (Guarded - Default):** Deflects personal queries, gives short 1-sentence answers (*"it's fine, just busy"*), minimizes stress.
   - **Stage 2 (Testing):** Tests counselor intentions (*"why do you care?"*), shares surface complaints.
   - **Stage 3 (Cracking):** Lets small truths slip (*"I don't know if I can keep doing this"*).
   - **Stage 4 (Open):** Shares genuine burnout and personal struggles only after sustained empathetic rapport.

3. **Hallucination & Artifact Mitigation Engine:**
   - **Few-Shot Context Prepending:** Dynamically conditions initial turns with target student responses to prevent role confusion.
   - **Anti-Repetition Limiter:** Deactivates few-shot injection after conversation establishment to eliminate context loops and random digit sequence hallucinations (`0, 1, 2, 3...`).
   - **Safety & Foreign Token Filter:** Real-time stream filters that block foreign script leaks, roleplay metadata (`"End of session..."`), and out-of-character tokens.

4. **Full-Duplex Streaming Web UI:**
   - Ultra-fast token-by-token streaming via Python standard library HTTP proxy and Server-Sent Events (SSE).
   - Modern, mobile-responsive interface with dark/light theme switching.

5. **Automated LLM Output Evaluation:**
   - Includes programmatic scenario testing (`evaluation/programmatic_test.py` and `evaluation/verify_chat.py`) to systematically verify persona adherence, deflection behavior, and empathy response thresholds.

---

## 📁 Repository Structure

```text
├── Modelfile                     # Ollama model definition with behavioral parameters
├── server.py                     # Zero-dependency Python proxy & streaming SSE relay
├── public/                       # Frontend web client
│   ├── index.html                # Responsive chat application markup
│   ├── style.css                 # Dark/Light theme styles with CSS variables
│   └── app.js                    # Client-side streaming reader & state manager
├── evaluation/                   # LLM Evaluation & Verification suite
│   ├── programmatic_test.py      # Automated scenario tests across multiple approaches
│   └── verify_chat.py            # Interactive CLI evaluation tool
├── .gitignore                    # Excludes heavy model weights (*.gguf) and temporary files
└── README.md                     # Documentation
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.9+**
- **Ollama** installed ([ollama.com](https://ollama.com))

### 2. Set Up the Model
1. Place your base GGUF model in the project root as `chat.gguf`.
2. Build the customized Ollama model:
   ```bash
   ollama create chat -f Modelfile
   ```

### 3. Run the Server
Launch the lightweight web application and proxy server:
```bash
python server.py
```

Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🧪 Running LLM Evaluations

Run the automated persona evaluation suite:
```bash
python evaluation/programmatic_test.py
```

Run the interactive terminal verification harness:
```bash
python evaluation/verify_chat.py
```
