#!/usr/bin/env python3
"""
Image Generation Playground
Test different image generation models side-by-side.
Supports: Qwen-Image (DashScope), Google Imagen, Gemini Flash Image
"""
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import os
import sys
import json
import requests
import base64
import hashlib
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Add parent scripts directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'scripts'))

# Load .env from project root (must run at import time for flask run / debugger)
try:
    from dotenv import load_dotenv
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
except Exception:
    pass

app = Flask(__name__)
CORS(app)

OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)
METADATA_FILE = OUTPUT_DIR / 'metadata.json'

# ---------------------------------------------------------------------------
# Model registry
# ---------------------------------------------------------------------------

MODELS = {
    "qwen-image-max": {
        "label": "Qwen-Image Max",
        "provider": "dashscope",
        "model_id": "qwen-image-max",
        "sizes": {
            "1:1":  "1328*1328",
            "16:9": "1664*928",
            "9:16": "928*1664",
            "4:3":  "1472*1104",
            "3:4":  "1104*1472",
        },
    },
    "qwen-image-plus": {
        "label": "Qwen-Image Plus",
        "provider": "dashscope",
        "model_id": "qwen-image-plus",
        "sizes": {
            "1:1":  "1328*1328",
            "16:9": "1664*928",
            "9:16": "928*1664",
            "4:3":  "1472*1104",
            "3:4":  "1104*1472",
        },
    },
    "wan2.6-t2i": {
        "label": "Wan 2.6 T2I",
        "provider": "dashscope",
        "model_id": "wan2.6-t2i",
        "sizes": {
            "1:1":  "1280*1280",
            "16:9": "1696*960",
            "9:16": "960*1696",
            "4:3":  "1472*1104",
            "3:4":  "1104*1472",
        },
    },
    "imagen-4.0": {
        "label": "Google Imagen 4.0",
        "provider": "google",
        "model_id": "imagen-4.0-generate-001",
    },
    "gemini-2.5-flash-image": {
        "label": "Gemini 2.5 Flash Image",
        "provider": "gemini-flash",
        "model_id": "gemini-2.5-flash-preview-image-generation",
    },
}

# ---------------------------------------------------------------------------
# Metadata helpers
# ---------------------------------------------------------------------------

def load_metadata():
    if METADATA_FILE.exists():
        return json.loads(METADATA_FILE.read_text())
    return []


def save_metadata(entries):
    METADATA_FILE.write_text(json.dumps(entries, indent=2))


def add_entry(filename, prompt, model, aspect_ratio, elapsed_sec):
    entries = load_metadata()
    entries.insert(0, {
        "filename": filename,
        "prompt": prompt,
        "model": model,
        "aspect_ratio": aspect_ratio,
        "elapsed_sec": round(elapsed_sec, 1),
        "created_at": datetime.now().isoformat(),
    })
    save_metadata(entries)

# ---------------------------------------------------------------------------
# Generation backends
# ---------------------------------------------------------------------------

DASHSCOPE_ENDPOINTS = {
    "us":        "https://dashscope-us.aliyuncs.com/api/v1",
    "singapore": "https://dashscope-intl.aliyuncs.com/api/v1",
    "beijing":   "https://dashscope.aliyuncs.com/api/v1",
}


