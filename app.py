from flask import Flask, render_template, request, jsonify
import face_recognition
import numpy as np
from PIL import Image
import os
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Gemini
api_key = os.getenv('GOOGLE_API_KEY')  # You'll need to set this in your .env file
if not api_key:
    raise ValueError("No Google API key found. Please set it in the .env file.")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def analyze_face(image_path):
    # Load the image
    image = face_recognition.load_image_file(image_path)
    
    # Find face locations
    face_locations = face_recognition.face_locations(image)
    
    if not face_locations:
        return None
    
    # Get face encodings
    face_encodings = face_recognition.face_encodings(image, face_locations)
    
    # Analyze face landmarks
    face_landmarks = face_recognition.face_landmarks(image, face_locations)
    
    # Basic analysis results
    results = {
        'num_faces': len(face_locations),
        'face_landmarks': face_landmarks[0] if face_landmarks else None
    }
    
    return results

def generate_advice(image_features, mode):
    if mode == "looksmaxxing":
        prompt = f"""You are a serene and supportive AI image consultant. Based on the facial features detected in the image ({image_features}), 
        provide peaceful and uplifting suggestions for enhancement. Format your response using HTML and emojis for better readability:

        1. Start with a warm greeting and introduction wrapped in <h3> tags
        2. Begin with 3-4 genuine compliments about their features, each in <p> tags with 🌟 emoji
        3. Use <strong> tags for emphasis on key positive points
        4. Use <em> tags for gentle suggestions
        5. Create a structured list of suggestions using <ul> and <li> tags
        6. Add relevant emojis (✨, 🌸, 🌊, 🌅, etc.) to make the text engaging
        7. End with an uplifting message in a <div class='inspiration'> tag

        Keep the tone peaceful and supportive, using metaphors of nature and tranquility."""

    elif mode == "dripmaxxing":
        prompt = f"""You are a tranquil AI style consultant. Based on the style elements detected ({image_features}), 
        offer serene and harmonious fashion advice. Format your response using HTML and emojis for better readability:

        1. Start with a warm greeting and style overview wrapped in <h3> tags
        2. Begin with 3-4 positive observations about their current style, each in <p> tags with 👔 emoji
        3. Use <strong> tags for emphasis on key style elements
        4. Use <em> tags for gentle style suggestions
        5. Create a structured list of style recommendations using <ul> and <li> tags
        6. Add relevant emojis (✨, 👕, 👖, 👟, etc.) to make the text engaging
        7. End with an inspiring style message in a <div class='inspiration'> tag

        Keep the tone peaceful and supportive, focusing on personal expression and comfort."""

    elif mode == "auramaxxing":
        prompt = f"""You are a peaceful AI presence coach. Based on the overall impression ({image_features}), 
        provide serene advice about enhancing personal presence. Format your response using HTML and emojis for better readability:

        1. Start with a warm greeting and energy reading wrapped in <h3> tags
        2. Begin with 3-4 positive observations about their aura, each in <p> tags with ✨ emoji
        3. Use <strong> tags for emphasis on key energy points
        4. Use <em> tags for gentle energy enhancement suggestions
        5. Create a structured list of presence-boosting tips using <ul> and <li> tags
        6. Add relevant emojis (🌟, 🌸, 🌊, 🧘‍♀️, etc.) to make the text engaging
        7. End with an inspiring spiritual message in a <div class='inspiration'> tag

        Keep the tone peaceful and mindful, focusing on inner beauty and personal growth."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating advice: {str(e)}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    mode = request.form.get('mode', 'looksmaxxing')  # Default to looksmaxxing if not specified
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file:
        # Save the uploaded file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'upload_{timestamp}.jpg'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the image
        analysis_results = analyze_face(filepath)
        
        # Generate advice using Gemini
        advice = generate_advice(analysis_results, mode)
        
        return jsonify({
            'success': True,
            'image_path': f'/static/uploads/{filename}',
            'advice': advice
        })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 