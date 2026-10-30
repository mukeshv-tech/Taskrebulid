import React, { useState, useEffect } from 'react';
import { supabase } from '../../lib/supabase';
import {
  listKnowledge,
  getKnowledgeDetail,
  createKnowledge,
  updateKnowledge,
  deleteKnowledge,
  archiveKnowledge,
  restoreKnowledge,
  checkKnowledgeDuplicate,
  createKnowledgeRelationship,
  deleteKnowledgeRelationship,
  getTaskKnowledgeSuggestions,
} from '../../lib/api';

interface KnowledgeTabProps {
  taskId?: string;
  taskName?: string;
}

const CONTROLLED_TYPES = ['concept', 'topic', 'question', 'insight', 'note', 'resource'] as const;
const RELATIONSHIP_TYPES = ['related_to', 'supports', 'contradicts', 'depends_on', 'explains', 'derived_from'] as const;

export const KnowledgeTab: React.FC<KnowledgeTabProps> = ({ taskId, taskName }) => {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('active');
  const [scopeToTask, setScopeToTask] = useState<boolean>(!!taskId);
  const [error, setError] = useState<string>('');

  // Creation / Editing State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState('');
  const [type, setType] = useState<string>('concept');
  const [summary, setSummary] = useState('');
  const [content, setContent] = useState('');
  const [duplicateWarning, setDuplicateWarning] = useState<any>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Detail View State
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<any>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState('');
  const [editType, setEditType] = useState('concept');
  const [editSummary, setEditSummary] = useState('');
  const [editContent, setEditContent] = useState('');

  // Relationship Linking State
  const [showAddRelModal, setShowAddRelModal] = useState(false);
  const [targetKnowledgeId, setTargetKnowledgeId] = useState('');
  const [relType, setRelType] = useState<string>('related_to');

  // AI Suggestions Drawer
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [isSuggesting, setIsSuggesting] = useState(false);

  const fetchItems = async () => {
    setLoading(true);
    setError('');
    try {
      const params: any = { status: filterStatus };
      if (filterType) params.type = filterType;
      if (scopeToTask && taskId) params.task_id = taskId;

      const res = await listKnowledge(params);
      setItems(res.items || []);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch knowledge');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, [filterType, filterStatus, scopeToTask, taskId]);

  // Realtime subscription for knowledge items (scoped to current user and active task scope)
  useEffect(() => {
    let channel: any = null;

    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session?.user?.id) return;
      const userId = session.user.id;

      channel = supabase
        .channel(`realtime-knowledge-${userId}-${taskId || 'all'}`)
        .on(
          'postgres_changes',
          {
            event: '*',
            schema: 'public',
            table: 'knowledge_items',
            filter: `user_id=eq.${userId}`
          },
          (payload: any) => {
            if (payload.eventType === 'INSERT') {
              // If scoped to a specific task, reload to ensure relationship filtering
              if (scopeToTask && taskId) {
                fetchItems();
              } else {
                setItems((prev) => {
                  if (prev.some((k) => k.id === payload.new.id)) return prev;
                  return [payload.new, ...prev];
                });
              }
            } else if (payload.eventType === 'UPDATE') {
              setItems((prev) =>
                prev.map((k) => (k.id === payload.new.id ? { ...k, ...payload.new } : k))
              );
              setDetail((prev: any) => (prev && prev.id === payload.new.id ? { ...prev, ...payload.new } : prev));
            } else if (payload.eventType === 'DELETE') {
              setItems((prev) => prev.filter((k) => k.id !== payload.old.id));
              setDetail((prev: any) => (prev && prev.id === payload.old.id ? null : prev));
              setSelectedId((prev: any) => (prev === payload.old.id ? null : prev));
            }
          }
        )
        .subscribe();
    });

    return () => {
      if (channel) {
        supabase.removeChannel(channel);
      }
    };
  }, [taskId, scopeToTask]);

  const loadDetail = async (id: string) => {
    try {
      const res = await getKnowledgeDetail(id);
      setDetail(res);
      setSelectedId(id);
      setEditTitle(res.title);
      setEditType(res.type);
      setEditSummary(res.summary || '');
      setEditContent(res.content || '');
      setIsEditing(false);
    } catch (e: any) {
      setError(e.message || 'Failed to load details');
    }
  };

  // Duplicate Check on Title Change
  const handleTitleBlur = async () => {
    if (!title.trim()) return;
    try {
      const res = await checkKnowledgeDuplicate(title);
      if (res.has_duplicate) {
        setDuplicateWarning(res);
      } else {
        setDuplicateWarning(null);
      }
    } catch (e) {
      // non-blocking
    }
  };

  const handleCreate = async () => {
    if (!title.trim()) return;
    setIsSubmitting(true);
    try {
      const sources: any[] = [];
      if (taskId) {
        sources.push({
          source_type: 'task',
          source_id: taskId,
          source_name: taskName || 'Current Task'
        });
      }

      await createKnowledge({
        type,
        title: title.trim(),
        summary: summary.trim(),
        content: content.trim(),
        sources
      });

      setShowCreateModal(false);
      setTitle('');
      setSummary('');
      setContent('');
      setDuplicateWarning(null);
      fetchItems();
    } catch (e: any) {
      setError(e.message || 'Failed to create knowledge item');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleUpdate = async () => {
    if (!selectedId) return;
    try {
      await updateKnowledge(selectedId, {
        title: editTitle,
        type: editType,
        summary: editSummary,
        content: editContent
      });
      setIsEditing(false);
      loadDetail(selectedId);
      fetchItems();
    } catch (e: any) {
      setError(e.message || 'Failed to update knowledge');
    }
  };

  const handleDelete = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this knowledge item? This action is permanent.')) {
      return;
    }
    try {
      await deleteKnowledge(id);
      if (selectedId === id) {
        setSelectedId(null);
        setDetail(null);
      }
      fetchItems();
    } catch (e: any) {
      setError(e.message || 'Failed to delete knowledge');
    }
  };

  const handleArchive = async (id: string) => {
    try {
      await archiveKnowledge(id);
      if (selectedId === id) loadDetail(id);
      fetchItems();
    } catch (e: any) {
      setError(e.message || 'Failed to archive');
    }
  };

  const handleRestore = async (id: string) => {
    try {
      await restoreKnowledge(id);
      if (selectedId === id) loadDetail(id);
      fetchItems();
    } catch (e: any) {
      setError(e.message || 'Failed to restore');
    }
  };

  const handleAddRelationship = async () => {
    if (!selectedId || !targetKnowledgeId) return;
    try {
      await createKnowledgeRelationship(selectedId, targetKnowledgeId, relType);
      setShowAddRelModal(false);
      setTargetKnowledgeId('');
      loadDetail(selectedId);
    } catch (e: any) {
      alert(e.message || 'Failed to add relationship');
    }
  };

  const handleDeleteRelationship = async (relId: string) => {
    if (!selectedId) return;
    try {
      await deleteKnowledgeRelationship(selectedId, relId);
      loadDetail(selectedId);
    } catch (e: any) {
      alert(e.message || 'Failed to delete relationship');
    }
  };

  const handleFetchAiSuggestions = async () => {
    if (!taskId) return;
    setIsSuggesting(true);
    setShowSuggestions(true);
    try {
      const res = await getTaskKnowledgeSuggestions(taskId);
      setSuggestions(res.suggestions || []);
    } catch (e: any) {
      setError(e.message || 'Failed to get suggestions');
    } finally {
      setIsSuggesting(false);
    }
  };

  const handleApproveSuggestion = async (sug: any) => {
    try {
      await createKnowledge({
        type: sug.type,
        title: sug.title,
        summary: sug.summary,
        content: sug.content,
        origin: 'ai_approved',
        confidence: sug.confidence,
        sources: [
          {
            source_type: sug.source_type || 'task',
            source_id: sug.source_id || taskId,
            source_name: sug.source_name || taskName || 'Task'
          }
        ]
      });
      setSuggestions(prev => prev.filter(s => s !== sug));
      fetchItems();
    } catch (e: any) {
      alert('Failed to approve suggestion: ' + e.message);
    }
  };

  return (
    <div style={{ marginTop: '20px', padding: '15px', background: '#0f172a', borderRadius: '8px', border: '1px solid #1e293b', color: '#f8fafc' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
        <h4 style={{ margin: 0, color: '#38bdf8', fontSize: '14px' }}>🧠 Personal Knowledge</h4>
        <div style={{ display: 'flex', gap: '6px' }}>
          {taskId && (
            <button
              onClick={handleFetchAiSuggestions}
              disabled={isSuggesting}
              style={{ background: '#6366f1', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
            >
              {isSuggesting ? 'AI Thinking...' : '✨ AI Suggestions'}
            </button>
          )}
          <button
            onClick={() => setShowCreateModal(true)}
            style={{ background: '#0284c7', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
          >
            + New Knowledge
          </button>
        </div>
      </div>

      {error && <p style={{ color: '#ef4444', fontSize: '11px', margin: '5px 0' }}>{error}</p>}

      {/* Scope, Filter, and Status Controls */}
      <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center', marginBottom: '10px', fontSize: '11px' }}>
        {taskId && (
          <label style={{ display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}>
            <input
              type="checkbox"
              checked={scopeToTask}
              onChange={e => setScopeToTask(e.target.checked)}
            />
            Scope to this Task
          </label>
        )}
        <select
          value={filterType}
          onChange={e => setFilterType(e.target.value)}
          style={{ background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '4px', padding: '2px 6px' }}
        >
          <option value="">All Types</option>
          {CONTROLLED_TYPES.map(t => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <select
          value={filterStatus}
          onChange={e => setFilterStatus(e.target.value)}
          style={{ background: '#1e293b', color: '#f8fafc', border: '1px solid #334155', borderRadius: '4px', padding: '2px 6px' }}
        >
          <option value="active">Active</option>
          <option value="archived">Archived</option>
        </select>
        <button
          onClick={fetchItems}
          disabled={loading}
          style={{ background: 'transparent', color: '#94a3b8', border: '1px solid #334155', borderRadius: '4px', padding: '2px 6px', cursor: 'pointer' }}
        >
          {loading ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* AI Suggestions Drawer */}
      {showSuggestions && (
        <div style={{ background: '#1e1b4b', border: '1px solid #4338ca', borderRadius: '6px', padding: '10px', marginBottom: '15px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '12px', fontWeight: 'bold', color: '#a5b4fc' }}>AI Suggested Knowledge (Review before saving)</span>
            <button
              onClick={() => setShowSuggestions(false)}
              style={{ background: 'transparent', color: '#94a3b8', border: 'none', cursor: 'pointer', fontSize: '12px' }}
            >
              ✕
            </button>
          </div>
          {suggestions.length === 0 ? (
            <p style={{ fontSize: '11px', color: '#cbd5e1', margin: '8px 0 0 0' }}>
              {isSuggesting ? 'Analyzing task activity and resources for concepts...' : 'No suggestions found or all approved.'}
            </p>
          ) : (
            <div style={{ marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {suggestions.map((s, idx) => (
                <div key={idx} style={{ background: '#312e81', borderRadius: '4px', padding: '8px', fontSize: '11px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ fontWeight: 'bold', color: '#f8fafc' }}>{s.title}</span>
                    <span style={{ background: '#4338ca', color: '#e0e7ff', padding: '1px 5px', borderRadius: '3px', fontSize: '9px' }}>{s.type}</span>
                  </div>
                  <p style={{ margin: '4px 0', color: '#cbd5e1' }}>{s.summary}</p>
                  <div style={{ display: 'flex', gap: '6px', marginTop: '6px' }}>
                    <button
                      onClick={() => handleApproveSuggestion(s)}
                      style={{ background: '#10b981', color: 'white', border: 'none', padding: '3px 8px', borderRadius: '3px', fontSize: '10px', cursor: 'pointer' }}
                    >
                      ✓ Approve
                    </button>
                    <button
                      onClick={() => setSuggestions(prev => prev.filter(x => x !== s))}
                      style={{ background: '#ef4444', color: 'white', border: 'none', padding: '3px 8px', borderRadius: '3px', fontSize: '10px', cursor: 'pointer' }}
                    >
                      ✕ Reject
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Main List */}
      {items.length === 0 && !loading ? (
        <p style={{ fontSize: '12px', color: '#94a3b8', textAlign: 'center', padding: '10px 0' }}>
          No personal knowledge items found. Turn useful task info into reusable knowledge!
        </p>
      ) : (
        <ul style={{ listStyleType: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {items.map(item => (
            <li
              key={item.id}
              onClick={() => loadDetail(item.id)}
              style={{
                background: selectedId === item.id ? '#1e293b' : '#0f172a',
                border: '1px solid #334155',
                borderRadius: '4px',
                padding: '8px',
                cursor: 'pointer',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ fontWeight: 'bold', fontSize: '12px', color: '#f8fafc' }}>{item.title}</span>
                  <span style={{ background: '#334155', color: '#cbd5e1', padding: '1px 4px', borderRadius: '3px', fontSize: '9px' }}>
                    {item.type}
                  </span>
                  {item.origin === 'ai_approved' && (
                    <span style={{ background: '#4c1d95', color: '#ddd6fe', padding: '1px 4px', borderRadius: '3px', fontSize: '9px' }}>
                      AI Approved
                    </span>
                  )}
                </div>
                {item.summary && (
                  <p style={{ margin: '3px 0 0 0', fontSize: '11px', color: '#94a3b8' }}>
                    {item.summary.length > 70 ? item.summary.substring(0, 70) + '...' : item.summary}
                  </p>
                )}
              </div>
              <div style={{ display: 'flex', gap: '4px' }}>
                {item.status === 'active' ? (
                  <button
                    onClick={(e) => { e.stopPropagation(); handleArchive(item.id); }}
                    title="Archive"
                    style={{ background: 'transparent', border: 'none', color: '#f59e0b', cursor: 'pointer', fontSize: '11px' }}
                  >
                    📦
                  </button>
                ) : (
                  <button
                    onClick={(e) => { e.stopPropagation(); handleRestore(item.id); }}
                    title="Restore"
                    style={{ background: 'transparent', border: 'none', color: '#10b981', cursor: 'pointer', fontSize: '11px' }}
                  >
                    ♻️
                  </button>
                )}
                <button
                  onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                  title="Delete"
                  style={{ background: 'transparent', border: 'none', color: '#ef4444', cursor: 'pointer', fontSize: '11px' }}
                >
                  ✕
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}

      {/* Detail View Modal/Panel */}
      {selectedId && detail && (
        <div style={{ marginTop: '15px', background: '#1e293b', border: '1px solid #475569', borderRadius: '6px', padding: '12px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '13px', fontWeight: 'bold', color: '#38bdf8' }}>Knowledge Details</span>
            <button
              onClick={() => { setSelectedId(null); setDetail(null); }}
              style={{ background: 'transparent', color: '#94a3b8', border: 'none', cursor: 'pointer', fontSize: '12px' }}
            >
              ✕ Close
            </button>
          </div>

          {!isEditing ? (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                <h5 style={{ margin: 0, fontSize: '13px', color: '#f8fafc' }}>{detail.title}</h5>
                <span style={{ background: '#334155', color: '#93c5fd', padding: '2px 5px', borderRadius: '3px', fontSize: '10px' }}>
                  {detail.type}
                </span>
                <span style={{ background: '#0284c7', color: 'white', padding: '2px 5px', borderRadius: '3px', fontSize: '10px' }}>
                  {detail.status}
                </span>
              </div>

              {detail.summary && (
                <p style={{ fontStyle: 'italic', color: '#cbd5e1', fontSize: '11px', margin: '5px 0' }}>
                  "{detail.summary}"
                </p>
              )}

              {detail.content && (
                <div style={{ background: '#0f172a', padding: '8px', borderRadius: '4px', fontSize: '11px', color: '#e2e8f0', whiteSpace: 'pre-wrap', margin: '8px 0' }}>
                  {detail.content}
                </div>
              )}

              {/* Provenance & Sources */}
              <div style={{ marginTop: '10px' }}>
                <strong style={{ fontSize: '11px', color: '#38bdf8' }}>Sources ({detail.sources?.length || 0}):</strong>
                {detail.sources && detail.sources.length > 0 ? (
                  <ul style={{ paddingLeft: '15px', margin: '4px 0', fontSize: '11px', color: '#94a3b8' }}>
                    {detail.sources.map((src: any) => (
                      <li key={src.id}>
                        <span style={{ color: '#cbd5e1' }}>{src.source_type.toUpperCase()}</span>: {src.source_name || src.source_id || 'Untitled'}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '10px', color: '#64748b', margin: '2px 0' }}>No sources recorded.</p>
                )}
              </div>

              {/* Related Knowledge & Backlinks */}
              <div style={{ marginTop: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <strong style={{ fontSize: '11px', color: '#38bdf8' }}>Related Knowledge ({detail.relationships?.length || 0}):</strong>
                  <button
                    onClick={() => setShowAddRelModal(true)}
                    style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '2px 6px', borderRadius: '3px', fontSize: '10px', cursor: 'pointer' }}
                  >
                    + Link
                  </button>
                </div>
                {detail.relationships && detail.relationships.length > 0 ? (
                  <ul style={{ paddingLeft: '15px', margin: '4px 0', fontSize: '11px', color: '#94a3b8' }}>
                    {detail.relationships.map((rel: any) => (
                      <li key={rel.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', margin: '2px 0' }}>
                        <span>
                          [{rel.relationship_type}] → <strong style={{ color: '#f8fafc' }}>{rel.target_knowledge?.title || rel.target_knowledge_id}</strong>
                        </span>
                        <button
                          onClick={() => handleDeleteRelationship(rel.id)}
                          style={{ background: 'transparent', color: '#ef4444', border: 'none', cursor: 'pointer', fontSize: '10px' }}
                        >
                          ✕
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '10px', color: '#64748b', margin: '2px 0' }}>No relationships linked.</p>
                )}
              </div>

              {/* Backlinks (Reused across tasks) */}
              <div style={{ marginTop: '10px' }}>
                <strong style={{ fontSize: '11px', color: '#38bdf8' }}>Backlinks & Reused In ({detail.backlinks?.length || 0}):</strong>
                {detail.backlinks && detail.backlinks.length > 0 ? (
                  <ul style={{ paddingLeft: '15px', margin: '4px 0', fontSize: '11px', color: '#94a3b8' }}>
                    {detail.backlinks.map((bl: any, i: number) => (
                      <li key={i}>
                        {bl.type === 'task' ? '📁 Task' : '🧠 Knowledge'}: <strong style={{ color: '#f8fafc' }}>{bl.title}</strong> ({bl.relationship})
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: '10px', color: '#64748b', margin: '2px 0' }}>No backlinks.</p>
                )}
              </div>

              <div style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                <button
                  onClick={() => setIsEditing(true)}
                  style={{ background: '#0284c7', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                >
                  Edit
                </button>
                {detail.status === 'active' ? (
                  <button
                    onClick={() => handleArchive(detail.id)}
                    style={{ background: '#f59e0b', color: 'black', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                  >
                    Archive
                  </button>
                ) : (
                  <button
                    onClick={() => handleRestore(detail.id)}
                    style={{ background: '#10b981', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                  >
                    Restore
                  </button>
                )}
                <button
                  onClick={() => handleDelete(detail.id)}
                  style={{ background: '#ef4444', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', cursor: 'pointer' }}
                >
                  Delete
                </button>
              </div>
            </div>
          ) : (
            // Edit Mode Form
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11px' }}>
              <div>
                <label>Title:</label>
                <input
                  type="text"
                  value={editTitle}
                  onChange={e => setEditTitle(e.target.value)}
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
                />
              </div>
              <div>
                <label>Type:</label>
                <select
                  value={editType}
                  onChange={e => setEditType(e.target.value)}
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
                >
                  {CONTROLLED_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
              <div>
                <label>Summary:</label>
                <input
                  type="text"
                  value={editSummary}
                  onChange={e => setEditSummary(e.target.value)}
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
                />
              </div>
              <div>
                <label>Content:</label>
                <textarea
                  rows={4}
                  value={editContent}
                  onChange={e => setEditContent(e.target.value)}
                  style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
                />
              </div>
              <div style={{ display: 'flex', gap: '6px' }}>
                <button
                  onClick={handleUpdate}
                  style={{ background: '#10b981', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Save Changes
                </button>
                <button
                  onClick={() => setIsEditing(false)}
                  style={{ background: '#64748b', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div style={{ marginTop: '12px', background: '#1e293b', border: '1px solid #0284c7', borderRadius: '6px', padding: '12px' }}>
          <h5 style={{ margin: '0 0 8px 0', color: '#38bdf8', fontSize: '13px' }}>Create Knowledge Item</h5>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11px' }}>
            <div>
              <label>Title *</label>
              <input
                type="text"
                placeholder="e.g. Browser Content Scripts"
                value={title}
                onChange={e => setTitle(e.target.value)}
                onBlur={handleTitleBlur}
                style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              />
            </div>

            {duplicateWarning && (
              <div style={{ background: '#451a03', border: '1px solid #b45309', borderRadius: '4px', padding: '6px', color: '#fde68a' }}>
                ⚠️ <strong>Similar knowledge already exists</strong> ({duplicateWarning.duplicate_type} match):
                <ul style={{ margin: '4px 0', paddingLeft: '15px' }}>
                  {duplicateWarning.existing_items.map((it: any) => (
                    <li key={it.id}>
                      <span style={{ textDecoration: 'underline', cursor: 'pointer' }} onClick={() => { setShowCreateModal(false); loadDetail(it.id); }}>
                        {it.title} ({it.type})
                      </span>
                    </li>
                  ))}
                </ul>
                <span style={{ fontSize: '10px' }}>You may still create anyway if this is distinct.</span>
              </div>
            )}

            <div>
              <label>Type</label>
              <select
                value={type}
                onChange={e => setType(e.target.value)}
                style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              >
                {CONTROLLED_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label>Summary (Optional)</label>
              <input
                type="text"
                placeholder="Short 1-line recap"
                value={summary}
                onChange={e => setSummary(e.target.value)}
                style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              />
            </div>

            <div>
              <label>Content *</label>
              <textarea
                rows={3}
                placeholder="Detailed explanations, patterns, or notes..."
                value={content}
                onChange={e => setContent(e.target.value)}
                style={{ width: '100%', background: '#0f172a', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              />
            </div>

            <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
              <button
                onClick={handleCreate}
                disabled={isSubmitting || !title.trim()}
                style={{ background: '#10b981', color: 'white', border: 'none', padding: '4px 10px', borderRadius: '4px', cursor: 'pointer' }}
              >
                {isSubmitting ? 'Saving...' : 'Save Knowledge'}
              </button>
              <button
                onClick={() => { setShowCreateModal(false); setDuplicateWarning(null); }}
                style={{ background: '#64748b', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer' }}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Add Relationship Link Modal */}
      {showAddRelModal && (
        <div style={{ marginTop: '10px', background: '#0f172a', border: '1px solid #3b82f6', borderRadius: '6px', padding: '10px', fontSize: '11px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <span style={{ fontWeight: 'bold', color: '#60a5fa' }}>Connect Related Knowledge</span>
            <button onClick={() => setShowAddRelModal(false)} style={{ background: 'transparent', color: '#94a3b8', border: 'none', cursor: 'pointer' }}>✕</button>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div>
              <label>Target Knowledge:</label>
              <select
                value={targetKnowledgeId}
                onChange={e => setTargetKnowledgeId(e.target.value)}
                style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              >
                <option value="">Select Target Item...</option>
                {items.filter(it => it.id !== selectedId).map(it => (
                  <option key={it.id} value={it.id}>{it.title} ({it.type})</option>
                ))}
              </select>
            </div>
            <div>
              <label>Relationship Type:</label>
              <select
                value={relType}
                onChange={e => setRelType(e.target.value)}
                style={{ width: '100%', background: '#1e293b', border: '1px solid #475569', color: '#f8fafc', padding: '4px', borderRadius: '4px' }}
              >
                {RELATIONSHIP_TYPES.map(rt => <option key={rt} value={rt}>{rt}</option>)}
              </select>
            </div>
            <button
              onClick={handleAddRelationship}
              disabled={!targetKnowledgeId}
              style={{ background: '#3b82f6', color: 'white', border: 'none', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', marginTop: '4px' }}
            >
              Add Relationship
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
export default KnowledgeTab;
