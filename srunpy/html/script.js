// document.addEventListener('DOMContentLoaded', function () {
//     updateInfo();
// });
let user_name = '';
let srun_host = '';
let srun_self = '';
let hasUpdate = false;

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
        if (e[2]) {
            document.getElementById('auto-login').setAttribute('data-state', "selected");
        }
        else {
            document.getElementById('auto-login').setAttribute('data-state', "unselected");
        }
        if (e[3]) {
            document.getElementById('auto-start').setAttribute('data-state', "selected");
        }
        else {
            document.getElementById('auto-start').setAttribute('data-state', "unselected");
        }
        hasUpdate = e[4];
        if (e[4] && !e[5]) {
            do_Update();
            window.pywebview.api.do_update(false);
        }
        srun_host=e[6];
        srun_self=e[7];
    });
}

function do_Update() {
    if (hasUpdate) {
        showConfirmAlert('检查到更新，立即下载吗？', () => { window.pywebview.api.do_update(true) });
    }
    else {
        showConfirmAlert('深澜网关第三方客户端',()=>{window.pywebview.api.webbrowser_open("https://github.com/HofNature/SRunPy-GUI")}, "icons/github.png");
    }
}
function set_auto_login() {
    if (document.getElementById('auto-login').getAttribute('data-state') == 'selected') {
        document.getElementById('auto-login').setAttribute('data-state', 'unselected');
        window.pywebview.api.set_auto_login(false);
    }
    else {
        document.getElementById('auto-login').setAttribute('data-state', 'selected');
        window.pywebview.api.get_online_data().then((e) => {
            is_online = e[1];
            if (is_online){
                window.pywebview.api.set_auto_login(true).then((e) => {
                    if (!e) {
                        showAlert("请至少用本工具登录一次！");
                        document.getElementById('auto-login').setAttribute('data-state', 'unselected');
                    }
                });
            }
            else{
                showAlert("仅限登录状态下启用！");
                document.getElementById('auto-login').setAttribute('data-state', 'unselected');
            }
        });
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
        if (is_online != (document.getElementsByClassName('login-pannel')[0].getAttribute('data-state') == 'online')) {
            updateInfo();
            document.getElementsByClassName('login-button')[0].disabled = false;
            return;
        }
        if (!is_online) {
            if (document.getElementById('username').value == '' || document.getElementById('password').value == '') {
                showAlert("用户名或密码不能为空！");
                document.getElementsByClassName('login-button')[0].disabled = false;
                return;
            }
            if (user_name != document.getElementById('username').value) {
                user_name = document.getElementById('username').value;
            }
            if (document.getElementById('password').value != '************') {
                password = document.getElementById('password').value;
            }
            else {
                password = '';
            }
            window.pywebview.api.set_config(user_name, password).then((e) => {
                window.pywebview.api.login().then((e) => {
                    if (e) {
                        if (document.getElementById('auto-start').getAttribute('data-state') == 'selected') {
                            window.pywebview.api.set_start_with_windows(true).then(() => {
                                setTimeout(updateInfo,500)
                            });
                        }
                        else {
                            setTimeout(updateInfo,500)
                        }
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
                        setTimeout(updateInfo,500)
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

function set_Host(){
    showInput("请输入深澜网关地址",function(srun_host){
        showInput("请输入自服务地址",function(srun_self){
            window.pywebview.api.set_srun_host(srun_host,srun_self).then((e) => {
                if (e) {
                    showAlert("设置成功！");
                    updateInfo();
                }
                else {
                    showAlert("设置失败！");
                }
            });
        },srun_self,false);
    },srun_host,false);
}

function showAlert(text, icon) {
    if (icon) {
        document.querySelector("#alert-mask img").src = icon;
    }
    else {
        document.querySelector("#alert-mask img").src = "icons/info.png";
    }
    showConfirmAlert(text, null);
}

function showConfirmAlert(text, callback,icon) {
    let ele = document.getElementsByClassName("alert-cancle");
    if (icon) {
        document.querySelector("#alert-mask img").src = icon;
    }
    else {
        document.querySelector("#alert-mask img").src = "icons/info.png";
    }
    if (callback) {
        ele[0].style.display = "block";
        ele[1].style.display = "block";
        document.getElementById("confirm-alert-button").onclick = () => {
            closeAlert();
            callback();
        };
    }
    else {
        ele[0].style.display = "none";
        ele[1].style.display = "none";
        document.getElementById("confirm-alert-button").onclick = closeAlert;
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

function showInput(text,callback,inputText="",ensureText=true) {
    let mask = document.getElementById("input-mask");
    let input = document.getElementById("input-input");
    input.value=inputText;
    if (ensureText) {
        document.getElementById("input-text").children[0].innerText = text;
    }
    else {
        document.getElementById("input-text").children[0].innerHTML = text
    }
    document.getElementById("input-confirm").onclick = function () {
        callback(input.value);
        closeInput();
    }
    mask.style.display = "block";
    setTimeout(function () {
        mask.style.opacity = "1";
    }, 20);
}

function closeInput() {
    let mask = document.getElementById("input-mask");
    if (mask.style.opacity != "0") {
        mask.style.opacity = "0";
        setTimeout(function () {
            if (mask.style.opacity == "0") {
                mask.style.display = "none";
            }
        }, 500);
    }
}