def generate_dashscope(model_cfg, prompt, aspect_ratio, negative_prompt, region="us"):
    """Generate via Alibaba DashScope (Qwen-Image) HTTP API."""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not set in environment / .env")

    size = model_cfg["sizes"].get(aspect_ratio, "1328*1328")
    base = DASHSCOPE_ENDPOINTS.get(region, DASHSCOPE_ENDPOINTS["us"])
    url = f"{base}/services/aigc/multimodal-generation/generation"

    payload = {
        "model": model_cfg["model_id"],
        "input": {
            "messages": [{"role": "user", "content": [{"text": prompt}]}]
        },
        "parameters": {
            "size": size,
            "prompt_extend": True,
            "watermark": False,
        },
    }
    if negative_prompt:
        payload["parameters"]["negative_prompt"] = negative_prompt

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    print(f"  DashScope URL: {url}")
    print(f"  DashScope model: {model_cfg['model_id']}")
    print(f"  DashScope region: {region}")
    print(f"  API key prefix: {api_key[:12]}...")

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    data = resp.json()

    print(f"  Response status: {resp.status_code}")
    print(f"  Response body: {json.dumps(data, indent=2)[:500]}")

    if resp.status_code != 200 or "output" not in data:
        err = data.get("message") or data.get("code") or str(data)
        raise RuntimeError(f"DashScope error ({resp.status_code}): {err}")

    image_url = data["output"]["choices"][0]["message"]["content"][0]["image"]
    img_resp = requests.get(image_url, timeout=60)
    img_resp.raise_for_status()
    return img_resp.content


def generate_google_imagen(prompt, aspect_ratio):
    """Generate via Google Imagen 4.0."""
    from google import genai
    from google.genai import types

    api_key = _get_gemini_key()
    client = genai.Client(api_key=api_key)

    config = types.GenerateImagesConfig(
        number_of_images=1,
        aspect_ratio=aspect_ratio,
        safety_filter_level="block_low_and_above",
        person_generation="allow_adult",
    )
    response = client.models.generate_images(
        model="imagen-4.0-generate-001",
        prompt=prompt,
        config=config,
    )
    img = response.generated_images[0].image
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp_path = tmp.name
    img.save(tmp_path)
    with open(tmp_path, "rb") as f:
        data = f.read()
    os.unlink(tmp_path)
    return data


def generate_gemini_flash(prompt, aspect_ratio):
    """Generate via Gemini 2.5 Flash Image Generation."""
    from google import genai
    from google.genai import types

    api_key = _get_gemini_key()
    client = genai.Client(api_key=api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data and part.inline_data.mime_type.startswith("image/"):
            return part.inline_data.data
    raise RuntimeError("Gemini Flash did not return an image")


def _get_gemini_key():
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        try:
            from config import GEMINI_API_KEY
            key = GEMINI_API_KEY
        except Exception:
            pass
    if not key:
        raise ValueError("GEMINI_API_KEY not set")
    return key

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, models=MODELS)


