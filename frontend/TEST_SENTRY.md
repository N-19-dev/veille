# Test Sentry Frontend

## Méthode 1 : Console du navigateur (Recommandé - Rapide)

1. **Lancer le dev server** :
```bash
cd frontend
npm run dev
```

2. **Ouvrir dans le navigateur** : http://localhost:5173

3. **Ouvrir la console** (F12 ou Cmd+Option+I sur Mac)

4. **Exécuter ce code dans la console** :
```javascript
// Importer Sentry depuis le module global
import("@sentry/react").then(Sentry => {
  // Test 1: Capturer un message
  Sentry.captureMessage("Test Sentry Frontend via console", "info");
  console.log("✅ Message envoyé à Sentry");

  // Test 2: Capturer une exception
  try {
    throw new Error("Test Sentry Frontend - Erreur volontaire");
  } catch (e) {
    Sentry.captureException(e);
    console.log("✅ Exception envoyée à Sentry");
  }
});
```

5. **Vérifier dans Sentry Dashboard** :
   - Aller sur https://sentry.io
   - Projet `veille-tech-frontend` → Issues
   - Vous devriez voir :
     - Message : "Test Sentry Frontend via console"
     - Erreur : "Error: Test Sentry Frontend - Erreur volontaire"

---

## Méthode 2 : Bouton de test temporaire (Optionnel)

Si vous préférez un bouton cliquable dans l'interface :

1. **Modifier temporairement `src/App.tsx`** :

Ajoutez ce code juste après la ligne `import * as Sentry from "@sentry/react";` au début du fichier :
```typescript
import * as Sentry from "@sentry/react";
```

Puis ajoutez cette fonction de test dans le composant App (avant le return) :
```typescript
const testSentry = () => {
  // Test 1: Message
  Sentry.captureMessage("Test Sentry Frontend - Bouton cliqué", "info");
  console.log("✅ Message envoyé à Sentry");

  // Test 2: Exception
  try {
    throw new Error("Test Sentry Frontend - Erreur depuis bouton");
  } catch (e) {
    Sentry.captureException(e);
    console.log("✅ Exception envoyée à Sentry");
  }

  alert("✅ Test Sentry envoyé ! Vérifiez le dashboard Sentry.");
};
```

Et ajoutez ce bouton dans le JSX (par exemple juste après `<Hero ... />`) :
```tsx
<Hero ... />

{/* Bouton de test Sentry - À SUPPRIMER après test */}
{import.meta.env.MODE === "development" && (
  <div className="max-w-6xl mx-auto px-4 py-2">
    <button
      onClick={testSentry}
      className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded shadow"
    >
      🧪 Test Sentry Frontend
    </button>
  </div>
)}

<main ...>
```

2. **Sauvegarder et rafraîchir le navigateur**

3. **Cliquer sur le bouton "Test Sentry Frontend"**

4. **Vérifier dans Sentry Dashboard**

5. **Supprimer le code de test** après vérification ✅

---

## Vérification

Dans le dashboard Sentry (https://sentry.io) :

### Backend (veille-tech-backend)
- ✅ Message : "Test message from Sentry integration test"
- ✅ Erreur : "ZeroDivisionError: division by zero"

### Frontend (veille-tech-frontend)
- ✅ Message : "Test Sentry Frontend..."
- ✅ Erreur : "Error: Test Sentry Frontend..."

Si vous voyez ces erreurs → **Sentry est parfaitement configuré** ! 🎉

---

## Nettoyage

Après vérification :
- **Backend** : Le fichier `test_sentry.py` peut être supprimé ou conservé pour de futurs tests
- **Frontend** : Supprimer le code de test ajouté (méthode 2) si vous l'avez utilisé

Sentry est maintenant actif et capturera automatiquement toutes les erreurs en production ! 🚀
