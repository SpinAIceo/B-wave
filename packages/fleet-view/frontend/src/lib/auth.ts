/**
 * Auth helpers — JWT-based login against fleet-view backend.
 *
 * Storage: localStorage (best-effort; falls back to in-memory if unavailable).
 * The token is read by api.ts on every request to attach the Authorization header.
 */

const TOKEN_KEY = 'bwave-auth-token';
const USER_KEY = 'bwave-auth-user';

export type Role = 'admin' | 'operator' | 'viewer';

export interface AuthUser {
  username: string;
  role: Role;
  /** Unix epoch seconds. */
  expiresAt: number;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  role: Role;
  expires_in: number;
}

const API_BASE = (import.meta.env.VITE_API_URL ?? '') + '/api/v1';
const AUTH_BASE = import.meta.env.VITE_API_URL ?? '';

// ── Token / user storage ─────────────────────────────────────────────────────

export function getStoredToken(): string | null {
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getStoredUser(): AuthUser | null {
  try {
    const raw = window.localStorage.getItem(USER_KEY);
    if (!raw) return null;
    const user = JSON.parse(raw) as AuthUser;
    // Drop expired tokens proactively
    if (user.expiresAt * 1000 < Date.now()) {
      clearStoredAuth();
      return null;
    }
    return user;
  } catch {
    return null;
  }
}

function setStoredAuth(token: string, user: AuthUser): void {
  try {
    window.localStorage.setItem(TOKEN_KEY, token);
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch {
    /* ignore — in-memory only */
  }
}

export function clearStoredAuth(): void {
  try {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  } catch {
    /* ignore */
  }
}

// ── JWT helpers ──────────────────────────────────────────────────────────────

interface JwtPayload {
  sub: string;
  role: Role;
  exp: number;
}

function decodeJwt(token: string): JwtPayload | null {
  try {
    const [, payload] = token.split('.');
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

// ── Login API ────────────────────────────────────────────────────────────────

export class LoginError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'LoginError';
  }
}

/**
 * POST /auth/token with form-urlencoded credentials (OAuth2 password grant).
 * On success, stores token + user and returns the user.
 */
export async function login(username: string, password: string): Promise<AuthUser> {
  if (!AUTH_BASE) {
    throw new LoginError(0, 'API URL not configured (VITE_API_URL missing)');
  }
  const body = new URLSearchParams({ username, password });
  let resp: Response;
  try {
    resp = await fetch(`${AUTH_BASE}/auth/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body,
    });
  } catch (e) {
    throw new LoginError(0, e instanceof Error ? e.message : 'network error');
  }

  if (!resp.ok) {
    const detail = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new LoginError(resp.status, detail.detail ?? `HTTP ${resp.status}`);
  }

  const data = (await resp.json()) as TokenResponse;
  const decoded = decodeJwt(data.access_token);
  const user: AuthUser = {
    username: decoded?.sub ?? username,
    role: data.role,
    expiresAt: decoded?.exp ?? Math.floor(Date.now() / 1000) + data.expires_in,
  };
  setStoredAuth(data.access_token, user);
  return user;
}

export function logout(): void {
  clearStoredAuth();
}

// Re-exposed for api.ts
export { API_BASE };
