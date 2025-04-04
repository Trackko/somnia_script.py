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
SOMNIA_RPC_URL = os.getenv("SOMNIA_RPC_URL", "https://rpc.ankr.com/somnia_testnet/6e3fd81558cf77b928b06b38e9409b4677b637118114e83364486294d5ff4811")  # Default to Ankr RPC
SOMNIA_TESTNET_URL = "https://testnet.somnia.network/"
CHAIN_ID_STR = os.getenv("CHAIN_ID", "50312")  # Default to Somnia Testnet Chain ID
try:
    CHAIN_ID = int(CHAIN_ID_STR)  # Convert to integer with error handling
except ValueError as e:
    raise ValueError(f"Invalid CHAIN_ID value '{CHAIN_ID_STR}'. Please set a numeric Chain ID (e.g., 50312).") from e

# Initialize Web3 with retry logic
w3 = Web3(Web3.HTTPProvider(SOMNIA_RPC_URL))
max_attempts = 3
for attempt in range(max_attempts):
    if w3.is_connected():
        print(f"Successfully connected to Somnia Testnet at {SOMNIA_RPC_URL}")
        break
    print(f"Attempt {attempt + 1} of {max_attempts} failed to connect. Retrying in 2 seconds...")
    time.sleep(2)  # Wait 2 seconds before retry
else:
    raise Exception(f"Failed to connect to Somnia Testnet at {SOMNIA_RPC_URL} after {max_attempts} attempts. Check RPC URL or network status.")

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
        # Wait for and locate the "Request Tokens" button
        request_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Request Tokens') or contains(@class, 'testnet-request-tokens')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", request_button)  # Scroll to top of element
        # Ensure button is clickable with additional wait
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((request_button)))
        # Force click to bypass overlap
        driver.execute_script("arguments[0].click();", request_button)
        print(f"Clicked 'Request Tokens' for {wallet_address}")

        # Wait for the popup modal
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup')]//input[@value='{wallet_address}']".format(wallet_address=wallet_address)))
        )
        time.sleep(random.uniform(1, 3))  # Wait for modal to stabilize

        # Click "Get STT" button in the popup
        get_stt_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Get STT')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", get_stt_button)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((get_stt_button)))
        driver.execute_script("arguments[0].click();", get_stt_button)
        print(f"Clicked 'Get STT' for {wallet_address}")

        # Wait for faucet response
        time.sleep(random.uniform(5, 10))
        print(f"Successfully claimed STT for {wallet_address}")
    except Exception as e:
        print(f"Failed to claim STT for {wallet_address}: {str(e)}")
        # Attempt to close the modal if it exists
        try:
            close_button = driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or @class='close']")
            if close_button:
                close_button[0].click()
        except:
            pass

# Function to generate a random Ethereum address (excluding wallets.json addresses)
def generate_random_address(exclude_wallets):
    while True:
        # Generate a random private key and derive address
        private_key = "0x" + "".join(random.choices("0123456789abcdef", k=64))
        account = Account.from_key(private_key)
        address = account.address.lower()
        if address not in [w["address"].lower() for w in exclude_wallets]:
            return address

# Function to send a transaction via UI
def send_transaction(wallet_address, private_key):
    driver.get(SOMNIA_TESTNET_URL)
    time.sleep(random.uniform(2, 5))  # Human-like delay
    try:
        # Click "Send Tokens" button
        send_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Send Tokens')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", send_button)  # Scroll to top of element
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((send_button)))
        driver.execute_script("arguments[0].click();", send_button)  # Force click to bypass overlap
        print(f"Clicked 'Send Tokens' for {wallet_address}")

        # Wait for and switch to the popup modal
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//div[contains(@class, 'modal') or contains(@class, 'popup')]"))
        )
        time.sleep(random.uniform(1, 3))  # Wait for modal to stabilize

        # Select random amount between 0.015 and 0.09 STT
        amount = round(random.uniform(0.015, 0.09), 3)  # Ensure 3 decimal places
        amount_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='number' or @type='text' and contains(@placeholder, 'Amount')]"))
        )
        amount_field.clear()
        amount_field.send_keys(str(amount))
        print(f"Set amount to {amount} STT for {wallet_address}")

        # Generate and fill random address
        wallets = load_wallets()
        random_address = generate_random_address(wallets)
        address_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' and contains(@placeholder, 'Address')]"))
        )
        address_field.clear()
        address_field.send_keys(random_address)
        print(f"Filled random address {random_address} for {wallet_address}")

        # Click "Send" button
        send_confirm_button = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//button[contains(text(), 'Send')]"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", send_confirm_button)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((send_confirm_button)))
        driver.execute_script("arguments[0].click();", send_confirm_button)  # Force click
        print(f"Clicked 'Send' for {wallet_address}")

        # Wait for transaction to process
        time.sleep(random.uniform(5, 10))
        print(f"Successfully sent {amount} STT to {random_address} from {wallet_address}")
    except Exception as e:
        print(f"Failed to send transaction for {wallet_address}: {str(e)}")
        # Attempt to close the modal if it exists
        try:
            close_button = driver.find_elements(By.XPATH, "//button[contains(text(), 'Close') or @class='close']")
            if close_button:
                close_button[0].click()
        except:
            pass

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
            send_transaction(wallet_address, private_key)
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
