import streamlit as st
import hashlib
import datetime
import json
import os
import pandas as pd

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
    def __init__(self, file_format="csv"):
        self.chain = [self.create_genesis_block()]
        self.file_format = file_format
        self.file_name = f"ticket_sales.{file_format}"

        # Load the existing blockchain from the file (if it exists)
        self.load_chain_from_file()

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
        # Save the updated blockchain to the file
        self.save_chain_to_file()

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def load_chain_from_file(self):
        # Check if file exists and load the blockchain data
        if os.path.exists(self.file_name):
            if self.file_format == "csv":
                df = pd.read_csv(self.file_name)
                for _, row in df.iterrows():
                    data = json.loads(row['data'])
                    block = Block(int(row['index']), row['timestamp'], data, row['previous_hash'])
                    self.chain.append(block)
            elif self.file_format == "json":
                with open(self.file_name, 'r') as file:
                    blockchain_data = json.load(file)
                    for block_data in blockchain_data:
                        block = Block(
                            block_data['index'], block_data['timestamp'], block_data['data'], block_data['previous_hash']
                        )
                        self.chain.append(block)

    def save_chain_to_file(self):
        # Save blockchain to file (either CSV or JSON)
        if self.file_format == "csv":
            # Prepare data for CSV
            data = []
            for block in self.chain:
                data.append({
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "data": json.dumps(block.data),
                    "previous_hash": block.previous_hash,
                    "hash": block
