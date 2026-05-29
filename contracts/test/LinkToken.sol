// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

// Interface for the receiver of the transferAndCall function
interface ERC677Receiver {
    function onTokenTransfer(
        address _sender,
        uint256 _value,
        bytes memory _data
    ) external;
}

contract LinkToken is ERC20 {
    uint256 constant INITIAL_SUPPLY = 10 ** 27;

    // FIXED: Modern 0.8.x constructor syntax leveraging OpenZeppelin
    constructor() ERC20("ChainLink Token", "LINK") {
        _mint(msg.sender, INITIAL_SUPPLY);
    }

    /**
     * @dev transfer token to a specified address with additional data if the recipient is a contract.
     * @param _to The address to transfer to.
     * @param _value The amount to be transferred.
     * @param _data The extra data to be passed to the receiving contract.
     */
    function transferAndCall(
        address _to,
        uint256 _value,
        bytes memory _data
    ) public returns (bool success) {
        // Standard ERC20 transfer
        super.transfer(_to, _value);

        // If the receiver is a contract, trigger onTokenTransfer (ERC677 behavior)
        if (isContract(_to)) {
            contractFallback(_to, _value, _data);
        }
        return true;
    }

    // INTERNAL FUNCTIONS

    function contractFallback(
        address _to,
        uint256 _value,
        bytes memory _data
    ) private {
        ERC677Receiver receiver = ERC677Receiver(_to);
        receiver.onTokenTransfer(msg.sender, _value, _data);
    }

    function isContract(address _addr) private view returns (bool hasCode) {
        uint256 length;
        assembly {
            length := extcodesize(_addr)
        }
        return length > 0;
    }
}