@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.json
        prompt = data.get("prompt", "").strip()
        model_key = data.get("model", "qwen-image-max")
        aspect_ratio = data.get("aspect_ratio", "1:1")
        negative_prompt = data.get("negative_prompt", "").strip()
        region = data.get("region", "singapore")

        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400

        model_cfg = MODELS.get(model_key)
        if not model_cfg:
            return jsonify({"error": f"Unknown model: {model_key}"}), 400

        print(f"\n{'='*60}")
        print(f"  Model: {model_cfg['label']}")
        print(f"  Aspect: {aspect_ratio}")
        print(f"  Prompt: {prompt[:120]}...")
        print(f"{'='*60}")

        import time
        t0 = time.time()

        provider = model_cfg["provider"]
        if provider == "dashscope":
            image_bytes = generate_dashscope(model_cfg, prompt, aspect_ratio, negative_prompt, region)
        elif provider == "google":
            image_bytes = generate_google_imagen(prompt, aspect_ratio)
        elif provider == "gemini-flash":
            image_bytes = generate_gemini_flash(prompt, aspect_ratio)
        else:
            return jsonify({"error": f"Unknown provider: {provider}"}), 400

        elapsed = time.time() - t0

        # Save to output/
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        short_hash = hashlib.md5(prompt.encode()).hexdigest()[:6]
        filename = f"{ts}_{model_key}_{short_hash}.png"
        filepath = OUTPUT_DIR / filename
        filepath.write_bytes(image_bytes)

        add_entry(filename, prompt, model_key, aspect_ratio, elapsed)

        b64 = base64.b64encode(image_bytes).decode("utf-8")
        print(f"  Done in {elapsed:.1f}s  ->  {filename}")

        return jsonify({
            "success": True,
            "image_base64": b64,
            "filename": filename,
            "elapsed_sec": round(elapsed, 1),
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/images")
def list_images():
    """Return metadata + base64 thumbnails for the feed."""
    entries = load_metadata()
    return jsonify(entries)


@app.route("/images/<filename>")
def serve_image(filename):
    filepath = OUTPUT_DIR / filename
    if not filepath.exists():
        return "Not found", 404
    return send_file(filepath, mimetype="image/png")


@app.route("/images/<filename>", methods=["DELETE"])
def delete_image(filename):
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        filepath.unlink()
    entries = load_metadata()
    entries = [e for e in entries if e["filename"] != filename]
    save_metadata(entries)
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Playground</title>
    <style>
        :root {
            --bg: #0f1117;
            --surface: #1a1d27;
            --surface2: #242736;
            --border: #2e3144;
            --text: #e4e4e7;
            --text2: #9ca3af;
            --accent: #6366f1;
            --accent-hover: #818cf8;
            --danger: #ef4444;
            --success: #22c55e;
            --radius: 10px;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .layout {
            display: grid;
            grid-template-columns: 420px 1fr;
            height: 100vh;
        }

        /* --- Sidebar --- */
        .sidebar {
            background: var(--surface);
            border-right: 1px solid var(--border);
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            overflow-y: auto;
        }
        .sidebar h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .sidebar h1 span { font-size: 0.8rem; font-weight: 400; color: var(--text2); -webkit-text-fill-color: var(--text2); display: block; margin-top: 2px; }

        label { font-size: 0.82rem; font-weight: 600; color: var(--text2); text-transform: uppercase; letter-spacing: 0.05em; display: block; margin-bottom: 6px; }
        textarea, select, input[type="text"] {
            width: 100%;
            padding: 10px 12px;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            color: var(--text);
            font-size: 0.95rem;
            font-family: inherit;
        }
        textarea { min-height: 120px; resize: vertical; }
        textarea:focus, select:focus, input:focus { outline: none; border-color: var(--accent); }
        select { cursor: pointer; }

        .row { display: flex; gap: 12px; }
        .row > * { flex: 1; }

        .generate-btn {
            background: var(--accent);
            color: white;
            border: none;
            padding: 14px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: var(--radius);
            cursor: pointer;
            transition: background 0.2s;
            position: relative;
        }
        .generate-btn:hover:not(:disabled) { background: var(--accent-hover); }
        .generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

        .status { font-size: 0.85rem; color: var(--text2); text-align: center; min-height: 1.2em; }
        .status.error { color: var(--danger); }
        .status.ok { color: var(--success); }

        .neg-toggle { font-size: 0.82rem; color: var(--accent); cursor: pointer; user-select: none; }
        .neg-toggle:hover { text-decoration: underline; }
        .neg-section { display: none; }
        .neg-section.open { display: block; }

        /* --- Feed --- */
        .feed {
            padding: 24px;
            overflow-y: auto;
        }
        .feed-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .feed-header h2 { font-size: 1.2rem; color: var(--text2); }
        .feed-count { font-size: 0.85rem; color: var(--text2); }

        .feed-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
            gap: 16px;
        }
        .feed-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
            transition: border-color 0.2s;
        }
        .feed-card:hover { border-color: var(--accent); }
        .feed-card img {
            width: 100%;
            display: block;
            cursor: pointer;
        }
        .feed-card-info {
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }
        .feed-card-prompt {
            font-size: 0.85rem;
            color: var(--text);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .feed-card-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--text2);
        }
        .badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 999px;
            font-size: 0.7rem;
            font-weight: 600;
            background: var(--surface2);
            border: 1px solid var(--border);
        }
        .feed-card-actions {
            display: flex;
            gap: 8px;
            padding: 0 12px 12px;
        }
        .feed-card-actions button {
            flex: 1;
            padding: 6px;
            font-size: 0.78rem;
            border-radius: 6px;
            border: 1px solid var(--border);
            background: var(--surface2);
            color: var(--text2);
            cursor: pointer;
        }
        .feed-card-actions button:hover { border-color: var(--accent); color: var(--text); }
        .feed-card-actions button.del:hover { border-color: var(--danger); color: var(--danger); }

        .empty-feed {
            text-align: center;
            padding: 80px 20px;
            color: var(--text2);
        }
        .empty-feed p { margin-top: 8px; font-size: 0.9rem; }

        /* Lightbox */
        .lightbox {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.85);
            z-index: 1000;
            align-items: center;
            justify-content: center;
            cursor: zoom-out;
        }
        .lightbox.open { display: flex; }
        .lightbox img {
            max-width: 90vw;
            max-height: 90vh;
            border-radius: var(--radius);
        }

        /* Spinner */
        @keyframes spin { to { transform: rotate(360deg); } }
        .spinner {
            display: inline-block;
            width: 18px; height: 18px;
            border: 2px solid transparent;
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
            vertical-align: middle;
            margin-right: 8px;
        }

        @media (max-width: 900px) {
            .layout { grid-template-columns: 1fr; }
            .sidebar { max-height: 50vh; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <div class="sidebar">
            <h1>Image Playground <span>Multi-model image generation</span></h1>

            <div>
                <label>Prompt</label>
                <textarea id="prompt" placeholder="Describe the image you want to generate..."></textarea>
            </div>

            <div class="row">
                <div>
                    <label>Model</label>
                    <select id="model">
                        <option value="qwen-image-max">Qwen-Image Max</option>
                        <option value="qwen-image-plus">Qwen-Image Plus</option>
                        <option value="wan2.6-t2i">Wan 2.6 T2I</option>
                        <option value="imagen-4.0">Google Imagen 4.0</option>
                        <option value="gemini-2.5-flash-image">Gemini 2.5 Flash Image</option>
                    </select>
                </div>
                <div>
                    <label>Aspect Ratio</label>
                    <select id="aspect-ratio">
                        <option value="1:1">1:1 Square</option>
                        <option value="16:9">16:9 Landscape</option>
                        <option value="9:16">9:16 Portrait</option>
                        <option value="4:3">4:3 Standard</option>
                        <option value="3:4">3:4 Portrait</option>
                    </select>
                </div>
            </div>

            <div id="region-row" class="row">
                <div>
                    <label>DashScope Region</label>
                    <select id="region">
                        <option value="singapore" selected>Singapore</option>
                        <option value="us">US (Virginia)</option>
                        <option value="beijing">China (Beijing)</option>
                    </select>
                </div>
            </div>

            <div>
                <span class="neg-toggle" onclick="toggleNeg()">+ Negative prompt</span>
                <div id="neg-section" class="neg-section">
                    <textarea id="negative-prompt" rows="2" placeholder="Things to avoid..."></textarea>
                </div>
            </div>

            <button class="generate-btn" id="gen-btn" onclick="generate()">Generate</button>
            <div class="status" id="status"></div>
        </div>

        <div class="feed" id="feed">
            <div class="feed-header">
                <h2>Generated Images</h2>
                <span class="feed-count" id="feed-count"></span>
            </div>
            <div class="feed-grid" id="feed-grid"></div>
            <div class="empty-feed" id="empty-feed">
                <p style="font-size:2rem;">No images yet</p>
                <p>Generate your first image using the controls on the left.</p>
            </div>
        </div>
    </div>

    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <img id="lightbox-img" src="" alt="Full size" />
    </div>

    <script>
        let feedData = [];

        function toggleNeg() {
            document.getElementById('neg-section').classList.toggle('open');
        }

        function setStatus(msg, type) {
            const el = document.getElementById('status');
            el.textContent = msg;
            el.className = 'status ' + (type || '');
        }

        async function generate() {
            const prompt = document.getElementById('prompt').value.trim();
            if (!prompt) { setStatus('Enter a prompt first', 'error'); return; }

            const btn = document.getElementById('gen-btn');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Generating...';
            setStatus('');

            try {
                const resp = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        prompt,
                        model: document.getElementById('model').value,
                        aspect_ratio: document.getElementById('aspect-ratio').value,
                        negative_prompt: document.getElementById('negative-prompt').value.trim(),
                        region: document.getElementById('region').value,
                    })
                });
                const data = await resp.json();
                if (!resp.ok) throw new Error(data.error || 'Generation failed');

                setStatus(`Done in ${data.elapsed_sec}s`, 'ok');
                loadFeed();
            } catch (e) {
                setStatus(e.message, 'error');
            } finally {
                btn.disabled = false;
                btn.textContent = 'Generate';
            }
        }

        async function loadFeed() {
            const resp = await fetch('/images');
            feedData = await resp.json();
            renderFeed();
        }

        function renderFeed() {
            const grid = document.getElementById('feed-grid');
            const empty = document.getElementById('empty-feed');
            const count = document.getElementById('feed-count');

            if (!feedData.length) {
                grid.innerHTML = '';
                empty.style.display = 'block';
                count.textContent = '';
                return;
            }

            empty.style.display = 'none';
            count.textContent = feedData.length + ' image' + (feedData.length !== 1 ? 's' : '');

            grid.innerHTML = feedData.map(entry => {
                const time = new Date(entry.created_at).toLocaleString();
                return `
                <div class="feed-card">
                    <img src="/images/${entry.filename}" alt="" loading="lazy" onclick="openLightbox('/images/${entry.filename}')" />
                    <div class="feed-card-info">
                        <div class="feed-card-prompt" title="${esc(entry.prompt)}">${esc(entry.prompt)}</div>
                        <div class="feed-card-meta">
                            <span><span class="badge">${esc(entry.model)}</span> &nbsp; ${entry.aspect_ratio} &nbsp; ${entry.elapsed_sec}s</span>
                            <span>${time}</span>
                        </div>
                    </div>
                    <div class="feed-card-actions">
                        <button onclick="downloadImg('${entry.filename}')">Download</button>
                        <button onclick="reusePrompt('${esc(entry.prompt)}')" title="Copy prompt back">Reuse</button>
                        <button class="del" onclick="deleteImg('${entry.filename}')">Delete</button>
                    </div>
                </div>`;
            }).join('');
        }

        function esc(s) { return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#39;'); }

        function openLightbox(src) {
            document.getElementById('lightbox-img').src = src;
            document.getElementById('lightbox').classList.add('open');
        }
        function closeLightbox() { document.getElementById('lightbox').classList.remove('open'); }

        function downloadImg(filename) {
            const a = document.createElement('a');
            a.href = '/images/' + filename;
            a.download = filename;
            a.click();
        }

        function reusePrompt(prompt) {
            document.getElementById('prompt').value = prompt.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'");
            document.getElementById('prompt').focus();
        }

        async function deleteImg(filename) {
            if (!confirm('Delete this image?')) return;
            await fetch('/images/' + filename, { method: 'DELETE' });
            loadFeed();
        }

        document.getElementById('prompt').addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                e.preventDefault();
                generate();
            }
        });

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeLightbox();
        });

        function updateRegionVisibility() {
            const model = document.getElementById('model').value;
            const isQwen = model.startsWith('qwen-') || model.startsWith('wan');
            document.getElementById('region-row').style.display = isQwen ? 'flex' : 'none';
        }
        document.getElementById('model').addEventListener('change', updateRegionVisibility);
        updateRegionVisibility();

        loadFeed();
    </script>
</body>
</html>
"""

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  IMAGE PLAYGROUND")
    print("=" * 60)
    print(f"\n  Open in browser: http://localhost:5001")
    print(f"  Images saved to: {OUTPUT_DIR}")
    print(f"\n  Models available:")
    for k, v in MODELS.items():
        print(f"    - {v['label']} ({k})")
    print("\n" + "=" * 60 + "\n")

    app.run(host="0.0.0.0", port=5001, debug=True)
