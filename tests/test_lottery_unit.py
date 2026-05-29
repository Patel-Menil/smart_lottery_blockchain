import pytest
from brownie import network, exceptions, accounts
from web3 import Web3
from scripts.deploy_lottery import deploy_lottery
from scripts.helpful_scripts import (
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
    get_account,
    get_contract,
)


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    lottery = deploy_lottery()
    expected_entrance_fee = Web3.to_wei(0.025, "ether")
    entrance_fee = lottery.getEntranceFee()
    assert entrance_fee == expected_entrance_fee


def test_cant_enter_unless_started():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": get_account(), "value": lottery.getEntranceFee()})


def test_can_start_and_enter_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    # Act
    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Assert
    assert lottery.players(0) == account


def test_can_end_lottery():
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})

    # Act
    lottery.endLottery({"from": account})

    # Assert
    assert lottery.lotteryState() == 2


def test_can_pick_winner_correctly():
    # 1. Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    account_1 = get_account(index=1)
    account_2 = get_account(index=2)

    lottery.startLottery({"from": account})

    # 3 Players enter the lottery
    lottery.enter({"from": account, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account_1, "value": lottery.getEntranceFee()})
    lottery.enter({"from": account_2, "value": lottery.getEntranceFee()})

    # Record the starting balances of all 3 players BEFORE the winner is picked
    starting_balances = {
        account.address: account.balance(),
        account_1.address: account_1.balance(),
        account_2.address: account_2.balance(),
    }

    # 2. Act
    # End the lottery and grab the V2 request ID
    transaction = lottery.endLottery({"from": account})
    request_id = transaction.events["RandomWordsRequested"]["requestId"]

    # Fulfill the randomness using the V2 Mock
    get_contract("vrf_coordinator").fulfillRandomWords(
        request_id, lottery.address, {"from": account}
    )

    # 3. Assert
    winner_address = lottery.recentWinner()

    # Check that a valid player actually won
    assert winner_address in starting_balances.keys()

    # Check that the contract was emptied
    assert lottery.balance() == 0

    # Check that the winner got the money!
    assert accounts.at(winner_address).balance() > starting_balances[winner_address]
