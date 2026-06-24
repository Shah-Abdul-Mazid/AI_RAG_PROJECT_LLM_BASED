import os
import json
import re
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Standard imports (will be fully active when pip completes)
import shap
import lime
import lime.lime_tabular

class ExplainabilityService:
    def __init__(self):
        self.model = None
        self.features = ["credit_score", "annual_income", "debt_to_income", "employment_years"]
        self.df = None
        self.X_train = None
        self.explainer_shap = None
        self.explainer_lime = None
        self.is_initialized = False

    def initialize(self):
        """Initializes the model and explainability frameworks if not already done."""
        if self.is_initialized:
            return
            
        try:
            # Generate synthetic loan data
            np.random.seed(42)
            n_samples = 1000
            credit_score = np.random.randint(300, 850, n_samples)
            annual_income = np.random.randint(25000, 200000, n_samples)
            debt_to_income = np.random.uniform(0.05, 0.65, n_samples)
            employment_years = np.random.randint(0, 30, n_samples)
            gender = np.random.choice(["Male", "Female"], n_samples, p=[0.5, 0.5])
            age_group = np.random.choice(["Young", "Mid", "Senior"], n_samples, p=[0.3, 0.5, 0.2])
            
            approved = []
            for i in range(n_samples):
                score = 0
                if credit_score[i] > 670: score += 3
                elif credit_score[i] > 580: score += 1
                if annual_income[i] > 70000: score += 2
                elif annual_income[i] > 40000: score += 1
                if debt_to_income[i] < 0.35: score += 2
                elif debt_to_income[i] > 0.50: score -= 2
                if employment_years[i] > 5: score += 1
                if age_group[i] in ["Young", "Senior"]:
                    score -= 1
                approved.append(1 if score >= 3 else 0)
                
            self.df = pd.DataFrame({
                "credit_score": credit_score,
                "annual_income": annual_income,
                "debt_to_income": debt_to_income,
                "employment_years": employment_years,
                "gender": gender,
                "age_group": age_group,
                "approved": approved
            })
            
            X = self.df[self.features]
            y = self.df["approved"]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.X_train = X_train
            self.model = RandomForestClassifier(n_estimators=50, random_state=42)
            self.model.fit(X_train, y_train)
            
            # Setup SHAP Explainer
            self.explainer_shap = shap.TreeExplainer(self.model)
            
            # Setup LIME Explainer
            self.explainer_lime = lime.lime_tabular.LimeTabularExplainer(
                training_data=np.array(X_train),
                feature_names=self.features,
                class_names=["Rejected", "Approved"],
                mode="classification",
                random_state=42
            )
            self.is_initialized = True
        except Exception as e:
            print(f"[ExplainabilityService] Initializer delay or error: {e}")

    def explain_applicant(self, applicant_id: int):
        self.initialize()
        if not self.is_initialized:
            raise RuntimeError("ExplainabilityService is not fully initialized. Check library installation.")
            
        if applicant_id < 0 or applicant_id >= len(self.df):
            applicant_id = 0
            
        row = self.df.iloc[applicant_id]
        applicant_data = row[self.features]
        pred_label = int(self.model.predict([applicant_data])[0])
        
        # Calculate SHAP Values
        shap_details = {}
        if self.explainer_shap:
            shap_values = self.explainer_shap.shap_values(pd.DataFrame([applicant_data]))
            if isinstance(shap_values, list):
                shap_class_1_val = shap_values[1][0]
            elif len(shap_values.shape) == 3:
                shap_class_1_val = shap_values[0, :, 1]
            else:
                shap_class_1_val = shap_values[0]
            shap_details = dict(zip(self.features, [float(v) for v in shap_class_1_val]))
            
        # Calculate LIME Explanation
        lime_details = {}
        if self.explainer_lime:
            lime_exp = self.explainer_lime.explain_instance(
                data_row=applicant_data,
                predict_fn=self.model.predict_proba,
                num_features=len(self.features)
            )
            lime_details = {rule: float(weight) for rule, weight in lime_exp.as_list()}
            
        return {
            "applicant_id": applicant_id,
            "profile": applicant_data.to_dict(),
            "decision": "Approved" if pred_label == 1 else "Rejected",
            "decision_binary": pred_label,
            "shap": shap_details,
            "lime": lime_details
        }
        
    def get_fairness_summary(self):
        self.initialize()
        if not self.is_initialized:
            raise RuntimeError("ExplainabilityService is not initialized.")
            
        gender_groups = self.df.groupby("gender")["approved"].mean().to_dict()
        age_groups = self.df.groupby("age_group")["approved"].mean().to_dict()
        return {
            "gender": {k: float(v) for k, v in gender_groups.items()},
            "age": {k: float(v) for k, v in age_groups.items()},
            "demographic_parity_gap_gender": float(max(gender_groups.values()) - min(gender_groups.values())),
            "demographic_parity_gap_age": float(max(age_groups.values()) - min(age_groups.values()))
        }

explainability_service = ExplainabilityService()
