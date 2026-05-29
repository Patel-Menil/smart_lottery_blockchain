import pytest
from brownie import network
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account
import time


def test_can_pick_winner():
    # 1. Arrange
    # Skip if we are on Ganache (this test is ONLY for Sepolia)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})

    # 2. Act
    # FIXED: Added the word 'Fee' to getEntranceFee()
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # FIXED: Removed fund_with_link() entirely!
    lottery.endLottery({"from": account})

    # Wait for the Chainlink node to respond on the real testnet
    print("Waiting 180 seconds for Chainlink node to fulfill request...")
    time.sleep(180)

    # 3. Assert
    # FIXED: Added .address so we are comparing two strings
    assert lottery.recentWinner() == account.address
    assert lottery.balance() == 0
