import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface ArchitectureDiagramProps {
  chartDefinition: string;
}

export const ArchitectureDiagram: React.FC<ArchitectureDiagramProps> = ({ chartDefinition }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [zoom, setZoom] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      themeVariables: {
        darkMode: true,
        background: '#070913',
        primaryColor: '#1e293b',
        primaryTextColor: '#f8fafc',
        primaryBorderColor: '#38bdf8',
        lineColor: '#64748b',
        secondaryColor: '#0f172a',
        tertiaryColor: '#1e293b',
        fontFamily: "'Plus Jakarta Sans', system-ui, sans-serif",
      },
      securityLevel: 'loose',
      flowchart: {
        htmlLabels: true,
        curve: 'basis',
        useMaxWidth: false,
      },
    });

    let isMounted = true;
    const renderDiagram = async () => {
      try {
        setLoading(true);
        setError(null);
        const uniqueId = `mermaid-svg-${Date.now()}`;
        const { svg } = await mermaid.render(uniqueId, chartDefinition);
        if (isMounted) {
          setSvgContent(svg);
          setLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          console.error('Mermaid render error:', err);
          setError(err?.message || 'Failed to render architecture diagram');
          setLoading(false);
        }
      }
    };

    renderDiagram();

    return () => {
      isMounted = false;
    };
  }, [chartDefinition]);

  const handleZoomIn = () => setZoom((prev) => Math.min(prev + 0.15, 2.0));
  const handleZoomOut = () => setZoom((prev) => Math.max(prev - 0.15, 0.5));
  const handleResetZoom = () => setZoom(1);

  return (
    <div className="architecture-diagram-container">
      <div className="diagram-header">
        <div className="diagram-title-info">
          <span className="diagram-badge">Interactive System Graph</span>
          <span className="diagram-hint">Click any component to navigate directly to its GitHub source file</span>
        </div>
        <div className="diagram-controls">
          <button className="diagram-btn" onClick={handleZoomOut} title="Zoom out" type="button">
            −
          </button>
          <button className="diagram-btn" onClick={handleResetZoom} title="Reset zoom" type="button">
            {Math.round(zoom * 100)}%
          </button>
          <button className="diagram-btn" onClick={handleZoomIn} title="Zoom in" type="button">
            +
          </button>
        </div>
      </div>

      <div className="diagram-viewport" ref={containerRef}>
        {loading && (
          <div className="diagram-loading">
            <div className="spinner" />
            <p>Rendering system architecture diagram...</p>
          </div>
        )}
        {error && (
          <div className="diagram-error">
            <p>⚠️ {error}</p>
          </div>
        )}
        {!loading && !error && (
          <div
            className="diagram-canvas"
            style={{
              transform: `scale(${zoom})`,
              transformOrigin: 'top center',
              transition: 'transform 0.15s ease-out',
            }}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        )}
      </div>

      <div className="diagram-legend">
        <div className="legend-item"><span className="legend-dot tone-blue" /> Browser Extension</div>
        <div className="legend-item"><span className="legend-dot tone-amber" /> Backend FastAPI Routes</div>
        <div className="legend-item"><span className="legend-dot tone-mint" /> Research Services</div>
        <div className="legend-item"><span className="legend-dot tone-rose" /> AI & Database Persistence</div>
        <div className="legend-item"><span className="legend-dot tone-indigo" /> User / Researcher</div>
      </div>
    </div>
  );
};
