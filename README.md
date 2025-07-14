# AI Image Editor

A comprehensive Flask-based image generation and editing application powered by Google's Gemini 2.0 Flash API. This application supports both text-to-image generation and iterative image editing with conversation history.

## ✨ Features

### 🎨 Dual Mode Operation
- **Text-to-Image Generation**: Create images from natural language descriptions
- **Image Editing**: Upload and modify existing images with AI-powered edits
- **Seamless Workflow**: Switch between creation and editing modes effortlessly

### 💬 Conversation History
- **Context-Aware Editing**: Maintain conversation context for iterative refinements
- **History Viewer**: See the complete conversation flow with images and text
- **Iterative Improvements**: Build upon previous edits with accumulated context

### 🖼️ Advanced Image Handling
- **Drag & Drop Upload**: Intuitive file upload with drag-and-drop support
- **Multiple Formats**: Support for PNG, JPG, JPEG, GIF, and WebP (up to 10MB)
- **Image Preview**: Instant preview of uploaded images
- **High-Quality Output**: Generated images saved in PNG format

### 🎯 User Experience
- **Real-time Processing**: AJAX-based interface with loading states
- **Error Handling**: Comprehensive error messages and validation
- **Download Functionality**: Save generated and edited images
- **Responsive Design**: Mobile-friendly Bootstrap interface
- **Dark Theme**: Professional dark theme with excellent contrast

### 🔧 Technical Features
- **Session Management**: Maintains state across requests
- **File Organization**: Separate directories for uploads and results
- **RESTful API**: JSON-based API endpoints for frontend integration
- **Logging**: Comprehensive debugging and error logging

## 🚀 How It Works

1. **Create Images**: Generate images from text prompts using Gemini 2.0 Flash
2. **Edit Images**: Upload an image and provide instructions to modify it
3. **Conversation Context**: Maintain context through a conversation with the AI
4. **Iterative Refinements**: Continue editing based on previous results
5. **Download Results**: Save your generated or edited images

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get yours here](https://aistudio.google.com/))

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-image-editor
   ```

2. **Install dependencies**
   ```bash
   pip install flask google-genai werkzeug gunicorn
   ```

3. **Set up environment variables**
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   SESSION_SECRET=your_session_secret_here
   ```
   
   Or set environment variables directly:
   ```bash
   export GEMINI_API_KEY="your-gemini-api-key"
   export SESSION_SECRET="your-secret-key"
   ```

4. **Run the application**
   ```bash
   python app.py
   ```
   
   Or with Gunicorn for production:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎯 Usage Examples

### Text-to-Image Generation
1. Leave the image upload area empty
2. Enter a detailed description: *"A 3D rendered image of a pig with wings and a top hat flying over a futuristic sci-fi city with lots of greenery"*
3. Click "Generate Image"
4. View your AI-generated image

### Image Editing
1. Upload an existing image using drag & drop or file selection
2. Enter editing instructions: *"Make the background blue and add a rainbow"*
3. Click "Edit Image"
4. See your edited result

### Iterative Editing
1. After generating or editing an image, use the "Continue Editing" section
2. Enter new instructions to further modify the image
3. The AI maintains context from previous edits
4. View conversation history to see the complete editing journey

## 🌐 API Endpoints

### `POST /api/process-image`
Process image generation or editing requests.

**Request Body:**
```json
{
  "prompt": "Description of desired image or edits",
  "image": "data:image/png;base64,..." (optional),
  "history": [] (optional conversation history)
}
```

**Response:**
```json
{
  "success": true,
  "image": "data:image/png;base64,...",
  "description": "AI-generated description",
  "filename": "unique-filename.png"
}
```

## 📁 Project Structure

```
/
├── app.py                 # Main Flask application
├── main.py                # Application entry point
├── templates/
│   ├── base.html         # Base template with Bootstrap theme
│   ├── index.html        # Main application interface
│   └── result.html       # Legacy result view
├── static/
│   ├── uploads/          # Original uploaded images
│   └── results/          # Generated/edited images
└── README.md             # This documentation
```

## 🔧 Configuration

### Environment Variables
- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `SESSION_SECRET`: Flask session secret key (optional, defaults to dev key)

### File Upload Limits
- Maximum file size: 10MB
- Supported formats: PNG, JPG, JPEG, GIF, WebP
- Files are automatically organized in timestamped directories

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install flask google-genai werkzeug gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

## 🛠️ Troubleshooting

### Common Issues

1. **"No module named 'main'" Error**
   - Ensure `main.py` exists in the project root
   - Check that `main.py` imports from `app.py`

2. **Gemini API Errors**
   - Verify your `GEMINI_API_KEY` is set correctly
   - Check API quota and billing status
   - Ensure you're using a valid API key from Google AI Studio

3. **File Upload Issues**
   - Check file size is under 10MB
   - Verify file format is supported
   - Ensure sufficient disk space

4. **Session Issues**
   - Set a secure `SESSION_SECRET` environment variable
   - Clear browser cookies if experiencing persistent issues

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](./LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 🔗 Links

- [Google Gemini API Documentation](https://ai.google.dev/gemini-api/docs)
- [Get Gemini API Key](https://aistudio.google.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/)