pragma solidity >=0.4.22 <0.7.0;
pragma experimental ABIEncoderV2;

contract Migrations {
  struct Task {
    uint    task_id;        // index from 0
    uint    cost;
    uint    deposit;
    string  check_sum;
    address sponsor;
    address target;
  }
  address public owner;
  Task[]  tasks;

  modifier restricted() {
    if (msg.sender == owner) _;
  }

  constructor() public {
    owner = msg.sender;
  }

  function submitTask(uint cost, string check_sum) public payable {
    require(cost <= msg.value, "cost lower");
    Task memory tmp_task;
    tmp_task.task_id = tasks.length;
    tmp_task.cost = cost;
    tmp_task.check_sum = check_sum;
    tmp_task.sponsor = msg.sender;
    tasks.push(tmp_task);
  }

  function receiveTask(uint id, uint deposit) public payable {
    require(deposit <= msg.value && id < tasks.length, "deposit lower or invalid id");
    require(msg.sender != tasks[id].sponsor, "sponsor cannot receive");
    tasks[id].target = msg.sender;
    tasks[id].deposit = deposit;
  }

  function returnResource(uint id, string check_sum) public payable {
    require(id < tasks.length, "invalid id");
    require(msg.sender == tasks[id].target, "only who receive it can return");
    require(keccak256(bytes(check_sum)) == keccak256(bytes(tasks[id].check_sum)), "files desdoryed");
    uint salary = (uint)(tasks[id].cost+tasks[id].deposit); // punishment
    (bool success) = msg.sender.call.value(salary)("");
    require(success, "get salary failed.");
  }

  function cancelTask(uint id) public payable {
    require(id < tasks.length, "invalid id");
    require(msg.sender == tasks[id].sponsor, "only sponsor can cancel it");
    uint ret_money = (uint)(tasks[id].cost*9/10);
    (bool success) = msg.sender.call.value(ret_money)("");
    require(success, "cancel failed.");
  }

  function getAllTasks() public view returns(Task[] memory Tasks) {
    return tasks;
  }

  function getTaskById(uint id) public view returns (Task memory task) {
    return tasks[id];
  }

  function getLastTaskId() public view returns (uint id) {
    return tasks[tasks.length-1].task_id;
  }
}
