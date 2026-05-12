# Feature Engineering Notebook Markdowns

This document contains the markdown cells to insert *before* each corresponding code cell in your `03_Feature_Engineering.ipynb` notebook.

---

### Before Cell 1
```markdown
# Phase 3: Feature Engineering

**Objective:** Transform the cleaned "Golden Dataset" into a numeric feature matrix optimized for Machine Learning.

This phase includes structural data preparation, categorical encoding, numerical transformations, derived feature creation, and finalizing the dataset for modeling.

## 1. Imports, DB Connection & Data Loading
Re-establishing the database connection to load the raw data and applying the same credibility filters from the EDA phase to ensure consistency.
```

---

### Before Cell 2 (This is the Markdown-only Cell 2)
*Note: This content replaces code cell 2 entirely.*
```markdown
## 2. Temporal Features: `release_year` Only

**Design Decision — Sub-Year Features Excluded**

The source dataset (IMDb basics) stores `release_date` at year-only precision — every entry defaults to `January 1st` of its release year.

As a result, the following features would carry **zero variance or false signals** and are deliberately **not engineered**:
- `release_month` — always January (1)
- `release_quarter` — always Q1
- `is_weekend_release` — Jan 1 day-of-week varies by year, not by actual release intent

**`release_year` is retained as the sole temporal feature** (integer, 2021–2025). It captures linear industry trends across the dataset window. In the Modeling phase, it can optionally be one-hot encoded to isolate year-specific market conditions (e.g., the 2023 WGA/SAG-AFTRA industry strikes).
```

---

### Before Cell 3
```markdown
## 3. Categorical Encoding (Text to Math)

### Multi-Label Genre Encoding
Transforming the `genres` list into individual binary columns using `MultiLabelBinarizer`. This creates a sparse matrix where each unique genre becomes a feature.
```

---

### Before Cell 4
```markdown
### Language Target Encoding
Replacing categorical language names with a "Quality Signal" by mapping each language to its global average rating within the dataset.
```

---

### Before Cell 5
```markdown
### Market Encoding
Applying One-Hot Encoding to the `market_type` to separate Hollywood and Indian cinema flags into distinct binary columns.
```

---

### Before Cell 6
```markdown
## 4. Numerical Transformation & Scaling

To ensure numerical inputs occupy the same mathematical space and prevent high-magnitude features from dominating:
1. **Missing Data Imputation:** Filling missing `runtime_minutes` with the median.
2. **Skewness Correction:** Applying a Log Transformation ($\log(x+1)$) to `vote_count` to handle its right-skewed distribution.
3. **Feature Scaling:** Using `StandardScaler` on continuous features. **Crucially**, the scaler is fitted *only* on the training data (years < 2025) to prevent data leakage.
```

---

### Before Cell 7
```markdown
## 5. Derived Feature Creation

Creating new signals from existing data:
- `genre_density`: The count of genres assigned to a movie.
- `votes_per_minute`: Measuring audience engagement relative to runtime. Unrated movies (NaN) are filled with 0.
```

---

### Before Cell 8
```markdown
## 6. Modeling Readiness

### Target Definition
Defining our target variables for the models:
- **Regression:** `rating` (continuous score)
- **Classification:** `is_hit` (binary flag where rating > 7.0)

Movies without a target rating are dropped at this stage.
```

---

### Before Cell 9
```markdown
### Feature Matrix Assembly
Concatenating all engineered numerical features, market dummies, and genre matrices into the final Feature Matrix (`X`). Raw text and pre-transformed columns are dropped.
```

---

### Before Cell 10
```markdown
### Chronological Train/Test Split
Partitioning the data chronologically to evaluate the model on "future" unseen data:
- **Training Set:** 2021–2024
- **Test Set:** 2025
```

---

### Before Cell 11
```markdown
### Export Artifacts
Saving the final matrices as `.parquet` files for efficient reading in the modeling phase, along with the fitted scaler and binarizer `.pkl` files for future inference.
```
