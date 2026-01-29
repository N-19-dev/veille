import { useEffect, useRef } from 'react';
import { Linking } from 'react-native';
import * as Notifications from 'expo-notifications';
import { useAuth } from './AuthContext';
import {
  registerForPushNotifications,
  removePushToken,
  addNotificationListener,
  addNotificationResponseListener,
} from './notifications';

export function useNotifications() {
  const { user } = useAuth();
  const notificationListener = useRef<Notifications.Subscription>();
  const responseListener = useRef<Notifications.Subscription>();

  useEffect(() => {
    if (user) {
      // Register for push notifications when user logs in
      registerForPushNotifications(user.uid);
    }

    // Handle notification received while app is foregrounded
    notificationListener.current = addNotificationListener((notification) => {
      console.log('Notification received:', notification);
    });

    // Handle notification tap
    responseListener.current = addNotificationResponseListener((response) => {
      const data = response.notification.request.content.data;

      // Handle navigation based on notification type
      if (data?.type === 'new_digest') {
        // Navigate to home / refresh
        console.log('New digest available');
      } else if (data?.type === 'comment_reply') {
        // Could open the article or comments modal
        console.log('Comment reply:', data.articleId);
      } else if (data?.url) {
        // Open URL if provided
        Linking.openURL(data.url as string);
      }
    });

    return () => {
      if (notificationListener.current) {
        Notifications.removeNotificationSubscription(notificationListener.current);
      }
      if (responseListener.current) {
        Notifications.removeNotificationSubscription(responseListener.current);
      }
    };
  }, [user]);

  // Cleanup token on logout
  useEffect(() => {
    return () => {
      if (user) {
        // Token cleanup is handled by AuthContext on logout
      }
    };
  }, [user]);
}
