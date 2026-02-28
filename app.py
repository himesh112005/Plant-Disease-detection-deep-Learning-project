import os
import io
import json
from flask import Flask, request, jsonify, render_template

try:
    import numpy as np
    from PIL import Image
    from tensorflow.keras.models import load_model
    from tensorflow.keras.preprocessing.image import img_to_array
    MODEL_AVAILABLE = True
except Exception as e:
    print(f"Error importing ML libraries: {e}")
    MODEL_AVAILABLE = False

app = Flask(__name__)

# Try to load model
model = None
if MODEL_AVAILABLE:
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'trained_plant_disease_model.keras')
        if os.path.exists(model_path):
            model = load_model(model_path)
            print("Model loaded successfully")
        else:
            print(f"Model file not found at {model_path}")
    except Exception as e:
        print(f"Error loading model: {e}")

# Class names (38 classes from PlantVillage dataset)
CLASS_NAMES = [
    'Apple___Apple_scab', 'Apple___Black_rot', 'Apple___Cedar_apple_rust', 'Apple___healthy',
    'Blueberry___healthy', 'Cherry_(including_sour)___Powdery_mildew', 'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot', 'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight', 'Corn_(maize)___healthy', 'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)', 'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)', 'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)', 'Peach___Bacterial_spot', 'Peach___healthy',
    'Pepper,_bell___Bacterial_spot', 'Pepper,_bell___healthy', 'Potato___Early_blight',
    'Potato___Late_blight', 'Potato___healthy', 'Raspberry___healthy', 'Soybean___healthy',
    'Squash___Powdery_mildew', 'Strawberry___Leaf_scorch', 'Strawberry___healthy',
    'Tomato___Bacterial_spot', 'Tomato___Early_blight', 'Tomato___Late_blight', 'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot', 'Tomato___Spider_mites Two-spotted_spider_mite', 'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus', 'Tomato___Tomato_mosaic_virus', 'Tomato___healthy'
]

