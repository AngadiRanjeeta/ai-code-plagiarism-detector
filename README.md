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

## Interface

  ![WhatsApp Image 2026-02-28 at 00 50 07](https://github.com/user-attachments/assets/010f0159-c658-4f65-91e6-10e7ce9b9168)
  ![WhatsApp Image 2026-02-28 at 00 50 38](https://github.com/user-attachments/assets/32524715-67ee-4d4f-83e1-284fb8f93cb8)
  ![WhatsApp Image 2026-02-28 at 00 51 05](https://github.com/user-attachments/assets/78472c83-87a5-40e2-b587-40d400add574)




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


