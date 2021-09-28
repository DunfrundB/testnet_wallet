# Import dependencies
import subprocess
import json
import bit
import os
from web3 import Web3, eth
from dotenv import load_dotenv
import web3
from web3.contract import NonExistentReceiveFunction
from web3.types import SignedTx

# Load and set environment variables
load_dotenv()
mnemonic=os.getenv("mnemonic")

# Import constants.py and necessary functions from bit and web3
from constants import * 
 
# Create a function called `derive_wallets`
def derive_wallets(coin, numderive=3, form='json'):
    command = f'php derive --mnemonic="{mnemonic}" --coin={coin} -g --numderive={numderive} --cols=address,index,path,privkey,pubkey,pubkeyhash,xprv,xpub --format={form}'
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, err = p.communicate(timeout=10)
    p_status = p.wait(timeout=10)
    return json.loads(output)

# Create a dictionary object called coins to store the output from `derive_wallets`.
coins = {}
coins[BTCTEST] = derive_wallets(BTCTEST)
coins[ETH] = derive_wallets(ETH)

# Create a function called `priv_key_to_account` that converts privkey strings to account objects.
def priv_key_to_account(coin, priv_key):
    if coin == ETH:
        return Web3.eth.privateKeyToAccount(priv_key)
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet(priv_key)
    else:
        print("Unrecognized-CoinType: please try again.")

# Create a function called `create_tx` that creates an unsigned transaction appropriate metadata.
def create_tx(coin, account, to, amount):
    if coin == ETH:
        gasPrice = Web3.eth.gasPrice()
        nonce = Web3.eth.getTransactionCount()
        chainId = Web3.eth.chain_id()

        tx = {'to': to, 
            'from': account, 
            'value': amount, 
            'gas': '', 
            'gasPrice': gasPrice, 
            'nonce': nonce, 
            'chainID':chainId
            }
        return tx
    elif coin == BTCTEST:
        return bit.PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])

# Create a function called `send_tx` that calls `create_tx`, signs and sends the transaction.
def send_tx(coin, account, to, amount):
    if coin == ETH:
        account = priv_key_to_account(coin, coins[coin][0]['privkey'])
        raw_tx = create_tx(coin, account,to, amount)
        signed_tx = Web3.eth.account.sign_transaction(raw_tx, priv_key_to_account(coin, coins[coin][0]['address']))
        return Web3.eth.sendRawTransaction(signed_tx.rawTrasaction)
    elif coin == BTCTEST:
        account = priv_key_to_account(coin, coins[coin][0]['privkey'])
        raw_tx = create_tx(coin, account, to, amount)
        account.send(raw_tx)
    else:
        print('Unknown Coin Type: please try again')
