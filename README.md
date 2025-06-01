# Hindi-OCR with Question-Answering

## Overview
This project combines Hindi OCR (Optical Character Recognition) with a question-answering system. It can extract text from Hindi documents/images and generate relevant question-answer pairs from the extracted content.

## Features
- Hindi text recognition from images
- Text normalization using IndicNLP
- Automatic question generation from Hindi text
- Question-answering based on the extracted content

## Installation Requirements
- Python 3.8+
- PyTorch
- Hugging Face Transformers
- IndicNLP
- Other dependencies in requirements.txt

## Setup

### Clone the repository
```
git clone https://github.com/yourusername/Hindi-OCR.git
cd Hindi-OCR
```
## Running the Backend
Navigate to the `backend` directory and run the following command:
```
cd backend
```
### 1. Create a virtual environment (optional but recommended)
```
python -m venv hindiocr
```
### 2. Activate the virtual environment
```
hindiocr\Scripts\activate
```
### 3. Install dependencies
```
pip install -r requirements.txt
```
### 4. Run the Flask server
```
python app.py
```
The server will start on `http://localhost:5000`.

## Running the Frontend
**Note**: The frontend is built using React. Make sure you have Node.js and npm installed.

Navigate to the `frontend` directory and run the following command:
```
cd frontend
```
### 1. Install dependencies
```
npm install
```
### 2. Start the React app
```
npm run dev
```
The app will open in your default web browser at `http://localhost:5173`.
## Usage
1. Upload a Hindi document/image using the frontend interface.
2. The OCR will extract the text from the image.
3. The extracted text will be normalized and processed to generate question-answer pairs.
4. The question-answer pairs will be displayed on the frontend.
