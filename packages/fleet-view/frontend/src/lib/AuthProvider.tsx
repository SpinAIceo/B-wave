import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react';
import {
  type AuthUser,
  clearStoredAuth,
  getStoredUser,
  login as loginApi,
  logout as logoutApi,
} from './auth';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  /** Called by the API layer when a 401 is received — forces re-login. */
  forceLogout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());

  // Re-check stored token periodically — drop if expired.
  //
  // BUG FIX: previous code compared object references with `!==`. Since
  // `getStoredUser()` calls JSON.parse and returns a fresh object every time,
  // the comparison was always true and `setUser` ran every interval, forcing
  // the whole subtree to re-render. Now we compare by token expiry which is
  // the only field that actually changes.
  useEffect(() => {
    const id = setInterval(() => {
      const fresh = getStoredUser();
      setUser(prev => {
        if (prev === null && fresh === null) return prev;
        if (prev?.expiresAt === fresh?.expiresAt && prev?.username === fresh?.username) {
          return prev;
        }
        return fresh;
      });
    }, 60_000);
    return () => clearInterval(id);
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const u = await loginApi(username, password);
    setUser(u);
  }, []);

  const logout = useCallback(() => {
    logoutApi();
    setUser(null);
  }, []);

  const forceLogout = useCallback(() => {
    clearStoredAuth();
    setUser(null);
  }, []);

  // Wire forceLogout into a global hook so api.ts can call it on 401
  useEffect(() => {
    (window as unknown as { __bwaveForceLogout?: () => void }).__bwaveForceLogout = forceLogout;
    return () => {
      delete (window as unknown as { __bwaveForceLogout?: () => void }).__bwaveForceLogout;
    };
  }, [forceLogout]);

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: user !== null, login, logout, forceLogout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider');
  return ctx;
}
