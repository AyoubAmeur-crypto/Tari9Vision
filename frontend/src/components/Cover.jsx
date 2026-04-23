import React from 'react';
import { Crosshair, Server, LayoutDashboard, ArrowRight, ShieldCheck, Zap } from 'lucide-react';
import natureImg from '../assets/nature.jpg';
import roadAnalysisImg from '../assets/road_analysis.png';
import tvLogo from '../assets/TV.png';

const Cover = ({ onGetStarted }) => {
    return (
        <div style={{ width: '100%', display: 'flex', flexDirection: 'column', backgroundColor: 'var(--black)' }}>

            {/* Section 1: Hero Banner */}
            <div className="cover-container" style={{
                backgroundImage: `url(${natureImg})`,
                backgroundSize: 'cover',
                backgroundPosition: 'center',
                minHeight: '100vh',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'flex-start',
                padding: '0 5rem',
                position: 'relative',
                width: '100%',
                margin: 0
            }}>
                <div style={{ borderLeft: '4px solid white', paddingLeft: '2rem', marginTop: '-4rem', alignSelf: 'flex-start' }}>
                    <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '5rem', fontWeight: 600, lineHeight: 1.1, letterSpacing: '2px', color: 'white', margin: 0, textAlign: 'left' }}>
                        Turning<br />Road Data<br />Into Action.
                    </h1>
                </div>

                <div style={{ marginTop: '3rem', marginLeft: '2rem' }}>
                    <button
                        onClick={onGetStarted}
                        style={{ backgroundColor: 'var(--accent)', color: 'var(--surface)', border: 'none', padding: '1rem 2.5rem', borderRadius: '50px', fontSize: '1.2rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', transition: 'all 0.3s ease' }}
                        onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 10px 20px rgba(16, 185, 129, 0.4)'; }}
                        onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}
                    >
                        Launch Studio <ArrowRight size={20} />
                    </button>
                </div>

                <div style={{ position: 'absolute', bottom: '8%', left: '5rem', display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '5px' }}>
                    <div style={{ background: '#0a100d', padding: '12px 24px', width: 'fit-content' }}>
                        <p style={{ color: '#FAFAFA', fontWeight: 600, letterSpacing: '1px', fontSize: '0.9rem', margin: 0, textAlign: 'left' }}>AI THAT SEES EVERY CRACK</p>
                    </div>
                    <div style={{ background: '#0a100d', padding: '12px 24px', width: 'fit-content' }}>
                        <p style={{ color: '#D4D4D8', fontSize: '0.9rem', margin: 0, textAlign: 'left' }}>The First AI Road Damage Detection Platform in Morocco</p>
                    </div>
                </div>
            </div>

            {/* Section 2: Clean White Background Block */}
            <div style={{ backgroundColor: '#ffffff', color: '#09090b', padding: '8rem 5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '2.5rem', marginBottom: '3rem', width: '100%' }}>
                    <img src={tvLogo} alt="Tari9 Vision" style={{ height: '200px', filter: 'brightness(0)', opacity: 0.85 }} />
                    <div style={{ width: '3px', height: '140px', backgroundColor: '#09090b', opacity: 1 }}></div>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', textAlign: 'left', fontWeight: 700, margin: 0, letterSpacing: '-1px', lineHeight: 1.2 }}>Uncompromising<br />Clarity.</h2>
                </div>
                <p style={{ fontSize: '1.2rem', maxWidth: '800px', lineHeight: 1.6, marginBottom: '4rem', color: '#52525b' }}>
                    Replace slow manual inspections with rapid, automated computer vision. We bring phenomenal precision to state infrastructure operations, pinpointing deep infrastructural degradation precisely before it transforms into a multi-million-dollar hazard.
                </p>

                <div style={{ display: 'flex', gap: '3rem', justifyContent: 'center', flexWrap: 'wrap', maxWidth: '1200px', marginBottom: '4rem' }}>
                    <div style={{ flex: '1 1 300px', textAlign: 'left', padding: '2.5rem', borderRadius: '16px', backgroundColor: '#f4f4f5' }}>
                        <ShieldCheck size={40} color="#10B981" style={{ marginBottom: '1.5rem' }} />
                        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem' }}>Safety Compliant</h3>
                        <p style={{ color: '#52525b', lineHeight: 1.5 }}>Our heavily-trained AI models adhere exactly to standardized road damage topological classifications.</p>
                    </div>
                    <div style={{ flex: '1 1 300px', textAlign: 'left', padding: '2.5rem', borderRadius: '16px', backgroundColor: '#f4f4f5' }}>
                        <Zap size={40} color="#10B981" style={{ marginBottom: '1.5rem' }} />
                        <h3 style={{ fontSize: '1.4rem', fontWeight: 700, marginBottom: '1rem' }}>Instant Results</h3>
                        <p style={{ color: '#52525b', lineHeight: 1.5 }}>Upload extreme high-res drone imagery and experience completely classified segmentation within milliseconds.</p>
                    </div>
                </div>

                <button
                    onClick={onGetStarted}
                    style={{ backgroundColor: '#09090b', color: '#ffffff', border: 'none', padding: '1.2rem 3rem', borderRadius: '50px', fontSize: '1.1rem', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px', transition: 'all 0.2s ease' }}
                    onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'var(--accent)'; }}
                    onMouseOut={(e) => { e.currentTarget.style.backgroundColor = '#09090b'; }}
                >
                    Launch Inference Studio <ArrowRight size={20} />
                </button>
            </div>

            {/* Section 3: Generated Picture Overlay Component */}
            <div style={{ position: 'relative', width: '100%', minHeight: '80vh', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 5rem' }}>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundImage: `url(${roadAnalysisImg})`, backgroundSize: 'cover', backgroundPosition: 'center', zIndex: 0 }}></div>
                <div style={{ position: 'absolute', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.5)', zIndex: 1 }}></div>

                <div style={{ position: 'relative', zIndex: 2, maxWidth: '600px', backgroundColor: 'rgba(10, 16, 13, 0.90)', padding: '4rem 3rem', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.1)', backdropFilter: 'blur(10px)' }}>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '2.5rem', fontWeight: 600, color: '#ffffff', marginBottom: '1.5rem', lineHeight: 1.2 }}>Pioneering Road Intelligence.</h2>
                    <p style={{ color: '#D4D4D8', fontSize: '1.1rem', lineHeight: 1.6, marginBottom: '2.5rem' }}>
                        Every fracture mapped. Every anomaly tracked. Dive into our enterprise-grade engine to seamlessly route your drone optical data through advanced YOLO architectures and DeepLab networks for unprecedented results.
                    </p>
                    <button
                        onClick={onGetStarted}
                        style={{ backgroundColor: 'white', color: 'black', border: 'none', padding: '1rem 2.5rem', borderRadius: '8px', fontSize: '1.1rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s ease' }}
                        onMouseOver={(e) => { e.currentTarget.style.backgroundColor = 'var(--accent)'; e.currentTarget.style.color = 'white'; }}
                        onMouseOut={(e) => { e.currentTarget.style.backgroundColor = 'white'; e.currentTarget.style.color = 'black'; }}
                    >
                        Open Workspace Environment
                    </button>
                </div>
                
                {/* Big Logo on the Right */}
                <div style={{ position: 'relative', zIndex: 2, flex: 1, display: 'flex', justifyContent: 'flex-end', paddingLeft: '4rem' }}>
                    <img src={tvLogo} alt="Tari9 Vision" style={{ width: '100%', maxWidth: '600px', maxHeight: '70vh', objectFit: 'contain', filter: 'drop-shadow(0 20px 50px rgba(0,0,0,0.8))', opacity: 0.95 }} />
                </div>
            </div>

            {/* Section 4: Deep Tech Showcase */}
            <div style={{ position: 'relative', backgroundColor: 'var(--surface)', padding: '8rem 5rem', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center', overflow: 'hidden' }}>
                
                {/* Massive Abstract Corner Watermark */}
                <img src={tvLogo} alt="Tari9 Vision Stamp" style={{ position: 'absolute', bottom: '-150px', right: '-150px', height: '700px', opacity: 0.03, pointerEvents: 'none', transform: 'rotate(-15deg)', zIndex: 0 }} />

                <div style={{ position: 'relative', zIndex: 2, width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                    <h2 style={{ fontFamily: 'var(--font-display)', fontSize: '3.5rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '1.5rem', letterSpacing: '-1px' }}>Enterprise Engineering.</h2>
                </div>

                <p style={{ position: 'relative', zIndex: 2, color: 'var(--text-secondary)', fontSize: '1.1rem', maxWidth: '800px', lineHeight: 1.6, marginBottom: '5rem' }}>
                    A perfectly clean, extraordinarily rapid workflow designed purely for civil engineering and government infrastructure teams attempting to transition optical surveillance into practical action.
                </p>

                <div style={{ position: 'relative', zIndex: 2, display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap', marginBottom: '5rem', maxWidth: '1200px' }}>
                    <div style={{ background: 'var(--surface-2)', padding: '2.5rem 2rem', borderRadius: '12px', border: '1px solid var(--border)', flex: '1 1 300px', textAlign: 'left' }}>
                        <div style={{ marginBottom: '1rem' }}><Crosshair size={32} color="var(--accent)" /></div>
                        <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.3rem', fontWeight: 600 }}>High Precision Zero-Shot</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', lineHeight: 1.5 }}>Segment Anything Model (SAM) integration allowing absolute pixel-perfect detection across diverse geographic asphalt varieties.</p>
                    </div>
                    <div style={{ background: 'var(--surface-2)', padding: '2.5rem 2rem', borderRadius: '12px', border: '1px solid var(--border)', flex: '1 1 300px', textAlign: 'left' }}>
                        <div style={{ marginBottom: '1rem' }}><Server size={32} color="var(--accent)" /></div>
                        <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.3rem', fontWeight: 600 }}>Massive Throughput</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', lineHeight: 1.5 }}>An asynchronous worker architecture capable of chewing through gigabytes of raw highway 4K video feeds sequentially.</p>
                    </div>
                    <div style={{ background: 'var(--surface-2)', padding: '2.5rem 2rem', borderRadius: '12px', border: '1px solid var(--border)', flex: '1 1 300px', textAlign: 'left' }}>
                        <div style={{ marginBottom: '1rem' }}><LayoutDashboard size={32} color="var(--accent)" /></div>
                        <h3 style={{ color: 'var(--text-primary)', marginBottom: '1rem', fontSize: '1.3rem', fontWeight: 600 }}>Fluid Interaction</h3>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', lineHeight: 1.5 }}>A stark contrast to legacy CLI tools. Run heavy inferences and tweak confidence matrices visually inside your browser securely.</p>
                    </div>
                </div>

                <button
                    onClick={onGetStarted}
                    onMouseOver={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 10px 20px rgba(0,0,0,0.5), 0 0 20px var(--accent-glow)'; }}
                    onMouseOut={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}
                    style={{
                        backgroundColor: 'var(--text-primary)',
                        color: 'var(--black)',
                        border: 'none',
                        padding: '1.2rem 3rem',
                        borderRadius: '8px',
                        fontFamily: 'var(--font-body)',
                        fontSize: '1.1rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                    }}
                >
                    Launch Studio Workspace →
                </button>
            </div>

            {/* Global Footer */}
            <div style={{ padding: '2.5rem 5rem', borderTop: '1px solid var(--border)', backgroundColor: 'var(--surface-2)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                    <img src={tvLogo} alt="Tari9 Vision Logo" style={{ height: '50px', filter: 'grayscale(1)', opacity: 0.5 }} />
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 500 }}>© 2026 Tari9 Vision Technologies.</span>
                </div>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', display: 'flex', gap: '3rem', fontWeight: 500 }}>
                    <span style={{ cursor: 'pointer', transition: 'color 0.2s ease' }} onMouseOver={(e) => e.target.style.color = 'white'} onMouseOut={(e) => e.target.style.color = 'var(--text-muted)'}>Privacy Policy</span>
                    <span style={{ cursor: 'pointer', transition: 'color 0.2s ease' }} onMouseOver={(e) => e.target.style.color = 'white'} onMouseOut={(e) => e.target.style.color = 'var(--text-muted)'}>Legal</span>
                </span>
            </div>
        </div>
    );
};

export default Cover;
