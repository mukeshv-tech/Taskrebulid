// WebAuthn Biometrics Helper (Windows Hello, Touch ID, Face ID, Security Keys)

export interface BiometricCredential {
  id: string; // base64url encoded credential ID
  rawId: string;
}

// Convert ArrayBuffer to Base64URL string
export function bufferToBase64Url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

// Convert Base64URL string back to Uint8Array
export function base64UrlToBuffer(base64url: string): Uint8Array {
  const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
  const pad = base64.length % 4 === 0 ? '' : '='.repeat(4 - (base64.length % 4));
  const binary = atob(base64 + pad);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

// Check if device supports platform biometric authentication (Windows Hello / Touch ID)
export async function isBiometricsAvailable(): Promise<boolean> {
  if (
    typeof window === 'undefined' ||
    !window.PublicKeyCredential ||
    !window.crypto
  ) {
    return false;
  }

  try {
    if (PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable) {
      return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    }
  } catch (e) {
    console.warn('Biometric platform authenticator check failed:', e);
  }
  return false;
}

// Register a biometric credential using WebAuthn
export async function registerBiometrics(userName: string = 'TaskRebuild User'): Promise<BiometricCredential> {
  const challenge = new Uint8Array(32);
  crypto.getRandomValues(challenge);

  const userId = new Uint8Array(16);
  crypto.getRandomValues(userId);

  const publicKeyCredentialCreationOptions: PublicKeyCredentialCreationOptions = {
    challenge,
    rp: {
      name: 'TaskRebuild',
      id: window.location.hostname || undefined,
    },
    user: {
      id: userId,
      name: userName,
      displayName: userName,
    },
    pubKeyCredParams: [
      { alg: -7, type: 'public-key' },  // ES256
      { alg: -257, type: 'public-key' } // RS256
    ],
    authenticatorSelection: {
      authenticatorAttachment: 'platform', // Built-in: Windows Hello / Touch ID
      userVerification: 'required',
      residentKey: 'preferred',
    },
    timeout: 60000,
    attestation: 'none'
  };

  const credential = (await navigator.credentials.create({
    publicKey: publicKeyCredentialCreationOptions,
  })) as PublicKeyCredential | null;

  if (!credential) {
    throw new Error('Biometric registration was cancelled or not supported.');
  }

  const credentialId = bufferToBase64Url(credential.rawId);
  return {
    id: credentialId,
    rawId: credentialId,
  };
}

// Verify user via Windows Hello / Touch ID biometric challenge
export async function verifyBiometrics(credentialId: string): Promise<boolean> {
  const challenge = new Uint8Array(32);
  crypto.getRandomValues(challenge);

  const rawIdBuffer = base64UrlToBuffer(credentialId);

  const publicKeyCredentialRequestOptions: PublicKeyCredentialRequestOptions = {
    challenge,
    rpId: window.location.hostname || undefined,
    allowCredentials: [
      {
        id: rawIdBuffer as any,
        type: 'public-key',
        transports: ['internal'],
      },
    ],
    userVerification: 'required',
    timeout: 60000,
  };

  try {
    const assertion = await navigator.credentials.get({
      publicKey: publicKeyCredentialRequestOptions,
    });
    return !!assertion;
  } catch (err: any) {
    if (err?.name === 'NotAllowedError') {
      throw new Error('Biometric prompt was cancelled or verification failed.');
    }
    throw err;
  }
}
