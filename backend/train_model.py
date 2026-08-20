import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

def train_and_save_model():
    # Load dataset
    df = pd.read_csv('../dataset/Crop_recommendation.csv')
    
    # 7 Feature parameters and label target
    X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
    y = df['label']
    
    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    preds = model.predict(X_test)
    print(f"Model Accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
    
    # Save the trained model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Saved model to backend/model.pkl successfully.")

if __name__ == '__main__':
    train_and_save_model()