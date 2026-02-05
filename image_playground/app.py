#!/usr/bin/env python3
"""
Standalone Image Generation Playground
Simple UI to generate images using Google Imagen 4.0
"""
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from google import genai
from google.genai import types
import os
import sys
from pathlib import Path
from datetime import datetime
import base64
from io import BytesIO
import tempfile

# Add parent scripts directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from config import GEMINI_API_KEY

app = Flask(__name__)
CORS(app)

# Create output directory
OUTPUT_DIR = Path(__file__).parent / 'generated_images'
OUTPUT_DIR.mkdir(exist_ok=True)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Playground - Imagen 4.0</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        h1 {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.9);
            text-align: center;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        }
        
        .input-section {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            resize: vertical;
            transition: border-color 0.3s;
        }
        
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .controls {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        
        .control-group {
            flex: 1;
            min-width: 200px;
        }
        
        select, input[type="number"] {
            width: 100%;
            padding: 10px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            background: white;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            width: 100%;
        }
        
        button:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 18px;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .result {
            margin-top: 30px;
        }
        
        .image-container {
            text-align: center;
            margin: 20px 0;
        }
        
        .generated-image {
            max-width: 100%;
            height: auto;
            border-radius: 12px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
        }
        
        .error {
            background: #fee;
            border: 2px solid #fcc;
            border-radius: 8px;
            padding: 15px;
            color: #c33;
            margin-top: 20px;
        }
        
        .tips {
            background: #f0f4ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        }
        
        .tips h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .tips ul {
            padding-left: 20px;
        }
        
        .tips li {
            margin-bottom: 5px;
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Image Playground</h1>
        <p class="subtitle">Generate images with Google Imagen 4.0</p>
        
        <div class="card">
            <div class="input-section">
                <label for="prompt">Image Description</label>
                <textarea 
                    id="prompt" 
                    placeholder="Describe the image you want to generate...&#10;&#10;Example: character: cool detective wearing trench coat, background: noir city street at night, portrait view, waist-up composition"
                >character: cool detective wearing trench coat, background: noir city street at night, portrait view, waist-up composition</textarea>
            </div>
            
            <div class="controls">
                <div class="control-group">
                    <label for="art-style">Art Style</label>
                    <select id="art-style">
                        <option value="none">None (Your prompt only)</option>
                        <option value="borderlands">Borderlands / Comic Book</option>
                        <option value="realistic">Photorealistic</option>
                        <option value="anime">Anime</option>
                        <option value="watercolor">Watercolor</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="aspect-ratio">Aspect Ratio</label>
                    <select id="aspect-ratio">
                        <option value="1:1" selected>Square (1:1)</option>
                        <option value="16:9">Landscape (16:9)</option>
                        <option value="9:16">Portrait (9:16)</option>
                        <option value="4:3">Standard (4:3)</option>
                        <option value="3:4">Portrait (3:4)</option>
                    </select>
                </div>
                
                <div class="control-group">
                    <label for="num-images">Number of Images</label>
                    <input type="number" id="num-images" min="1" max="8" value="1">
                </div>
            </div>
            
            <button id="generate-btn" onclick="generateImage()">
                Generate Image
            </button>
            
            <div id="loading" class="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Generating your image with Imagen 4.0...</p>
                <p style="color: #999; font-size: 14px; margin-top: 10px;">This may take 10-30 seconds</p>
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
            
            <div id="result" class="result" style="display: none;"></div>
        </div>
        
        <div class="card tips">
            <h3>💡 Tips for Better Results</h3>
            <ul>
                <li><strong>Choose a style:</strong> Select from dropdown or use "None" for full control</li>
                <li><strong>Be specific:</strong> Include subject, clothing, colors, mood, and composition</li>
                <li><strong>Details matter:</strong> "wearing leather jacket", "neon highlights", "dramatic lighting"</li>
                <li><strong>Composition:</strong> "portrait view", "waist-up", "full body", "close-up"</li>
                <li><strong>Background:</strong> "dark city street", "futuristic lab", "simple gradient"</li>
                <li><strong>Borderlands style:</strong> Great for game characters, comic book heroes</li>
                <li><strong>Realistic style:</strong> Perfect for portraits, product photos, realistic scenes</li>
            </ul>
        </div>
    </div>
    
    <script>
        async function generateImage() {
            const prompt = document.getElementById('prompt').value.trim();
            const artStyle = document.getElementById('art-style').value;
            const aspectRatio = document.getElementById('aspect-ratio').value;
            const numImages = parseInt(document.getElementById('num-images').value);
            
            if (!prompt) {
                alert('Please enter a prompt!');
                return;
            }
            
            // UI state
            document.getElementById('generate-btn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        prompt: prompt,
                        art_style: artStyle,
                        aspect_ratio: aspectRatio,
                        num_images: numImages
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    displayResults(data.images);
                } else {
                    showError(data.error || 'Failed to generate image');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('generate-btn').disabled = false;
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(images) {
            const resultDiv = document.getElementById('result');
            resultDiv.innerHTML = '';
            
            images.forEach((imageData) => {
                const container = document.createElement('div');
                container.className = 'image-container';
                
                const img = document.createElement('img');
                img.src = 'data:image/png;base64,' + imageData.base64;
                img.className = 'generated-image';
                img.alt = 'Generated image ' + imageData.index;
                
                const downloadBtn = document.createElement('button');
                downloadBtn.textContent = '⬇️ Download Image ' + imageData.index;
                downloadBtn.style.marginTop = '15px';
                downloadBtn.style.padding = '10px 20px';
                downloadBtn.onclick = () => downloadImage(imageData.base64, imageData.index);
                
                container.appendChild(img);
                container.appendChild(downloadBtn);
                resultDiv.appendChild(container);
            });
            
            resultDiv.style.display = 'block';
        }
        
        function downloadImage(base64Data, index) {
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + base64Data;
            link.download = 'generated_image_' + index + '.png';
            link.click();
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = '❌ Error: ' + message;
            errorDiv.style.display = 'block';
        }
        
        // Allow Enter key to submit (with Shift+Enter for new line)
        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                generateImage();
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    """Generate image using Imagen 4.0"""
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        aspect_ratio = data.get('aspect_ratio', '1:1')
        num_images = min(int(data.get('num_images', 1)), 8)
        art_style = data.get('art_style', 'none')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Apply art style prefix if selected
        if art_style == 'borderlands':
            style_prefix = """2D illustration, comic book art style, bold thick outlines, 
cell-shaded, flat colors with subtle gradients, Borderlands game aesthetic, 
graphic novel style, vibrant saturated colors, stylized proportions, 
hand-drawn look, inked linework, simplified details, expressive characters, 
set in year 2020, contemporary clothing and technology (not futuristic), """
            prompt = style_prefix + prompt
        elif art_style == 'realistic':
            style_prefix = "Photorealistic, high detail, professional photography, natural lighting, "
            prompt = style_prefix + prompt
        elif art_style == 'anime':
            style_prefix = "Anime art style, detailed illustration, vibrant colors, expressive, "
            prompt = style_prefix + prompt
        elif art_style == 'watercolor':
            style_prefix = "Watercolor painting, soft colors, artistic brushstrokes, gentle aesthetic, "
            prompt = style_prefix + prompt
        
        print(f"🎨 Generating {num_images} image(s)...")
        print(f"🎭 Style: {art_style}")
        print(f"📝 Prompt: {prompt}")
        print(f"📐 Aspect ratio: {aspect_ratio}")
        
        # Create Gemini client
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        # Generate images with Imagen 4.0
        config = types.GenerateImagesConfig(
            number_of_images=num_images,
            aspect_ratio=aspect_ratio,
            safety_filter_level='block_low_and_above',
            person_generation='allow_adult'
        )
        
        response = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=config
        )
        
        # Convert images to base64 (no disk saving)
        results = []
        
        for i, generated_image in enumerate(response.generated_images):
            # Save to temporary BytesIO to get PNG bytes
            # The genai Image object has a save() method that takes a file path
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp_path = tmp.name
            
            # Save image to temp file
            generated_image.image.save(tmp_path)
            
            # Read back as bytes
            with open(tmp_path, 'rb') as f:
                image_bytes = f.read()
            
            # Clean up temp file
            os.unlink(tmp_path)
            
            # Convert to base64 for display
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            results.append({
                'index': i + 1,
                'base64': image_base64
            })
            
            print(f"✅ Generated image {i+1}/{num_images}")
        
        return jsonify({
            'success': True,
            'images': results
        })
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500

# Removed - images are not saved to disk anymore

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  🎨 IMAGE PLAYGROUND - Imagen 4.0")
    print("="*60)
    print(f"\n🌐 Open in browser: http://localhost:5001")
    print(f"\n💡 Images are displayed in browser (not saved to disk)")
    print(f"   Click download button to save images you like")
    print("\n" + "="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
