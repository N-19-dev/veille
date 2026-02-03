import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { auth, googleProvider } from './firebase';
import { onAuthStateChanged, getRedirectResult, signInWithRedirect, signInWithPopup, type User } from 'firebase/auth';

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
    // Handle redirect result when page loads
    getRedirectResult(auth)
      .then((result) => {
        if (result?.user) {
          setIsLoginModalOpen(false);
        }
      })
      .catch((error) => {
        console.error('Redirect sign in error:', error);
      });

    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const signInWithGoogle = async () => {
    try {
      // Try popup first (better UX on desktop)
      const result = await signInWithPopup(auth, googleProvider);
      if (result.user) {
        setIsLoginModalOpen(false);
      }
    } catch (error: unknown) {
      const firebaseError = error as { code?: string };
      // If popup blocked, fall back to redirect
      if (firebaseError.code === 'auth/popup-blocked' || firebaseError.code === 'auth/popup-closed-by-user') {
        console.log('Popup blocked, falling back to redirect...');
        await signInWithRedirect(auth, googleProvider);
      } else {
        console.error('Sign in error:', error);
        throw error;
      }
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
