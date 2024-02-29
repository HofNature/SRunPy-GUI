let imageIndex = -1;
let label_data
let imageIndexList = []
let ts_now = (new Date()).getTime();
let curImg
let labelContainer
let labelCanvas
let workingMode = 1;
let imageLoaded = false;
let confirmAlertCallback = null;
let autoSaveEnabled = true;
let tagIndex = -1;
let lineHor
let lineVer

document.addEventListener('DOMContentLoaded', function () {
    curImg = document.getElementById("current-img-img");
    labelContainer = document.getElementById("label-conatiner");
    labelCanvas = document.getElementById("label-canvas");
    lineHor = document.getElementById("line-hor");
    lineVer = document.getElementById("line-ver");
    curImg.onload = function () {
        imageLoaded = true;
        labelContainer.style.display = "block";
        labelContainer.style.height = curImg.clientHeight + "px";
        labelContainer.style.width = curImg.clientWidth + "px";
        if (workingMode == 1) {
            labelCanvas.style.display = "block";
        }

        labelCanvas.style.height = curImg.clientHeight;
        labelCanvas.style.width = curImg.clientWidth;
    };
    // 设置在labelContainer中画框的事件
    labelCanvas.onpointerenter = function (e) {
        if (workingMode == 1) {
            lineHor.style.display = "block";
            lineVer.style.display = "block";
        }
    }
    labelCanvas.onpointerleave = function (e) {
        lineHor.style.display = "none";
        lineVer.style.display = "none";
    }
    labelCanvas.onmousemove = canvasMouseMove;
    labelCanvas.onmousedown = function (e) {
        let labelItem = document.createElement("div");
        labelItem.className = "label-item";
        labelItem.setAttribute("data-index", labelContainer.children.length);
        labelItem.setAttribute("data-selected", false);
        labelItem.style.left = e.offsetX + "px";
        labelItem.style.top = e.offsetY + "px";
        labelItem.style.right = (labelCanvas.clientWidth - e.offsetX) + "px";
        labelItem.style.bottom = (labelCanvas.clientHeight - e.offsetY) + "px";
        labelContainer.appendChild(labelItem);
        labelCanvas.onmousemove = function (e) {
            labelItem.style.right = (labelCanvas.clientWidth - e.offsetX) + "px";
            labelItem.style.bottom = (labelCanvas.clientHeight - e.offsetY) + "px";
            canvasMouseMove(e);
        };
        document.onmouseup = function (e) {
            labelCanvas.onmousemove = canvasMouseMove;
            document.onmouseup = null;
            if (labelItem.clientWidth < 3 || labelItem.clientHeight < 3) {
                labelContainer.removeChild(labelItem);
                return
            }
            if (tagIndex < 0 || tagIndex >= label_data.classes.length) {
                showAlert("请选择一个标签");
                return
            }
            let labelItemText = document.createElement("div");
            labelItemText.className = "label-item-text";
            labelItemText.innerText = label_data.classes[tagIndex];
            labelItem.appendChild(labelItemText);
            labelItem.onclick = function () {
                deleteLabel(labelItem);
            }
            label_data.images[imageIndexList[imageIndex]].push({
                id: tagIndex,
                bbox: [labelItem.style.left.replace('px', '') / labelCanvas.clientWidth,
                labelItem.style.top.replace('px', '') / labelCanvas.clientHeight,
                (labelCanvas.clientWidth - labelItem.style.right.replace('px', '')) / labelCanvas.clientWidth,
                (labelCanvas.clientHeight - labelItem.style.bottom.replace('px', '')) / labelCanvas.clientHeight
                ]
            });
            labelItem.style.left = label_data.images[imageIndexList[imageIndex]][label_data.images[imageIndexList[imageIndex]].length - 1].bbox[0] * 100 + "%";
            labelItem.style.top = label_data.images[imageIndexList[imageIndex]][label_data.images[imageIndexList[imageIndex]].length - 1].bbox[1] * 100 + "%";
            labelItem.style.right = (1 - label_data.images[imageIndexList[imageIndex]][label_data.images[imageIndexList[imageIndex]].length - 1].bbox[2]) * 100 + "%";
            labelItem.style.bottom = (1 - label_data.images[imageIndexList[imageIndex]][label_data.images[imageIndexList[imageIndex]].length - 1].bbox[3]) * 100 + "%";
            saveLabelAuto();
        };
    };
    document.addEventListener('keydown', function (e) {
        if (document.activeElement.tagName != "INPUT") {
            if (e.key == "ArrowLeft" || e.key == "a") {
                navSwitcher(-1);
            }
            else if (e.key == "ArrowRight" || e.key == "d") {
                navSwitcher(1);
            }
        }
    });
    fetch('/api/get_label?time=' + ts_now).then(r => r.json()).then(json => {
        if (json.classes) {
            label_data = json
            generate_List()
        } else {
            showAlert(json.msg);
        }
    })
        .catch(error => { showAlert("获取数据失败"), console.log(error) });
});

