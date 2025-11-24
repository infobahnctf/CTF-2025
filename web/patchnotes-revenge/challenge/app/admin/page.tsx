'use client';
import React, { useState } from 'react';

export default function AdminPreviewPage() {
  const [file, setFile] = useState('patch-1.0.3.json');
  const [resp, setResp] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function preview() {
    setLoading(true);
    setResp(null);
    try {
      const r = await fetch('/admin/api/preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file }),
      });
      const j = await r.json();
      setResp(j);
    } catch (e) {
      setResp({ error: 'fetch failed' });
    }
    setLoading(false);
  }

  return (
    <div style={{ padding: 24, fontFamily: 'Inter, system-ui, -apple-system, Roboto', color: '#111' }}>
      <header style={{ marginBottom: 18 }}>
        <h1 style={{ margin: 0 }}>PatchNotes CMS — Admin Preview</h1>
        <p style={{ margin: '6px 0 0', color: '#666' }}>
          Preview how a public note will look.
        </p>
      </header>

      <div style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
        <div style={{ minWidth: 420 }}>
          <div style={{ marginBottom: 12 }}>
            <label style={{ marginRight: 8 }}>File to preview:</label>
            <input
              value={file}
              onChange={(e) => setFile(e.target.value)}
              style={{ width: 360, padding: '6px 8px', borderRadius: 6, border: '1px solid #ddd' }}
            />
            <button onClick={preview} style={{ marginLeft: 8, padding: '6px 10px' }}>
              Preview
            </button>
          </div>

          {loading && <div style={{ color: '#444' }}>Rendering preview…</div>}
          {resp?.error && (
            <div style={{ color: 'crimson', marginTop: 8 }}>
              Error: {resp.error}
            </div>
          )}

        </div>

        <div style={{ flex: 1, minWidth: 320 }}>
          <div
            style={{
              border: '1px solid #e6e6e6',
              padding: 12,
              borderRadius: 8,
              background: '#fff',
              minHeight: 240,
              maxHeight: '60vh',
              overflow: 'auto',
              boxShadow: '0 1px 2px rgba(0,0,0,0.03)',
            }}
          >
            <h3 style={{ marginTop: 0, marginBottom: 8 }}>Rendered Preview</h3>

            {resp?.rendered ? (
              <div
                style={{
                  minHeight: 120,
                  overflow: 'auto',
                }}
                dangerouslySetInnerHTML={{ __html: resp.rendered }}
              />
            ) : (
              <div style={{ color: '#999' }}>No preview yet — choose a file and click Preview.</div>
            )}
          </div>

          {resp && !resp.error && (
            <div style={{ marginTop: 12 }}>
              <strong>Server response</strong>
              <pre
                style={{
                  background: '#f7f7f8',
                  padding: 10,
                  borderRadius: 6,
                  maxHeight: '20vh',
                  overflow: 'auto',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {JSON.stringify(resp, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}