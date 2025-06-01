import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = () => {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p className="loading-text">Processing your image...</p>
      <p className="loading-subtext">This may take a minute for large images or complex text</p>
    </div>
  );
};

export default LoadingSpinner;
