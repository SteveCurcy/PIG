#!/usr/bin/python3
# -*- coding: utf-8 -*-

from web3 import Web3
import json, abi

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
sponsor = web3.toChecksumAddress("0xc8686eF0a8C8b29389c60622Cf03D5F9D3bEfB97")
sponsor_key = "dabef10cc35cbc4a615ecf8b83340f5c7d10e03718f92de280e3ad141b983780"
target	= web3.toChecksumAddress("0x1805DA2Dd464D6208137edcB8AF13C4175ff1bAe")
target_key	= "65f29887c9290f1651302fbe5c34b47562496b2aa6d3f4d28c80237eb5d6c8e7"
contract_addr = web3.toChecksumAddress("0xccce5ac352092ca96020a2343ee456a97348d1b5")
contract = web3.eth.contract(address=contract_addr, abi=abi.abi)

def submitTask(cost: int, file_name: str, check_sum: str):
	gas_price = web3.toWei('40', 'gwei')
	nonce = web3.eth.getTransactionCount(sponsor)
	# 构造交易
	txn = contract.functions.submitTask(cost, file_name, check_sum).buildTransaction({
	    "from": sponsor,
	    "gasPrice": web3.toHex(gas_price),
	    "gas": web3.toHex(200000),
	    "value": web3.toHex(web3.toWei(cost+200000*gas_price, "wei")),# 发送总额必须大于转账金额+手续费否则会打包失败
	    "nonce": nonce # 防重放nonce,这个是必须的
	})
	# print(txn)
	# 发送交易
	signed_txn = web3.eth.account.signTransaction(txn, private_key=sponsor_key)
	# 发送到网络打包，如果报错 already known 就是上一笔交易正在打包，需要打包完成才能下一笔
	txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	# 取得转账哈希
	txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
	txn_receipt = web3.eth.getTransactionReceipt(txn_hash)
	# print(txhash, txn_receipt)

def cancelTask(task_id):
	gas_price = web3.toWei('40', 'gwei')
	nonce = web3.eth.getTransactionCount(sponsor)
	txn = contract.functions.cancelTask(task_id).buildTransaction({
	    "from": sponsor,
	    "gasPrice": web3.toHex(gas_price),
	    "gas": web3.toHex(200000),
	    "value": web3.toHex(web3.toWei(200000*gas_price, "wei")),
	    "nonce": nonce
	})
	signed_txn = web3.eth.account.signTransaction(txn, private_key=sponsor_key)
	txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
	txn_receipt = web3.eth.getTransactionReceipt(txn_hash)

def receiveTask(task_id, deposit):
	gas_price = web3.toWei('40', 'gwei')
	nonce = web3.eth.getTransactionCount(target)
	txn = contract.functions.receiveTask(task_id, deposit).buildTransaction({
	    "from": target,
	    "gasPrice": web3.toHex(gas_price),
	    "gas": web3.toHex(210000),
	    "value": web3.toHex(web3.toWei(deposit+210000*gas_price, "wei")),
	    "nonce": nonce
	})
	signed_txn = web3.eth.account.signTransaction(txn, private_key=target_key)
	txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
	txn_receipt = web3.eth.getTransactionReceipt(txn_hash)

def askResource(task_id):
	gas_price = web3.toWei('40', 'gwei')
	nonce = web3.eth.getTransactionCount(sponsor)
	txn = contract.functions.askResource(task_id).buildTransaction({
	    "from": sponsor,
	    "gasPrice": web3.toHex(gas_price),
	    "gas": web3.toHex(210000),
	    "value": web3.toHex(web3.toWei(210000*gas_price, "wei")),
	    "nonce": nonce
	})
	signed_txn = web3.eth.account.signTransaction(txn, private_key=sponsor_key)
	txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
	txn_receipt = web3.eth.getTransactionReceipt(txn_hash)

def returnResource(task_id, check_sum):
	gas_price = web3.toWei('40', 'gwei')
	nonce = web3.eth.getTransactionCount(target)
	txn = contract.functions.returnResource(task_id, check_sum).buildTransaction({
	    "from": target,
	    "gasPrice": web3.toHex(gas_price),
	    "gas": web3.toHex(210000),
	    "value": web3.toHex(web3.toWei(210000*gas_price, "wei")),
	    "nonce": nonce
	})
	signed_txn = web3.eth.account.signTransaction(txn, private_key=target_key)
	txn_hash = web3.eth.sendRawTransaction(signed_txn.rawTransaction)
	txhash = web3.toHex(web3.sha3(signed_txn.rawTransaction))
	txn_receipt = web3.eth.getTransactionReceipt(txn_hash)

if __name__ == '__main__':
	# submitTask(web3.toWei(0.1, 'ether'), "my_file", "something")
	# result = contract.functions.getAllTasks().call()
	# print(result)
	# receiveTask(0, web3.toWei(0.1, 'ether'))
	# result = contract.functions.getAllTasks().call()
	# print(result)
	# askResource(0)
	# result = contract.functions.getAllTasks().call()
	# print(result)
	# returnResource(0, "something")
	# result = contract.functions.getAllTasks().call()
	# print(result)
	cancelTask(1)
	result = contract.functions.getAllTasks().call()
	print(result)