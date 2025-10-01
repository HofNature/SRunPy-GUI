// document.addEventListener('DOMContentLoaded', function () {
//     updateInfo();
// });
let user_name = '';
let srun_host = '';
let srun_self = '';
let hasUpdate = false;
let selected_ips = [];
let active_ip = null;
let available_ips = [];

const DEFAULT_IP_TOKEN = '__auto__';

function updateInfo(hope) {
    let callback = (e) => {
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
    }
    const ipParam = active_ip === null ? null : active_ip;
    const hopeParam = typeof hope === 'undefined' ? null : hope;
    let init = () => {
        if (!(window.pywebview && window.pywebview.api && typeof window.pywebview.api.get_online_data === 'function')) {
            setTimeout(init, 100);
        }
        else {
            window.pywebview.api.get_online_data(ipParam, hopeParam).then(callback);
        }
    }
    init();
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
        active_ip = e[8] === null ? null : e[8];
        selected_ips = Array.isArray(e[9]) ? e[9].slice() : [];
        renderIpSelector();
    });
}

function renderIpSelector() {
    const selector = document.getElementById('ip-selector');
    if (!selector) {
        return;
    }
    const desiredValue = active_ip === null ? DEFAULT_IP_TOKEN : String(active_ip);
    selector.innerHTML = '';
    const defaultOption = document.createElement('option');
    defaultOption.value = DEFAULT_IP_TOKEN;
    defaultOption.innerText = '自动选择';
    selector.appendChild(defaultOption);
    const seen = new Set();
    selected_ips.forEach((ip) => {
        if (ip === null || ip === undefined) {
            return;
        }
        const ipStr = String(ip);
        if (seen.has(ipStr)) {
            return;
        }
        seen.add(ipStr);
        const option = document.createElement('option');
        option.value = ipStr;
        option.innerText = ipStr;
        selector.appendChild(option);
    });
    selector.value = desiredValue;
    selector.onchange = handleIpSelectionChange;
}

