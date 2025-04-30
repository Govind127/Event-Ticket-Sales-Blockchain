import streamlit as st
import hashlib
import json
import os
from datetime import datetime

BLOCKCHAIN_FILE = "blockchain.json"

# --- Blockchain Logic ---

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain = []
        self.load_chain()

    def create_genesis_block(self):
        genesis_block = Block(0, str(datetime.now()), {"message": "Genesis Block"}, "0")
        self.chain.append(genesis_block)
        self.save_chain()

    def add_block(self, data):
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            timestamp=str(datetime.now()),
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()

    def save_chain(self):
        with open(BLOCKCHAIN_FILE, "w") as file:
            json.dump([block.to_dict() for block in self.chain], file, indent=4)

    def load_chain(self):
        if os.path.exists(BLOCKCHAIN_FILE):
            with open(BLOCKCHAIN_FILE, "r") as file:
                chain_data = json.load(file)
                self.chain = []
                for block_data in chain_data:
                    block = Block(
                        block_data["index"],
                        block_data["timestamp"],
                        block_data["data"],
                        block_data["previous_hash"]
                    )
                    self.chain.append(block)
        else:
            self.create_genesis_block()


# --- Streamlit UI ---

st.set_page_config(page_title="Event Ticket Blockchain", layout="centered")
st.title("🎟️ Event Ticket Sales - Blockchain")

blockchain = Blockchain()

st.header("Add New Ticket")
with st.form("ticket_form"):
    buyer_name = st.text_input("Buyer Name")
    event_name = st.text_input("Event Name")
    seat_number = st.text_input("Seat Number")
    submit = st.form_submit_button("Add Ticket")

if submit:
    if buyer_name and event_name and seat_number:
        ticket_data = {
            "buyer": buyer_name,
            "event": event_name,
            "seat": seat_number
        }
        blockchain.add_block(ticket_data)
        st.success("✅ Ticket added to blockchain.")
    else:
        st.error("❌ Please fill in all fields.")

st.header("📦 Blockchain Ledger")
for block in blockchain.chain:
    with st.expander(f"Block {block.index}"):
        st.json(block.to_dict())
