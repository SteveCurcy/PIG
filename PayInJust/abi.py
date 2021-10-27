abi="""[
    {
      "constant": true,
      "inputs": [],
      "name": "owner",
      "outputs": [
        {
          "name": "",
          "type": "address"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "inputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "constructor"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "cost",
          "type": "uint256"
        },
        {
          "name": "check_sum",
          "type": "string"
        }
      ],
      "name": "submitTask",
      "outputs": [],
      "payable": true,
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "uint256"
        },
        {
          "name": "deposit",
          "type": "uint256"
        }
      ],
      "name": "receiveTask",
      "outputs": [],
      "payable": true,
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "uint256"
        },
        {
          "name": "check_sum",
          "type": "string"
        }
      ],
      "name": "returnResource",
      "outputs": [],
      "payable": true,
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "constant": false,
      "inputs": [
        {
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "cancelTask",
      "outputs": [],
      "payable": true,
      "stateMutability": "payable",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "getAllTasks",
      "outputs": [
        {
          "components": [
            {
              "name": "task_id",
              "type": "uint256"
            },
            {
              "name": "cost",
              "type": "uint256"
            },
            {
              "name": "deposit",
              "type": "uint256"
            },
            {
              "name": "check_sum",
              "type": "string"
            },
            {
              "name": "sponsor",
              "type": "address"
            },
            {
              "name": "target",
              "type": "address"
            }
          ],
          "name": "Tasks",
          "type": "tuple[]"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {
          "name": "id",
          "type": "uint256"
        }
      ],
      "name": "getTaskById",
      "outputs": [
        {
          "components": [
            {
              "name": "task_id",
              "type": "uint256"
            },
            {
              "name": "cost",
              "type": "uint256"
            },
            {
              "name": "deposit",
              "type": "uint256"
            },
            {
              "name": "check_sum",
              "type": "string"
            },
            {
              "name": "sponsor",
              "type": "address"
            },
            {
              "name": "target",
              "type": "address"
            }
          ],
          "name": "task",
          "type": "tuple"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [],
      "name": "getLastTaskId",
      "outputs": [
        {
          "name": "id",
          "type": "uint256"
        }
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    }
  ]"""