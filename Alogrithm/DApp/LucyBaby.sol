pragma solidity ^0.4.16;

contract LuckyBaby {

    address public owner;
    uint public totalReward;
    uint public minTicket;
    uint public maxPool;
    
    address[] lottery;
    
    event Awared(address awareder, uint amount);
    event Pay(address payer, uint amount);
    
    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }
    
    function () payable {
        require(msg.value >= minTicket);
        require(msg.value % minTicket == 0);
        var amount = msg.value;
        var num = amount / minTicket;
        for (uint p = 0; p < num; p++) {
            lottery.push(msg.sender);
        }
        Pay(msg.sender, msg.value);
        totalReward += amount;
        if (totalReward >= maxPool) {
            award();
        }
    }
    
    function award () private {
        uint random_number = uint(block.blockhash(block.number-1)) % lottery.length;
        owner.transfer(minTicket);
        lottery[random_number].transfer(totalReward-minTicket);
        Awared(lottery[random_number],totalReward-minTicket);
        delete lottery;
        totalReward = 0;
    }
    
    function LuckyBaby() {
        owner = msg.sender;
        minTicket = 10**17;
        maxPool = 5*10**18;
    }
    
    function changeOwner(address _newOwner) onlyOwner {
        if (_newOwner != address(0)) {
            owner = _newOwner;
        }
    }
}

