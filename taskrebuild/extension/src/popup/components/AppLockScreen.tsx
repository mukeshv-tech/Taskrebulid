import React, { useState, useEffect } from 'react';
import { hashPassword } from '../../lib/crypto';
import { verifyBiometrics, isBiometricsAvailable } from '../../lib/webauthn';

interface AppLockScreenProps {
  salt: string;
  expectedHash: string;
  biometricCredentialId?: string | null;
  onUnlock: () => void;
  onResetAccount: () => void;
}

export const AppLockScreen: React.FC<AppLockScreenProps> = ({
  salt,
  expectedHash,
  biometricCredentialId,
  onUnlock,
  onResetAccount
}) => {
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [bioLoading, setBioLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [hasBiometrics, setHasBiometrics] = useState(false);

  useEffect(() => {
    isBiometricsAvailable().then((available) => {
      setHasBiometrics(available && !!biometricCredentialId);
      // Auto-trigger biometric prompt if credential is saved
      if (available && biometricCredentialId) {
        handleBiometricUnlock(biometricCredentialId);
      }
    });
  }, [biometricCredentialId]);

  const handleBiometricUnlock = async (credIdToUse?: string) => {
    const targetId = credIdToUse || biometricCredentialId;
    if (!targetId) return;

    setBioLoading(true);
    setError('');
    try {
      const verified = await verifyBiometrics(targetId);
      if (verified) {
        onUnlock();
      }
    } catch (err: any) {
      console.warn('Biometric unlock failed:', err);
      // If user cancelled, don't scream error, just fall back to password
      if (err?.message?.includes('cancelled')) {
        setError('Biometric authentication cancelled. Enter your password.');
      } else {
        setError(err?.message || 'Biometric authentication failed.');
      }
    } finally {
      setBioLoading(false);
    }
  };

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
        Unlock using Windows Hello / Touch ID or your master password.
      </p>

      {/* Biometric Quick Unlock Button */}
      {hasBiometrics && (
        <div style={{ marginBottom: '18px' }}>
          <button
            type="button"
            onClick={() => handleBiometricUnlock()}
            disabled={bioLoading}
            style={{
              width: '100%',
              padding: '11px',
              background: '#0ea5e9',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '13px',
              fontWeight: 600,
              cursor: bioLoading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              transition: 'background 0.15s ease'
            }}
          >
            <span>👆</span>
            <span>{bioLoading ? 'Scanning Biometrics...' : 'Unlock with Windows Hello / Touch ID'}</span>
          </button>
          <div style={{ display: 'flex', alignItems: 'center', margin: '14px 0', color: '#94a3b8' }}>
            <div style={{ flex: 1, height: '1px', background: '#e2e8f0' }} />
            <span style={{ padding: '0 10px', fontSize: '11px', textTransform: 'uppercase' }}>or password</span>
            <div style={{ flex: 1, height: '1px', background: '#e2e8f0' }} />
          </div>
        </div>
      )}

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
            placeholder="Enter master password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoFocus={!hasBiometrics}
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
          {loading ? 'Verifying...' : 'Unlock with Password'}
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
