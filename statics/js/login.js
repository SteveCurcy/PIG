function chose_user() {
    let user=document.getElementById("user");
    let pass=document.getElementById("pass");
    user.className="active";
    pass.className="not_chosen";
	document.getElementById("err").className="no_err";
}

function chose_pass() {
    let user=document.getElementById("user");
    let pass=document.getElementById("pass");
    user.className="not_chosen";
    pass.className="active";
	document.getElementById("err").className="no_err";
}

function log() {
	let user = document.getElementById("log-user-name");
	let pass = document.getElementById("log-password");
	if (user.value === null || user.value === "") {
		document.getElementById("err").className="err";
		return false;
	}
	if (pass.value === null || pass.value === "") {
		document.getElementById("err").className="err";
		return false;
	}
	sessionStorage.setItem("user", user.value);
	return true;
	// $.ajax({
	// 	url:"/login/",
	// 	type: "post",
	// 	dataType: 'JSON',
	// 	contentType: "application/json",
	// 	data: JSON.stringify({"user": user.value, "pass": pass.value}),
	// 	success: (res)=> {
	// 		console.log(res);
	// 		document.write(res);
	// 	},
	// 	error: (err)=>{
	// 		console.log(err);
	// 	}
	// });
}