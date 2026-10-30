import React, { useState } from 'react';
import { hashPassword } from '../../lib/crypto';

interface AppLockScreenProps {
  salt: string;
  expectedHash: string;
  onUnlock: () => void;
  onResetAccount: () => void;
}

export const AppLockScreen: React.FC<AppLockScreenProps> = ({
  salt,
  expectedHash,
  onUnlock,
  onResetAccount
}) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  const handleUnlock = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!password) return;
    setLoading(true);
    setError('');

    try {
      const hashedInput = await hashPassword(password, salt);
      if (hashedInput === expectedHash) {
        onUnlock();
      } else {
        setError('Incorrect password. Please try again.');
        setPassword('');
      }
    } catch (err: any) {
      setError(err?.message || 'Failed to verify password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        padding: '30px 20px',
        maxWidth: '380px',
        margin: '0 auto',
        fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        textAlign: 'center',
        color: '#1e293b'
      }}
    >
      <div
        style={{
          width: '54px',
          height: '54px',
          borderRadius: '50%',
          background: '#e0e7ff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          margin: '0 auto 16px auto',
          color: '#4f46e5',
          fontSize: '24px'
        }}
      >
        🔒
      </div>

      <h2 style={{ margin: '0 0 6px 0', fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>
        TaskRebuild Locked
      </h2>
      <p style={{ margin: '0 0 20px 0', fontSize: '12px', color: '#64748b' }}>
        Enter your master password to access your tasks and research.
      </p>

      {error && (
        <div
          style={{
            background: '#fee2e2',
            color: '#dc2626',
            padding: '8px 12px',
            borderRadius: '6px',
            fontSize: '12px',
            marginBottom: '14px',
            textAlign: 'left'
          }}
        >
          {error}
        </div>
      )}

      <form onSubmit={handleUnlock} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ position: 'relative' }}>
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoFocus
            required
            style={{
              width: '100%',
              padding: '10px 38px 10px 12px',
              borderRadius: '6px',
              border: '1px solid #cbd5e1',
              fontSize: '13px',
              outline: 'none',
              boxSizing: 'border-box'
            }}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            style={{
              position: 'absolute',
              right: '8px',
              top: '50%',
              transform: 'translateY(-50%)',
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#94a3b8',
              fontSize: '13px',
              padding: '4px'
            }}
            title={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? '👁️' : '🔒'}
          </button>
        </div>

        <button
          type="submit"
          disabled={loading || !password}
          style={{
            padding: '10px',
            background: '#4f46e5',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: loading || !password ? 'not-allowed' : 'pointer',
            opacity: loading || !password ? 0.7 : 1,
            transition: 'background 0.15s ease'
          }}
        >
          {loading ? 'Verifying...' : 'Unlock Extension'}
        </button>
      </form>

      <div style={{ marginTop: '24px', borderTop: '1px solid #f1f5f9', paddingTop: '16px' }}>
        <button
          type="button"
          onClick={() => {
            if (confirm('Forgot your password? You can sign out and re-authenticate via your Supabase account to reset your password lock.')) {
              onResetAccount();
            }
          }}
          style={{
            background: 'none',
            border: 'none',
            color: '#64748b',
            fontSize: '11px',
            cursor: 'pointer',
            textDecoration: 'underline'
          }}
        >
          Forgot password? Sign out & reset lock
        </button>
      </div>
    </div>
  );
};
