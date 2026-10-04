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
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopyLink = async (e: React.MouseEvent, url: string, id: string) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(url);
      setCopiedId(id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (err) {
      console.error("Copy failed", err);
      alert("Failed to copy link");
    }
  };

  
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);


  
  const handleInputChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setQuery(val);
    if (!val.trim()) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    try {
      const endpoint = `/api/search/suggestions?q=${encodeURIComponent(val)}`;
      const data = await fetchApi(endpoint);
      if (data.suggestions && data.suggestions.length > 0) {
        setSuggestions(data.suggestions);
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
      }
    } catch (err) {
      console.error("Suggestions failed", err);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    setShowSuggestions(false);
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
      
      <div style={{ position: 'relative', marginBottom: '15px' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '8px' }}>
          <input
            type="text"
            value={query}
            onChange={handleInputChange}
            onFocus={() => { if(suggestions.length > 0) setShowSuggestions(true); }}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
            placeholder="Keywords or semantic question..."
            style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1' }}
          />
          <button type="submit" disabled={loading} style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer' }}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </form>
        {showSuggestions && suggestions.length > 0 && (
          <ul style={{ 
            position: 'absolute', top: '100%', left: 0, right: '70px', 
            background: 'white', border: '1px solid #e2e8f0', borderRadius: '4px', 
            listStyle: 'none', padding: 0, margin: '4px 0 0 0', 
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', zIndex: 50 
          }}>
            {suggestions.map((sug, idx) => (
              <li 
                key={idx}
                onMouseDown={(e) => {
                  e.preventDefault();
                  setQuery(sug);
                  setShowSuggestions(false);
                }}
                style={{ padding: '8px 12px', fontSize: '13px', cursor: 'pointer', borderBottom: idx === suggestions.length - 1 ? 'none' : '1px solid #f1f5f9' }}
                onMouseEnter={(e) => e.currentTarget.style.background = '#f8fafc'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
              >
                {sug}
              </li>
            ))}
          </ul>
        )}
      </div>

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
                          <a href={item.url} target="_blank" rel="noopener noreferrer" onClick={(e) => e.stopPropagation()} style={{ fontSize: '10px', padding: '4px 8px', background: '#f1f5f9', border: '1px solid #cbd5e1', borderRadius: '4px', cursor: 'pointer', textDecoration: 'none', color: '#0f172a' }}>
                            Open Resource
                          </a>
                        )}
                        {item.url && (
                          <button 
                            onClick={(e) => handleCopyLink(e, item.url!, item.id)} 
                            style={{ 
                              fontSize: '10px', 
                              padding: '4px 8px', 
                              background: copiedId === item.id ? '#dcfce7' : '#f1f5f9', 
                              color: copiedId === item.id ? '#166534' : '#0f172a', 
                              border: '1px solid', 
                              borderColor: copiedId === item.id ? '#bbf7d0' : '#cbd5e1', 
                              borderRadius: '4px', 
                              cursor: 'pointer', 
                              transition: 'all 0.2s' 
                            }}
                          >
                            {copiedId === item.id ? '✓ Copied!' : 'Copy Link'}
                          </button>
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
