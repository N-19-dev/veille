import { View, Text, Pressable, Image } from 'react-native';
import { useAuth } from '../lib/AuthContext';
import { auth } from '../lib/firebase';
import { signOut } from 'firebase/auth';

export default function AuthButton() {
  const { user, loading, openLoginModal } = useAuth();

  const handleLogout = async () => {
    try {
      await signOut(auth);
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  if (loading) {
    return null;
  }

  if (user) {
    return (
      <Pressable
        onPress={handleLogout}
        className="active:opacity-70"
      >
        {user.photoURL ? (
          <Image
            source={{ uri: user.photoURL }}
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <View className="w-8 h-8 rounded-full bg-neutral-200 items-center justify-center">
            <Text className="text-neutral-600 text-sm font-bold">
              {user.email?.charAt(0).toUpperCase() || '?'}
            </Text>
          </View>
        )}
      </Pressable>
    );
  }

  return (
    <Pressable
      onPress={openLoginModal}
      className="bg-neutral-900 rounded-lg px-4 py-2 active:bg-neutral-700"
    >
      <Text className="text-sm text-white font-medium">Connexion</Text>
    </Pressable>
  );
}
