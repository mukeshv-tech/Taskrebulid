import codecs

path = 'taskrebuild/extension/src/popup/components/LearningPathTab.tsx'
content = """import React, { useState, useEffect } from 'react';
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
        <div className="markdown-body" style={{ color: '#cbd5e1', fontSize: '12px', lineHeight: '1.5', maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
          <ReactMarkdown
            components={{
              h1: ({node, ...props}) => <h1 style={{ color: '#f8fafc', fontSize: '16px', borderBottom: '1px solid #334155', paddingBottom: '4px', marginTop: '10px' }} {...props} />,
              h2: ({node, ...props}) => <h2 style={{ color: '#f8fafc', fontSize: '14px', marginTop: '10px' }} {...props} />,
              h3: ({node, ...props}) => <h3 style={{ color: '#e2e8f0', fontSize: '13px' }} {...props} />,
              p: ({node, ...props}) => <p style={{ marginBottom: '10px' }} {...props} />,
              ul: ({node, ...props}) => <ul style={{ paddingLeft: '20px', marginBottom: '10px' }} {...props} />,
              li: ({node, ...props}) => <li style={{ marginBottom: '4px' }} {...props} />,
              strong: ({node, ...props}) => <strong style={{ color: '#f8fafc' }} {...props} />,
              a: ({node, ...props}) => <a style={{ color: '#3b82f6', textDecoration: 'none' }} target="_blank" rel="noopener noreferrer" {...props} />
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
"""
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

def fix_newlines(path):
    with open(path, 'rb') as f:
        file_content = f.read()
    file_content = file_content.replace(b'\r\n', b'\n').replace(b'\r', b'')
    with open(path, 'wb') as f:
        f.write(file_content)
fix_newlines(path)