# Simple remedies dictionary corresponding to classes
REMEDIES = {
    'Apple___Apple_scab': 'Remove and destroy fallen leaves. Apply fungicides as a preventative measure.',
    'Apple___Black_rot': 'Prune out dead or diseased wood. Remove mummified fruit. Apply appropriate fungicides.',
    'Apple___Cedar_apple_rust': 'Remove nearby cedar hosts if possible. Apply fungicides during the susceptible period.',
    'Apple___healthy': 'Your apple plant is healthy! Continue with regular care and observation.',
    'Blueberry___healthy': 'Your blueberry plant is healthy! Keep ensuring acidic soil and proper watering.',
    'Cherry_(including_sour)___Powdery_mildew': 'Apply sulfur-based or chemical fungicides. Ensure adequate air circulation.',
    'Cherry_(including_sour)___healthy': 'Your cherry plant is healthy! Monitor regularly for any signs of early issues.',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot': 'Use resistant hybrids. Implement crop rotation. Apply foliar fungicides if severe.',
    'Corn_(maize)___Common_rust_': 'Plant resistant varieties. Apply fungicides when rust pustules first appear.',
    'Corn_(maize)___Northern_Leaf_Blight': 'Rotate away from corn. Apply fungicides before disease becomes severe.',
    'Corn_(maize)___healthy': 'Your corn is healthy! Ensure adequate nitrogen and well-timed watering.',
    'Grape___Black_rot': 'Practice good canopy management for airflow. Apply protective fungicides early.',
    'Grape___Esca_(Black_Measles)': 'Prune out infected wood during dry weather to protect pruning wounds.',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)': 'Apply recommended fungicides for leaf spot diseases. Remove infected leaves.',
    'Grape___healthy': 'Your grape vine is healthy! Continue pruning for sunlight and air exposure.',
    'Orange___Haunglongbing_(Citrus_greening)': 'Manage Asian citrus psyllid populations. Infected trees cannot be cured and should be removed.',
    'Peach___Bacterial_spot': 'Plant resistant varieties. Apply copper-based bactericides during fall and early spring.',
    'Peach___healthy': 'Your peach tree is healthy! Prune yearly to maintain healthy shape and fruit production.',
    'Pepper,_bell___Bacterial_spot': 'Use disease-free seeds. Rotate crops and apply copper sprays when needed.',
    'Pepper,_bell___healthy': 'Your bell pepper is healthy! Ensure consistent moisture and appropriate sunlight.',
    'Potato___Early_blight': 'Use certified disease-free seeds. Apply protective fungicides and rotate your crops.',
    'Potato___Late_blight': 'Apply preventative fungicides. Destroy infected plants immediately to prevent spreading.',
    'Potato___healthy': 'Your potato plant is healthy! Continue hilling the potatoes as they grow.',
    'Raspberry___healthy': 'Your raspberry plant is healthy! Make sure to prune old canes regularly.',
    'Soybean___healthy': 'Your soybean plant is healthy! Keep weed control in check and monitor insect activity.',
    'Squash___Powdery_mildew': 'Apply appropriate fungicides like sulfur or potassium bicarbonate. Use resistant variants.',
    'Strawberry___Leaf_scorch': 'Improve air circulation across the beds. Remove infected leaves to reduce spores.',
    'Strawberry___healthy': 'Your strawberry plant is healthy! Provide adequate spacing to prevent overcrowding.',
    'Tomato___Bacterial_spot': 'Use copper-based sprays. Switch to drip irrigation instead of overhead watering.',
    'Tomato___Early_blight': 'Space plants adequately. Apply mulch to stop dirt from splashing onto leaves.',
    'Tomato___Late_blight': 'Apply appropriate preventative fungicides. Remove and destroy infected materials.',
    'Tomato___Leaf_Mold': 'Improve greenhouse/ambient ventilation. Avoid watering the foliage directly.',
    'Tomato___Septoria_leaf_spot': 'Remove lower infected leaves. Apply chlorothalonil or copper-based fungicides.',
    'Tomato___Spider_mites Two-spotted_spider_mite': 'Introduce predatory mites. Use insecticidal soaps or neem oil carefully.',
    'Tomato___Target_Spot': 'Control weeds around plants. Improve air circulation and use targeted fungicides.',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus': 'Control whitefly populations actively. Use resistant tomato varieties.',
    'Tomato___Tomato_mosaic_virus': 'Wash tools thoroughly before and after use. Remove infected plants promptly.',
    'Tomato___healthy': 'Your tomato plant is healthy! Ensure consistent watering to prevent cracking.'
}

def preprocess_image(image_bytes):
    if not MODEL_AVAILABLE:
        return None
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img = img.convert('RGB')
        img = img.resize((128, 128))
        # Convert to numpy array
        img_array = img_to_array(img)
        # Assuming the model is trained with scaling values / 255.0
        # Check standard training procedures or adjust if needed
        # img_array = img_array / 255.0  (if scaling was used)
        img_array = np.expand_dims(img_array, axis=0) # Add batch dimension
        return img_array
    except Exception as e:
        print(f"Error in image preprocessing: {e}")
        return None

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Machine learning model not loaded or dependencies missing.'}), 500

    if 'image' not in request.files:
        return jsonify({'error': 'No image provided.'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected.'}), 400

    try:
        image_bytes = file.read()
        processed_img = preprocess_image(image_bytes)

        if processed_img is None:
             return jsonify({'error': 'Failed to process image. Make sure it is a valid image format.'}), 400

        # Predict using keras model
        predictions = model.predict(processed_img)
        predicted_class_idx = np.argmax(predictions, axis=1)[0]
        confidence = float(np.max(predictions)) * 100
        
        predicted_class_name = CLASS_NAMES[predicted_class_idx]
        formatted_name = predicted_class_name.replace('___', ' - ').replace('_', ' ')
        remedy = REMEDIES.get(predicted_class_name, "Consult a local agricultural extension office for more specialized care details.")

        return jsonify({
            'disease': formatted_name,
            'confidence': f"{confidence:.2f}%",
            'remedy': remedy
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
