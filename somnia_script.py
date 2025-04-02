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
        print(f"Attempt {attempt + 1} of {max_attempts} failed on fallback. Retrying in 2 seconds...")
        time.sleep(2)
    else:
        raise Exception(f"Failed to connect to Somnia Testnet at {SOMNIA_RPC_URL} or {fallback_rpc} after {max_attempts} attempts. Check RPC URLs or network status.")

# Set up Selenium with human-like behavior
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in background
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm_usage")
driver = webdriver.Chrome(options=chrome_options)

# Load wallets from wallets.json in the repository
def load_wallets():
    with open("wallets.json", "r") as f:
        wallets = json.load(f)
    return wallets

# Function to add network (manual step or via wallet API if available)
def add_testnet():
    network_data = {
        "chainId": CHAIN_ID,
        "chainName": "Somnia Testnet",
        "rpcUrls": [SOMNIA_RPC_URL],
        "nativeCurrency": {"name": "STT", "symbol": "STT", "decimals": 18},
        "blockExplorerUrls": ["https://somnia-testnet.socialscan.io"]
    }
    print("Network data prepared. Add this to your wallet manually if not pre-configured.")
    return network_data

# Function to claim faucet tokens with Selenium
def claim_faucet(wallet_address):
    driver.get(SOMNIA_TESTNET_URL)
    time.sleep(random.uniform(2, 5))  # Human-like delay
    try:
        # Click "Request Tokens" button
        request_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Request Tokens')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", request_button)
        time.sleep(random.uniform(1, 2))
        request_button.click()
        print(f"Clicked 'Request Tokens' for {wallet_address}")

        # Wait for and switch to the popup
        WebDriverWait(driver, 20).until(EC.alert_is_present())
        popup = driver.switch_to.alert  # Switch to the popup (assuming it's an alert or modal)
        time.sleep(random.uniform(1, 3))  # Wait for popup to stabilize

        # Click "Get STT" button in the popup
        get_stt_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Get STT')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView();", get_stt_button)
        time.sleep(random.uniform(1, 2))
        get_stt_button.click()
        print(f"Clicked 'Get STT' for {wallet_address}")

        # Wait for faucet response
        time.sleep(random.uniform(5, 10))
        print(f"Successfully claimed STT for {wallet_address}")
    except Exception as e:
        print(f"Failed to claim STT for {wallet_address}: {str(e)}")
        # Attempt to close the popup if it exists
        try:
            driver.switch_to.alert.dismiss()
        except:
            pass

# Function to send a transaction (to a burn address or Testnet default)
def send_transaction(private_key, amount):
    account = Account.from_key(private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    # Use a burn address to avoid interaction between wallets
    burn_address = "0x000000000000000000000000000000000000dEaD"
    tx = {
        "nonce": nonce,
        "to": burn_address,
        "value": w3.to_wei(amount, "ether"),
        "gas": 200000,
        "gasPrice": w3.to_wei(str(random.uniform(20, 50)), "gwei"),  # Random gas price
        "chainId": CHAIN_ID,
    }
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)  # Corrected attribute
    print(f"Transaction sent to burn address: {tx_hash.hex()}")
    time.sleep(random.uniform(3, 6))  # Human-like delay
    return tx_hash

# Main function to run tasks for multiple accounts
def run_somnia_tasks():
    add_testnet()  # Initial network setup (manual or automated via wallet)
    wallets = load_wallets()
    for wallet in wallets[:100]:  # Limit to 100 accounts
        wallet_address = wallet["address"]
        private_key = wallet["private_key"]

        # Claim STT tokens with human-like behavior
        claim_faucet(wallet_address)

        # Perform 1-2 transactions with random amounts
        num_transactions = random.randint(1, 2)
        for _ in range(num_transactions):
            amount = random.uniform(0.001, 0.1)  # Random amount between 0.001 and 0.1 STT
            send_transaction(private_key, amount)
            time.sleep(random.uniform(5, 15))  # Random delay between transactions

        print(f"Completed tasks for {wallet_address}")
        time.sleep(random.uniform(60, 300))  # Random delay between accounts (1-5 minutes)

    driver.quit()
    print("All tasks completed for the day.")

# Schedule to run daily
if __name__ == "__main__":
    while True:
        run_somnia_tasks()
        time.sleep(86400)  # Wait 24 hours
