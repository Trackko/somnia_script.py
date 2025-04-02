import os
import time
import random
import json
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import requests

# Load environment variables
load_dotenv()
SOMNIA_RPC_URL = os.getenv("SOMNIA_RPC_URL", "https://rpc.somnia.network")  # Default to official RPC
SOMNIA_TESTNET_URL = "https://testnet.somnia.network/"
CHAIN_ID_STR = os.getenv("CHAIN_ID", "50312")  # Default to Somnia Testnet Chain ID
try:
    CHAIN_ID = int(CHAIN_ID_STR)  # Convert to integer with error handling
except ValueError as e:
    raise ValueError(f"Invalid CHAIN_ID value '{CHAIN_ID_STR}'. Please set a numeric Chain ID (e.g., 50312).") from e

# Initialize Web3 with retry logic and fallback RPC
w3 = Web3(Web3.HTTPProvider(SOMNIA_RPC_URL))
max_attempts = 3
for attempt in range(max_attempts):
    if w3.is_connected():
        print(f"Successfully connected to Somnia Testnet at {SOMNIA_RPC_URL}")
        break
    print(f"Attempt {attempt + 1} of {max_attempts} failed to connect. Retrying in 2 seconds...")
    time.sleep(2)  # Wait 2 seconds before retry
else:
    fallback_rpc = "https://50312.rpc.thirdweb.com"  # Fallback RPC
    print(f"Switching to fallback RPC: {fallback_rpc}")
    w3 = Web3(Web3.HTTPProvider(fallback_rpc))
    for attempt in range(max_attempts):
        if w3.is_connected():
            print(f"Successfully connected to Somnia Testnet at {fallback_rpc}")
            SOMNIA_RPC_URL = fallback_rpc  # Update for consistency
            break
