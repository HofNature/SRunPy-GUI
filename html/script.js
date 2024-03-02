// document.addEventListener('DOMContentLoaded', function () {
//     updateInfo();
// });
let user_name = '';

function updateInfo() {
    window.pywebview.api.get_online_data().then((e) => {
        is_available = e[0];
        if (!is_available) {
            showAlert("不在校园网环境！");
            document.getElementsByClassName('login-pannel')[0].setAttribute('data-state', 'offline');
            load_data();
            return;
        }
        is_online = e[1];
        if (!is_online) {
            document.getElementsByClassName('login-pannel')[0].setAttribute('data-state', 'offline');
        }
        else {
            document.getElementsByClassName('login-pannel')[0].setAttribute('data-state', 'online');
            online_data = e[2];
            // console.log(online_data);
            document.getElementById('ip-address').innerText = online_data.online_ip;
            document.getElementById('username-text').innerText = online_data.user_name;
            document.getElementById('used-flow').innerText = (online_data.sum_bytes / 1024 / 1024).toFixed(2) + 'MB';
            document.getElementById('balance-last').innerText = online_data.user_balance + '元';
        }
        load_data();
    })
}
function load_data() {
    window.pywebview.api.get_config().then((e) => {
        document.getElementById('username').value = e[0];
        user_name = e[0];
        if (e[1]) {
            document.getElementById('password').value = '************';
        }
        else {
            document.getElementById('password').value = '';
        }
        if (e[2]){
            document.getElementById('auto-login').setAttribute('data-state',"selected");
        }
        else {
            document.getElementById('auto-login').setAttribute('data-state',"unselected");
        }
        if (e[3]){
            document.getElementById('auto-start').setAttribute('data-state',"selected");
        }
        else {
            document.getElementById('auto-start').setAttribute('data-state',"unselected");
        }
    });
}
function set_auto_login() {
    if (document.getElementById('auto-login').getAttribute('data-state') == 'selected') {
        document.getElementById('auto-login').setAttribute('data-state', 'unselected');
        window.pywebview.api.set_auto_login(false);
    }
    else {
        document.getElementById('auto-login').setAttribute('data-state', 'selected');
        window.pywebview.api.set_auto_login(true);
    }
}
function set_auto_start() {
    if (document.getElementById('auto-start').getAttribute('data-state') == 'selected') {
        document.getElementById('auto-start').setAttribute('data-state', 'unselected');
        window.pywebview.api.set_start_with_windows(false);
    }
    else {
        document.getElementById('auto-start').setAttribute('data-state', 'selected');
        window.pywebview.api.set_start_with_windows(true);
    }
}
function login() {
    document.getElementsByClassName('login-button')[0].disabled = true;
    window.pywebview.api.get_online_data().then((e) => {
        is_available = e[0];
        if (!is_available) {
            showAlert("不在校园网环境！");
            document.getElementsByClassName('login-button')[0].disabled = false;
            return;
        }
        is_online = e[1];
        if (is_online != (document.getElementsByClassName('login-pannel')[0].getAttribute('data-state')=='online')){
            updateInfo();
            document.getElementsByClassName('login-button')[0].disabled = false;
            return;
        }
        if (!is_online) {
            if (document.getElementById('username').value==''||document.getElementById('password').value=='') {
                showAlert("用户名或密码不能为空！");
                document.getElementsByClassName('login-button')[0].disabled = false;
                return;
            }
            if (user_name != document.getElementById('username').value){
                user_name = document.getElementById('username').value;
            }
            if (document.getElementById('password').value != '************'){
                password = document.getElementById('password').value;
            }
            else {
                password = '';
            }
            window.pywebview.api.set_config(user_name,password).then((e) => {
                window.pywebview.api.login().then((e) => {
                    if (e) {
                        updateInfo();
                    }
                    else {
                        showAlert("登录失败！");
                    }
                    document.getElementsByClassName('login-button')[0].disabled = false;
                });
            });
        }
        else {
            window.pywebview.api.logout().then((e) => {
                if (e) {
                    window.pywebview.api.set_auto_login(false).then((e) => {
                        updateInfo();
                    });
                }
                else {
                    showAlert("注销失败！");
                }
                document.getElementsByClassName('login-button')[0].disabled = false;
            });
        }
    });
}

function showAlert(text) {
    showConfirmAlert(text, null);
}

function showConfirmAlert(text, callback) {
    confirmAlertCallback = callback;
    let ele = document.getElementsByClassName("alert-cancle");
    if (callback) {
        ele[0].style.display = "block";
        ele[1].style.display = "block";
    }
    else {
        ele[0].style.display = "none";
        ele[1].style.display = "none";
    }
    let mask = document.getElementById("alert-mask");
    document.getElementById("alert-text").children[0].innerText = text;
    mask.style.display = "block";
    setTimeout(function () {
        mask.style.opacity = "1";
    }, 20);
}


function closeAlert() {
    let mask = document.getElementById("alert-mask");
    if (mask.style.opacity != "0") {
        mask.style.opacity = "0";
        setTimeout(function () {
            if (mask.style.opacity == "0") {
                mask.style.display = "none";
            }
        }, 500);
    }
}

function confirmAlert() {
    if (confirmAlertCallback) {
        confirmAlertCallback();
    }
    closeAlert();
}