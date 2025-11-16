from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
import sqlite3, json, time
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Drug Interaction Verifier")
Instrumentator().instrument(app).expose(app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500" 
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#above I added CORS to allow requests from localhost as I had problems testing it without it

DB_PATH = "app.db"
HISTORY_PATH = Path(__file__).resolve().parents[1] / "data" / "history.json"


# The following part of the code defines a class called CheckReq which is a subclass of BaseModel which comes from python's
# pydantic library which is used for data validation. This means that the data the user inputs into the FastAPI
# will be checked to make sure it has the same datatype as the class attributes. So if the user inputs a non-string
# value an error will appear.

class CheckReq(BaseModel):
    drug_a: str = Field(..., example="Ibuprofen")
    drug_b: str = Field(..., example="Aspirin")

class CheckResp(BaseModel):
    found: bool
    severity: str | None = None
    description: str | None = None
    message: str | None = None
    suggest_add: bool | None = None
    how_to_add: dict | None = None 

#The fastAPI consists of the request and response, here the request is asking for 2 medications and the response
# follows a structure that depends on whether the interaction was found or not (but that is always included, while the rest
# like severity, description etc are optional and depend on the situation)

class RuleIn(BaseModel):
    id: str | None = None  
    a: str
    b: str
    severity: str = Field(..., description="contraindicated | major | moderate | minor")
    description: str

class RuleOut(BaseModel):
    id: str
    a: str
    b: str
    severity: str
    description: str


def normalize_pair(a: str, b: str) -> tuple[str, str]:
    a = a.strip().lower()
    b = b.strip().lower()
    return (a, b) if a <= b else (b, a)

def ensure_history_file():
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        HISTORY_PATH.write_text("[]", encoding="utf-8")

def append_history(drug_a: str, drug_b: str, found: bool, severity: str | None):
    ensure_history_file()
    data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    data.append({
        "drug_a": drug_a,
        "drug_b": drug_b,
        "found": found,
        "severity": severity,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    HISTORY_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def rule_exists_for_pair(a: str, b: str) -> bool:
    a, b = normalize_pair(a, b)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM rules WHERE a=? AND b=?", (a, b))
        return cur.fetchone() is not None

#The post /check endpoint checks if there is an interaction between two drugs
# if it doesn't find any interaction it tells it to the user and explains how to add a new interaction
# but if it finds it, it logs it in the history json file and returns the severity and description to the user

@app.post("/check", response_model=CheckResp)
def check_interaction(req: CheckReq):
    a, b = normalize_pair(req.drug_a, req.drug_b)

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT severity, description FROM rules WHERE a=? AND b=?", (a, b))
        row = cur.fetchone()

    if not row:
        append_history(a, b, False, None)

        return CheckResp(
            found=False,
            message="No known interaction in local DB.",
            suggest_add=True,
            how_to_add={
                "endpoint": "POST /rules",
                "body_example": {
                    "a": a, "b": b,
                    "severity": "moderate",
                    "description": "Describe the interaction here..."
                },
                "note": "Pairs are order-independent; inputs are stored alphabetically."
            }
        )

    severity, description = row
    append_history(a, b, True, severity)
    return CheckResp(found=True, severity=severity, description=description)

#the get /history endpoint checks if a history file exists, if yes it reads it and if not creates an empty one

@app.get("/history")
def get_history(limit: int = 50):
    ensure_history_file()
    data = json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
    return data[-limit:] if limit > 0 else data

#get /rules lists all the rules in the database but we can also call it with an id to get one specific rule from the database

@app.get("/rules", response_model=list[RuleOut])
def list_rules():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, a, b, severity, description FROM rules ORDER BY id")
        rows = cur.fetchall()
    return [RuleOut(id=r[0], a=r[1], b=r[2], severity=r[3], description=r[4]) for r in rows]

@app.get("/rules/{rule_id}", response_model=RuleOut)
def get_rule(rule_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, a, b, severity, description FROM rules WHERE id=?", (rule_id,))
        r = cur.fetchone()
    if not r:
        raise HTTPException(404, "Rule not found")
    return RuleOut(id=r[0], a=r[1], b=r[2], severity=r[3], description=r[4])

#app.post creates a new rule but before that normalizes the pair and if it exists already yields a 409 error

@app.post("/rules")
def create_rule(rule: RuleIn):
    if rule.severity not in {"contraindicated", "major", "moderate", "minor"}:
        raise HTTPException(400, "Invalid severity")

    a, b = normalize_pair(rule.a, rule.b)
    rule_id = rule.id or f"{a}_{b}"

    if rule_exists_for_pair(a, b):
        raise HTTPException(409, "Pair already exists (order-independent)")

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO rules (id,a,b,severity,description) VALUES (?,?,?,?,?)",
                (rule_id, a, b, rule.severity, rule.description)
            )
            conn.commit()
        except sqlite3.IntegrityError as e:
            raise HTTPException(409, f"Conflict: {e}")
    return {"ok": True, "id": rule_id}

#app.put updates a rule based on its id and if it is not found it yiekds a 404 error

@app.put("/rules/{rule_id}")
def update_rule(rule_id: str, severity: str, description: str):
    if severity not in {"contraindicated", "major", "moderate", "minor"}:
        raise HTTPException(400, "Invalid severity")
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE rules SET severity=?, description=? WHERE id=?", (severity, description, rule_id))
        changed = cur.rowcount
        conn.commit()
    if not changed:
        raise HTTPException(404, "Rule not found")
    return {"ok": True}

#app.delete deletes a rule based on its id and if it cannot delete it because it doesn't exist it yields a 404 error

@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: str):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM rules WHERE id=?", (rule_id,))
        changed = cur.rowcount
        conn.commit()
    if not changed:
        raise HTTPException(404, "Rule not found")
    return {"ok": True}

@app.get("/health")
def health():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = "error"
    return {
        "status" : "ok",
        "db": db_status,
        "version": "1.0.0"
    }