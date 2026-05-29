// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

contract VRFCoordinatorV2Mock {
    uint96 public immutable BASE_FEE;
    uint96 public immutable GAS_PRICE_LINK;

    uint256 private s_nextRequestId = 1;
    uint64 private s_nextSubId = 1;

    struct Subscription {
        address owner;
        uint96 balance;
        address[] consumers;
    }
    mapping(uint64 => Subscription) private s_subscriptions;

    event RandomWordsRequested(
        bytes32 indexed keyHash,
        uint256 requestId,
        uint32 preSeed,
        uint64 indexed subId,
        uint16 minimumRequestConfirmations,
        uint32 callbackGasLimit,
        uint32 numWords,
        address indexed sender
    );
    event RandomWordsFulfilled(
        uint256 indexed requestId,
        uint256 outputSeed,
        uint96 payment,
        bool success
    );
    event SubscriptionCreated(uint64 indexed subId, address owner);
    event SubscriptionFunded(
        uint64 indexed subId,
        uint256 oldBalance,
        uint256 newBalance
    );

    constructor(uint96 _baseFee, uint96 _gasPriceLink) {
        BASE_FEE = _baseFee;
        GAS_PRICE_LINK = _gasPriceLink;
    }

    function createSubscription() external returns (uint64 subId) {
        subId = s_nextSubId++;
        s_subscriptions[subId] = Subscription({
            owner: msg.sender,
            balance: 0,
            consumers: new address[](0)
        });
        emit SubscriptionCreated(subId, msg.sender);
        return subId;
    }

    function fundSubscription(uint64 subId, uint96 amount) external {
        require(
            s_subscriptions[subId].owner != address(0),
            "InvalidSubscription"
        );
        uint256 oldBalance = s_subscriptions[subId].balance;
        s_subscriptions[subId].balance += amount;
        emit SubscriptionFunded(
            subId,
            oldBalance,
            s_subscriptions[subId].balance
        );
    }

    function addConsumer(uint64 subId, address consumer) external {
        require(
            s_subscriptions[subId].owner != address(0),
            "InvalidSubscription"
        );
        s_subscriptions[subId].consumers.push(consumer);
    }

    function requestRandomWords(
        bytes32 keyHash,
        uint64 subId,
        uint16 minimumRequestConfirmations,
        uint32 callbackGasLimit,
        uint32 numWords
    ) external returns (uint256 requestId) {
        require(
            s_subscriptions[subId].owner != address(0),
            "InvalidSubscription"
        );
        requestId = s_nextRequestId++;
        emit RandomWordsRequested(
            keyHash,
            requestId,
            0,
            subId,
            minimumRequestConfirmations,
            callbackGasLimit,
            numWords,
            msg.sender
        );
        return requestId;
    }

    function fulfillRandomWords(
        uint256 requestId,
        address consumerContract
    ) external {
        uint256[] memory words = new uint256[](1);
        words[0] = uint256(keccak256(abi.encode(requestId, block.timestamp)));

        // This fires the v2 specific internal receipt handler inside VRFConsumerBaseV2
        bytes memory resp = abi.encodeWithSignature(
            "rawFulfillRandomWords(uint256,uint256[])",
            requestId,
            words
        );
        (bool success, ) = consumerContract.call(resp);
        emit RandomWordsFulfilled(requestId, words[0], 0, success);
    }
}