function handleIpSelectionChange(event) {
    const value = event.target.value;
    const nextActive = value === DEFAULT_IP_TOKEN ? null : value;
    if ((nextActive || null) === (active_ip || null)) {
        return;
    }
    window.pywebview.api.set_active_client_ip(nextActive).then((ok) => {
        if (ok) {
            active_ip = nextActive;
            updateInfo();
        }
        else {
            showAlert("无法切换到所选IP！");
            renderIpSelector();
        }
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
    window.pywebview.api.get_online_data(active_ip === null ? null : active_ip).then((e) => {
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
    window.pywebview.api.get_online_data(active_ip === null ? null : active_ip).then((e) => {
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
                window.pywebview.api.login(active_ip === null ? null : active_ip).then((e) => {
                    if (e) {
                        if (document.getElementById('auto-start').getAttribute('data-state') == 'selected') {
                            window.pywebview.api.set_start_with_windows(true).then(() => {
                                updateInfo(true);
                            });
                        }
                        else {
                            updateInfo(true);
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
            window.pywebview.api.logout(active_ip === null ? null : active_ip).then((e) => {
                if (e) {
                    window.pywebview.api.set_auto_login(false).then((e) => {
                        updateInfo(false);
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

function openSettings(){
    window.pywebview.api.get_ip_settings().then((settings)=>{
        available_ips = Array.isArray(settings.available) ? settings.available : [];
        document.getElementById('settings-gateway').value = settings.gateway || '';
        document.getElementById('settings-self-service').value = settings.self_service || '';
        populateSettingsIpList(settings);
        const mask = document.getElementById('settings-mask');
        mask.style.display = 'block';
        setTimeout(()=>{mask.style.opacity = '1';},20);
    });
}

function closeSettings(){
    const mask = document.getElementById('settings-mask');
    if (!mask) {
        return;
    }
    if (mask.style.opacity !== '0') {
        mask.style.opacity = '0';
        setTimeout(()=>{
            if (mask.style.opacity === '0') {
                mask.style.display = 'none';
            }
        },300);
    }
}

function populateSettingsIpList(settings){
    const ipList = document.getElementById('settings-ip-list');
    if (!ipList) {
        return;
    }
    ipList.innerHTML = '';
    const selectedTokens = new Set();
    if (Array.isArray(settings.selected) && settings.selected.length > 0) {
        settings.selected.forEach((ip)=>{
            selectedTokens.add(ip === null ? DEFAULT_IP_TOKEN : String(ip));
        });
    }
    else {
        selectedTokens.add(DEFAULT_IP_TOKEN);
    }
    const activeToken = settings.active === null ? DEFAULT_IP_TOKEN : String(settings.active);
    const entries = [{ token: DEFAULT_IP_TOKEN, label: '自动选择', value: null }];
    const seen = new Set(entries.map((item)=>item.token));
    if (Array.isArray(settings.selected)) {
        settings.selected.forEach((ip)=>{
            if (ip === null || ip === undefined) {
                return;
            }
            const token = String(ip);
            if (!seen.has(token)) {
                entries.push({ token, label: token, value: token });
                seen.add(token);
            }
        });
    }
    available_ips.forEach((ip)=>{
        const token = String(ip);
        if (!seen.has(token)) {
            entries.push({ token, label: token, value: token });
            seen.add(token);
        }
    });
    entries.forEach((entry)=>{
        const row = document.createElement('div');
        row.className = 'settings-ip-item';

        const checkboxLabel = document.createElement('label');
        checkboxLabel.className = 'settings-ip-checkbox-label';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'settings-ip-checkbox';
        checkbox.value = entry.token;
        if (selectedTokens.has(entry.token)) {
            checkbox.checked = true;
        }
        const textSpan = document.createElement('span');
        textSpan.innerText = entry.label;
        checkboxLabel.appendChild(checkbox);
        checkboxLabel.appendChild(textSpan);

        const radioLabel = document.createElement('label');
        radioLabel.className = 'settings-ip-radio-label';
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'settings-active-ip';
        radio.value = entry.token;
        radio.className = 'settings-ip-radio';
        if (entry.token === activeToken) {
            radio.checked = true;
        }
        radio.addEventListener('change',()=>{
            checkbox.checked = true;
        });
        checkbox.addEventListener('change',()=>{
            if (!checkbox.checked && radio.checked) {
                radio.checked = false;
            }
        });
        const radioText = document.createElement('span');
        radioText.innerText = '设为当前';
        radioLabel.appendChild(radio);
        radioLabel.appendChild(radioText);

        row.appendChild(checkboxLabel);
        row.appendChild(radioLabel);
        ipList.appendChild(row);
    });
}

function saveSettings(){
    const gateway = document.getElementById('settings-gateway').value.trim();
    const selfService = document.getElementById('settings-self-service').value.trim();
    const checkboxEls = Array.from(document.querySelectorAll('.settings-ip-checkbox'));
    let selectedTokens = checkboxEls.filter((cb)=>cb.checked).map((cb)=>cb.value);
    if (selectedTokens.length === 0) {
        selectedTokens = [DEFAULT_IP_TOKEN];
    }
    const activeRadio = document.querySelector('input[name="settings-active-ip"]:checked');
    let activeToken = activeRadio ? activeRadio.value : DEFAULT_IP_TOKEN;
    if (!selectedTokens.includes(activeToken)) {
        activeToken = selectedTokens[0];
    }
    const payload = {
        gateway: gateway,
        self_service: selfService,
        selected: selectedTokens.map((token)=> token === DEFAULT_IP_TOKEN ? null : token),
        active: activeToken === DEFAULT_IP_TOKEN ? null : activeToken
    };
    window.pywebview.api.update_ip_settings(payload).then((ok)=>{
        if (ok) {
            closeSettings();
            setTimeout(()=>{showAlert("设置成功！");},320);
            updateInfo();
        }
        else {
            showAlert("设置失败！");
        }
    });
}

function refreshSettingsIps(){
    const checkboxEls = Array.from(document.querySelectorAll('.settings-ip-checkbox'));
    const currentSelection = checkboxEls.filter((cb)=>cb.checked).map((cb)=>cb.value);
    const activeRadio = document.querySelector('input[name="settings-active-ip"]:checked');
    const currentActive = activeRadio ? activeRadio.value : DEFAULT_IP_TOKEN;
    window.pywebview.api.get_ip_settings().then((settings)=>{
        available_ips = Array.isArray(settings.available) ? settings.available : [];
        settings.selected = currentSelection.map((token)=> token === DEFAULT_IP_TOKEN ? null : token);
        settings.active = currentActive === DEFAULT_IP_TOKEN ? null : currentActive;
        settings.gateway = document.getElementById('settings-gateway').value.trim() || settings.gateway;
        settings.self_service = document.getElementById('settings-self-service').value.trim() || settings.self_service;
        populateSettingsIpList(settings);
    });
}

function startSelfService(){
    window.pywebview.api.start_self_service(active_ip === null ? null : active_ip);
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