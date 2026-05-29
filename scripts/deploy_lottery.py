from scripts.helpful_scripts import (
    get_account,
    get_contract,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from brownie import Lottery, network, config
import time


def deploy_lottery():
    account = get_account()

    price_feed_address = get_contract("eth_usd_price_feed").address
    vrf_coordinator = get_contract("vrf_coordinator")
    keyhash = config["networks"][network.show_active()]["keyhash"]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        tx = vrf_coordinator.createSubscription({"from": account})
        subscription_id = tx.events["SubscriptionCreated"]["subId"]
        vrf_coordinator.fundSubscription(
            subscription_id, 1000000000000000000, {"from": account}
        )
    else:
        subscription_id = config["networks"][network.show_active()]["subscription_id"]

    lottery = Lottery.deploy(
        price_feed_address,
        vrf_coordinator.address,
        keyhash,
        subscription_id,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("Adding contract as an authorized consumer...")
    tx = vrf_coordinator.addConsumer(
        subscription_id, lottery.address, {"from": account}
    )
    tx.wait(1)

    print("deployed lovely")
    return lottery


def start_lottery():
    account = get_account()
    lottery = Lottery[-1]
    starting_tx = lottery.startLottery({"from": account})
    starting_tx.wait(1)
    print("The lottery is started!")


def enter_lottery():
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 100000000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)
    print("You entered the lottery!")


def end_lottery():
    account = get_account()
    lottery = Lottery[-1]

    ending_transaction = lottery.endLottery({"from": account})
    ending_transaction.wait(1)

    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        request_id = ending_transaction.events["RandomWordsRequested"]["requestId"]
        vrf_coordinator = get_contract("vrf_coordinator")
        vrf_coordinator.fulfillRandomWords(
            request_id, lottery.address, {"from": account}
        )
    else:
        time.sleep(180)

    print(f"{lottery.recentWinner()} is the new winner!")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
