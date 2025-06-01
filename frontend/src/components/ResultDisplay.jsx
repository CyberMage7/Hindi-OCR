import React, { useState } from 'react';
import './ResultDisplay.css';

const ResultDisplay = ({ extractedText, qaResults }) => {
  // State to track which answers are visible
  const [visibleAnswers, setVisibleAnswers] = useState({});

  const toggleAnswer = (index) => {
    setVisibleAnswers(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  return (
    <div className="result-display">
      <div className="section-container">
        <h2 className="section-title">Extracted Text</h2>
        <div className="extracted-text">
          {extractedText || <span className="no-text">No text detected</span>}
        </div>
      </div>

      {qaResults && qaResults.length > 0 ? (
        <div className="section-container">
          <h2 className="section-title">Generated Questions</h2>
          <div className="qa-list">
            {qaResults.map((pair, index) => (
              <div key={index} className="qa-item">
                <div className="question">
                  <span className="question-number">{index + 1}.</span>
                  <p>{pair.question}</p>
                </div>
                
                <div className="answer-container">
                  <button 
                    className="toggle-answer" 
                    onClick={() => toggleAnswer(index)}
                  >
                    {visibleAnswers[index] ? 'Hide Answer' : 'Show Answer'}
                  </button>
                  
                  {visibleAnswers[index] && (
                    <div className="answer">
                      <p>{pair.answer}</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        extractedText && (
          <div className="no-questions">
            <p>No questions could be generated from the extracted text.</p>
          </div>
        )
      )}
    </div>
  );
};

export default ResultDisplay;
