import React, { useState, useEffect } from 'react';
import { generateLearningPath, getLearningPath } from '../../lib/api';
import ReactMarkdown from 'react-markdown';

interface LearningPathTabProps {
  taskId: string;
}

const LearningPathTab: React.FC<LearningPathTabProps> = ({ taskId }) => {
  const [markdown, setMarkdown] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchPath = async () => {
    try {
      const res = await getLearningPath(taskId);
      if (res && res.markdown) {
        setMarkdown(res.markdown);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchPath();
  }, [taskId]);

  const handleGenerate = async () => {
    setIsLoading(true);
    setError('');
    try {
      const res = await generateLearningPath(taskId);
      if (res && res.markdown) {
        setMarkdown(res.markdown);
      }
    } catch (e: any) {
      console.error(e);
      setError(e.message || 'Failed to generate learning path. Make sure you have analyzed the graph first.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ marginTop: '20px', padding: '15px', background: '#1e293b', borderRadius: '8px', border: '1px solid #334155' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <h4 style={{ margin: 0, color: '#f8fafc', fontSize: '13px' }}>📚 Auto-Documentation</h4>
        <button 
          onClick={handleGenerate} 
          disabled={isLoading}
          style={{ background: '#10b981', color: 'white', padding: '4px 8px', fontSize: '11px', border: 'none', borderRadius: '4px', cursor: 'pointer', opacity: isLoading ? 0.7 : 1 }}
        >
          {isLoading ? 'Generating...' : markdown ? 'Regenerate Docs' : 'Generate Docs'}
        </button>
      </div>

      {error && <p style={{ color: '#ef4444', fontSize: '12px' }}>{error}</p>}

      {!markdown && !isLoading && !error && (
        <div style={{ color: '#94a3b8', fontSize: '12px', textAlign: 'center', padding: '20px 0' }}>
          No documentation exists for this task. Click 'Generate Docs' to auto-generate a structured learning path from your Knowledge Graph.
        </div>
      )}

      {markdown && (
        <div style={{ color: '#cbd5e1', fontSize: '12px', lineHeight: '1.6', maxHeight: '400px', overflowY: 'auto', paddingRight: '10px', wordBreak: 'normal', overflowWrap: 'break-word' }}>
          <ReactMarkdown
            components={{
              h1: ({node, ...props}) => <h1 style={{ color: '#ffffff', fontSize: '16px', fontWeight: 700, borderBottom: '1px solid #334155', paddingBottom: '6px', marginTop: '12px', marginBottom: '10px' }} {...props} />,
              h2: ({node, ...props}) => <h2 style={{ color: '#ffffff', fontSize: '14px', fontWeight: 600, marginTop: '14px', marginBottom: '8px' }} {...props} />,
              h3: ({node, ...props}) => <h3 style={{ color: '#f1f5f9', fontSize: '13px', fontWeight: 600, marginTop: '12px', marginBottom: '6px' }} {...props} />,
              p: ({node, ...props}) => <p style={{ color: '#cbd5e1', fontSize: '12px', marginBottom: '10px', lineHeight: '1.6', wordBreak: 'normal', overflowWrap: 'break-word' }} {...props} />,
              ul: ({node, ...props}) => <ul style={{ color: '#cbd5e1', paddingLeft: '20px', marginBottom: '10px' }} {...props} />,
              ol: ({node, ...props}) => <ol style={{ color: '#cbd5e1', paddingLeft: '20px', marginBottom: '10px' }} {...props} />,
              li: ({node, ...props}) => <li style={{ color: '#cbd5e1', marginBottom: '4px', lineHeight: '1.5' }} {...props} />,
              strong: ({node, ...props}) => <strong style={{ color: '#ffffff', fontWeight: 700 }} {...props} />,
              code: ({node, ...props}) => <code style={{ background: '#0f172a', color: '#38bdf8', padding: '2px 4px', borderRadius: '4px', fontSize: '11px' }} {...props} />,
              a: ({node, ...props}) => <a style={{ color: '#38bdf8', textDecoration: 'underline' }} target="_blank" rel="noopener noreferrer" {...props} />
            }}
          >
            {markdown}
          </ReactMarkdown>
        </div>
      )}
    </div>
  );
};

export default LearningPathTab;
