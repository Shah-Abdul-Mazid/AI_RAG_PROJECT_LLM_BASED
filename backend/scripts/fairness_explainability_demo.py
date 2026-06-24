import os
import sys
import re
import json
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import requests

# 1. Environment and configuration setup
load_dotenv()

# We will use scikit-learn, Fairlearn, SHAP, and LIME which are being installed.
# We import them here.
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Import Fairlearn metrics
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    demographic_parity_difference,
    equalized_odds_difference
)

# Import SHAP and LIME
import shap
import lime
import lime.lime_tabular

def generate_mock_loan_data(n_samples=1000, random_state=42):
    """
    Generates a synthetic banking credit/loan decision dataset.
    Features:
      - credit_score: 300 to 850 (creditworthiness)
      - annual_income: $25k to $200k (financial capacity)
      - debt_to_income: 0.05 to 0.65 (financial risk)
      - employment_years: 0 to 30 (stability)
    Sensitive Attributes (tracked for fairness but excluded from model training):
      - gender: Male, Female
      - age_group: Young (18-30), Mid (31-59), Senior (60+)
    """
    np.random.seed(random_state)
    
    # Financial metrics
    credit_score = np.random.randint(300, 850, n_samples)
    annual_income = np.random.randint(25000, 200000, n_samples)
    debt_to_income = np.random.uniform(0.05, 0.65, n_samples)
    employment_years = np.random.randint(0, 30, n_samples)
    
    # Sensitive attributes (independent of financial parameters in this generator)
    gender = np.random.choice(["Male", "Female"], n_samples, p=[0.5, 0.5])
    age_group = np.random.choice(["Young", "Mid", "Senior"], n_samples, p=[0.3, 0.5, 0.2])
    
    # Target variable: 'approved' (0 or 1)
    # Built using a composite rule with simulated historic demographic bias (e.g. system favors Mid over Young/Senior)
    approved = []
    for i in range(n_samples):
        # Base credit scoring logic
        score = 0
        if credit_score[i] > 670: score += 3
        elif credit_score[i] > 580: score += 1
        
        if annual_income[i] > 70000: score += 2
        elif annual_income[i] > 40000: score += 1
        
        if debt_to_income[i] < 0.35: score += 2
        elif debt_to_income[i] > 0.50: score -= 2
        
        if employment_years[i] > 5: score += 1
        
        # Add simulated historic bias to target label (Young/Senior get a -1 penalty in the historic label)
        if age_group[i] in ["Young", "Senior"]:
            score -= 1
            
        # Decision boundary (pass if score >= 3)
        decision = 1 if score >= 3 else 0
        approved.append(decision)
        
    df = pd.DataFrame({
        "credit_score": credit_score,
        "annual_income": annual_income,
        "debt_to_income": debt_to_income,
        "employment_years": employment_years,
        "gender": gender,
        "age_group": age_group,
        "approved": approved
    })
    return df

