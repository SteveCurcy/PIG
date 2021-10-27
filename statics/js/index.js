function logout(){
    sessionStorage.removeItem('user');
}
function input_key() {
	key = $("#key").val();
	// console.log(key);
	if (key.length != 64){
		alert("The private key must be exactly 32 bytes long");
		return;
	}
	data=JSON.stringify({'key': key});
	$.ajax({
		url: '/in_key/',
		type: 'post',
		dataType: 'JSON',
		data: data,
		success: (res)=>{
			$("#balance").text("余额: "+(res['balance'].toFixed(2)).toString());
		},
		error: (err)=>{
			console.log(err);
		}
	});
}
function key_tog(){
	let key = document.getElementById("_key");
	if (key.className == 'in') key.className = 'in_hid';
	else key.className = 'in';
}
function key_hid(){
	document.getElementById("_key").className = 'in_hid';
}
function calc_cost(){
	let files = $("#file")[0].files, cnt_size = 0;
	for (let i in files) {
		if (i == 'length') break;
		cnt_size += files[i].size;
	}
	$("#pay").attr("placeholder", "推荐金额: "+(cnt_size * 250).toString());
	$("#pay").val(cnt_size * 25 / 1e9);	// 25 GWei/B
}
function ch_typ(){
    let opts = document.getElementsByTagName("option");
    let types = [];
    for (let i in opts) {
        if (i == 'length') break;
        if (opts[i].value == "") continue;
        types.push(opts[i].value);
    }
    for (let i in types) {
        document.getElementById(types[i]).className="hid";
    }
    if ($("#task_type").val())document.getElementById($("#task_type").val()).className=$("#task_type").val();
}
function home(){
	document.getElementById("func").style.display="none";
	document.getElementById("home").style.display="";
}
function func(){
	document.getElementById("home").style.display="none";
	document.getElementById("func").style.display="";
}
function ch_navi(e){
	let navis=['sub', 'recv', 'my_sub', 'my_recv', 'my_tk'];
	for (let i in navis) {
        document.getElementById(navis[i]).className="";
    }
    document.getElementById(e.id).className="chosen";
}
function sub_tk() {
	$("#op_tk").empty();
	$("#op_tk").html('<label for="task_type">请选择任务类型</label><select id="task_type">\
        <option value="">--请选择任务类型--</option>\
        <option value="file-store" selected="selected" onclick="opt()">文件云存储</option>\
    </select><div id="file-store" class="file-store">\
    <form enctype="multipart/form-data" style="width:100%;">\
        <label id="for-file" for="file"><p>点击此区域上传文件</p></label><input type="file" id="file" style="display:none;" />\
        </br><label for="pay" style="margin-right:45px;">支付金额</label><input id="pay" placeholder="支付金额" />Ether</br>\
        <!-- <label for="deposit">交易打包费用</label><input id="deposit" placeholder="Tips:费用越高您的排队时延可能越小哦～ 推荐: 大于21219" />Wei</br> -->\
        <input id="load" type="button" onclick="submitTask()" /></form></div>');
	$("#task_type").change(ch_typ);
    $("#file").change(calc_cost);
}
function submitTask(){
	if ($("#balance").text() === '余额') {
		alert("请先输入您的私钥");
		return;
	}
	let files = $("#file")[0].files;
	if (files[0].type != "application/zip") {
		alert("您只能上传打包好的zip");
		return;
	}
	let cost = parseFloat($("#pay").val())*1e18;
	let balance = parseFloat($("#balance"))*1e18;
	if (balance < cost+200000*1e9) {
		alert("余额不足！");
		return;
	}
	let cnt_size = 0;
	for (let i in files) {
		if (i == 'length') break;
		cnt_size += files[i].size;
	}
	if (cnt_size*25/1e9 > parseFloat($("#pay").val())){
		alert("请输入大于等于推荐值的金额！");
		return;
	}
	let form_data = new FormData(), size = files[0].size, name = files[0].name;
	form_data.append(files[0].name, files[0]);
	$.ajax({
        url: "/submit_file/",
        data: form_data,
        type: "POST",
        contentType: false,
        processData: false,
        cache: false,
        dataType: "json",
        success: function (res) {
        	$.ajax({
			    url: '/submit_cost/',
				type: 'post',
				dataType: 'JSON',
				data: JSON.stringify({"check_sum": res["check_sum"], "cost": $("#pay").val(), "size": size, "name": name}),
			    success: function (res) {
			        $("#balance").text("余额: "+(res['balance'].toFixed(2)).toString());
	        		alert("上传成功");
			    },
			    error: function (err) {
			        alert("上传失败，请重新尝试");
				}
			});
        },
        error: function (err) {
        	alert("上传失败，请重新尝试");
        }
    });
}
function stop(e){e.parentNode.parentNode.parentNode.parentNode.removeChild(e.parentNode.parentNode.parentNode);}
function recv_tk(e){
	data = JSON.stringify({'id': parseInt(e.parentNode.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.innerText),
		// 'file_name': e.parentNode.previousSibling.previousSibling.previousSibling.previousSibling.innerText,
		'deposit': 0.1});
	$("body").append(`<div style="background-color:rgba(0,0,0,0.5);position:absolute;top:0;width:100%;height:100%;display:flex;justify-content:center;align-items:center;">\
    <div style="background-color:#fff;width:500px;height:400px;border-radius:5px;display:flex;flex-direction:column;justify-content:space-around;align-items:center;"><span style="display:flex;width:80%;justify-content:space-around;align-items:center;"><label for="deposit">押金</label><input id="deposit" style="margin:20px 0;border:1px solid #3B78CC;display:flex;width:80%;height:46px;display:inline-block;">Ether</span><span style="display:flex;width:80%;justify-content:space-around;align-items:center;"><input type="button" value="取消" onclick="stop(this)" style="width:100px;height:50px;border-radius:10px;"><input type="button" value="确定" onclick='recvTask(${data})' style="width:100px;height:50px;border-radius:10px;"></span></div>\
</div>`);
};
function recvTask(data) {
	if ($("#deposit").val() == "") {alert("请输入押金金额");return;}
	data['deposit'] = parseFloat($("#deposit").val());
	let body = document.getElementsByTagName("body")[0];body.removeChild(body.lastChild);
	const xhr = new XMLHttpRequest();
	xhr.open('POST', '/recv_task/', true);
	xhr.setRequestHeader('content-type', 'application/json');
	//定义responseType='blob', 是读取文件成功的关键，这样设置可以解决下载文件乱码的问题
	xhr.responseType = "blob";    
	xhr.onload = () => {
	 	if (xhr.response['type'] == "application/json") {
	 		alert("接受失败");
	 		return;
	 	}
	//'\ufeff' 这个变量是定义字符集为utf-8, 防止中文乱码的问题。
	// {type: 'application/msword'} 根据文档类型来定义这个type。MIMA type
	  	const blob = new Blob(["\ufeff", xhr.response], {type: 'application/zip'});
	  	const blobUrl = URL.createObjectURL(blob);
	  	const a = document.createElement('a');
	  	a.style.display = 'none';
	  	a.download = `Task-${data['id']}.zip`;
	  	a.href = blobUrl;
	 	a.target = '_blank';
	 	a.click();
	 	window.URL.revokeObjectURL(a.href);
	 	delete a;
	 	$.ajax({
			url: '/clear_cache/',
			type: 'post',
			dataType: 'JSON',
			data: JSON.stringify({'id': data['id']}),
			success: (res)=>{
				$("#balance").text("余额: "+(res['balance'].toFixed(2)).toString());
				get_avil_tk();
			},
			error: (err)=>{
				console.log(err);
			}
		});
	};
	xhr.send(JSON.stringify(data));
}
function askResource(e) {
	let id = parseInt(e[0].parentNode.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.innerText);
	$.ajax({
		url: "/ask_src/",
		type: 'post',
		dataType: 'JSON',
		data: JSON.stringify({'id': id}),
		success: (res)=>{
			if (res['ok']) {
				if (e[1] == 0) get_sub_tk();
				else get_my_tk();
			} else {
				alert('失败，请重试');
			}
		},
		error: (err)=>{
			console.log(err);
			alert('失败，请重试');
		}
	});
}
function ret_rsc(e) {
	data = JSON.stringify({'which': e[1],'id': parseInt(e[0].parentNode.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.innerText)});
	$("body").append(`<div style="background-color:rgba(0,0,0,0.5);position:absolute;top:0;width:100%;height:100%;display:flex;justify-content:center;align-items:center;">\
    <div style="background-color:#fff;width:500px;height:400px;border-radius:5px;display:flex;flex-direction:column;justify-content:space-around;align-items:center;"><span style="display:flex;width:80%;justify-content:space-around;align-items:center;"><label style="background-color:#F3F3F3;display:flex;width:100%;height:100px;margin:14px 0;border:1px dashed silver;display:flex;justify-content:center;align-items:center;cursor:pointer;"for="ret_file"><p>点击此区域上传文件</p></label><input id="ret_file" type="file" style="display:none;"></span><span style="display:flex;width:80%;justify-content:space-around;align-items:center;"><input type="button" value="取消" onclick="stop(this)" style="width:100px;height:50px;border-radius:10px;"><input type="button" value="提交" onclick='returnResource(${data})' style="width:100px;height:50px;border-radius:10px;"></span></div>\
</div>`);
}
function returnResource(data){
	let files = $("#ret_file")[0].files;
	let form_data = new FormData(), name = files[0].name;
	form_data.append(files[0].name, files[0]);
	let body = document.getElementsByTagName("body")[0];body.removeChild(body.lastChild);
	$.ajax({
        url: "/submit_file/",
        data: form_data,
        type: "POST",
        contentType: false,
        processData: false,
        cache: false,
        dataType: "json",
        success: function (res) {
        	$.ajax({
			    url: '/ret_src/',
				type: 'post',
				dataType: 'JSON',
				data: JSON.stringify({"id":data['id'],"check_sum": res["check_sum"], "name": name}),
			    success: function (res) {
			        $("#balance").text("余额: "+(res['balance'].toFixed(2)).toString());
			        if (data['which'] == 0) get_recv_tk();
			        else get_my_tk();
	        		alert("提交成功");
			    },
			    error: function (err) {
			        alert("上传失败，请检查文件正确性并重新尝试");
				}
			});
        },
        error: function (err) {
        	alert("上传失败，请请检查文件正确性并重新尝试");
        }
    });
}
function download(e){
	let id = parseInt(e[0].parentNode.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.innerText);
	const xhr = new XMLHttpRequest();
	xhr.open('POST', '/download/', true);
	xhr.setRequestHeader('content-type', 'application/json');
	//定义responseType='blob', 是读取文件成功的关键，这样设置可以解决下载文件乱码的问题
	xhr.responseType = "blob";    
	xhr.onload = () => {
	 	if (xhr.response['type'] == "application/json") {
	 		alert("下载失败");
	 		return;
	 	}
	//'\ufeff' 这个变量是定义字符集为utf-8, 防止中文乱码的问题。
	// {type: 'application/msword'} 根据文档类型来定义这个type。MIMA type
	  	const blob = new Blob(["\ufeff", xhr.response], {type: 'application/zip'});
	  	const blobUrl = URL.createObjectURL(blob);
	  	const a = document.createElement('a');
	  	a.style.display = 'none';
	  	a.download = `Task-${id}.zip`;
	  	a.href = blobUrl;
	 	a.target = '_blank';
	 	a.click();
	 	window.URL.revokeObjectURL(a.href);
	 	delete a;
	 	$.ajax({
			url: '/clear_cache/',
			type: 'post',
			dataType: 'JSON',
			data: JSON.stringify({'id': id}),
			success: (res)=>{
				$("#balance").text("余额: "+(res['balance'].toFixed(2)).toString());
				if(e[1]==0) get_sub_tk();
				else get_my_tk();
			},
			error: (err)=>{
				console.log(err);
				alert("下载失败");
			}
		});
	};
	xhr.send(JSON.stringify({'id': id}));
}
function cancel(e) {
	let id = parseInt(e.parentNode.previousSibling.previousSibling.previousSibling.previousSibling.previousSibling.innerText);
	$.ajax({
		url: '/cancel/',
		type: 'post',
		dataType: 'JSON',
		data: JSON.stringify({'id': id}),
		success: (res)=>{
			get_sub_tk();
		},
		error: (err)=>{
			console.log(err);
		}
	});
}
function get_avil_tk() {
	$.ajax({
		url: '/get_avils/',
		type: 'post',
		dataType: 'JSON',
		data: {},
		success: (res)=>{
			$("#op_tk").empty();
			let html_str = '<table><thead><th>Index</th><th>FileName</th><th>Size</th><th>Cost</th><th>Status</th><th>Operate</th></thead><tbody>';
			for (let i in res['tasks']) {
				let task = res['tasks'][i], func = "", btn_name = "";
				let status = "已发布";
				func = "recv_tk(this)", btn_name = "接受";
				html_str += `<tr><td>${task['id']}</td><td>${task['file_name']}</td><td>${task['file_size']}</td><td>${(task['cost']/1e18).toFixed(4).toString()+' ether'}</td><td>${status}</td><td><input type="button" onclick="${func}" value="${btn_name}"/></td></tr>`;
			}
			html_str += "</tbody></table>";
			$("#op_tk").html(html_str);
		},
		error: (err)=>{
			console.log(err);
		}
	});
}
function get_sub_tk() {
	$.ajax({
		url: '/get_subs/',
		type: 'post',
		dataType: 'JSON',
		data: {},
		success: (res)=>{
			$("#op_tk").empty();
			let html_str = '<table><thead><th>Index</th><th>FileName</th><th>Size</th><th>Cost</th><th>Status</th><th>Operate</th></thead><tbody>';
			for (let i in res['tasks']) {
				let task = res['tasks'][i], func = "", btn_name = "";
				let status = parseInt(task['status']);
				if(!status){status="已发布";func="cancel(this)";btn_name = "取消";}
				else if(status==1){status="已被接受";func="askResource([this, 0])",btn_name="请求取回";}
				else if(status==2){status="等待资源";btn_name="无";}
				else if(status==3){status="待下载";func="download([this, 0])";btn_name="下载";}
				else if(status==4){status="已完成";btn_name="无";}
				else {status="已取消";btn_name="无";}
				html_str += `<tr><td>${task['id']}</td><td>${task['file_name']}</td><td>${task['file_size']}</td><td>${(task['cost']/1e18).toFixed(4).toString()+' ether'}</td><td>${status}</td><td><input type="button" onclick="${func}" value="${btn_name}"/></td></tr>`;
			}
			html_str += "</tbody></table>";
			$("#op_tk").html(html_str);
		},
		error: (err)=>{
			console.log(err);
		}
	});
}
function get_recv_tk() {
	$.ajax({
		url: '/get_recvs/',
		type: 'post',
		dataType: 'JSON',
		data: {},
		success: (res)=>{
			$("#op_tk").empty();
			let html_str = '<table><thead><th>Index</th><th>FileName</th><th>Size</th><th>Cost</th><th>Status</th><th>Operate</th></thead><tbody>';
			for (let i in res['tasks']) {
				let task = res['tasks'][i], func = "", btn_name = "";
				let status = parseInt(task['status']);
				if(status==1){status="已接受";btn_name="无";}
				else if (status==2){func="ret_rsc([this, 0])";status="待提交";btn_name="提交";}
				else{status="已结束";btn_name="无";}
				html_str += `<tr><td>${task['id']}</td><td>${task['file_name']}</td><td>${task['file_size']}</td><td>${(task['cost']/1e18).toFixed(4).toString()+' ether'}</td><td>${status}</td><td><input type="button" onclick="${func}" value="${btn_name}"/></td></tr>`;
			}
			html_str += "</tbody></table>";
			$("#op_tk").html(html_str);
		},
		error: (err)=>{
			console.log(err);
		}
	});
}
function get_my_tk() {
	$.ajax({
		url: '/get_mines/',
		type: 'post',
		dataType: 'JSON',
		data: {},
		success: (res)=>{
			$("#op_tk").empty();
			let html_str = '<table><thead><th>Index</th><th>FileName</th><th>Size</th><th>Cost</th><th>Status</th><th>Operate</th></thead><tbody>';
			for (let i in res['tasks']) {
				let task = res['tasks'][i], func = "", btn_name = "";
				let status = parseInt(task['status']);
				if(!status){status="已发布";btn_name = "取消";}
				else if(status==1&&task['mine']==1){status="已被接受";func="askResource([this,1])",btn_name="请求取回";}
				else if(status==1){status="已接受";btn_name="无";}
				else if(status==2&&task['mine']==1){status="等待资源";btn_name="无";}
				else if(status==2){status="待提交";func="ret_rsc([this, 1])";btn_name="提交";}
				else if(status==3&&task['mine']==1){status="待下载";func="download([this, 1])";btn_name="下载";}
				else if(status==5){status="已取消";btn_name="无";}
				else {status="已结束";btn_name="无";}
				html_str += `<tr><td>${task['id']}</td><td>${task['file_name']}</td><td>${task['file_size']}</td><td>${(task['cost']/1e18).toFixed(4).toString()+' ether'}</td><td>${status}</td><td><input type="button" onclick="${func}" value="${btn_name}"/></td></tr>`;
			}
			html_str += "</tbody></table>";
			$("#op_tk").html(html_str);
		},
		error: (err)=>{
			console.log(err);
		}
	});
}