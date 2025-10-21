import streamlit as st
import pickle
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Customer Churn Prediction",
    page_icon="📊",
    layout="centered"
)

# Load the model
@st.cache_resource
def load_model():
    try:
        with open('churn_pred.pkl', 'rb') as f:
            model = pickle.load(f)
        return model
    except FileNotFoundError:
        st.error("Model file 'churn_pred.pkl' not found. Please ensure it's in the same directory.")
        return None
    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None

# Main title
st.title(" Customer Churn Prediction System")
st.markdown("---")

# Load model
model = load_model()

if model is not None:
    # Create two columns for input
    col1, col2 = st.columns(2)
    
    with col1:
        customer_id = st.text_input("Customer ID", placeholder="e.g., CUST001")
        age = st.number_input("Age", min_value=18, max_value=100, value=30, step=1)
        gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
        tenure = st.number_input("Tenure (months)", min_value=0, max_value=120, value=12, step=1)
    
    with col2:
        support_calls = st.number_input("Support Calls", min_value=0, max_value=50, value=2, step=1)
        contract_length = st.number_input("Contract Length (months)", min_value=1, max_value=36, value=12, step=1)
        payment_delay = st.number_input("Payment Delay (days)", min_value=0, max_value=365, value=0, step=1)
    
    st.markdown("---")
    
    # Predict button
    if st.button("🔮 Predict Churn", type="primary", use_container_width=True):
        if not customer_id:
            st.warning("⚠️ Please enter a Customer ID")
        else:
            # Convert gender to numeric (common encoding)
            gender_mapping = {"Male": 0, "Female": 1, "Other": 2}
            gender_encoded = gender_mapping[gender]
            
            # Prepare input data
            # Convert CustomerID to numeric (extract numbers from ID)
            try:
                customer_id_numeric = int(''.join(filter(str.isdigit, customer_id)))
            except:
                customer_id_numeric = hash(customer_id) % 100000  # fallback to hash
            
            input_data = pd.DataFrame({
                'CustomerID': [customer_id_numeric],
                'Age': [age],
                'Gender': [gender_encoded],
                'Tenure': [tenure],
                'Support Calls': [support_calls],
                'Contract Length': [contract_length],
                'Payment Delay': [payment_delay]
            })
            
            try:
                # Make prediction with all 7 features
                prediction = model.predict(input_data)
                
                # Try to get prediction probability if available
                try:
                    prediction_proba = model.predict_proba(features)
                    churn_probability = prediction_proba[0][1] * 100
                except:
                    churn_probability = None
                
                # Display results
                st.markdown("### 📋 Prediction Results")
                
                result_col1, result_col2 = st.columns(2)
                
                with result_col1:
                    st.metric("Customer ID", customer_id)
                
                with result_col2:
                    if prediction[0] == 1:
                        pass
                    else:
                        st.success("✅ Low Churn Risk")
                
                if churn_probability is not None:
                    st.progress(churn_probability / 100)
                    st.metric("Churn Probability", f"{churn_probability:.2f}%")
                
                # Customer insights
                st.markdown("### 💡 Customer Insights")
                
                insights = []
                if support_calls > 5:
                    insights.append("⚠️ High number of support calls - may indicate dissatisfaction")
                if payment_delay > 7:
                    insights.append("⚠️ Payment delays detected - financial stress or dissatisfaction")
                if tenure < 6:
                    insights.append("ℹ️ New customer - higher churn risk in early months")
                if tenure > 24:
                    insights.append("✅ Long-term customer - lower churn risk")
                if contract_length >= 12:
                    insights.append("✅ Annual contract - shows commitment")
                
                if insights:
                    for insight in insights:
                        st.write(insight)
                else:
                    st.write("✅ No major risk factors detected")
                    
            except Exception as e:
                st.error(f"Error making prediction: {str(e)}")
                st.info("Please ensure your input features match the model's expected format.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <small>Customer Churn Prediction System | Powered by Machine Learning</small>
    </div>
    """, 
    unsafe_allow_html=True
)