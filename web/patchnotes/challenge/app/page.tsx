'use client';
import React, { useState } from 'react';

export default function NotesPage() {
  const [file, setFile] = useState('patch-1.0.3.json');
  const [resp, setResp] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [editText, setEditText] = useState('');
  const [message, setMessage] = useState('');

  async function fetchFile() {
    setLoading(true);
    setMessage('');
    setResp(null);
    try {
      const r = await fetch(`/api/notes/read?file=${encodeURIComponent(file)}`);
      const j = await r.json();
      setResp(j);
      if (j?.content) setEditText(j.content);
    } catch (e) {
      setResp({ error: 'fetch error' });
    }
    setLoading(false);
  }

  async function saveFile() {
    setMessage('');
    try {
      const r = await fetch('/api/notes/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file, content: editText }),
      });
      const j = await r.json();
      if (j?.ok) setMessage('Saved');
      else setMessage('Save failed: ' + (j?.error ?? 'unknown'));
    } catch (e) {
      setMessage('Save error');
    }
  }

  return (
    <div style={{ padding: 24, fontFamily: 'Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial' }}>
      <header style={{ marginBottom: 18 }}>
        <h1 style={{ margin: 0 }}>PatchNotes CMS — Viewer & Editor</h1>
        <p style={{ margin: '6px 0 0', color: '#666' }}>
          Edit public patch notes and plain-text community posts. Allowed extensions: <code>.json</code>, <code>.txt</code>.
        </p>
      </header>

      <div style={{ marginBottom: 12 }}>
        <label style={{ marginRight: 8 }}>File:</label>
        <input value={file} onChange={e => setFile(e.target.value)} style={{ width: 420, padding: '6px 8px' }} />
        <button onClick={fetchFile} style={{ marginLeft: 8, padding: '6px 10px' }}>View</button>
      </div>

      {loading && <p>Loading…</p>}

      {resp && !resp.error && (
        <section style={{ marginTop: 12 }}>
          <h3 style={{ marginTop: 0 }}>File: {resp.filename}</h3>

          {resp?.json ? (
            <div style={{ marginBottom: 10 }}>
              <strong>Parsed JSON</strong>
              <pre style={{ background: '#f7f7f8', padding: 10 }}>{JSON.stringify(resp.json, null, 2)}</pre>
            </div>
          ) : null}

          <div>
            <strong>Raw content</strong>
            <textarea value={editText} onChange={e => setEditText(e.target.value)} rows={12} cols={90} style={{ display: 'block', marginTop: 6 }} />
          </div>

          <div style={{ marginTop: 8 }}>
            <button onClick={saveFile} style={{ padding: '6px 10px' }}>Save</button>
            <span style={{ marginLeft: 12 }}>{message}</span>
          </div>
        </section>
      )}
    </div>
  );
}
