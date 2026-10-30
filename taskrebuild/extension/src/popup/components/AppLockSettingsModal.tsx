import React, { useState } from 'react';
import { hashPassword, generateSalt } from '../../lib/crypto';

interface AppLockSettingsModalProps {
  hasLock: boolean;
  salt?: string;
  expectedHash?: string;
  onClose: () => void;
  onSaveLock: (newSalt: string, newHash: string) => void;
  onDisableLock: () => void;
}

export const AppLockSettingsModal: React.FC<AppLockSettingsModalProps> = ({
  hasLock,
  salt,
  expectedHash,
  onClose,
  onSaveLock,
  onDisableLock
}) => {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // If changing existing lock, verify current password first
    if (hasLock && salt && expectedHash) {
      const currentHashed = await hashPassword(currentPassword, salt);
      if (currentHashed !== expectedHash) {
        setError('Current password is incorrect.');
        return;
      }
    }

    if (newPassword.length < 4) {
      setError('New password must be at least 4 characters.');
      return;
    }

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const newSalt = generateSalt();
      const newHash = await hashPassword(newPassword, newSalt);
      onSaveLock(newSalt, newHash);
      setSuccess('App lock password updated successfully!');
      setTimeout(() => {
        onClose();
      }, 1000);
    } catch (err: any) {
      setError(err?.message || 'Failed to update lock password.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable = async () => {
    if (hasLock && salt && expectedHash) {
      const currentHashed = await hashPassword(currentPassword, salt);
      if (currentHashed !== expectedHash) {
        setError('Please enter your current password to disable App Lock.');
        return;
      }
    }
    if (confirm('Are you sure you want to remove password protection from opening the extension?')) {
      onDisableLock();
      onClose();
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.65)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 99999,
        padding: '16px'
      }}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '10px',
          padding: '20px',
          width: '100%',
          maxWidth: '350px',
          boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.2)',
          color: '#1e293b',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span>🔒</span> {hasLock ? 'Change Master Password' : 'Set Master Password'}
          </h3>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', fontSize: '18px', color: '#94a3b8', cursor: 'pointer' }}
          >
            &times;
          </button>
        </div>

        <p style={{ margin: '0 0 14px 0', fontSize: '12px', color: '#64748b' }}>
          {hasLock
            ? 'Update your master password or disable password protection.'
            : 'Protect TaskRebuild with a master password required whenever the extension is opened.'}
        </p>

        {error && (
          <div style={{ background: '#fee2e2', color: '#dc2626', padding: '8px', borderRadius: '4px', fontSize: '11px', marginBottom: '12px' }}>
            {error}
          </div>
        )}
        {success && (
          <div style={{ background: '#dcfce7', color: '#16a34a', padding: '8px', borderRadius: '4px', fontSize: '11px', marginBottom: '12px' }}>
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {hasLock && (
            <div>
              <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#475569', marginBottom: '4px' }}>
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                placeholder="Enter current password"
                required
                style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '12px', boxSizing: 'border-box' }}
              />
            </div>
          )}

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#475569', marginBottom: '4px' }}>
              {hasLock ? 'New Password' : 'Create Password'}
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="At least 4 characters"
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '12px', boxSizing: 'border-box' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '11px', fontWeight: 600, color: '#475569', marginBottom: '4px' }}>
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm new password"
              required
              style={{ width: '100%', padding: '8px', borderRadius: '4px', border: '1px solid #cbd5e1', fontSize: '12px', boxSizing: 'border-box' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '8px', marginTop: '6px' }}>
            <button
              type="submit"
              disabled={loading}
              style={{
                flex: 1,
                padding: '8px',
                background: '#4f46e5',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '12px',
                fontWeight: 600,
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              {loading ? 'Saving...' : hasLock ? 'Update Password' : 'Set Password'}
            </button>
            <button
              type="button"
              onClick={onClose}
              style={{
                padding: '8px 12px',
                background: '#f1f5f9',
                color: '#475569',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: 'pointer'
              }}
            >
              Cancel
            </button>
          </div>
        </form>

        {hasLock && (
          <div style={{ marginTop: '14px', paddingTop: '12px', borderTop: '1px solid #f1f5f9', textAlign: 'center' }}>
            <button
              type="button"
              onClick={handleDisable}
              style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '11px', cursor: 'pointer', fontWeight: 600 }}
            >
              Disable Password Protection
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