def run_openai_explanation(applicant_id, applicant_details, decision, shap_details, lime_details):
    """
    Uses OpenAI GPT-4o-mini to synthesize a plain-English explainability report
    based on SHAP values and LIME local linear approximations.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("\n[OpenAI Integration] Skipping OpenAI explanation synthesis (OPENAI_API_KEY is not set).")
        return "OpenAI API key missing. Could not generate plain-English report."
        
    print(f"\n[OpenAI Integration] Requesting plain-English translation for Applicant #{applicant_id}...")
    
    system_prompt = (
        "You are the Nexus Intelligence Transparent Credit Explainer. "
        "Your task is to take mathematical explainability outputs (SHAP features & LIME coefficients) "
        "for a banking credit decision and write a clear, empathetic, and compliant letter to the applicant "
        "or loan officer. "
        "Rules:\n"
        "1. Start by stating the decision clearly (Approved or Rejected).\n"
        "2. Detail the primary mathematical drivers (both positive and negative) using the SHAP and LIME details provided.\n"
        "3. Provide actionable suggestions on what they can do to improve their profile to reverse the decision (e.g. debt reduction, income boost).\n"
        "4. Emphasize that demographic properties (gender, age_group) are protected and were EXCLUDED from the training variables."
    )
    
    user_content = (
        f"Applicant ID: {applicant_id}\n"
        f"Loan Decision: {'APPROVED' if decision == 1 else 'REJECTED'}\n\n"
        f"Applicant Financial Profile:\n"
        f"- Credit Score: {applicant_details['credit_score']}\n"
        f"- Annual Income: ${applicant_details['annual_income']:,}\n"
        f"- Debt-To-Income Ratio: {applicant_details['debt_to_income']:.2f}\n"
        f"- Employment Years: {applicant_details['employment_years']}\n\n"
        f"SHAP Feature Importance Values (Positive is in favor of approval, Negative is against approval):\n"
        f"{json.dumps(shap_details, indent=2)}\n\n"
        f"LIME Rule/Weights:\n"
        f"{json.dumps(lime_details, indent=2)}\n"
    )
    
    try:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.5
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as exc:
        return f"OpenAI lookup failed: {exc}"

def main():
    print("=" * 70)
    print("      Nexus Intelligence: Fairlearn & SHAP/LIME Banking Demo")
    print("=" * 70)
    
    # 2. Ingest and split dataset
    print("\n[Step 1] Generating synthetic loan decision dataset (n=1000)...")
    df = generate_mock_loan_data()
    
    # We train our model ONLY on financial variables, excluding protected categories (gender, age_group)
    features = ["credit_score", "annual_income", "debt_to_income", "employment_years"]
    sensitive_attributes = ["gender", "age_group"]
    
    X = df[features]
    y = df["approved"]
    S = df[sensitive_attributes] # Sensitive demographics
    
    X_train, X_test, y_train, y_test, S_train, S_test = train_test_split(
        X, y, S, test_size=0.2, random_state=42
    )
    
    # 3. Model training
    print("[Step 2] Training Credit Predictor Model (Random Forest)...")
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"  -> Model trained successfully. Test Accuracy: {accuracy * 100:.2f}%")
    
    # 4. Fairlearn Bias Assessment
    print("\n[Step 3] Assessing Historical Bias and Disparities with Fairlearn...")
    
    # Calculate demographic parity difference (gender)
    dp_diff_gender = demographic_parity_difference(
        y_test, y_pred, sensitive_features=S_test["gender"]
    )
    
    # Calculate demographic parity difference (age_group)
    dp_diff_age = demographic_parity_difference(
        y_test, y_pred, sensitive_features=S_test["age_group"]
    )
    
    # Let's inspect group metric details using Fairlearn's MetricFrame
    metric_frame_gender = MetricFrame(
        metrics=selection_rate,
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=S_test["gender"]
    )
    
    metric_frame_age = MetricFrame(
        metrics=selection_rate,
        y_true=y_test,
        y_pred=y_pred,
        sensitive_features=S_test["age_group"]
    )
    
    print("\n  --- Fairlearn Metrics Report ---")
    print(f"  Demographic Parity Difference (Gender): {dp_diff_gender:.4f}")
    print(f"  Demographic Parity Difference (Age Group): {dp_diff_age:.4f}")
    
    print("\n  Selection Rate (Approval Rate) by Gender:")
    for group, val in metric_frame_gender.by_group.items():
        print(f"    - {group}: {val * 100:.2f}%")
        
    print("\n  Selection Rate (Approval Rate) by Age Group:")
    for group, val in metric_frame_age.by_group.items():
        print(f"    - {group}: {val * 100:.2f}%")
        
    # 5. SHAP Explainability
    print("\n[Step 4] Computing Feature Contributions with SHAP...")
    # Initialize tree explainer
    explainer_shap = shap.TreeExplainer(model)
    shap_values = explainer_shap.shap_values(X_test)
    
    # In SHAP multi-class (or binary class output), class 1 represents Approval.
    # Check shape of shap_values. If it is 3D or list of 2D arrays, retrieve class 1.
    if isinstance(shap_values, list):
        # Older shap versions return a list [class_0_values, class_1_values]
        shap_class_1 = shap_values[1]
    elif len(shap_values.shape) == 3:
        # Shap returns (n_samples, n_features, n_classes)
        shap_class_1 = shap_values[:, :, 1]
    else:
        shap_class_1 = shap_values
        
    # 6. LIME Explainability
    print("[Step 5] Initializing LIME Tabular Explainer...")
    explainer_lime = lime.lime_tabular.LimeTabularExplainer(
        training_data=np.array(X_train),
        feature_names=features,
        class_names=["Rejected", "Approved"],
        mode="classification",
        random_state=42
    )
    
    # 7. Select a test applicant to explain (let's pick one that got rejected)
    # Find a rejected index
    rejected_indices = np.where(y_pred == 0)[0]
    if len(rejected_indices) == 0:
        target_idx = 0
    else:
        target_idx = rejected_indices[0] # Pick the first rejected applicant
        
    applicant_data = X_test.iloc[target_idx]
    actual_label = y_test.iloc[target_idx]
    pred_label = y_pred[target_idx]
    
    # Map raw SHAP values for this applicant
    applicant_shap = dict(zip(features, [float(v) for v in shap_class_1[target_idx]]))
    
    # Run LIME local explanation
    lime_exp = explainer_lime.explain_instance(
        data_row=applicant_data,
        predict_fn=model.predict_proba,
        num_features=len(features)
    )
    # LIME explanation features as dictionary
    lime_list = lime_exp.as_list()
    lime_details = {rule: float(weight) for rule, weight in lime_list}
    
    print("\n  --- Explainability Diagnostics for Applicant #{} ---".format(target_idx))
    print(f"  True Status: {'Approved' if actual_label == 1 else 'Rejected'}")
    print(f"  Model Prediction: {'Approved' if pred_label == 1 else 'Rejected'}")
    print("\n  Applicant Profile:")
    for col in features:
        print(f"    - {col}: {applicant_data[col]}")
        
    print("\n  SHAP Contribution Scores (positive pushes towards Approval, negative pulls towards Rejection):")
    for feat, val in applicant_shap.items():
        print(f"    - {feat:18s} : {val:+.4f}")
        
    print("\n  LIME Rules & Linear Weights:")
    for rule, weight in lime_details.items():
        print(f"    - {rule:28s} : {weight:+.4f}")
        
    # 8. OpenAI translation layer
    print("\n[Step 6] Running OpenAI Translation Agent...")
    openai_explanation = run_openai_explanation(
        applicant_id=target_idx,
        applicant_details=applicant_data.to_dict(),
        decision=pred_label,
        shap_details=applicant_shap,
        lime_details=lime_details
    )
    
    print("\n" + "=" * 70)
    print("             OpenAI Generated Explainability Letter")
    print("=" * 70)
    print(openai_explanation)
    print("=" * 70)

if __name__ == "__main__":
    main()
