import sqlite3

DB_PATH = "app.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    a  TEXT NOT NULL,
    b  TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL
);
""")

cur.execute("""
CREATE UNIQUE INDEX IF NOT EXISTS ux_rules_pair
ON rules (
    CASE WHEN a < b THEN a ELSE b END,
    CASE WHEN a < b THEN b ELSE a END
);
""")

def canon(a: str, b: str):
    a = a.strip().lower()
    b = b.strip().lower()
    return (a, b) if a <= b else (b, a)

seed_rules = [
    ("ibuprofen_aspirin", "ibuprofen", "aspirin", "major",
    "Talk to your doctor before using aspirin together with ibuprofen. Frequent or regular use of ibuprofen may reduce the effectiveness of aspirin if you are taking it to prevent heart attacks or strokes. In addition, combining these medications may increase your risk of developing gastrointestinal ulcers and bleeding. You may need a dose adjustment or more frequent monitoring by your doctor to safely use both medications. Contact your doctor immediately if you develop severe abdominal pain, bloating, sudden dizziness or lightheadedness, nausea, vomiting (especially with blood), loss of appetite, and/or black, tarry stools. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("ethanol_acetaminophen", "ethanol", "acetaminophen", "major", "Ask your doctor before using acetaminophen together with ethanol (alcohol). This can cause serious side effects that affect your liver. Call your doctor immediately if you experience a fever, chills, joint pain or swelling, excessive tiredness or weakness, unusual bleeding or bruising, skin rash or itching, loss of appetite, nausea, vomiting, or yellowing of the skin or the whites of your eyes. If your doctor does prescribe these medications together, you may need a dose adjustment or special tests to safely take both medications. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("azithromycin_zoloft", "azithromycin", "zoloft", "moderate", "Using azithromycin together with sertraline can increase the risk of an irregular heart rhythm that may be serious and potentially life-threatening, although it is a relatively rare side effect. You may be more susceptible if you have a heart condition called congenital long QT syndrome, other cardiac diseases, conduction abnormalities, or electrolyte disturbances (for example, magnesium or potassium loss due to severe or prolonged diarrhea or vomiting). Talk to your doctor if you have any questions or concerns. You should seek immediate medical attention if you develop sudden dizziness, lightheadedness, fainting, shortness of breath, or heart palpitations during treatment with these medications, whether together or alone. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("azithromycin_ondansetron", "azithromycin", "ondansetron", "moderate", "Using azithromycin together with ondansetron can increase the risk of an irregular heart rhythm that may be serious and potentially life-threatening, although it is a relatively rare side effect. You may be more susceptible if you have a heart condition called congenital long QT syndrome, other cardiac diseases, conduction abnormalities, or electrolyte disturbances (for example, magnesium or potassium loss due to severe or prolonged diarrhea or vomiting). Talk to your doctor if you have any questions or concerns. You should seek immediate medical attention if you develop sudden dizziness, lightheadedness, fainting, shortness of breath, or heart palpitations during treatment with these medications, whether together or alone. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("prednisone_aspirin", "prednisone", "aspirin", "moderate", "Using aspirin together with predniSONE may increase the risk of side effects in the gastrointestinal tract such as inflammation, bleeding, ulceration, and rarely, perforation. Gastrointestinal perforation is a potentially fatal condition and medical emergency where a hole forms all the way through the stomach or intestine. You should take these medications with food to lessen the risk. In addition, steroid medications like predniSONE have been reported to decrease the blood levels of aspirin and similar drugs in some cases, which may make them less effective in treating your condition. On the other hand, if you have been receiving both medications and predniSONE is stopped, blood levels of aspirin may subsequently increase and a dosage reduction may be required to avoid toxicity. Talk to your doctor if you have any questions or concerns. You may need a dose adjustment or more frequent monitoring by your doctor to safely use both medications. Your doctor may also be able to recommend medications to help protect the stomach and intestine if you are at high risk for developing serious gastrointestinal complications. You should seek immediate medical attention if you experience any unusual bleeding or bruising, or have other signs and symptoms of bleeding such as dizziness; lightheadedness; red or black, tarry stools; coughing up or vomiting fresh or dried blood that looks like coffee grounds; severe headache; and weakness. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("prednisone_xanax", "prednisone", "xanax", "minor", "Certain corticosteroids may decrease the plasma concentration of some benzodiazepines. Limited data are available for midazolam and triazolam. The mechanism is related to induction of hepatic cytochrome P450 enzymes responsible for benzodiazepine metabolism. The clinical significance may depend on the dosage and duration of corticosteroid therapy and be of greater importance with oral administration of benzodiazepines"),
    ("prednisone_vitamind3", "prednisone", "vitaminD3", "moderate", "PredniSONE may reduce the effects of cholecalciferol. You may require increased monitoring and/or an adjustment in the dosing of cholecalciferol to safely use this combination. Speak with your healthcare provider if you have any questions or concerns. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("prednisone_insulin", "prednisone", "insulin", "moderate", "PredniSONE may interfere with blood glucose control and reduce the effectiveness of insulin and other diabetic medications. Monitor your blood sugar levels closely. You may need a dose adjustment of your diabetic medications during and after treatment with predniSONE. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor.")
    ("insulin_aspirin", "insulin", "aspirin", "moderate", "Using aspirin together with insulin or certain other diabetes medications may increase the risk of hypoglycemia, or low blood sugar. Symptoms of hypoglycemia include headache, dizziness, drowsiness, nervousness, confusion, tremor, nausea, hunger, weakness, perspiration, palpitation, and rapid heartbeat. Talk to your doctor if you have any questions or concerns. You may need a dose adjustment or more frequent monitoring of your blood sugar to safely use both medications. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
    ("insulin_lexapro", "insulin", "lexapro", "moderate", "Using escitalopram (Lexapro) together with insulin or certain other diabetes medications may increase the risk of hypoglycemia, or low blood sugar. Symptoms of hypoglycemia include headache, dizziness, drowsiness, nervousness, confusion, tremor, nausea, hunger, weakness, perspiration, palpitation, and rapid heartbeat. Talk to your doctor if you have any questions or concerns. You may need a dose adjustment or more frequent monitoring of your blood sugar to safely use both medications. It is important to tell your doctor about all other medications you use, including vitamins and herbs. Do not stop using any medications without first talking to your doctor."),
]

rows = []
for id_, A, B, sev, desc in seed_rules:
    a, b = canon(A, B)
    rows.append((id_, a, b, sev, desc))

cur.executemany("INSERT OR REPLACE INTO rules (id,a,b,severity,description) VALUES (?,?,?,?,?)", rows)

conn.commit()
conn.close()

print(f"app.db is ready.")
