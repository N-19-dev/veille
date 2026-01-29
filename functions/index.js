const functions = require('firebase-functions');
const admin = require('firebase-admin');
const { Expo } = require('expo-server-sdk');

admin.initializeApp();
const db = admin.firestore();
const expo = new Expo();

// Send notification when someone replies to a comment
exports.onCommentReply = functions.firestore
  .document('comments/{commentId}')
  .onCreate(async (snap, context) => {
    const comment = snap.data();

    // Only process replies (comments with parent_id)
    if (!comment.parent_id) {
      return null;
    }

    try {
      // Get the parent comment to find the original author
      const parentDoc = await db.collection('comments').doc(comment.parent_id).get();
      if (!parentDoc.exists) {
        return null;
      }

      const parentComment = parentDoc.data();
      const parentUserId = parentComment.user_id;

      // Don't notify if replying to own comment
      if (parentUserId === comment.user_id) {
        return null;
      }

      // Get the push token for the parent comment author
      const tokenDoc = await db.collection('push_tokens').doc(parentUserId).get();
      if (!tokenDoc.exists) {
        return null;
      }

      const { token } = tokenDoc.data();

      if (!Expo.isExpoPushToken(token)) {
        console.log('Invalid Expo push token:', token);
        return null;
      }

      // Send the notification
      const messages = [{
        to: token,
        sound: 'default',
        title: 'Nouvelle réponse',
        body: `${comment.user_name} a répondu à votre commentaire`,
        data: {
          type: 'comment_reply',
          articleId: comment.article_id,
          commentId: context.params.commentId,
        },
      }];

      const chunks = expo.chunkPushNotifications(messages);
      for (const chunk of chunks) {
        await expo.sendPushNotificationsAsync(chunk);
      }

      console.log('Reply notification sent to:', parentUserId);
      return null;
    } catch (error) {
      console.error('Error sending reply notification:', error);
      return null;
    }
  });

// Send notification when article gets significant votes
exports.onVoteMilestone = functions.firestore
  .document('votes/{voteId}')
  .onCreate(async (snap, context) => {
    const vote = snap.data();

    // Only notify on upvotes
    if (vote.vote_value !== 1) {
      return null;
    }

    try {
      // Count total votes for this article
      const votesSnapshot = await db.collection('votes')
        .where('article_id', '==', vote.article_id)
        .where('week_label', '==', vote.week_label)
        .where('vote_value', '==', 1)
        .get();

      const voteCount = votesSnapshot.size;

      // Only notify on milestones (5, 10, 25, 50, 100)
      const milestones = [5, 10, 25, 50, 100];
      if (!milestones.includes(voteCount)) {
        return null;
      }

      // Get all users who have upvoted this article (they're interested)
      const interestedUsers = new Set();
      votesSnapshot.forEach((doc) => {
        const data = doc.data();
        if (data.user_id !== vote.user_id) {
          interestedUsers.add(data.user_id);
        }
      });

      // Get push tokens for interested users
      const messages = [];
      for (const userId of interestedUsers) {
        const tokenDoc = await db.collection('push_tokens').doc(userId).get();
        if (tokenDoc.exists) {
          const { token } = tokenDoc.data();
          if (Expo.isExpoPushToken(token)) {
            messages.push({
              to: token,
              sound: 'default',
              title: 'Article populaire',
              body: `Un article que vous avez liké a atteint ${voteCount} votes !`,
              data: {
                type: 'vote_milestone',
                articleId: vote.article_id,
                voteCount,
              },
            });
          }
        }
      }

      if (messages.length > 0) {
        const chunks = expo.chunkPushNotifications(messages);
        for (const chunk of chunks) {
          await expo.sendPushNotificationsAsync(chunk);
        }
        console.log(`Milestone notification sent to ${messages.length} users`);
      }

      return null;
    } catch (error) {
      console.error('Error sending milestone notification:', error);
      return null;
    }
  });

// HTTP endpoint to send weekly digest notification (called by backend)
exports.sendWeeklyDigest = functions.https.onRequest(async (req, res) => {
  // Verify secret key
  const secretKey = req.headers['x-api-key'];
  if (secretKey !== process.env.NOTIFICATION_API_KEY) {
    res.status(401).send('Unauthorized');
    return;
  }

  const { weekLabel, title } = req.body;

  try {
    // Get all push tokens
    const tokensSnapshot = await db.collection('push_tokens').get();

    const messages = [];
    tokensSnapshot.forEach((doc) => {
      const { token } = doc.data();
      if (Expo.isExpoPushToken(token)) {
        messages.push({
          to: token,
          sound: 'default',
          title: 'Nouveau digest disponible',
          body: title || `Le Top 3 de la semaine ${weekLabel} est arrivé !`,
          data: {
            type: 'new_digest',
            weekLabel,
          },
        });
      }
    });

    if (messages.length > 0) {
      const chunks = expo.chunkPushNotifications(messages);
      let successCount = 0;
      for (const chunk of chunks) {
        const results = await expo.sendPushNotificationsAsync(chunk);
        successCount += results.filter((r) => r.status === 'ok').length;
      }

      res.json({
        success: true,
        sent: successCount,
        total: messages.length,
      });
    } else {
      res.json({ success: true, sent: 0, total: 0 });
    }
  } catch (error) {
    console.error('Error sending weekly digest:', error);
    res.status(500).json({ error: error.message });
  }
});
