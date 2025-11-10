import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# ✅ Load dataset
data_path = os.path.join('data', 'Crop_recommendation.csv')
data = pd.read_csv(data_path)

# ✅ Split features and target
X = data[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = data['label']

# ✅ Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ✅ Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# ✅ Evaluate accuracy
accuracy = model.score(X_test, y_test)
print(f"✅ Model trained successfully with accuracy: {accuracy * 100:.2f}%")

# ✅ Save model
os.makedirs('models', exist_ok=True)
pickle.dump(model, open('models/crop_model.pkl', 'wb'))
print("💾 Model saved as models/crop_model.pkl")
