# Push Notifications Setup

This guide explains how to set up push notifications for the Veille Tech mobile app.

## Overview

The notification system supports:
1. **Weekly digest** - Notify all users when new Top 3 is available
2. **Comment replies** - Notify when someone replies to your comment
3. **Vote milestones** - Notify when an article you liked reaches 5, 10, 25, 50, or 100 votes

## Architecture

```
Mobile App (Expo)
    ↓ registers push token
Firebase Firestore (push_tokens collection)
    ↓ triggers on new comments/votes
Firebase Cloud Functions
    ↓ sends via
Expo Push Notification Service
    ↓ delivers to
iOS/Android devices
```

## Setup Steps

### 1. Configure Expo Project

Add your Expo project ID to `mobile/app.json`:

```json
{
  "expo": {
    "extra": {
      "eas": {
        "projectId": "your-expo-project-id"
      }
    }
  }
}
```

Get your project ID from [expo.dev](https://expo.dev).

### 2. Deploy Firebase Cloud Functions

```bash
cd functions
npm install
firebase deploy --only functions
```

Set the notification API key:

```bash
firebase functions:config:set notification.api_key="your-secret-key"
```

### 3. Configure Backend Environment

Add to `backend/.env`:

```
NOTIFICATION_FUNCTION_URL=https://your-region-your-project.cloudfunctions.net/sendWeeklyDigest
NOTIFICATION_API_KEY=your-secret-key
```

### 4. Update GitHub Actions (Optional)

Add to weekly pipeline after digest generation:

```yaml
- name: Send push notification
  run: python send_push_notification.py
  env:
    NOTIFICATION_FUNCTION_URL: ${{ secrets.NOTIFICATION_FUNCTION_URL }}
    NOTIFICATION_API_KEY: ${{ secrets.NOTIFICATION_API_KEY }}
```

## Firestore Collections

### push_tokens

Stores user push tokens:

```json
{
  "userId": "user-uid",
  "token": "ExponentPushToken[xxx]",
  "platform": "ios",
  "updatedAt": "2025-01-29T12:00:00Z"
}
```

## Testing

### Test on Device

Push notifications only work on physical devices, not simulators.

1. Build development client: `npx expo run:ios` or `npx expo run:android`
2. Log in to the app
3. Grant notification permissions
4. Add a comment reply in Firebase console to test

### Test Weekly Digest

```bash
curl -X POST https://your-function-url/sendWeeklyDigest \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"weekLabel": "2025w05", "title": "Test notification"}'
```

## Notification Types

| Type | Trigger | Data |
|------|---------|------|
| `new_digest` | Weekly pipeline | `weekLabel` |
| `comment_reply` | New reply to comment | `articleId`, `commentId` |
| `vote_milestone` | Article reaches 5/10/25/50/100 votes | `articleId`, `voteCount` |
