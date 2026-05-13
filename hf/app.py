import os
import joblib
import numpy as np
import pandas as pd
import gradio as gr
import warnings

# Suppress inconsistent version warnings from joblib/sklearn (e.g. training environment vs deployment)
warnings.filterwarnings("ignore", category=UserWarning)

# --- Configuration & Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")
PREPROCESSORS_DIR = os.path.join(BASE_DIR, "preprocessors")

# --- Load Artifacts ---
print("Loading ML artifacts...")
try:
    regressor = joblib.load(os.path.join(MODELS_DIR, "lgbm_rating_regressor.joblib"))
    classifier = joblib.load(os.path.join(MODELS_DIR, "rf_hit_classifier.joblib"))
    scaler = joblib.load(os.path.join(PREPROCESSORS_DIR, "standard_scaler.pkl"))
    mlb = joblib.load(os.path.join(PREPROCESSORS_DIR, "genre_mlb.pkl"))
    print("Artifacts loaded successfully!")
except Exception as e:
    print(f"Error loading artifacts: {e}")
    raise

# Dynamically extract genre list from the MultiLabelBinarizer
GENRE_CHOICES = list(mlb.classes_)

# Constant configurations mapped from training data analysis
BASELINE_VOTE_COUNT = 1000
DEFAULT_RELEASE_YEAR = 2025
GLOBAL_LANG_MEAN = 5.9244
HOLLYWOOD_LANG_MEAN = 5.9206
INDIAN_LANG_MEAN = 5.9214

# The exact feature order expected by the models:
FEATURE_ORDER = [
    'release_year', 'language_quality_score', 'runtime_minutes_scaled', 
    'vote_count_log_scaled', 'genre_density', 'votes_per_minute', 
    'market_Hollywood', 'market_Indian'
] + GENRE_CHOICES

# --- Prediction Logic ---
def predict_movie_success(title, market, genres_selected, runtime):
    """
    Processes user input and predicts Expected Rating and Hit/Flop Probability.
    """
    # 1. Base Variables
    vote_count_log = np.log1p(BASELINE_VOTE_COUNT)
    genre_density = len(genres_selected)
    votes_per_minute = BASELINE_VOTE_COUNT / runtime if runtime > 0 else 0
    
    # 2. Scale Numerical Features
    # Scaler was fit on ["runtime_minutes_filled", "vote_count_log"]
    num_features = pd.DataFrame([[runtime, vote_count_log]], columns=["runtime_minutes_filled", "vote_count_log"])
    scaled_nums = scaler.transform(num_features)
    runtime_scaled = scaled_nums[0, 0]
    vote_count_log_scaled = scaled_nums[0, 1]
    
    # 3. Market & Language Features
    market_Hollywood = 1 if market == "Hollywood" else 0
    market_Indian = 1 if market == "Indian" else 0
    
    # Target Encoding proxy based on market
    if market == "Hollywood":
        lang_score = HOLLYWOOD_LANG_MEAN
    elif market == "Indian":
        lang_score = INDIAN_LANG_MEAN
    else:
        lang_score = GLOBAL_LANG_MEAN
        
    # 4. Genre Binarization
    # mlb.transform expects a 2D array-like, where each element is a list of genres
    genre_matrix = mlb.transform([genres_selected])
    
    # 5. Construct Feature Vector
    # Build dictionary of features to construct DataFrame
    feature_dict = {
        'release_year': DEFAULT_RELEASE_YEAR,
        'language_quality_score': lang_score,
        'runtime_minutes_scaled': runtime_scaled,
        'vote_count_log_scaled': vote_count_log_scaled,
        'genre_density': genre_density,
        'votes_per_minute': votes_per_minute,
        'market_Hollywood': market_Hollywood,
        'market_Indian': market_Indian
    }
    
    # Add genre binarized features
    for idx, genre in enumerate(GENRE_CHOICES):
        feature_dict[genre] = genre_matrix[0, idx]
        
    # Create DataFrame in exact required order
    X_inference = pd.DataFrame([feature_dict], columns=FEATURE_ORDER)
    
    # 6. Model Inference
    # Regression prediction (Expected Rating)
    predicted_rating = regressor.predict(X_inference)[0]
    
    # Classification prediction (Hit or Flop)
    # The random forest returns a probability or direct class prediction.
    # We will use predict() which returns 1 for Hit, 0 for Flop.
    hit_prediction = classifier.predict(X_inference)[0]
    hit_prob = classifier.predict_proba(X_inference)[0, 1] if hasattr(classifier, 'predict_proba') else None
    
    # Format Results
    rating_display = round(predicted_rating, 1)
    
    if hit_prediction == 1:
        hit_label = f"🔥 Hit (Probability: {hit_prob*100:.1f}%)" if hit_prob is not None else "🔥 Hit"
    else:
        hit_label = f"❄️ Flop (Probability: {hit_prob*100:.1f}%)" if hit_prob is not None else "❄️ Flop"
        
    return hit_label, rating_display

# --- Gradio User Interface ---
theme = gr.themes.Soft(
    primary_hue="indigo", 
    secondary_hue="blue", 
    neutral_hue="slate"
)

with gr.Blocks(theme=theme) as app:
    gr.Markdown("# 🎬 Cinema Intelligence: Market Success Predictor (2021–2025)")
    gr.Markdown(
        "Predict a movie's **Expected IMDb Rating** and **Hit/Flop status** before it releases. "
        "Based on extensive data modeling from Hollywood and Indian cinema trends (2021-2025)."
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            # Inputs
            title_input = gr.Textbox(label="Primary Title", placeholder="Enter movie title...")
            market_input = gr.Dropdown(choices=["Hollywood", "Indian"], label="Target Market", value="Hollywood")
            runtime_input = gr.Slider(minimum=40, maximum=240, value=120, step=1, label="Runtime (Minutes)")
            genres_input = gr.CheckboxGroup(choices=GENRE_CHOICES, label="Genres (Select up to 3 for best results)", value=["Action", "Drama"])
            
            predict_btn = gr.Button("🔮 Predict Success", variant="primary")
            
        with gr.Column(scale=1):
            # Outputs
            hit_output = gr.Label(label="Market Classification")
            rating_output = gr.Number(label="Expected Rating (1-10)", precision=1)
            
    # Footer Documentation
    gr.Markdown(
        """
        ---
        **Limitations & Technical Notes:**
        * Designed for CPU Basic Hardware constraints.
        * Predictions assume a baseline organic reach (~1000 votes) and standard release window.
        * Model relies on historical trends (2021-2025); highly unprecedented phenomena (e.g. unexpected viral marketing) may not be fully captured.
        """
    )
            
    # Connect logic
    predict_btn.click(
        fn=predict_movie_success,
        inputs=[title_input, market_input, genres_input, runtime_input],
        outputs=[hit_output, rating_output]
    )

if __name__ == "__main__":
    app.launch()
