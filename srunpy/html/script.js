// document.addEventListener('DOMContentLoaded', function () {
//     updateInfo();
// });
let user_name = '';
let srun_host = '';
let srun_self = '';
let hasUpdate = false;
let selected_ips = [];
let active_ip = null;

const DEFAULT_IP_TOKEN = '__auto__';

const settingsWizard = {
    gateway: '',
    selfService: '',
    selectedTokens: new Set(),
    activeToken: DEFAULT_IP_TOKEN,
    results: [],
    reachableCount: 0,
    probeMeta: null,
    step: 'gateway'
};

function resetSettingsWizardState() {
    settingsWizard.gateway = '';
    settingsWizard.selfService = '';
    settingsWizard.selectedTokens = new Set();
    settingsWizard.activeToken = DEFAULT_IP_TOKEN;
    settingsWizard.results = [];
    settingsWizard.reachableCount = 0;
    settingsWizard.probeMeta = null;
    settingsWizard.step = 'gateway';
}

function tokenForIp(ip) {
    return (ip === null || typeof ip === 'undefined' || ip === '') ? DEFAULT_IP_TOKEN : String(ip);
}

function ipFromToken(token) {
    return token === DEFAULT_IP_TOKEN ? null : token;
}

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
        resetSettingsWizardState();
        settingsWizard.gateway = settings.gateway || '';
        settingsWizard.selfService = settings.self_service || '';
        const selectedFromConfig = Array.isArray(settings.selected) ? settings.selected.slice() : (Array.isArray(selected_ips) ? selected_ips.slice() : []);
        if (selectedFromConfig.length > 0) {
            settingsWizard.selectedTokens = new Set(selectedFromConfig.map(tokenForIp));
        } else {
            settingsWizard.selectedTokens = new Set([DEFAULT_IP_TOKEN]);
        }
        const activeFromConfig = (settings.active !== undefined && settings.active !== null) ? settings.active : active_ip;
        settingsWizard.activeToken = tokenForIp(activeFromConfig);
        if (!settingsWizard.selectedTokens.has(settingsWizard.activeToken)) {
            settingsWizard.selectedTokens.add(settingsWizard.activeToken);
        }
        document.getElementById('settings-gateway').value = settingsWizard.gateway;
        document.getElementById('settings-self-service').value = settingsWizard.selfService;
        document.getElementById('settings-step-gateway').classList.add('active');
        document.getElementById('settings-step-ip').classList.remove('active');
        document.getElementById('settings-probe-status').innerText = '请填写网关后下一步进行检查。';
        document.getElementById('settings-probe-results').innerHTML = '';
        document.getElementById('settings-confirm-ips').disabled = true;
        document.getElementById('settings-action-next').classList.remove('hidden');
        document.getElementById('settings-action-refresh').classList.add('hidden');
        document.getElementById('settings-action-save').classList.add('hidden');
        document.getElementById('settings-action-back').classList.add('hidden');
        document.getElementById('settings-action-next').disabled = false;
        const refreshButton = document.getElementById('settings-action-refresh');
        if (refreshButton) {
            refreshButton.disabled = false;
        }
        const saveButton = document.getElementById('settings-action-save');
        if (saveButton) {
            saveButton.disabled = false;
        }
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

