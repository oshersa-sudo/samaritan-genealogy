# -*- coding: utf-8 -*-
# Adds a "בית הכהונה" house to master_v2.json, built from the priestly-family
# genealogy in "תולדות בני ישראל השומרונים" pp.575-576 (section צ, "משפחת הכהנים
# התבסטיים מבני איתמר") — only the clearly-read, connecting recent high-priest spine.
import json, io

P = io.open('master_v2.json', encoding='utf-8')
master = json.load(P); P.close()

# already added? avoid duplicate
master['houses'] = [h for h in master['houses'] if 'הכהונה' not in h['house']]

def person(pid, name, father_id=None, children=None, note=None, born=None):
    d = {"id": pid, "name": name, "sex": "M"}
    if father_id: d["father_id"] = father_id
    if children: d["children_ids"] = children
    if note: d["note"] = note
    if born is not None: d["birth"] = born
    return d

# Confident spine read from the source (begetting genealogy, by generation).
# Father links set only where the source is explicit; murky middle generations omitted.
persons = [
    person("כ-אברהם", "אברהם", children=["כ-טביה"],
           note="אב הענף הכהני 'התבסטיים מבני איתמר' (לפי הספר)"),
    person("כ-טביה", "טביה", father_id="כ-אברהם", children=["כ-צדקה"]),
    person("כ-צדקה", "צדקה", father_id="כ-טביה", children=["כ-שלמה"],
           note="ראש משפחת הכהנים, בימי הרבן צדקה האחרון מבני פינחס. [דורות-ביניים מקוצרים לפי המקור]"),
    # --- recent high-priest line (matches the references already in the census) ---
    person("כ-שלמה", "שלמה (הכהן הגדול)", father_id="כ-צדקה", children=["כ-עמרם"],
           note="ראש שלשלת הכהנים הגדולים הקרובה (דור שביעי במקור)"),
    person("כ-עמרם", "עמרם (בן שלמה)", father_id="כ-שלמה", children=["כ-יצחק","כ-שלמה2"],
           note="כהן גדול. = ההפניות 'הכה\"ג עמרם בן שלמה' שבמיפקד"),
    person("כ-שלמה2", "שלמה (בן עמרם)", father_id="כ-עמרם"),
    person("כ-יצחק", "יצחק (בן עמרם)", father_id="כ-עמרם", children=["כ-פינחס","כ-אהרן"],
           note="כהן גדול. = ההפניות 'הכה\"ג יצחק בן עמרם' שבמיפקד"),
    person("כ-פינחס", "פינחס (בן יצחק)", father_id="כ-יצחק",
           children=["כ-מצליח","כ-אבישע","כ-טביה2","כ-אלעזר"],
           note="כהן גדול. = ההפניות 'פינחס בן יצחק' שבמיפקד"),
    person("כ-מצליח", "מצליח (בן פינחס)", father_id="כ-פינחס",
           note="כהן גדול. = ההפניות 'מצליח בן פינחס' שבמיפקד"),
    person("כ-אבישע", "אבישע (בן פינחס)", father_id="כ-פינחס"),
    person("כ-טביה2", "טביה (בן פינחס)", father_id="כ-פינחס"),
    person("כ-אלעזר", "אלעזר (בן פינחס)", father_id="כ-פינחס"),
    # parallel branch: Aaron -> Yaakov ben Aharon (the other well-known high priest)
    person("כ-אהרן", "אהרן (בן יצחק)", father_id="כ-יצחק", children=["כ-יעקב"],
           note="[שיוך-האב לפי המקור]"),
    person("כ-יעקב", "יעקב (בן אהרן)", father_id="כ-אהרן", children=["כ-פינחס2"],
           note="כהן גדול. = ההפניות 'הכה\"ג יעקב בן אהרן' שבמיפקד"),
    person("כ-פינחס2", "פינחס (בן יעקב)", father_id="כ-יעקב"),
]

master['houses'].append({
    "house": "ו. בית אב הכהונה",
    "source_note": "מתוך 'תולדות בני ישראל השומרונים', עמ' 575–576, סעיף צ — משפחת הכהנים מבני איתמר. שלשלת הכהנים הגדולים הקרובים בלבד (החלק שנקרא בוודאות ומתחבר למיפקד). דורות-ביניים קדומים והרשימה הקדומה המלאה — טעונים אימות מול הסריקה.",
    "families": [{
        "family_no": 1,
        "family": "משפחת הכהנים (מבני איתמר)",
        "ref_code": "כהן",
        "persons": persons
    }]
})

io.open('master_v2.json', 'w', encoding='utf-8').write(json.dumps(master, ensure_ascii=False, indent=1))
print("added priestly house with", len(persons), "persons")
