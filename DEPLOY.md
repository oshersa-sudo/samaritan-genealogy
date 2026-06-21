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
הקישור הפומבי פתוח לכולם לקריאה. כדי להגביל **צפייה** למורשים בלבד אפשר להפעיל
**Cloudflare Access** (Zero Trust → Access → Applications) על הפרויקט.

---

# עריכה בענן (מצב מנהל) — התקנת צד-השרת

האפליקציה תומכת בעריכה מכל מקום עם **סיסמת-מנהל**: עריכת טקסט/שם/שנים, וגם
שינוי-מבנה (שיוך-אב, הוספת אדם, מחיקה). הקהל רואה הכל לקריאה בלבד; רק עם הסיסמה
מופיע כפתור עריכה. השינויים נשמרים ב-**Cloudflare KV** כ"שכבת-תיקונים" מעל הנתונים
(הנתונים המקוריים נשארים ב-git ובטוחים), ומיושמים בדפדפן בעת הטעינה.

קבצים שנוספו: `src/worker.js` (ה-API) ו-`wrangler.toml` (הגדרות ה-Worker).
ה-API: `GET /api/data` (קריאת תיקונים), `POST /api/login` (בדיקת סיסמה),
`POST /api/save` (שמירה — דורש את הסיסמה).

## שלב 1 — יצירת מאגר KV (פעם אחת, בדשבורד)
1. [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **KV**.
2. **Create a namespace** → שם: `genealogy-overrides` → **Add**.
3. העתיקו את ה-**Namespace ID** (מחרוזת ארוכה).
4. הדביקו אותו ב-`wrangler.toml` במקום `PUT_YOUR_KV_NAMESPACE_ID_HERE`
   (או מסרו לי אותו ואדביק ואדחוף).

## שלב 2 — הגדרת שם-משתמש וסיסמת-המנהל (סודות)
ב-**Worker** של הפרויקט → **Settings** → **Variables and Secrets**. הוסיפו **שני** סודות
(סוג **Secret** בכל אחד), בשמות בדיוק כך:
- `ADMIN_USER` → הערך: שם-המשתמש (לדוגמה `oshersa`)
- `ADMIN_PASSWORD` → הערך: הסיסמה שתבחרו

**Save**. הערכים נשמרים מוצפנים בצד-השרת בלבד — **לעולם לא בקוד ולא ב-git**.
(אפשר לשנות אותם בכל עת בדשבורד; שינוי מנתק את כל המנהלים המחוברים.)
הסיסמה היא הסוד האמיתי; שם-המשתמש הוא בדיקה נוספת.

## שלב 3 — פרסום עם ה-Worker
ה-Worker חייב לרוץ (לא רק assets סטטיים). לאחר שה-id והסוד מוגדרים:
- **דרך Git (מומלץ):** דוחפים את `wrangler.toml` + `src/` + `public/`. אם הפרויקט
  ב-Cloudflare הוא **Worker מחובר ל-Git**, הוא מזהה את `wrangler.toml` ומפרסם את
  ה-Worker יחד עם תיקיית `public/` כ-assets. (Build command ריק — `public/` כבר בנוי ומחויב.)
- **או דרך CLI** (אם יש Node במחשב): `npx wrangler deploy` מתוך תיקיית הריפו
  (אחרי `build.ps1`).

## שלב 4 — בדיקה
1. פתחו את האתר → לחצו **🔧 מנהל** (פינת הכותרת) → הזינו את הסיסמה.
2. לחצו על אדם → בתחתית הפאנל יופיע **✏️ עריכת מנהל** (שם/מין/שנים/אב/סיפור)
   עם כפתורי **שמור / הוסף ילד / מחק**.
3. כל שמירה כותבת ל-KV ומופיעה לכל הצופים בטעינה הבאה.

> **שיוך-אב:** בשדה "מזהה האב" מדביקים את מזהה האדם שיהיה האב (המזהה מוצג בתחתית
> טופס-העריכה של כל אדם, לחיצה אחת להעתקה). שינוי האב מעביר את האדם וכל צאצאיו.
>
> **שחזור:** התיקונים נפרדים מהנתונים המקוריים. למחיקת כל התיקונים — לרוקן את מפתח
> `overrides` ב-KV (דשבורד → KV → הערך → מחיקה).