window.addEventListener('resize', () => {
    labelContainer.style.height = curImg.clientHeight + "px";
    labelContainer.style.width = curImg.clientWidth + "px";
    labelCanvas.style.height = curImg.clientHeight;
    labelCanvas.style.width = curImg.clientWidth;
});

function canvasMouseMove(e) {
    lineHor.style.top = e.offsetY + labelCanvas.offsetTop - labelCanvas.clientHeight / 2 + "px";
    lineVer.style.left = e.offsetX + labelCanvas.offsetLeft - labelCanvas.clientWidth / 2 + "px";
}

function labelMode() {
    workingMode = 1;
    if (imageLoaded) {
        labelCanvas.style.display = "block";
    }
}

function deleteMode() {
    workingMode = 0;
    labelCanvas.style.display = "none";
}

function deleteLabel(item) {
    if (workingMode == 0) {
        showConfirmAlert("确定删除这个标签吗？", function () {
            labelContainer.removeChild(item);
            label_data.images[imageIndexList[imageIndex]].splice(item.getAttribute("data-index"), 1);
            switchToImage(imageIndex);
            saveLabelAuto();
        });
    }
}

function addTag() {
    let newTag = document.getElementById("add-tag-input").value;
    document.getElementById("add-tag-input").value = "";
    if (newTag.length > 0) {
        let index = label_data.classes.length;
        label_data.classes.push(newTag);
        let tagList = document.getElementById("tag-list");
        let tagItem = document.createElement("div");
        tagItem.className = "tag-item";
        tagItem.setAttribute("data-index", index);
        tagItem.setAttribute("data-selected", false);
        tagItem.innerText = newTag;
        tagItem.onclick = function () {
            switchToTag(index);
        }
        tagList.appendChild(tagItem);
        switchToTag(index);
    }
}

function autoSave() {
    if (autoSaveEnabled) {
        autoSaveEnabled = false;
        document.getElementById("auto-save-button").title = "自动保存：关闭";
        document.getElementById("auto-save-button").src = "icon/autosave_disabled.svg";
    }
    else {
        autoSaveEnabled = true;
        document.getElementById("auto-save-button").title = "自动保存：开启";
        document.getElementById("auto-save-button").src = "icon/autosave.svg";
    }
}
function saveLabel() {
    fetch('/api/submit_all_label', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(label_data)
    }).then(r => r.text()).then(r => {
        if (r == "OK") {
            showAlert("保存成功");
        } else {
            showAlert(r);
        }
    })
        .catch(error => { showAlert("保存失败"), console.log(error) });
}
function saveLabelAuto() {
    if (autoSaveEnabled) {
        fetch('/api/submit_label', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                classes: label_data.classes,
                image_id: imageIndexList[imageIndex],
                label: label_data.images[imageIndexList[imageIndex]]
            })
        }).then(r => r.text()).then(r => {
            if (r == "OK") {
                console.log("自动保存成功");
            } else {
                showAlert(r);
            }
        })
            .catch(error => { showAlert("自动保存失败"), console.log(error) });
    }

}
function generate_List() {
    let imageList = document.getElementById("image-list");
    for (var key in label_data.images) {
        imageIndexList.push(key)
    }
    let tagList = document.getElementById("tag-list");
    label_data.classes.forEach(function (item, index) {
        let tagItem = document.createElement("div");
        tagItem.className = "tag-item";
        tagItem.setAttribute("data-index", index);
        tagItem.setAttribute("data-selected", false);
        tagItem.innerText = item;
        tagItem.onclick = function () {
            switchToTag(index);
        }
        tagList.appendChild(tagItem);
    });
    if (label_data.classes.length > 0) {
        switchToTag(0);
    }
    imageIndexList.forEach(function (key, index) {
        setTimeout(function () {
            let imageItem = document.createElement("div");
            imageItem.className = "image-item";
            imageItem.setAttribute("data-index", index);
            imageItem.title = key;
            imageItem.setAttribute("data-selected", false);
            imageItem.onclick = function () {
                switchToImage(imageItem.getAttribute("data-index"));
            }
            let imageItemImg = document.createElement("img");
            imageItemImg.src = '/dataset/' + key;
            imageItemImg.loading = 'lazy';
            imageItem.appendChild(imageItemImg);
            imageList.appendChild(imageItem);
            if (index == 0) {
                switchToImage(0);
            }
        }, index * 25);
    });
}

