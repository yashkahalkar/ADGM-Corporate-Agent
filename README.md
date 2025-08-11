# 🏛️ ADGM Corporate Agent

### AI-Powered Legal Document Analysis & Compliance Assistant for Abu Dhabi Global Market

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamlit-red.svg)](https://streamlit.io/)

---

## 🎯 Overview

**ADGM Corporate Agent** is a production-ready AI assistant that analyzes legal documents for Abu Dhabi Global Market (ADGM) compliance. It uses RAG (Retrieval Augmented Generation) with official ADGM templates to provide professional-grade legal document analysis.

### ✨ Key Features

- 🔍 **Smart Document Analysis** - Multi-document processing with auto-detection
- 🤖 **RAG-Powered AI** - Uses official ADGM knowledge base + Gemini 2.5 Pro
- 📝 **Professional Output** - Comments injected directly into Word documents  
- ⚖️ **ADGM-Specific** - Jurisdiction validation, template compliance, regulatory citations
- 📊 **Real-time Dashboard** - Compliance scoring and issue prioritization

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- [Google AI Studio API key](https://makersuite.google.com/app/apikey)
- [Pinecone account](https://www.pinecone.io/)

### 1-Minute Setup
git clone https://github.com/your-username/adgm-corporate-agent.git
cd adgm-corporate-agent
pip install -r requirements.txt
cp .env.example .env

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI** | Gemini 2.5 Pro | Legal analysis & reasoning |
| **Vector DB** | Pinecone | ADGM knowledge storage |
| **Embeddings** | Sentence Transformers | Text to vector conversion |
| **Interface** | Streamlit | Web application |
| **Documents** | python-docx | Word processing |

---

## 🎯 What It Detects

- ❌ **Jurisdiction Issues**: UAE Federal Courts → ADGM Courts
- ❌ **Missing Clauses**: Required ADGM-specific provisions
- ❌ **Template Violations**: Non-compliance with official forms
- ❌ **Incomplete Sections**: Unfilled placeholders
- ❌ **Wrong References**: UAE Commercial Code → ADGM Regulations

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| Processing Speed | ~2 mins for 5 documents |
| Accuracy | 95%+ vs ADGM templates |
| Knowledge Base | 2,000+ document chunks |
| Supported Types | 8+ official templates |

---

created by Yash Kahalkar with 💻
