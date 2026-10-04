import React, { useState } from 'react';
import { fetchApi } from '../../lib/api';

interface SearchResult {
  id: string;
  type: string;
  task_id: string;
  title: string;
  snippet: string;
  url?: string;
  score: number;
  matched_by: string[];
}

interface SearchProps {
  taskId?: string;
  onNavigateToTask?: (taskId: string) => void;
}

const SearchTab: React.FC<SearchProps> = ({ taskId, onNavigateToTask }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Record<string, SearchResult[]>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    console.log("Search button clicked! Query:", query);
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResults({});

    try {
      console.log("Making fetch request to endpoint:", taskId ? `/api/search?q=${encodeURIComponent(query)}&task_id=${taskId}` : `/api/search?q=${encodeURIComponent(query)}`);
        const endpoint = taskId ? `/api/search?q=${encodeURIComponent(query)}&task_id=${taskId}` : `/api/search?q=${encodeURIComponent(query)}`;
      console.log("Calling fetchApi...");
        const data = await fetchApi(endpoint);
        console.log("Fetch returned:", data);
      if (data.results) {
        setResults(data.results);
      } else {
        setResults({});
      }
    } catch (err: any) {
      console.error(err);
      setError('Search failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const hasResults = Object.keys(results).length > 0 && Object.values(results).some(arr => arr.length > 0);

  const getSourceDisplay = (type: string) => {
    switch(type) {
      case 'task': return 'TASKS';
      case 'resource': return 'RESOURCES';
      case 'analysis': return 'AI ANALYSES';
      case 'snapshot': return 'SNAPSHOTS';
      case 'graph_node': return 'GRAPH NODES';
      case 'question': return 'QUESTIONS';
      default: return type.toUpperCase();
    }
  };

  return (
    <div style={{ marginTop: '20px', padding: '15px', background: '#f8fafc', borderRadius: '4px', border: '1px solid #e2e8f0' }}>
      <h3 style={{ margin: '0 0 10px 0', color: '#0f172a' }}>{taskId ? 'Search this task...' : 'Search TaskRebuild...'}</h3>
      
      <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px', marginBottom: '15px' }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Keywords or semantic question..."
          style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
        />
        <button type="submit" disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </form>

      {error && <p style={{ color: '#ef4444', fontSize: '12px' }}>{error}</p>}

      {!loading && !hasResults && query && Object.keys(results).length > 0 && (
        <p style={{ fontSize: '12px', color: '#64748b' }}>No results found. Try different keywords or a broader question.</p>
      )}

      {hasResults && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {Object.entries(results).map(([type, items]) => {
            if (!items || items.length === 0) return null;
            return (
              <div key={type}>
                <h4 style={{ margin: '0 0 8px 0', color: '#475569', fontSize: '11px', letterSpacing: '0.05em', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px' }}>
                  {getSourceDisplay(type)}
                </h4>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {items.map((item) => (
                    <li 
                      key={item.id} 
                      onClick={() => {
                        if (onNavigateToTask) {
                          onNavigateToTask(item.task_id);
                        }
                      }}
                      style={{ background: 'white', padding: '10px', borderRadius: '4px', border: '1px solid #e2e8f0', cursor: 'pointer', transition: 'background 0.2s' }}
                      onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                      onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <strong style={{ fontSize: '13px', color: '#1e293b' }}>{item.title}</strong>
                        {item.matched_by && item.matched_by.length > 0 && (
                          <span style={{ fontSize: '9px', background: '#f1f5f9', color: '#64748b', padding: '2px 6px', borderRadius: '10px' }}>
                            {item.matched_by.join(' + ')}
                          </span>
                        )}
                      </div>
                      
                      <p 
                        style={{ margin: '6px 0', fontSize: '12px', color: '#334155', display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}
                        dangerouslySetInnerHTML={{ __html: item.snippet || '' }}
                      />
                      
                      {item.url && (
                        <p style={{ margin: '0 0 8px 0', fontSize: '10px', color: '#94a3b8', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {item.url}
                        </p>
                      )}
                      
                      <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
                        {type === 'task' && !taskId && onNavigateToTask && (
                          <button onClick={() => onNavigateToTask(item.task_id)} style={{ fontSize: '10px', padding: '4px 8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer' }}>
                            Open Task
                          </button>
                        )}
                        {item.url && (
                          <a href={item.url} target="_blank" rel="noopener noreferrer" style={{ fontSize: '10px', padding: '4px 8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', textDecoration: 'none', color: '#0f172a' }}>
                            Open Resource
                          </a>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default SearchTab;
