# Hindi OCR + Hindi Q&A Generator

Turn images of Hindi text into extracted text and auto‑generated question–answer pairs. Frontend is a React app; backend is a Flask API with OCR and QA models.

— Fast start, clear results, Hindi-first.

## ✨ Features
- Hindi OCR from images (EasyOCR primary, Tesseract fallback)
- Text cleanup/normalization (IndicNLP)
- Auto question generation + extractive answers in Hindi
- REST API with JSON output and processing time
- Ready-to-run React UI for upload and results

## 🏗️ Architecture
```
[React (Vite) UI]
	 └── uploads image → POST /api/ocr
												 ↓
								 [Flask API]
									 ├─ OCR: EasyOCR → Tesseract (fallback)
									 ├─ Normalization (IndicNLP)
									 └─ QA: QG + QA models → Hindi Q&A pairs
												 ↓
										JSON { text, qa_pairs, processing_time }
```

Key files
- Backend
	- backend/app.py — Flask API (/api/health, /api/ocr)
	- backend/ocr/hindi_ocr.py — OCR pipeline and image preprocessing
	- backend/qa/question_answer.py — Hindi Q&A generation pipeline
	- backend/requirements.txt — Python deps
- Frontend
	- frontend/src/App.jsx — App state and API call
	- frontend/src/components/* — Upload, Spinner, Results
	- frontend/vite.config.js — Dev proxy to backend

## 🧰 Prerequisites
- Windows, macOS, or Linux
- Python 3.8+
- Node.js 18+ and npm
- Optional (for Tesseract fallback): Tesseract OCR installed and Hindi language data (hin)

Note: EasyOCR works out-of-the-box and is the default. Tesseract is only used as a fallback if present.

## 🚀 Quick Start (Local Dev)

Clone
```bash
git clone https://github.com/CyberMage7/Hindi-OCR.git
cd Hindi-OCR
```

### 1) Backend (Flask)
```bash
cd backend

# Create and activate a virtual env (Windows Git Bash)
python -m venv .venv
source .venv/Scripts/activate

# If using PowerShell instead:
# .venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt

# Run API
python app.py
# Serves at http://localhost:5000
```

First run may download model weights; allow some time.

### 2) Frontend (React + Vite)
Open a new terminal and run:
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

The frontend currently targets http://localhost:5000 directly (see `src/App.jsx`). Vite’s proxy is also configured if you later switch the frontend calls to a relative path like `/api/ocr`.

## 🖱️ Usage
1. In the UI, choose or drag-drop an image containing Hindi text (JPG/PNG/WebP/TIFF…).
2. Click upload; the app calls POST /api/ocr.
3. See extracted text and generated Hindi Q&A pairs.

## 📡 API Reference
POST /api/ocr
- Content-Type: multipart/form-data
- Fields:
	- image: file (required)

Response 200
```json
{
	"text": "निकाला गया हिंदी पाठ…",
	"qa_pairs": [
		{ "question": "प्रश्न…", "answer": "उत्तर…" }
	],
	"processing_time": "2.41 seconds"
}
```

Errors
- 400: Missing/invalid image
- 500: Processing error (message included)

Health check
- GET /api/health → { status: "ok" }

## ⚙️ Configuration Notes
- CORS allows http://localhost:5173 by default (see `backend/app.py`).
- Max upload size is 16 MB.
- Supported image types: png, jpg, jpeg, gif, bmp, tiff, webp.
- Tesseract (optional):
	- Install Tesseract and Hindi language data (hin).
	- On Windows, set TESSDATA_PREFIX if needed so pytesseract can find language data.

## 🧪 Tips & Troubleshooting
- First-time model downloads are large; keep the backend alive and connected to the internet.
- If OCR returns empty text:
	- Try a sharper image, higher contrast, or larger font.
	- Ensure the image actually contains Hindi script (Devanagari).
	- The API returns helpful fallback messages when no text is detected.
- If you hit CORS in dev:
	- Ensure backend is running on port 5000.
	- Keep frontend on http://localhost:5173 or adjust CORS origins in `backend/app.py`.
- If you prefer the Vite proxy:
	- Change the frontend request to a relative path `/api/ocr`.
	- Optionally set `VITE_API_URL` in a `.env` file for the dev server.

## 📂 Project Structure
```
backend/
	app.py
	requirements.txt
	ocr/hindi_ocr.py
	qa/question_answer.py
frontend/
	src/
		App.jsx
		components/
			UploadForm.jsx
			ResultDisplay.jsx
			LoadingSpinner.jsx
```

## 🙌 Acknowledgements
- EasyOCR, Tesseract OCR
- Hugging Face Transformers and Hindi QG/QA models
- IndicNLP Library

## 📄 License
This project is provided as-is for educational and research purposes. Add a LICENSE file to define terms for production use.

