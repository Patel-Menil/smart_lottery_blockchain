from scripts.helpful_scripts import get_account, get_contract
from brownie import config, network

def main():
    account = get_account()
    
    # Your specific Subscription ID
    sub_id = 12596
    amount = 10 * 10**18  # 10 LINK (it has 18 decimal places)
    
    link_token = get_contract("link_token")
    vrf_coordinator = config["networks"][network.show_active()]["vrf_coordinator"]
    
    print(f"Funding Subscription {sub_id} with 10 LINK...")
    
    # We must convert your ID (12596) into a 32-byte hexadecimal string for the blockchain
    data = "0x" + hex(sub_id)[2:].zfill(64)
    
    # transferAndCall sends the LINK and triggers the VRF Coordinator to credit your subscription
    tx = link_token.transferAndCall(
        vrf_coordinator,
        amount,
        data,
        {"from": account}
    )
    tx.wait(1)
    
    print("🎉 Subscription funded successfully!")