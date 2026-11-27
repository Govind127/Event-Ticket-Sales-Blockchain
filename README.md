# 🎟️ EventChain — Blockchain Event Ticket Sales Ledger

A full-stack decentralized event ticketing prototype built with **Python**, **FastAPI**, and **SQLite**. EventChain prevents ticket counterfeiting, duplicate seat issuance, and silent ledger manipulation by anchoring every ticket minting transaction onto an immutable, Proof-of-Work (PoW) SHA-256 blockchain secured with **ECDSA** digital signatures and verifiable **QR codes**.

---

## 🚀 Key Features

* **Proof-of-Work (PoW) Consensus:** Mines blocks using an adjustable leading-zero difficulty target (`nonce` discovery) to enforce computational integrity.
* **ECDSA Cryptographic Ticket Signing:** Generates a unique `SECP256R1` elliptic-curve keypair per transaction to sign each ticket ID and embed a Base64-encoded **QR pass** directly into the block payload.
* **Double-Spend & Seat Lock Enforcement:** Validates incoming mint requests against the existing ledger to prevent duplicate seat issuance for the same event.
* **Interactive Security Tamper Simulator:** Allows users to modify historical block payloads directly in SQLite and watch real-time **SHA-256 hash chain verification** detect broken links and data tampering immediately.
* **Live Sales & Ledger Analytics:** Exposes REST endpoints tracking total minted tickets, gross revenue, and event-level sales distribution.
* **Modern Dark Dashboard UI:** Lightweight HTML/Tailwind CSS/JavaScript frontend served directly by FastAPI with an immutable block explorer and interactive Swagger API docs (`/docs`).

---

## 🛠️ Tech Stack

* **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic
* **Cryptography & Verification:** `cryptography` (ECDSA SECP256R1, SHA-256), `qrcode`, Pillow
* **Database:** SQLite3 (Relational block persistence)
* **Frontend:** HTML5, Tailwind CSS, Vanilla JavaScript (Fetch API)

---

## 📂 Project Structure

```text
Event-Ticket-Sales-Blockchain/
├── blockchain.py       # Block & Blockchain classes, PoW mining, ECDSA signing, QR generation, SQLite persistence
├── main.py             # FastAPI application, REST endpoints, analytics aggregation, static file routing
├── static/
│   └── index.html      # Interactive dashboard UI, block explorer, analytics KPIs & tamper simulator
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

---

## ⚙️ Local Setup & Execution

### 1. Clone the Repository
```bash
git clone [https://github.com/](https://github.com/)<your-username>/Event-Ticket-Sales-Blockchain.git
cd Event-Ticket-Sales-Blockchain
```

### 2. Create & Activate a Virtual Environment
**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn main:app --reload
```

### 5. Access the Interfaces
* **Web Dashboard:** `http://127.0.0.1:8000`
* **Interactive API Docs (Swagger UI):** `http://127.0.0.1:8000/docs`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Serves the frontend dashboard UI |
| `GET` | `/api/chain` | Returns the full blockchain ledger and SHA-256 validation status |
| `POST` | `/api/tickets` | Mines a new block with ECDSA signature and QR code for a ticket purchase |
| `GET` | `/api/analytics` | Returns total tickets sold, total revenue, and per-event breakdown |
| `POST` | `/api/tamper` | Simulates a database intrusion by altering a block's buyer record |

---

## 🧪 Testing Ledger Immutability

1. Mint 2–3 tickets using the **Mint New Ticket** form on the dashboard.
2. Confirm the header status reads **`✅ Chain Verified (SHA-256 Valid)`**.
3. Use the **Security Tamper Simulator** in the bottom-left panel to alter the buyer name of `Block #1`.
4. The ledger validator immediately flags **`❌ TAMPER DETECTED: Block #1 data tampered (Hash mismatch)`**, demonstrating cryptographic immutability.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).
