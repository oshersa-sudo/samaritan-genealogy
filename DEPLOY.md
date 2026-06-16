# פרסום אילן היוחסין דרך Git → Cloudflare Pages

האפליקציה היא קובץ סטטי יחיד. הפרסום נעשה דרך Git: דוחפים את הריפו ל-GitHub,
מחברים אותו פעם אחת ל-Cloudflare Pages, ומאז **כל `git push` מפרסם אוטומטית**.

## מבנה הריפו
```
public/index.html          ← האתר שמוגש (תיקיית הפלט של Cloudflare)
index.html                 ← עותק זהה לפתיחה מקומית בלחיצה כפולה
genealogy_template.html    ← קוד-המקור של האפליקציה (עם placeholders)
master_v2.json             ← נתוני המיפקד
stories.json               ← סיפורי-החיים
page_*.txt                 ← תמלולי הפרוזה (מקור)
build.ps1                  ← בונה מחדש את index.html + public/index.html
```

## שלב 1 — יצירת ריפו ב-GitHub ודחיפה
הריפו כבר אותחל מקומית עם commit ראשון. צרו ריפו ריק ב-GitHub (בלי README),
ואז הריצו (החליפו USERNAME ו-REPO):
```
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

## שלב 2 — חיבור ל-Cloudflare Pages (פעם אחת)
1. היכנסו ל-[dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages**.
2. **Create application** → לשונית **Pages** → **Connect to Git**.
3. אשרו ל-Cloudflare גישה לריפו ובחרו אותו.
4. הגדרות הבנייה:
   - **Framework preset:** None
   - **Build command:** *(להשאיר ריק)*
   - **Build output directory:** `public`
5. **Save and Deploy**. הכתובת תהיה `https://<שם-הפרויקט>.pages.dev`.

> רק התיקייה `public/` מוגשת — קובצי המקור (json/תבנית/פרוזה) נשארים בריפו אך לא נחשפים באתר.

## עדכון התוכן בעתיד
1. ערכו את `master_v2.json` ו/או `stories.json` (או את התבנית).
2. הריצו בנייה מחדש:
   ```
   powershell -ExecutionPolicy Bypass -File build.ps1
   ```
3. דחפו:
   ```
   git add -A
   git commit -m "עדכון נתונים"
   git push
   ```
   Cloudflare יזהה את ה-push ויפרסם אוטומטית תוך שניות.

## הגבלת גישה (אופציונלי)
הקישור `*.pages.dev` פומבי. כדי להגביל לצופים מורשים בלבד אפשר להפעיל
**Cloudflare Access** (Zero Trust → Access → Applications) על הפרויקט.