function populateSettingsIpList(results){
    const ipList = document.getElementById('settings-ip-list');
    if (!ipList) {
        return;
    }
    ipList.innerHTML = '';
    if (!Array.isArray(results) || results.length === 0) {
        const empty = document.createElement('div');
        empty.className = 'settings-ip-empty';
        empty.innerText = '未检测到任何IP地址';
        ipList.appendChild(empty);
        return;
    }
    results.forEach((entry)=>{
        const token = tokenForIp(entry.ip);
        const row = document.createElement('div');
        row.className = 'settings-ip-item';

        const status = document.createElement('div');
        status.className = 'settings-ip-status';
        status.innerText = entry.reachable ? '可用' : '不可用';
        status.dataset.state = entry.reachable ? 'ok' : 'fail';

        const checkboxLabel = document.createElement('label');
        checkboxLabel.className = 'settings-ip-checkbox-label';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'settings-ip-checkbox';
        checkbox.value = token;
        if (settingsWizard.selectedTokens.has(token)) {
            checkbox.checked = true;
        }
        const textSpan = document.createElement('div');
        textSpan.className = 'settings-ip-description';
        const title = document.createElement('span');
        title.className = 'settings-ip-label';
        title.innerText = entry.label || (entry.ip === null ? '默认路由' : String(entry.ip));
        const detail = document.createElement('span');
        detail.className = 'settings-ip-message';
        detail.innerText = entry.message || '';
        textSpan.appendChild(title);
        textSpan.appendChild(detail);
        checkboxLabel.appendChild(checkbox);
        checkboxLabel.appendChild(textSpan);

        const radioLabel = document.createElement('label');
        radioLabel.className = 'settings-ip-radio-label';
        const radio = document.createElement('input');
        radio.type = 'radio';
        radio.name = 'settings-active-ip';
        radio.value = token;
        radio.className = 'settings-ip-radio';
        if (token === settingsWizard.activeToken) {
            radio.checked = true;
        }
        radio.addEventListener('change',()=>{
            settingsWizard.activeToken = token;
            settingsWizard.selectedTokens.add(token);
            checkbox.checked = true;
        });
        checkbox.addEventListener('change',()=>{
            if (checkbox.checked) {
                settingsWizard.selectedTokens.add(token);
                if (settingsWizard.activeToken === DEFAULT_IP_TOKEN && token !== DEFAULT_IP_TOKEN) {
                    settingsWizard.activeToken = token;
                    radio.checked = true;
                }
            }
            else {
                settingsWizard.selectedTokens.delete(token);
                if (settingsWizard.activeToken === token) {
                    settingsWizard.activeToken = DEFAULT_IP_TOKEN;
                    const defaultRadio = document.querySelector('input[name="settings-active-ip"][value="'+DEFAULT_IP_TOKEN+'"]');
                    if (defaultRadio) {
                        defaultRadio.checked = true;
                    }
                }
            }
        });
        const radioText = document.createElement('span');
        radioText.innerText = '设为当前';
        radioLabel.appendChild(radio);
        radioLabel.appendChild(radioText);

        row.appendChild(status);
        row.appendChild(checkboxLabel);
        row.appendChild(radioLabel);
        ipList.appendChild(row);
    });
    updateSettingsFooterNote();
}

