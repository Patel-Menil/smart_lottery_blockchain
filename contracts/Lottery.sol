// SPDX-License-Identifier: MIT
pragma solidity ^0.8.6;

import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.8/vrf/VRFConsumerBaseV2.sol";
import "@chainlink/contracts/src/v0.8/interfaces/VRFCoordinatorV2Interface.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBaseV2, Ownable {
    address payable[] public players;
    uint256 public usdEntryFee;
    AggregatorV3Interface internal _ethUsdPriceFeed;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;

    VRFCoordinatorV2Interface COORDINATOR;
    bytes32 public keyhash;
    uint64 public subscriptionId;
    uint32 callbackGasLimit = 100000;
    uint16 requestConfirmations = 3;
    uint32 numWords = 1;
    event RequestedRandomness(uint256 requestId);

    address public recentWinner;

    constructor(
        address _priceFeedAddress,
        address _vrfCoordinator,
        bytes32 _keyhash,
        uint64 _subscriptionId
    ) VRFConsumerBaseV2(_vrfCoordinator) {
        usdEntryFee = 50 * (10 ** 18);
        _ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED;
        COORDINATOR = VRFCoordinatorV2Interface(_vrfCoordinator);
        keyhash = _keyhash;
        subscriptionId = _subscriptionId;
    }

    function fulfillRandomWords(
        uint256 requestId,
        uint256[] memory randomWords
    ) internal override {
        require(
            lotteryState == LOTTERY_STATE.CALCULATING_WINNER,
            "Not ready yet!"
        );
        require(randomWords.length > 0, "Random not found!");

        uint256 indexOfWinner = randomWords[0] % players.length;
        address payable winner = players[indexOfWinner];
        recentWinner = winner;

        winner.transfer(address(this).balance);

        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATE.OPEN, "Lottery not open!");
        require(msg.value >= getEntranceFee(), "Not Enough ETH!");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (, int price, , , ) = _ethUsdPriceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10 ** 10;
        uint256 costToEnter = (usdEntryFee * 10 ** 18) / adjustedPrice;
        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(
            lotteryState == LOTTERY_STATE.CLOSED,
            "Can't Start a new lottery yet!"
        );
        lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        lotteryState = LOTTERY_STATE.CALCULATING_WINNER;

        uint256 requestId = COORDINATOR.requestRandomWords(
            keyhash,
            subscriptionId,
            requestConfirmations,
            callbackGasLimit,
            numWords
        );
        emit RequestedRandomness(requestId);
    }
}
