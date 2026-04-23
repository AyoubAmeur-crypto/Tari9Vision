import React, { useState, useRef } from 'react';

const Solution = ({ onBack }) => {
  const [file, setFile] = useState(null);
  const [model, setModel] = useState("YOLO");
  const [confidence, setConfidence] = useState(0.25);
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState(null);
  const [isHovered, setIsHovered] = useState(false);
  const [error, setError] = useState(null);
  
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsHovered(true);
  };

  const handleDragLeave = () => {
    setIsHovered(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsHovered(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile) => {
    setFile(selectedFile);
    setResultUrl(null); // reset old result
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', model);
    formData.append('confidence', confidence);

    try {
      const isVideo = file.type.startsWith('video');
      const endpoint = isVideo ? 'http://localhost:8000/api/analyze-video' : 'http://localhost:8000/api/analyze-image';
      
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error("API Error: " + response.statusText);

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setResultUrl(url);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="solution-container">
      <div className="dashboard-header">
        <h1>Damage Intelligence Studio</h1>
        <p>Upload infrastructure media for AI-driven segmentation & analysis.</p>
      </div>

      <div className="dashboard-grid">
        {/* Controls Sidebar */}
        <div className="controls">
          <div className="panel" style={{ marginBottom: '1.5rem' }}>
             <div className="form-group">
                <label>Target Media (Image/Video)</label>
                <div 
                  className={`file-drop-area ${isHovered ? 'drag-over' : ''}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
                >
                  <p>{file ? file.name : "Drag & drop or click to upload"}</p>
                  {!file && <span className="browse-btn">Browse Files</span>}
                  <input 
                     type="file" 
                     ref={fileInputRef} 
                     onChange={(e) => e.target.files && handleFileSelect(e.target.files[0])} 
                     accept="image/*,video/*"
                  />
                </div>
             </div>
          </div>

          <div className="panel">
            <div className="form-group">
              <label>AI Model Architecture</label>
              <select className="form-select" value={model} onChange={(e) => setModel(e.target.value)}>
                <option value="YOLO">YOLO Base (Fast)</option>
                <option value="YOLO + SAM">YOLO + SAM (High Precision)</option>
                <option value="YOLO + UNet">YOLO + UNet (Lightweight)</option>
                <option value="YOLO + DeepLab">YOLO + DeepLab (Semantic)</option>
              </select>
            </div>

            <div className="form-group">
              <label>Confidence Threshold <span className="val-display">{confidence}</span></label>
              <input 
                 type="range" 
                 className="form-range" 
                 min="0.1" max="1.0" step="0.05"
                 value={confidence} 
                 onChange={(e) => setConfidence(parseFloat(e.target.value))} 
              />
            </div>

            <button 
                className="action-btn" 
                onClick={handleAnalyze} 
                disabled={!file || loading}
            >
              {loading ? (
                <><div className="spinner" style={{width: 20, height: 20, borderWidth: 2}}></div> Processing...</>
              ) : "Execute Inference"}
            </button>
          </div>
        </div>

        {/* Display Area */}
        <div className="display-area">
            {error && <div className="notif" style={{color: 'red', borderColor: 'red'}}>{error}</div>}
            
            {loading ? (
               <div style={{textAlign: 'center'}}>
                  <div className="spinner" style={{margin: '0 auto 1rem auto'}}></div>
                  <p style={{color: 'var(--text-secondary)'}}>Running models, this may take a moment...</p>
               </div>
            ) : resultUrl ? (
               file && file.type.startsWith('video') ? (
                  <video src={resultUrl} className="result-media" controls autoPlay loop />
               ) : (
                  <img src={resultUrl} className="result-media" alt="Inference Result" />
               )
            ) : (
               <p className="empty-state">No inference active. Upload media to begin.</p>
            )}
        </div>
      </div>
    </div>
  );
};

export default Solution;
