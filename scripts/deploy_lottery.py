from scripts.helpful_scripts import get_account, get_contract, get_subscription_id, fund_with_link
from brownie import Lottery, config, network

def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()

def deploy_lottery():
    account = get_account()
    # address _priceFeedAddress,
    # uint64 subscriptionId
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_subscription_id(),
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False)
    )
    print("Deployed Lottery!")
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
    print("Entered lottery!")

def end_lottery():
    account = get_account()
    lottery = Lottery[-1]
    #tx = fund_with_link(lottery.address)
    #tx.wait(1)
    ending_tx = lottery.endLottery({"from": account})
    ending_tx.wait(1)
    time.sleep(60)
    print(f"{lottery.recentWinner()} is the new winner!")