function switchToTag(index) {
    let tagList = document.getElementById("tag-list");
    if (tagIndex >= 0 && tagIndex <= label_data.classes.length - 1) {
        tagItem = tagList.children[tagIndex];
        tagItem.setAttribute("data-selected", false);
    }
    tagIndex = Number(index);
    tagItem = tagList.children[tagIndex];
    tagItem.setAttribute("data-selected", true);
}

function switchToImage(index) {
    let imageList = document.getElementById("image-list");
    let imageItem
    if (imageIndex >= 0 && imageIndex <= imageIndexList.length - 1) {
        imageItem = imageList.children[imageIndex];
        imageItem.setAttribute("data-selected", false);
    }
    imageIndex = Number(index);
    imageItem = imageList.children[imageIndex];
    imageItem.setAttribute("data-selected", true);
    document.getElementById("image-counter").innerText = (imageIndex + 1) + "/" + imageIndexList.length;
    document.getElementById("current-img-img").src = '/dataset/' + imageIndexList[index];
    labelContainer.innerHTML = "";
    imageLoaded = false;
    labelContainer.style.display = "none";
    labelCanvas.style.display = "none";
    label_data.images[imageIndexList[index]].forEach(function (item, index) {
        let labelItem = document.createElement("div");
        labelItem.className = "label-item";
        labelItem.setAttribute("data-index", index);
        labelItem.setAttribute("data-selected", false);
        labelItem.style.left = item.bbox[0] * 100 + "%";
        labelItem.style.top = item.bbox[1] * 100 + "%";
        labelItem.style.right = (1 - item.bbox[2]) * 100 + "%";
        labelItem.style.bottom = (1 - item.bbox[3]) * 100 + "%";
        let labelItemText = document.createElement("div");
        labelItemText.className = "label-item-text";
        labelItemText.innerText = label_data.classes[item.id];
        labelItem.appendChild(labelItemText);
        labelItem.onclick = function () {
            deleteLabel(labelItem);
        }
        labelContainer.appendChild(labelItem);
    });

    imageList.scrollTo({
        top: imageItem.offsetTop - imageList.clientHeight / 2 + imageItem.clientHeight / 2,
        behavior: "smooth"
    })
}


function navSwitcher(dirc) {
    if (dirc == -1) {
        if (imageIndex > 0) {
            switchToImage(imageIndex - 1);
        }
        else {
            showAlert("前面没有了");
        }
    }
    else if (dirc == 1) {
        if (imageIndex < imageIndexList.length - 1) {
            switchToImage(imageIndex + 1);
        }
        else {
            showAlert("后面没有了");
        }
    }
    else if (dirc == 0) {
        switchToImage(imageIndex);
    }
}

function sidebarSwitcher() {
    let sidebar = document.getElementById("sidebar");
    if (sidebar.clientWidth > 0) {
        sidebar.style.width = "0px";
        sidebar.style.opacity = "0";
    }
    else {
        sidebar.style.width = "200px";
        sidebar.style.opacity = "1";
    }
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