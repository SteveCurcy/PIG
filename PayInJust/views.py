from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from web3 import Web3, HTTPProvider
import json, codecs, hashlib, zipfile
import PayInJust.abi, os, shutil, pymysql

w3 = Web3(HTTPProvider("http://localhost:8545"))
contract_addr = w3.toChecksumAddress("0x039298f13175107da647db6aeaf2b8069507cdb6")
contract = w3.eth.contract(address=contract_addr, abi=PayInJust.abi.abi)
user, user_key = None, None     # user - PK, user_key - SK

def login(request):
    if request.method == "GET":
        return render(request, "login.html")
    # data = json.loads(request.body.decode("utf-8"))
    username = request.POST.get('user')
    password = request.POST.get('pass')
    if username != "cx" or password != "123":
        return JsonResponse({})
    rep = redirect("/index/")
    rep.set_cookie("is_log", "sessionid")
    request.session['user'] = username
    return rep
    
def index(request):
    status = request.COOKIES.get('is_log') # 收到浏览器的再次请求,判断浏览器携带的cookie是不是登录成功的时候响应的 cookie
    if not status:
        return redirect('/login/')
    if user:
        return render(request, "index.html", {"balance": w3.eth.getBalance(user)/1e18})
    else:
        return render(request, "index.html", {"balance": ""})

def in_key(request):
    global user, user_key
    if request.method == 'GET':
        return JsonResponse({})
    data = json.loads(request.body.decode('utf-8'))
    cur_acnt = w3.eth.account.from_key(data['key'])
    user_key = data['key']
    user = w3.toChecksumAddress(cur_acnt.address)
    if cur_acnt.address in w3.eth.accounts:
        return JsonResponse({'balance': w3.eth.getBalance(cur_acnt.address)/1e18})
    else:
        user = None
        user_key = None
        return JsonResponse({})

def submit_file(request):
    if request.method == 'GET':
        return redirect('/index')
    check_sum = ""
    sha3 = hashlib.sha3_256()
    for i in request.FILES:
        with open('./repo/'+i, 'wb') as f:
            f.write(request.FILES[i].read())
            sha3.update(request.FILES[i].read())
    check_sum = sha3.hexdigest()
    return JsonResponse({"check_sum": check_sum})

def submit_cost(request):
    global user, user_key, contract
    if request.method == 'GET':
        return JsonResponse({})
    data = json.loads(request.body.decode('utf-8'))
    file_name = data['name']
    file_size = data['size']
    check_sum = data['check_sum']
    try:
        cost = int(float(data['cost'])*1e18)
        gas_price = w3.toWei('40', 'gwei')
        nonce = w3.eth.getTransactionCount(user)
        # 构造交易
        txn = contract.functions.submitTask(cost, check_sum).buildTransaction({
            "from": user,
            "gasPrice": w3.toHex(gas_price),
            "gas": w3.toHex(200000),
            "value": w3.toHex(cost+200000*gas_price),# 发送总额必须大于转账金额+手续费否则会打包失败
            "nonce": nonce # 防重放nonce,这个是必须的
        })
        # 发送交易
        signed_txn = w3.eth.account.signTransaction(txn, private_key=user_key)
        # 发送到网络打包，如果报错 already known 就是上一笔交易正在打包，需要打包完成才能下一笔
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # 取得转账哈希
        txhash = w3.toHex(w3.sha3(signed_txn.rawTransaction))
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
    except Exception as e:
        print(e)
        os.remove("./repo/"+file_name)
        return JsonResponse({})
    id = contract.functions.getLastTaskId().call()
    if file_size >= 2**40:
        file_size = "{:.1f}TB".format(file_size/(2**40))
    elif file_size >= 2**30:
        file_size = "{:.1f}GB".format(file_size/(2**30))
    elif file_size >= 2**20:
        file_size = "{:.1f}MB".format(file_size/(2**20))
    elif file_size >= 2**10:
        file_size = "{:.1f}KB".format(file_size/(2**10))
    else:
        file_size = "{:.1f}B".format(file_size)
    # 把相关信息写进数据库
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "INSERT INTO tasks (id, name, size) VALUES ({}, \"{}\", \"{}\")".format(id, file_name, file_size)
    cursor.execute(sql)
    con.commit()
    con.close()
    os.mkdir('./repo/'+str(id))
    shutil.move('./repo/'+file_name, './repo/'+str(id)+'/'+file_name)
    return JsonResponse({'balance': w3.eth.getBalance(user)/1e18})

