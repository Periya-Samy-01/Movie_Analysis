# Cinema Intelligence

Welcome to the **Cinema Intelligence** project, an end-to-end Machine Learning pipeline that predicts movie success metrics such as the **Expected IMDb Rating** and **Hit/Flop** probability.

This project covers a robust feature engineering pipeline, addressing temporal data shifts, text-to-math categorical encoding (MultiLabelBinarizer for genres, Target Encoding for languages), and extensive handling of numerical distributions.

## Live Demo

A live, interactive web interface powered by Gradio is hosted on Hugging Face Spaces!

👉 **[Launch the Cinema Intelligence Predictor (Live Demo)](#)** 
*(Placeholder: Update the `#` with your Hugging Face Space URL once deployed)*

## Model Performance Summary

To demonstrate the technical depth of the modeling phase, we compared simple baseline models against advanced tree-based architectures.

### Regression (Target: `averageRating`)
| Model | MAE | RMSE | R² Score | Notes |
|-------|-----|------|----------|-------|
| **Linear Regression** (Baseline) | 1.0131 | 1.3351 | 0.2059 | Initial Benchmark |
| **LightGBM** (Advanced) | **0.9860** | **1.3126** | **0.2325** | Best MAE — Selected as primary regressor |

### Classification (Target: `is_hit` | Rating > 7.0)
| Model | ROC AUC | Hit F1-Score | True Positives | False Negatives | Notes |
|-------|---------|--------------|----------------|-----------------|-------|
| **Logistic Regression** (Baseline)| 0.7253 | 0.50 | 637 | 488 | Initial Benchmark |
| **Random Forest** (Advanced) | **0.7468** | **0.52** | **696** | **429** | Best Hit F1 & lowest FN — Selected as primary classifier |

## Instructions for Deployment

The deployment-ready files are located in the `hf/` directory.

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces) and create a new Space.
2. Select **Gradio** as the SDK and use the **CPU Basic** hardware (free tier).
3. Upload the contents of the `hf/` folder (including `models/` and `preprocessors/`) directly to your Hugging Face Space repository.
4. The space will automatically install the libraries from `requirements.txt` and launch `app.py`.
