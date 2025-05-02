import React, { useEffect, useState } from 'react';
import { fetchHealth } from '../../api/healthApi';

export default function LLMStatus() {
  const [llm, setLlm] = useState<{ ok: boolean; msg: string; model?: string } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth()
      .then((data) => {
        setLlm(data.llm);
        setLoading(false);
      })
      .catch((e) => {
        setError('Unable to fetch backend health');
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Checking LLM status…</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!llm) return <div>LLM status unknown</div>;

  return (
    <div style={{ fontSize: 14, padding: 4 }}>
      <b>LLM:</b> {llm.model && llm.model !== 'None' ? llm.model : 'Unknown'}{' '}
      <span style={{ color: llm.ok ? 'green' : 'red', fontWeight: 500 }}>
        {llm.ok ? 'Connected' : 'Not Connected'}
      </span>
      {!llm.ok && (
        <div style={{ color: 'red', marginTop: 2 }}>
          {llm.msg}
        </div>
      )}
    </div>
  );
}
