from flask import Flask, render_template, request, redirect, url_for
import os
import pytesseract
from deep_translator import GoogleTranslator
import cv2

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_image(image_path, confidence_threshold=50):
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        d = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        extracted_text = ""
        for i in range(len(d["text"])):
            text = d["text"][i]
            conf = int(d["conf"][i]) if 'conf' in d else 0
            if conf > confidence_threshold:
                extracted_text += text + " "
        return extracted_text.strip()
    except Exception as e:
        print(f"Error in extract_text_from_image: {e}")
        return None

def translate_to_preferred_language(text, preferred_language_code):
    try:
        translated_text = GoogleTranslator(source='auto', target=preferred_language_code).translate(text)
        return translated_text
    except Exception as e:
        print(f"Error in translate_to_preferred_language: {e}")
        return None

supported_languages = {
    'english': 'en',
    'french': 'fr',
    'spanish': 'es',
    'telugu': 'te',
    'tamil': 'ta',
    'arabic': 'ar',
    'hindi': 'hi',
    'urdu': 'ur',
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return redirect(request.url)
        file = request.files['image']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            language = request.form.get('language')
            preferred_language_code = supported_languages.get(language.lower())
            if preferred_language_code:
                extracted_text = extract_text_from_image(file_path)
                if extracted_text:
                    translated_text = translate_to_preferred_language(extracted_text, preferred_language_code)
                    if translated_text:
                        return render_template('results.html', extracted_text=extracted_text, translated_text=translated_text)
    return render_template('index.html')

# Function to check if the file extension is allowed
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True)