@csrf_exempt
def recv_task(request):
    if request.method == 'GET':
        return JsonResponse({})
    global user, user_key, contract
    data = json.loads(request.body.decode('utf-8'))
    # contract work
    try:
        gas_price = w3.toWei('40', 'gwei')
        nonce = w3.eth.getTransactionCount(user)
        deposit = w3.toWei(data['deposit'], 'ether')
        txn = contract.functions.receiveTask(data['id'], deposit).buildTransaction({
            "from": user,
            "gasPrice": w3.toHex(gas_price),
            "gas": w3.toHex(210000),
            "value": w3.toHex(deposit+210000*gas_price),
            "nonce": nonce
        })
        signed_txn = w3.eth.account.signTransaction(txn, private_key=user_key)
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        txhash = w3.toHex(w3.sha3(signed_txn.rawTransaction))
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
    except Exception as e:
        print(e)
        return JsonResponse({})
    # end of contract
    # os.chdir('./repo/'+str(data['id']))
    # with zipfile.ZipFile('./cache/'+str(data['id'])+'.zip', "w", zipfile.ZIP_DEFLATED) as zf:
    #     for i in os.walk('.'):
    #         for n in i[2]:
    #             zf.write(''.join((i[0], '/', n)))
    # os.chdir('../../')
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "SELECT name from tasks where id={}".format(data['id'])
    cursor.execute(sql)
    info = cursor.fetchone()
    sql = "UPDATE tasks SET status=1 where id={}".format(data['id'])
    cursor.execute(sql)
    con.commit()
    con.close()
    f = open('./repo/'+str(data['id'])+'/'+info[0], 'rb')
    response = FileResponse(f)
    response['Content-Type'] = 'application/zip'
    # content_dis = 'attachment;filename="'+info[0]+'"'
    # response['Content-Disposition'] = content_dis
    return response

def clear_cache(request):
    if request.method == 'GET':
        return JsonResponse({})
    data = json.loads(request.body.decode('utf-8'))
    shutil.rmtree('./repo/'+str(data['id']))
    return JsonResponse({'balance': w3.eth.getBalance(user)/1e18})

def ask_src(request):
    if request.method == 'GET':
        return JsonResponse({})
    data = json.loads(request.body.decode('utf-8'))
    task = contract.functions.getTaskById(data['id']).call()
    if user != task[4]:
        return JsonResponse({})
    last_id = contract.functions.getLastTaskId().call()
    if (data['id'] > last_id):
        return JsonResponse({})
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "UPDATE tasks SET status=2 where id={}".format(data['id'])
    cursor.execute(sql)
    con.commit()
    con.close()
    return JsonResponse({"ok":1})

def ret_src(request):
    if request.method == 'GET':
        return JsonResponse({})
    global user, user_key, contract
    data = json.loads(request.body.decode('utf-8'))
    file_name = data['name']
    check_sum = data['check_sum']
    id = data['id']
    try:
        gas_price = w3.toWei('40', 'gwei')
        nonce = w3.eth.getTransactionCount(user)
        # 构造交易
        txn = contract.functions.returnResource(id, check_sum).buildTransaction({
            "from": user,
            "gasPrice": w3.toHex(gas_price),
            "gas": w3.toHex(200000),
            "value": w3.toHex(200000*gas_price),# 发送总额必须大于转账金额+手续费否则会打包失败
            "nonce": nonce # 防重放nonce,这个是必须的
        })
        # 发送交易
        signed_txn = w3.eth.account.signTransaction(txn, private_key=user_key)
        # 发送到网络打包，如果报错 already known 就是上一笔交易正在打包，需要打包完成才能下一笔
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # 取得转账哈希
        txhash = w3.toHex(w3.sha3(signed_txn.rawTransaction))
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
    except Exception as e:
        print(e)
        os.remove("./repo/"+file_name)
        return JsonResponse({})
    # 把相关信息写进数据库
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "UPDATE tasks SET status=3 where id={}".format(id)
    cursor.execute(sql)
    con.commit()
    con.close()
    os.mkdir('./repo/'+str(id))
    shutil.move('./repo/'+file_name, './repo/'+str(id)+'/'+file_name)
    return JsonResponse({'balance': w3.eth.getBalance(user)/1e18})

@csrf_exempt
def download(request):
    if request.method == 'GET':
        return JsonResponse({})
    data = json.loads(request.body.decode('utf-8'))
    tar = (os.listdir('./repo/'+str(data['id'])))[0]
    f = open('./repo/'+str(data['id'])+'/'+tar, 'rb')
    response = FileResponse(f)
    response['Content-Type'] = 'application/zip'
    # content_dis = 'attachment;filename="'+info[0]+'"'
    # response['Content-Disposition'] = content_dis
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "UPDATE tasks SET status=4 where id={}".format(data['id'])
    cursor.execute(sql)
    con.commit()
    con.close()
    return response

