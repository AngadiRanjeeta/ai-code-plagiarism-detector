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

![WhatsApp Image 2026-02-28 at 14 26 03](https://github.com/user-attachments/assets/be7e1a76-804b-49ae-bb21-e816ec7497d1)
![WhatsApp Image 2026-02-28 at 14 26 27](https://github.com/user-attachments/assets/d4a3176a-8d71-4611-976f-9ca03b8df45f)
![WhatsApp Image 2026-02-28 at 14 26 56](https://github.com/user-attachments/assets/096bc516-759e-40c9-b534-892a3bfba5a6)




 




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



