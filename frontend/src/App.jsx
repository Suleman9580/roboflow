import React, { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (data.error) {
        setError(data.error);
        setResult(null);
      } else {
        setResult(data);
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Failed to process image');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <div className="app-header">
        Dental X-ray Analyzer
      </div>
      <div className="container">
        <div className="left-panel">
          <form onSubmit={handleSubmit}>
            <input 
              type="file" 
              onChange={handleFileChange}
              accept=".dcm,.rvg"
            />
            <button type="submit" disabled={!file || loading}>
              {loading ? 'Processing...' : 'Analyze Image'}
            </button>
          </form>
          
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}
          
          {result && result.image && (
            <div className="image-container">
              <img 
                src={`data:image/png;base64,${result.image}`} 
                alt="Dental X-ray"
                style={{
                  maxWidth: '100%',
                  height: 'auto',
                  marginTop: '20px'
                }}
              />
            </div>
          )}
        </div>

        <div className="right-panel">
          {result && result.report && (
            <div className="report">
              <h2>Diagnostic Report</h2>
              <pre>{result.report}</pre>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default App;