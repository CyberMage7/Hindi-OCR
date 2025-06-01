import React, { useState } from 'react';
import './App.css';
import UploadForm from './components/UploadForm';
import ResultDisplay from './components/ResultDisplay';
import LoadingSpinner from './components/LoadingSpinner';
import axios from 'axios';

const API_URL = 'http://localhost:5000';

function App() {
  const [extractedText, setExtractedText] = useState('');
  const [qaResults, setQaResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const processImage = async (imageFile) => {
    setLoading(true);
    setError('');
    setExtractedText('');
    setQaResults([]);

    const formData = new FormData();
    formData.append('image', imageFile);

    try {
      const response = await axios.post(`${API_URL}/api/ocr`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      if (response.data) {
        setExtractedText(response.data.text);
        setQaResults(response.data.qa_pairs);
      }
    } catch (err) {
      console.error('Error processing image:', err);
      setError('Error processing image. Please try again with a different image.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Hindi OCR & Question Generation</h1>
        <p>Upload an image with Hindi text to extract content and generate questions</p>
      </header>

      <main className="app-main">
        <UploadForm onImageSubmit={processImage} />

        {loading && <LoadingSpinner />}

        {error && <div className="error-message">{error}</div>}

        {!loading && extractedText && (
          <ResultDisplay 
            extractedText={extractedText} 
            qaResults={qaResults} 
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Built with React, Flask, and Neural Networks</p>
      </footer>
    </div>
  );
}

export default App;
