import os
import logging
import base64
import json
from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify, session
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
from google import genai
from google.genai import types
import uuid
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

UPLOAD_FOLDER = 'static/uploads'
RESULTS_FOLDER = 'static/results'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)
Path(RESULTS_FOLDER).mkdir(parents=True, exist_ok=True)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "your-api-key")
client = genai.Client(api_key=GEMINI_API_KEY)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_mime_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    mime_types = {
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'webp': 'image/webp'
    }
    return mime_types.get(ext, 'image/jpeg')

def process_with_gemini(prompt, image_data=None, history=None):
    try:
        formatted_history = []
        if history:
            for item in history:
                formatted_item = {
                    "role": item["role"],
                    "parts": []
                }
                for part in item.get("parts", []):
                    if part.get("text"):
                        formatted_item["parts"].append({"text": part["text"]})
                    elif part.get("image") and item["role"] == "user":
                        if part["image"].startswith("data:"):
                            img_parts = part["image"].split(",")
                            if len(img_parts) > 1:
                                formatted_item["parts"].append({
                                    "inlineData": {
                                        "data": img_parts[1],
                                        "mimeType": "image/png" if "image/png" in part["image"] else "image/jpeg"
                                    }
                                })
                if formatted_item["parts"]:
                    formatted_history.append(formatted_item)

        message_parts = [{"text": f"Please edit the following image. {prompt}"}]

        if image_data:
            if isinstance(image_data, str) and image_data.startswith("data:"):
                img_parts = image_data.split(",")
                if len(img_parts) > 1:
                    message_parts.append({
                        "inlineData": {
                            "data": img_parts[1],
                            "mimeType": "image/png" if "image/png" in image_data else "image/jpeg"
                        }
                    })
            else:
                with open(image_data, "rb") as f:
                    image_bytes = f.read()
                    img_data = base64.b64encode(image_bytes).decode()
                message_parts.append({
                    "inlineData": {
                        "data": img_data,
                        "mimeType": get_mime_type(image_data)
                    }
                })

        formatted_history.append({
            "role": "user",
            "parts": message_parts
        })

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=formatted_history,
            config=types.GenerateContentConfig(
                temperature=1,
                top_p=0.95,
                top_k=40,
                response_modalities=["Text", "Image"]
            )
        )

        if not response.candidates:
            raise Exception("No response candidates from Gemini")

        content = response.candidates[0].content
        if not content or not content.parts:
            raise Exception("No content parts in response")

        text_response = None
        image_data = None

        for part in content.parts:
            if hasattr(part, 'text') and part.text:
                text_response = part.text
            elif hasattr(part, 'inline_data') and part.inline_data:
                if hasattr(part.inline_data, 'data') and part.inline_data.data:
                    image_data = part.inline_data.data

        if not image_data:
            retry_prompt = f"Generate an image: {prompt}. Please create and return an actual image."
            retry_response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=[[{"text": retry_prompt}]],
                config=types.GenerateContentConfig(
                    temperature=1,
                    top_p=0.95,
                    top_k=40,
                    response_modalities=["Text", "Image"]
                )
            )
            if retry_response.candidates and retry_response.candidates[0].content:
                for part in retry_response.candidates[0].content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data and hasattr(part.inline_data, 'data'):
                        image_data = part.inline_data.data
                        break
            if not image_data:
                raise Exception("Unable to generate image. Try a different prompt.")

        return {
            'image_data': image_data,
            'description': text_response,
            'mime_type': 'image/png'
        }

    except Exception as e:
        logging.error(f"Error processing with Gemini: {e}")
        raise e

@app.route('/')
def index():
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    if 'current_image' not in session:
        session['current_image'] = None
    if 'generated_image' not in session:
        session['generated_image'] = None
    return render_template('index.html')

@app.route('/api/process-image', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        image_data = data.get('image')
        history = data.get('history', [])

        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400

        result = process_with_gemini(prompt, image_data, history)

        image_data_url = f"data:{result['mime_type']};base64,{base64.b64encode(result['image_data']).decode()}"

        file_id = str(uuid.uuid4())
        filename = f"{file_id}_generated.png"
        file_path = os.path.join(RESULTS_FOLDER, filename)

        with open(file_path, 'wb') as f:
            f.write(result['image_data'])

        return jsonify({
            'success': True,
            'image': image_data_url,
            'description': result['description'],
            'filename': filename
        })

    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return jsonify({'success': False, 'error': 'Failed to process image', 'details': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']
    prompt = request.form.get('prompt', '').strip()

    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    if not prompt:
        flash('Please enter an editing instruction', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        try:
            file_id = str(uuid.uuid4())
            original_ext = file.filename.rsplit('.', 1)[1].lower()
            original_filename = f"{file_id}_original.{original_ext}"
            original_path = os.path.join(UPLOAD_FOLDER, original_filename)
            file.save(original_path)

            result = process_with_gemini(prompt, original_path)

            edited_filename = f"{file_id}_edited.png"
            edited_path = os.path.join(RESULTS_FOLDER, edited_filename)
            with open(edited_path, 'wb') as f:
                f.write(result['image_data'])

            flash('Image processed successfully!', 'success')
            return render_template('result.html',
                                   original_image=original_filename,
                                   edited_image=edited_filename,
                                   prompt=prompt,
                                   description=result.get('description'))
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            flash(f'Error processing image: {str(e)}', 'error')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP files.', 'error')
        return redirect(url_for('index'))

@app.route('/reset')
def reset_session():
    session.clear()
    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/results/<filename>')
def result_file(filename):
    return send_from_directory(RESULTS_FOLDER, filename)

@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Please upload a smaller image.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    host = '127.0.0.1' if os.environ.get('ENVIRONMENT') != 'production' else '0.0.0.0'
    app.run(host=host, port=5000, debug=True)
