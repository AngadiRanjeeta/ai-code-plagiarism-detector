# AI Code Plagiarism Detection System

## Overview
Hybrid AI-based system that detects code similarity using:
- Transformer-based semantic embeddings (Sentence-BERT)
- AST-based structural normalization
- Hybrid weighted scoring model

## Architecture
1. Semantic Similarity → Sentence-BERT embeddings
2. Structural Similarity → AST normalization + Jaccard similarity
3. Final Score → 70% Semantic + 30% Structural

## Features
- Semantic similarity detection
- Structural similarity analysis
- Confidence classification
- Code diff highlighting
- Modern UI

## Tech Stack
- Python
- Flask
- Sentence-Transformers
- Scikit-Learn
- AST Parsing

## How to Run Locally
- pip install -r requirements.txt
- python main.py


Then open:
http://127.0.0.1:5000/

## Future Improvements
- Tree Edit Distance structural comparison
- Multi-language support
- REST API mode

- Cloud deployment
