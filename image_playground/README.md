# 🎨 Image Playground

Standalone image generation UI using Google Imagen 4.0. Simple Midjourney-style interface where you type a prompt and get AI-generated images.

## Features

✨ **Clean UI**: Simple, beautiful interface  
🎨 **Imagen 4.0**: High-quality AI image generation  
📐 **Multiple Aspect Ratios**: Square, landscape, portrait  
🖼️ **Batch Generation**: Generate up to 8 images at once  
💾 **Optional Download**: Download only the images you want  
🚀 **Fast**: ~10-30 seconds per image  

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   python app.py
   ```

3. **Open in browser:**
   ```
   http://localhost:5001
   ```

## Usage

1. **Enter a prompt** describing the image you want
2. **Choose aspect ratio** (1:1, 16:9, 9:16, 4:3, 3:4)
3. **Select number of images** (1-8)
4. **Click "Generate Image"**
5. **Wait 10-30 seconds** for Imagen to create your image
6. **View images** in browser
7. **Click download button** on images you want to keep (optional)

## Example Prompts

### Comic Book Style (Borderlands)
```
2D illustration, comic book art style, bold thick outlines, 
cell-shaded, Borderlands game aesthetic, 
character: cool detective wearing trench coat, 
background: noir city street at night, 
portrait view, waist-up composition
```

### Realistic Portrait
```
Professional portrait photograph, 
character: confident business executive, 
wearing elegant suit, modern office background,
natural lighting, high detail, photorealistic
```

### Fantasy Art
```
Digital painting, fantasy art style, 
character: mystical wizard with glowing staff,
background: enchanted forest with magical particles,
dramatic lighting, vibrant colors, full body view
```

## Tips for Better Results

- **Be specific**: Include art style, subject, colors, mood, and composition
- **Art styles**: "2D illustration", "comic book", "photorealistic", "watercolor"
- **Details matter**: "wearing leather jacket", "neon highlights", "dramatic lighting"
- **Composition**: "portrait view", "waist-up", "full body", "close-up"
- **Background**: "dark city street", "futuristic lab", "simple gradient"

## File Structure

```
image_playground/
├── app.py                    # Flask server + UI
├── requirements.txt          # Python dependencies
├── README.md                 # This file
└── generated_images/         # Output folder (auto-created)
    └── generated_*.png       # Your generated images
```

## Tech Stack

- **Backend**: Flask (Python web framework)
- **AI Model**: Google Imagen 4.0 (`imagen-4.0-generate-001`)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **API**: Google GenAI SDK

## Notes

- Uses your existing `GEMINI_API_KEY` from parent project
- All images are saved with timestamps
- Completely standalone - doesn't affect the main heist game
- No database required
- No authentication (local use only)

## Troubleshooting

**Port already in use?**
```bash
# Change port in app.py, line: app.run(port=5001)
```

**API key not found?**
- Make sure parent project has `.env` with `GEMINI_API_KEY`
- Or set it directly in `app.py`

**Images not generating?**
- Check API key is valid
- Check internet connection
- Look for error messages in terminal

---

Enjoy generating images! 🎨✨
