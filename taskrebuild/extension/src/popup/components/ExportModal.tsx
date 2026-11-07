import React, { useState } from 'react';

interface ExportModalProps {
  task: any;
  resources: any[];
  activities: any[];
  aiAnalysis: any;
  onClose: () => void;
}

export const ExportModal: React.FC<ExportModalProps> = ({
  task,
  resources,
  activities,
  aiAnalysis,
  onClose,
}) => {
  const [format, setFormat] = useState<'markdown' | 'json' | 'obsidian'>('markdown');
  const [copied, setCopied] = useState(false);

  const generateMarkdown = (isObsidian = false) => {
    const createdDate = new Date(task.created_at || Date.now()).toISOString().split('T')[0];
    const tags = (aiAnalysis?.result?.topics || []).map((t: any) => `#${String(t.name || t).replace(/\s+/g, '-')}`).join(' ');

    let doc = '';

    if (isObsidian) {
      // Serialize title safely in YAML frontmatter to escape quotes, backslashes, and newlines
      const safeTitle = JSON.stringify(task.name || 'Untitled Task');
      doc += `---\ntitle: ${safeTitle}\ndate: ${createdDate}\ntype: research-brief\nsource: TaskRebuild\n---\n\n`;
    }

    doc += `# ${task.name}\n\n`;
    doc += `> **Captured with TaskRebuild** — ${createdDate}\n\n`;

    if (tags) {
      doc += `**Topics:** ${tags}\n\n`;
    }

    // AI Executive Summary
    if (aiAnalysis?.result?.task_summary) {
      doc += `## Executive Summary\n\n${aiAnalysis.result.task_summary}\n\n`;
    }

    // Topics & Concepts
    if (aiAnalysis?.result?.topics && aiAnalysis.result.topics.length > 0) {
      doc += `## Extracted Topics\n\n`;
      aiAnalysis.result.topics.forEach((topic: any) => {
        const name = topic.name || topic;
        const confidence = topic.confidence ? ` *(Confidence: ${Math.round(topic.confidence * 100)}%)*` : '';
        doc += `- ${isObsidian ? `[[${name}]]` : `**${name}**`}${confidence}\n`;
      });
      doc += '\n';
    }

    // Curated Resources
    doc += `## Curated Resources (${resources.length})\n\n`;
    if (resources.length === 0) {
      doc += `*No web resources saved for this task.*\n\n`;
    } else {
      resources.forEach((r, idx) => {
        const title = r.title || 'Untitled Resource';
        doc += `${idx + 1}. [${title}](${r.url})\n`;
      });
      doc += '\n';
    }

    // Resource Analysis
    if (aiAnalysis?.result?.resource_analysis && aiAnalysis.result.resource_analysis.length > 0) {
      doc += `## Resource Insights & Relevance\n\n`;
      aiAnalysis.result.resource_analysis.forEach((ra: any) => {
        const res = resources.find((x) => x.id === ra.resource_id);
        const name = res ? res.title || res.url : ra.resource_id;
        doc += `### ${name}\n`;
        doc += `- **Relevance:** ${ra.relevance || 'Medium'}\n`;
        if (ra.reason) doc += `- **Key Insight:** ${ra.reason}\n`;
        doc += '\n';
      });
    }

    // Next Steps
    if (aiAnalysis?.result?.suggested_next_steps && aiAnalysis.result.suggested_next_steps.length > 0) {
      doc += `## Recommended Next Steps\n\n`;
      aiAnalysis.result.suggested_next_steps.forEach((step: string) => {
        doc += `- [ ] ${step}\n`;
      });
      doc += '\n';
    }

    // Activity Log
    if (activities.length > 0) {
      doc += `## Activity Timeline (${activities.length} events)\n\n`;
      activities.slice(0, 30).forEach((act) => {
        const dateObj = new Date(act.timestamp);
        const dateStr = dateObj.toISOString().split('T')[0];
        const timeStr = dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        doc += `- \`${dateStr} ${timeStr}\` **${act.event_type}**: [${act.title || act.url}](${act.url})\n`;
      });
      doc += '\n';
    }

    return doc;
  };

  const generateJSON = () => {
    return JSON.stringify(
      {
        task,
        summary: aiAnalysis?.result?.task_summary || null,
        topics: aiAnalysis?.result?.topics || [],
        suggested_next_steps: aiAnalysis?.result?.suggested_next_steps || [],
        resource_analysis: aiAnalysis?.result?.resource_analysis || [],
        resources: resources.map((r) => ({ id: r.id, title: r.title, url: r.url, created_at: r.created_at })),
        recent_activity: activities.map((a) => ({ type: a.event_type, title: a.title, url: a.url, time: a.timestamp })),
        exported_at: new Date().toISOString(),
      },
      null,
      2
    );
  };

  const getOutputText = () => {
    if (format === 'json') return generateJSON();
    if (format === 'obsidian') return generateMarkdown(true);
    return generateMarkdown(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getOutputText());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const text = getOutputText();
    const extension = format === 'json' ? 'json' : 'md';
    const filename = `${task.name.replace(/[^a-z0-9_-]/gi, '_').toLowerCase()}-brief.${extension}`;
    const blob = new Blob([text], { type: format === 'json' ? 'application/json' : 'text/markdown;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.65)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        padding: '16px',
      }}
    >
      <div
        style={{
          background: 'var(--bg-primary, #ffffff)',
          color: 'var(--text-primary, #1e293b)',
          borderRadius: '10px',
          width: '100%',
          maxWidth: '520px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3)',
          border: '1px solid var(--border-color, #cbd5e1)',
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: '12px 16px',
            borderBottom: '1px solid var(--border-color, #cbd5e1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700 }}>Export Research Brief</h3>
            <p style={{ margin: 0, fontSize: '11px', color: 'var(--text-muted, #64748b)' }}>
              {task.name}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '16px',
              cursor: 'pointer',
              color: 'var(--text-muted, #64748b)',
            }}
          >
            ✕
          </button>
        </div>

        {/* Format Selector */}
        <div style={{ padding: '10px 16px', background: 'var(--bg-subtle, #f8fafc)', borderBottom: '1px solid var(--border-subtle, #e2e8f0)', display: 'flex', gap: '8px' }}>
          {[
            { id: 'markdown', label: '📄 Markdown' },
            { id: 'obsidian', label: '🔮 Obsidian Note' },
            { id: 'json', label: '📦 JSON Data' },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => setFormat(item.id as any)}
              style={{
                padding: '4px 10px',
                fontSize: '11px',
                borderRadius: '4px',
                border: 'none',
                cursor: 'pointer',
                fontWeight: format === item.id ? 700 : 500,
                background: format === item.id ? 'var(--accent-indigo, #6366f1)' : 'transparent',
                color: format === item.id ? '#ffffff' : 'var(--text-secondary, #475569)',
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        {/* Preview Code View */}
        <div style={{ padding: '12px 16px', flex: 1, overflowY: 'auto' }}>
          <textarea
            readOnly
            value={getOutputText()}
            style={{
              width: '100%',
              height: '240px',
              fontFamily: 'monospace',
              fontSize: '11px',
              lineHeight: 1.45,
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid var(--border-color, #cbd5e1)',
              backgroundColor: 'var(--bg-card, #f1f5f9)',
              color: 'var(--text-primary, #0f172a)',
              resize: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>

        {/* Footer Actions */}
        <div
          style={{
            padding: '12px 16px',
            borderTop: '1px solid var(--border-color, #cbd5e1)',
            display: 'flex',
            justifyContent: 'flex-end',
            gap: '8px',
          }}
        >
          <button
            onClick={onClose}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              background: 'transparent',
              border: '1px solid var(--border-color, #cbd5e1)',
              borderRadius: '4px',
              cursor: 'pointer',
              color: 'var(--text-secondary, #475569)',
            }}
          >
            Close
          </button>
          <button
            onClick={handleCopy}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              background: copied ? 'var(--accent-emerald, #10b981)' : 'var(--bg-card, #e2e8f0)',
              color: copied ? '#ffffff' : 'var(--text-primary, #0f172a)',
              border: '1px solid var(--border-color, #cbd5e1)',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            {copied ? '✓ Copied!' : 'Copy to Clipboard'}
          </button>
          <button
            onClick={handleDownload}
            style={{
              padding: '6px 14px',
              fontSize: '12px',
              background: 'var(--accent-indigo, #6366f1)',
              color: '#ffffff',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer',
              fontWeight: 600,
            }}
          >
            Download .{format === 'json' ? 'json' : 'md'}
          </button>
        </div>
      </div>
    </div>
  );
};
