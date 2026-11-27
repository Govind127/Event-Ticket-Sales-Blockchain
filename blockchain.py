import hashlib
import json
import sqlite3
import base64
from io import BytesIO
from datetime import datetime
import qrcode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization

DB_FILE = "eventchain.db"
DIFFICULTY = 3  # Leading zeros for Proof-of-Work


class Blockchain:
    def __init__(self):
        self.init_db()
        if not self.get_chain():
            self.create_genesis_block()

    def init_db(self):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS blocks (
                    idx INTEGER PRIMARY KEY,
                    timestamp TEXT,
                    data TEXT,
                    previous_hash TEXT,
                    nonce INTEGER,
                    hash TEXT
                )
            """)

    def compute_hash(self, idx, timestamp, data, previous_hash, nonce):
        payload = json.dumps({
            "index": idx,
            "timestamp": timestamp,
            "data": data,
            "previous_hash": previous_hash,
            "nonce": nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def mine_block(self, idx, timestamp, data, previous_hash):
        nonce = 0
        target = "0" * DIFFICULTY
        while True:
            h = self.compute_hash(idx, timestamp, data, previous_hash, nonce)
            if h.startswith(target):
                return nonce, h
            nonce += 1

    def create_genesis_block(self):
        ts = datetime.utcnow().isoformat()
        data = {"type": "GENESIS", "message": "EventChain Ledger Initialized"}
        nonce, h = self.mine_block(0, ts, data, "0")
        self._insert_block(0, ts, data, "0", nonce, h)

    def _insert_block(self, idx, ts, data, prev_hash, nonce, h):
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute(
                "INSERT INTO blocks VALUES (?, ?, ?, ?, ?, ?)",
                (idx, ts, json.dumps(data), prev_hash, nonce, h)
            )

    def get_chain(self):
        with sqlite3.connect(DB_FILE) as conn:
            rows = conn.execute("SELECT * FROM blocks ORDER BY idx ASC").fetchall()
        return [
            {
                "index": r[0],
                "timestamp": r[1],
                "data": json.loads(r[2]),
                "previous_hash": r[3],
                "nonce": r[4],
                "hash": r[5]
            }
            for r in rows
        ]

    def is_seat_taken(self, event: str, seat: str) -> bool:
        for block in self.get_chain()[1:]:
            d = block["data"]
            if d.get("event", "").lower() == event.lower() and d.get("seat", "").lower() == seat.lower():
                return True
        return False

    def issue_ticket(self, buyer: str, event: str, seat: str, price: float):
        if self.is_seat_taken(event, seat):
            raise ValueError(f"Seat {seat} for '{event}' is already minted on-chain.")

        # Generate ECDSA keypair & digital signature for ticket authenticity
        priv_key = ec.generate_private_key(ec.SECP256R1())
        pub_pem = priv_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        ticket_id = hashlib.sha256(f"{event}-{seat}-{buyer}-{datetime.utcnow()}".encode()).hexdigest()[:12].upper()
        signature = priv_key.sign(ticket_id.encode(), ec.ECDSA(hashes.SHA256())).hex()

        qr = qrcode.make(json.dumps({"ticket_id": ticket_id, "event": event, "seat": seat, "sig": signature[:24]}))
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()

        chain = self.get_chain()
        last = chain[-1]
        idx = last["index"] + 1
        ts = datetime.utcnow().isoformat()
        data = {
            "type": "TICKET_MINT",
            "ticket_id": ticket_id,
            "buyer": buyer,
            "event": event,
            "seat": seat,
            "price": price,
            "signature": signature,
            "public_key": pub_pem,
            "qr_base64": qr_b64
        }
        nonce, h = self.mine_block(idx, ts, data, last["hash"])
        self._insert_block(idx, ts, data, last["hash"], nonce, h)
        return self.get_chain()[-1]

    def validate_chain(self):
        chain = self.get_chain()
        for i in range(1, len(chain)):
            curr, prev = chain[i], chain[i - 1]
            recomputed = self.compute_hash(curr["index"], curr["timestamp"], curr["data"], curr["previous_hash"], curr["nonce"])
            if curr["hash"] != recomputed:
                return {"valid": False, "error": f"Block #{curr['index']} data tampered (Hash mismatch)."}
            if curr["previous_hash"] != prev["hash"]:
                return {"valid": False, "error": f"Block #{curr['index']} broken link to Block #{prev['index']}."}
        return {"valid": True, "error": None}

    def simulate_tamper(self, idx: int, new_buyer: str):
        with sqlite3.connect(DB_FILE) as conn:
            row = conn.execute("SELECT data FROM blocks WHERE idx = ?", (idx,)).fetchone()
            if not row or idx == 0:
                raise ValueError("Invalid block index for tamper test.")
            data = json.loads(row[0])
            data["buyer"] = new_buyer
            conn.execute("UPDATE blocks SET data = ? WHERE idx = ?", (json.dumps(data), idx))