def cancel(request):
    if request.method == 'GET':
        return JsonResponse({})
    global user, user_key, contract
    data = json.loads(request.body.decode('utf-8'))
    id = data['id']
    try:
        gas_price = w3.toWei('40', 'gwei')
        nonce = w3.eth.getTransactionCount(user)
        # 构造交易
        txn = contract.functions.cancelTask(id).buildTransaction({
            "from": user,
            "gasPrice": w3.toHex(gas_price),
            "gas": w3.toHex(200000),
            "value": w3.toHex(200000*gas_price),# 发送总额必须大于转账金额+手续费否则会打包失败
            "nonce": nonce # 防重放nonce,这个是必须的
        })
        # 发送交易
        signed_txn = w3.eth.account.signTransaction(txn, private_key=user_key)
        # 发送到网络打包，如果报错 already known 就是上一笔交易正在打包，需要打包完成才能下一笔
        txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        # 取得转账哈希
        txhash = w3.toHex(w3.sha3(signed_txn.rawTransaction))
        txn_receipt = w3.eth.getTransactionReceipt(txn_hash)
    except Exception as e:
        return JsonResponse({})
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "UPDATE tasks SET status=5 where id={}".format(id)
    cursor.execute(sql)
    con.commit()
    con.close()
    shutil.rmtree('./repo/'+str(data['id']))
    return JsonResponse({})

# find tasks which are submited but not received
def get_avils(request):
    if request.method == 'GET':
        return JsonResponse({})
    result = contract.functions.getAllTasks().call()
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "SELECT * from tasks"
    cursor.execute(sql)
    info = cursor.fetchall()
    con.close()
    tasks = list()
    for j in range(len(result)):
        i = result[j]
        if info[j][3] != 0 or i[4] == user:
            continue
        task = dict()
        task.update({"id":i[0],"cost":i[1],"status":info[j][3],"file_name":info[j][1],"file_size": info[j][2]})
        tasks.append(task)
    return JsonResponse({"tasks": tasks})

# get tasks which I submited
def get_subs(request):
    if request.method == 'GET':
        return JsonResponse({})
    result = contract.functions.getAllTasks().call()
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "SELECT * from tasks"
    cursor.execute(sql)
    info = cursor.fetchall()
    con.close()
    tasks = list()
    for j in range(len(result)):
        i = result[j]
        if i[4] != user:
            continue
        task = dict()
        task.update({"id":i[0],"cost":i[1],"status":info[j][3],"file_name":info[j][1],"file_size": info[j][2]})
        tasks.append(task)
    return JsonResponse({"tasks": tasks})

# get tasks which I received
def get_recvs(request):
    if request.method == 'GET':
        return JsonResponse({})
    result = contract.functions.getAllTasks().call()
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "SELECT * from tasks"
    cursor.execute(sql)
    info = cursor.fetchall()
    con.close()
    tasks = list()
    for j in range(len(result)):
        i = result[j]
        if i[5] != user:
            continue
        task = dict()
        task.update({"id":i[0],"cost":i[1],"status":info[j][3],"file_name":info[j][1],"file_size": info[j][2]})
        tasks.append(task)
    return JsonResponse({"tasks": tasks})

# return tasks which are relative to me
def get_mines(request):
    if request.method == 'GET':
        return JsonResponse({})
    result = contract.functions.getAllTasks().call()
    con = pymysql.connect(host='localhost',user='root',password='123',database='PIJ')
    cursor = con.cursor()
    sql = "SELECT * from tasks"
    cursor.execute(sql)
    info = cursor.fetchall()
    con.close()
    tasks = list()
    for j in range(len(result)):
        i = result[j]
        if i[4] != user and i[5] != user:
            continue
        task = dict()
        if i[4] == user:
            task.update({"id":i[0],"cost":i[1],"status":info[j][3],"file_name":info[j][1],"file_size": info[j][2],"mine":1})
        else:
            task.update({"id":i[0],"cost":i[1],"status":info[j][3],"file_name":info[j][1],"file_size": info[j][2],"mine":0})
        tasks.append(task)
    return JsonResponse({"tasks": tasks})

def logout(request):
    request.session.flush()
    rep = redirect('/login/')
    rep.delete_cookie("is_log")
    user = None
    user_key = None
    return rep # 点击注销后执行,删除cookie,不再保存用户状态，并弹到登录页面