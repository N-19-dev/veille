import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { auth, googleProvider } from './firebase';
import { onAuthStateChanged, signInWithRedirect, getRedirectResult, type User } from 'firebase/auth';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  openLoginModal: () => void;
  closeLoginModal: () => void;
  isLoginModalOpen: boolean;
  signInWithGoogle: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  useEffect(() => {
    console.log('[Auth] Initializing...');

    // Handle redirect result first (for when user comes back from Google)
    getRedirectResult(auth)
      .then((result) => {
        if (result?.user) {
          console.log('[Auth] Redirect login successful:', result.user.email);
          setIsLoginModalOpen(false);
        }
      })
      .catch((error) => {
        console.error('[Auth] Redirect error:', error);
      });

    // Set a timeout to prevent infinite loading
    const loadingTimeout = setTimeout(() => {
      console.log('[Auth] Loading timeout - forcing ready state');
      setLoading(false);
    }, 5000);

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      console.log('[Auth] Auth state changed:', currentUser?.email || 'no user');
      clearTimeout(loadingTimeout);
      setUser(currentUser);
      setLoading(false);
    });

    return () => {
      clearTimeout(loadingTimeout);
      unsubscribe();
    };
  }, []);

  const signInWithGoogle = async () => {
    try {
      console.log('[Auth] Starting Google sign in with redirect...');
      await signInWithRedirect(auth, googleProvider);
      // User will be redirected to Google, then back to the app
    } catch (error: unknown) {
      const firebaseError = error as { code?: string; message?: string };
      console.error('[Auth] Sign in error:', firebaseError.code, firebaseError.message);
      throw error;
    }
  };

  const openLoginModal = () => setIsLoginModalOpen(true);
  const closeLoginModal = () => setIsLoginModalOpen(false);

  return (
    <AuthContext.Provider value={{ user, loading, openLoginModal, closeLoginModal, isLoginModalOpen, signInWithGoogle }}>
      {children}
    </AuthContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
