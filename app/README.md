#  Website UI Builder Agent

An AI-powered autonomous agent that designs and builds responsive websites from natural language prompts — using a **LangGraph workflow**, **multi-agent collaboration**, and **real-time code generation**.

> ✨ *Describe a UI → Agent plans, writes, and deploys live HTML/CSS/JS — all in your browser.*

![Demo Screenshot](https://via.placeholder.com/1200x600/0a0f1c/4da6ff?text=AI+Website+Builder+Agent+Demo)  
*(Replace with actual screenshot when publishing)*

---

## 🌟 Features

- **Natural Language to UI**: “Create a dark-themed landing page with a hero section and CTA button” → full website.
- **Autonomous Workflow**: Router → Planner → Code Agent → Validation loop.
- **Live Sandbox Preview**: Real-time iframe rendering of generated code.
- **Stateful Session**: Chat history, iterative refinement, and code updates.
- **Local & Private**: Runs entirely on your machine — no external APIs required.
- **Optimized for High VRAM GPUs**: Designed for A6000 (48GB VRAM) with vLLM backend.

---

## 🏗️ Architecture

```mermaid
graph LR
A[User Prompt] --> B(Router Agent)
B -->|Plan| C(Planner Agent)
C --> D(Code Agent)
D -->|Save Code| E[website_sandbox/]
E --> F[Sandbox Preview]
D --> B{Check Completion}
B -->|End| G[Final Output]

