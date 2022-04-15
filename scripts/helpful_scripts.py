from brownie import (
    network, 
    config, 
    accounts, 
    MockV3Aggregator, 
    VRFCoordinatorV2Mock,
    LinkToken,
    Contract,
    interface
)

FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork-dev", "mainnet-fork"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]


def get_account(index=None, id=None):
    # 1. accounts[0] - local ganache, first account
    # 2. accounts.add("env") - account from env variables in brownie-config
    # 3. accounts.load("id") - account from id
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS 
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorV2Mock,
    "link_token": LinkToken
}

def get_contract(contract_name):
    """
    This function will grab the contract addresses from the brownie-config 
    if defined, otherwise it will deploy a mock version of that contract and
    return that mock contract.

        Args:
            contract_name (string)
        Returns:
            brownie.network.contract.ProjectContract : The most recently deployed
            version of this contract.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            #MockV3Aggregator.length
            deploy_mocks()
        contract = contract_type[-1] # grab the most recent deployment of MockV3Aggregator
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address & ABI
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
    return contract

DECIMALS = 8
INITIAL_VALUE = 200000000000

def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_VALUE):
    account = get_account()
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    VRFCoordinatorV2Mock.deploy(10, 2, {"from": account})
    LinkToken.deploy({"from": account})
    print("Deployed mocks: Price feed, coordinator and LinkToken")

def get_subscription_id():
    return config["networks"]["rinkeby"]["s_subscriptionId"]

def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    #tx = link_token.transfer(contract_address, amount, {"from": account})
    link_token_contract = interface.LinkTokenInterface(link_token.address)
    tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    tx.wait(1)
    print("Fund contract!")
    return tx