function saveSettings(){
    const selectedList = Array.from(settingsWizard.selectedTokens);
    if (selectedList.length === 0) {
        settingsWizard.selectedTokens.add(DEFAULT_IP_TOKEN);
    }
    let activeToken = settingsWizard.activeToken;
    if (!settingsWizard.selectedTokens.has(activeToken)) {
        activeToken = Array.from(settingsWizard.selectedTokens)[0];
    }
    const payload = {
        gateway: settingsWizard.gateway,
        self_service: settingsWizard.selfService,
        selected: Array.from(settingsWizard.selectedTokens).map(ipFromToken),
        active: ipFromToken(activeToken)
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
    if (settingsWizard.step !== 'ip') {
        return;
    }
    const inlineButton = document.getElementById('settings-confirm-ips');
    const refreshButton = document.getElementById('settings-action-refresh');
    if (inlineButton) {
        inlineButton.disabled = true;
    }
    if (refreshButton) {
        refreshButton.disabled = true;
    }
    document.getElementById('settings-probe-status').innerText = '正在重新检查...';
    window.pywebview.api.probe_gateway_ips(settingsWizard.gateway, settingsWizard.selfService).then((result)=>{
        if (inlineButton) {
            inlineButton.disabled = false;
        }
        if (refreshButton) {
            refreshButton.disabled = false;
        }
        if (!result.ok) {
            const message = result.error || '重新检查失败';
            document.getElementById('settings-probe-status').innerText = message;
            showAlert(message);
            return;
        }
        settingsWizard.probeMeta = result;
        settingsWizard.results = Array.isArray(result.results) ? result.results : [];
        settingsWizard.reachableCount = result.reachable_count || 0;
        initializeSelectionFromProbe(result);
        document.getElementById('settings-probe-status').innerText = `共检测到 ${settingsWizard.results.length} 个IP，其中 ${settingsWizard.reachableCount} 个可访问。`;
        renderProbeResults();
        populateSettingsIpList(settingsWizard.results);
    }).catch((error)=>{
        if (inlineButton) {
            inlineButton.disabled = false;
        }
        if (refreshButton) {
            refreshButton.disabled = false;
        }
        document.getElementById('settings-probe-status').innerText = '重新检查失败';
        if (error) {
            console.error('refreshSettingsIps failed', error);
        }
        showAlert('重新检查失败，请稍后再试');
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
    resetSettingsWizardState();
}

function proceedSettingsStep(){
    if (settingsWizard.step === 'gateway') {
        const gatewayInput = document.getElementById('settings-gateway').value.trim();
        const selfInput = document.getElementById('settings-self-service').value.trim();
        if (!gatewayInput) {
            showAlert('请先填写网关地址');
            return;
        }
        settingsWizard.gateway = gatewayInput;
        settingsWizard.selfService = selfInput;
        document.getElementById('settings-probe-status').innerText = '正在检查各IP连通性...';
        document.getElementById('settings-probe-results').innerHTML = '';
        document.getElementById('settings-action-next').disabled = true;
        window.pywebview.api.probe_gateway_ips(gatewayInput, selfInput).then((result)=>{
            document.getElementById('settings-action-next').disabled = false;
            if (!result.ok) {
                document.getElementById('settings-probe-status').innerText = result.error || '网关检查失败';
                return;
            }
            settingsWizard.probeMeta = result;
            settingsWizard.results = Array.isArray(result.results) ? result.results : [];
            settingsWizard.reachableCount = result.reachable_count || 0;
            initializeSelectionFromProbe(result);
            document.getElementById('settings-probe-status').innerText = `共检测到 ${settingsWizard.results.length} 个IP，其中 ${settingsWizard.reachableCount} 个可访问。`;
            renderProbeResults();
            settingsWizard.step = 'ip';
            renderIpSelectionStep();
        });
    } else if (settingsWizard.step === 'ip') {
        saveSettings();
    }
}

function initializeSelectionFromProbe(result){
    const availableTokens = new Set();
    if (Array.isArray(result.results)) {
        result.results.forEach((item)=>{
            availableTokens.add(tokenForIp(item.ip));
        });
    }
    const nextSelected = new Set();
    if (settingsWizard.selectedTokens instanceof Set && settingsWizard.selectedTokens.size > 0) {
        settingsWizard.selectedTokens.forEach((token)=>{
            if (availableTokens.has(token)) {
                nextSelected.add(token);
            }
        });
    }
    if (nextSelected.size === 0 && Array.isArray(result.results)) {
        result.results.forEach((item)=>{
            if (item.reachable) {
                nextSelected.add(tokenForIp(item.ip));
            }
        });
    }
    if (nextSelected.size === 0) {
        nextSelected.add(DEFAULT_IP_TOKEN);
    }
    settingsWizard.selectedTokens = nextSelected;
    if (!availableTokens.has(settingsWizard.activeToken) || !settingsWizard.activeToken) {
        settingsWizard.activeToken = Array.from(settingsWizard.selectedTokens)[0] || DEFAULT_IP_TOKEN;
    }
    if (!settingsWizard.selectedTokens.has(settingsWizard.activeToken)) {
        settingsWizard.selectedTokens.add(settingsWizard.activeToken);
    }
}

function renderProbeResults(){
    const container = document.getElementById('settings-probe-results');
    if (!container) {
        return;
    }
    container.innerHTML = '';
    if (!settingsWizard.results.length) {
        const empty = document.createElement('div');
        empty.className = 'settings-probe-empty';
        empty.innerText = '未检测到任何IP地址或无法测试。';
        container.appendChild(empty);
        return;
    }
    settingsWizard.results.forEach((entry)=>{
        const row = document.createElement('div');
        row.className = 'settings-probe-item';
        const label = entry.label || (entry.ip === null ? '默认路由' : String(entry.ip));
        const status = document.createElement('span');
        status.className = 'settings-probe-status';
        status.dataset.state = entry.reachable ? 'ok' : 'fail';
        status.innerText = entry.reachable ? '可访问' : '不可访问';
        const detail = document.createElement('span');
        detail.className = 'settings-probe-message';
        detail.innerText = entry.message || '';
        row.appendChild(document.createTextNode(label));
        row.appendChild(status);
        row.appendChild(detail);
        container.appendChild(row);
    });
}

function renderIpSelectionStep(){
    settingsWizard.step = 'ip';
    document.getElementById('settings-step-gateway').classList.remove('active');
    document.getElementById('settings-step-ip').classList.add('active');
    document.getElementById('settings-action-next').classList.add('hidden');
    document.getElementById('settings-action-save').classList.remove('hidden');
    document.getElementById('settings-action-refresh').classList.remove('hidden');
    document.getElementById('settings-action-back').classList.remove('hidden');
    document.getElementById('settings-confirm-ips').disabled = false;
    populateSettingsIpList(settingsWizard.results);
}

function goBackToGatewayStep(){
    if (settingsWizard.step !== 'ip') {
        return;
    }
    settingsWizard.step = 'gateway';
    document.getElementById('settings-step-gateway').classList.add('active');
    document.getElementById('settings-step-ip').classList.remove('active');
    document.getElementById('settings-action-next').classList.remove('hidden');
    document.getElementById('settings-action-save').classList.add('hidden');
    document.getElementById('settings-action-refresh').classList.add('hidden');
    document.getElementById('settings-action-back').classList.add('hidden');
    document.getElementById('settings-action-next').disabled = false;
}

function updateSettingsFooterNote(){
    const note = document.getElementById('settings-ip-note');
    if (!note) {
        return;
    }
    const total = settingsWizard.results.length;
    const ok = settingsWizard.results.filter(item => item.reachable).length;
    note.innerText = `共检测到 ${total} 个IP，其中 ${ok} 个可访问。请至少选择一个可访问的IP。`;
}