from scripts.helpful_scripts import get_account, get_contract

def main():
    account = get_account()
    print(f"Connected to wallet: {account}")
    
    vrf_coordinator = get_contract("vrf_coordinator")
    print("Creating a brand new v2.0 Subscription on Sepolia...")
    
    # This reaches out to the blockchain directly, ignoring your browser!
    tx = vrf_coordinator.createSubscription({"from": account})
    tx.wait(1)
    
    # Grab the ID directly from the blockchain receipt
    try:
        sub_id = tx.events["SubscriptionCreated"]["subId"]
        print(f"\n🎉 SUCCESS! Your new v2.0 Subscription ID is: {sub_id}")
        print("👉 Copy that number and put it in your brownie-config.yaml!")
    except Exception:
        print("Transaction succeeded, but couldn't print the ID. Check the Chainlink Dashboard.")