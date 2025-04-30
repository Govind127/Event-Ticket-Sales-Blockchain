import streamlit as st
import hashlib
import datetime
import json

# ---- Blockchain Block ----
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data  # Ticket sale info
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.data)}{self.previous_hash}"
        return hashlib.sha256(block_string.encode()).hexdigest()

# ---- Blockchain ----
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, str(datetime.datetime.now()), {"message": "Genesis Block"}, "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_data):
        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            timestamp=str(datetime.datetime.now()),
            data=new_data,
            previous_hash=latest_block.hash
        )
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

# ---- Streamlit Interface ----
st.title("🎟️ Blockchain Event Ticket Sales")

# Initialize session blockchain
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain()

st.header("Add Ticket Sale")
with st.form("ticket_form"):
    event_name = st.text_input("Event Name")
    buyer = st.text_input("Buyer Name")
    num_tickets = st.number_input("Number of Tickets", min_value=1, step=1)
    submitted = st.form_submit_button("Add to Blockchain")

    if submitted and event_name and buyer:
        sale_data = {
            "event": event_name,
            "buyer": buyer,
            "tickets": num_tickets
        }
        st.session_state.blockchain.add_block(sale_data)
        st.success("Ticket sale added to blockchain!")

# Display Blockchain
st.header("Blockchain Ledger")
for block in st.session_state.blockchain.chain:
    st.write(f"**Block #{block.index}**")
    st.json({
        "timestamp": block.timestamp,
        "data": block.data,
        "hash": block.hash,
        "previous_hash": block.previous_hash
    })

# Chain Validation
if st.button("Validate Blockchain"):
    if st.session_state.blockchain.is_chain_valid():
        st.success("✅ Blockchain is valid.")
    else:
        st.error("❌ Blockchain is NOT valid!")
