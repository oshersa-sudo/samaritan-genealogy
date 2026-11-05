# -*- coding: utf-8 -*-
# 2026-11-06 — «אברהם בן יעקב» (דנ-אברהם-ב, son of יעקב in the apex tree): the printed tree gives him the epithet «אלעיה»;
# it was left out because the reading was uncertain — now confirmed by the owner. Adds the epithet, a link to his Hebrew-Wikipedia
# article and a summary (own words) of that article. Idempotent.
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
master = json.load(io.open('master_v2.json', encoding='utf-8'))
stories = json.load(io.open('stories.json', encoding='utf-8'))
P = {p['id']: p for h in master['houses'] for f in h['families'] for p in f['persons']}
p = P['דנ-אברהם-ב']
p['name'] = 'אברהם = אלעיה'
p['note'] = 'נקרא «אלעיה».'
p['links'] = [{'label': 'ויקיפדיה — אברהם בן יעקב הדנפי', 'url': 'https://he.wikipedia.org/wiki/%D7%90%D7%91%D7%A8%D7%94%D7%9D_%D7%91%D7%9F_%D7%99%D7%A2%D7%A7%D7%91_%D7%94%D7%93%D7%A0%D7%A4%D7%99'}]
stories['דנ-אברהם-ב'] = {
    'g': '1719–1786',
    't': ('הידוע בכינויו «אלעיה» (בערבית אל-עיה, «המתחנן / המפצר» — על שם התחנונים הרבים שחיבר לעדה). פייטן, פרשן, מדקדק והיסטוריון ועסקן ציבור; '
          'כתב בעברית, בארמית ובערבית. לפי זכרונותיו היה פקיד בכיר בחצר מושל שכם, וכתב גם על מלחמתו של טאהר אל-עמר. '
          'מפעלו הגדול: פירוש לתורה בהיקף של כ-5,000 עמודים, שחיבר יחד עם טביה בן אב-זהותה המטרי, על בסיס פירוש שהתחיל בו דודו ומורהו שלמה בן אב-סכוה. '
          'חיבר גם חיבורי דקדוק והגייה, פיוטים רבים שנאמרים בבתי הכנסת (כגון «שרת בך הברכה») וכמאתיים עד שלוש מאות חיבורים בערבית. '
          'תרם לרכישת קרקע להקרבת הפסח ולשיפוץ קברי הכהנים. אחיו: שלמה (הבכור, ראש המשפחה אחרי דודו) וצדקה; אחותו הצעירה נישאה לכהן הגדול טביה בן יצחק. '
          'שנת הלידה 1719 נגזרת מכתב יד משנת 1786 שבו כתב שהוא בן 67; הפטירה כנראה ב-1786 (יש המאחרים ל-1787–1788). '
          'הערה: בערך מופיע גם שם ערבי מלא שלפיו סבו הוא מורג׳אן — לא הוכרע מול «אב-סכוה». סיכום מתוך הערך בוויקיפדיה.')}
io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
io.open('stories.json', 'w', encoding='utf-8').write(json.dumps(stories, ensure_ascii=False, indent=1))
print('ok')
