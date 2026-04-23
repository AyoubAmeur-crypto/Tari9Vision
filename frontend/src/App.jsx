import React, { useState } from 'react';
import Cover from './components/Cover';
import Solution from './components/Solution';
import tvLogo from './assets/TV.png';
import './App.css';

function App() {
  const [showSolution, setShowSolution] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  React.useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <>
      <nav className="navbar" style={{
        background: isScrolled ? 'rgba(10, 16, 13, 0.60)' : 'transparent',
        backdropFilter: isScrolled ? 'blur(12px)' : 'none',
        borderBottom: isScrolled ? '1px solid rgba(255,255,255,0.1)' : 'none',
        boxShadow: isScrolled ? '0 4px 30px rgba(0, 0, 0, 0.2)' : 'none',
        transition: 'all 0.3s ease'
      }}>
        <div className="nav-brand" style={{ display: 'flex', alignItems: 'center' }}>
          <img src={tvLogo} alt="TV Logo" style={{ height: isScrolled ? '40px' : '50px', transition: 'height 0.3s ease' }} />
        </div>
        <button className="nav-cta" onClick={() => setShowSolution(!showSolution)}>
          {showSolution ? "Back" : "Open Studio"}
        </button>
      </nav>
      {showSolution ? (
        <Solution onBack={() => setShowSolution(false)} />
      ) : (
        <Cover onGetStarted={() => setShowSolution(true)} />
      )}
    </>
  );
}

export default App;
