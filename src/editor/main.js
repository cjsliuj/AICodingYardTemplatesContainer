import {uploadFile} from './uploader.ts'

const STATE_NORMAL = 0;
const STATE_EDIT_PICKING = 2;
const STATE_TEXT_EDITTING = 3;
const STATE_DIV_EDITTING = 4;
const DIV_EDIT_highlightBorder = "2px solid #34a853";
const DIV_EDIT_highlightBoxshadow = "0 0 10px rgba(52, 168, 83, 0.5)";
window.editorVars = {
    state: STATE_NORMAL,
    textEidttingStateInfo: {
        edittingElement: null
    },
    divEidttingStateInfo:{
        selectedElementParent: null,
        selectedElement: null,
        oldBorder:null,
        oldBoxShadow:null,
        duplicatedElements: [],
    },
    hoveredHighlightElement: null,
    saveBtn: null,
    fileSelectorInputElement: null,
    replaceImgElement: null
};

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function () {
    initEditor();
    window.addEventListener('message', (event) => {
        const data = event.data
        const msgType = data["msgType"]
        if (msgType !== "switchMode") {
            return
        }
        const dstModeType = data["dstModeType"]
        if (dstModeType === STATE_NORMAL) {
            swithcToNormalMode();
        } else if (dstModeType === STATE_EDIT_PICKING) {
            switchToInspectorMode()
        }
    });

    document.addEventListener('click', onClickedDocument);

    document.addEventListener('mousemove', onMouseMoved);

    window.parent.postMessage({
        "msgType": "requestEditMode"
    }, '*');
});

// 初始化编辑器功能
function initEditor() {
    const divElement = document.createElement("div");
    divElement.id = "_aiyard_editor_elementInspector";
    document.body.appendChild(divElement);

    const divEditBtnsCtn = document.createElement("div");
    divEditBtnsCtn.id = "_aiyard_editor_divEditorButtons";
    divEditBtnsCtn.innerHTML = `
    <button id="_aiyard_editor_editDuplicateBtn">+</button>
    <button id="_aiyard_editor_editRemoveBtn">-</button>
    `;
    document.body.appendChild(divEditBtnsCtn);
    // 复制按钮点击事件
    const duplicateBtn = document.getElementById('_aiyard_editor_editDuplicateBtn');
    duplicateBtn.addEventListener('click', onClickedDuplicateElementBtn);

    // 删除按钮点击事件
    const removeBtn = document.getElementById('_aiyard_editor_editRemoveBtn');
    removeBtn.addEventListener('click',  onClickedRemoveElement);

    // 阻止编辑按钮冒泡
    const editorButtons = document.getElementById('_aiyard_editor_divEditorButtons');
    editorButtons.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    const v = window.editorVars;
    // 检查检查高亮元素
    const highlight = document.createElement('div');
    highlight.id = '_aiyard_editor_highlight';
    highlight.className = 'element-highlight-div-edit-hint';
    highlight.style.display = 'none';
    document.body.appendChild(highlight);
    v.hoveredHighlightElement = highlight;

    // 保存按钮
    const saveCtn = document.createElement('div');
    saveCtn.id = '_aiyard_editor_savebtn_ctn';
    const saveBtn = document.createElement('button');
    saveBtn.id = '_aiyard_editor_editor_savebtn'
    saveBtn.className = '_aiyard_editor_saveBtn_nor';
    saveBtn.innerText = '保存';
    saveBtn.addEventListener('click', onclickedSaveBtn);
    saveBtn.style.visibility = 'hidden';
    saveCtn.appendChild(saveBtn);
    document.body.appendChild(saveCtn);
    window.editorVars.saveBtn = saveBtn;

    // 文件选择框
    const fileSelectorInputElement = document.createElement('input');
    fileSelectorInputElement.type = 'file';
    fileSelectorInputElement.setAttribute('accept', 'image/*');
    fileSelectorInputElement.id = '_aiyard_editor_imageSelectInput';
    fileSelectorInputElement.style.display = 'none';
    fileSelectorInputElement.addEventListener('change', (e) => {
        onInputFileSelectChanged(e);
    });
    document.body.appendChild(fileSelectorInputElement);
    window.editorVars.fileSelectorInputElement = fileSelectorInputElement;
}

function onclickedSaveBtn(event) {
    const v = window.editorVars;
    if(v.state === STATE_DIV_EDITTING){
        swithcToNormalMode()
        switchToInspectorMode()
    } else {
        swithcToNormalMode()
        const clonedBody = document.body.cloneNode(true)
        const elementsToRemove = clonedBody.querySelectorAll(`[id^="_aiyard_editor_"]`);
        elementsToRemove.forEach(element => {
            element.remove();
        });
        const msg = {
            msgType: 'save',
            bodyInnerHTML:clonedBody.innerHTML,
            baseURI:event.target.baseURI
        }
        window.parent.postMessage(msg,"*")
    }

}
function onClickedDocument(event) {
    if (currentModeType() === STATE_EDIT_PICKING) {
        const target = event.target;
        if (target.id !== undefined && target.id.startsWith("_aiyard_editor_")) {
            return;
        }
        const editableTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'li', 'td', 'th', 'button', 'a'];
        // 点击的是可编辑的文字标签
        if (editableTags.includes(target.tagName.toLowerCase()) && !target.hasAttribute('contentEditable')) {
            window.editorVars.state = STATE_TEXT_EDITTING;
            window.editorVars.textEidttingStateInfo.edittingElement = target;
            target.contentEditable = true;
            target.focus();
            target.addEventListener('blur', onBlur);
        }
        // 点击的是图片
        else if (target.tagName.toLowerCase() === 'img') {
            window.editorVars.replaceImgElement = target;
            window.editorVars.fileSelectorInputElement.click()
        } else if (target.tagName.toLowerCase() === 'div') {
            switchToDivEditMode(event);
        }
    }
}

function onBlur(event){
    console.log('blur', event.target);
    const target = event.target;
    if (target !== window.editorVars.textEidttingStateInfo.edittingElement) {
        return;
    }
    target.removeAttribute('contentEditable');
    swithcToNormalMode()
    switchToInspectorMode()
}

function onInputFileSelectChanged(inputEvent) {
    const selectFile = inputEvent.target.files[0];
    inputEvent.target.value = "";
    uploadFile(selectFile).then((newSrc) => {
        window.editorVars.replaceImgElement.src = newSrc;
    })
}

function onMouseMoved(e) {
    const v = window.editorVars;
    if (v.state === STATE_EDIT_PICKING) {
        const x = e.clientX;
        const y = e.clientY;
        const element = document.elementFromPoint(x, y);
        // 忽略编辑器自身的元素
        if (element.id.startsWith("_aiyard_editor_") ) {
            return;
        }
        showInspector(x, y, element);
    }
}
function switchToDivEditMode(event) {
    swithcToNormalMode()
    const v = window.editorVars;
    v.saveBtn.className = '_aiyard_editor_saveBtn_divEdit';
    v.saveBtn.innerText = '完成';
    v.saveBtn.style.visibility = 'visible';
    const target = event.target;

    v.state = STATE_DIV_EDITTING;
    v.divEidttingStateInfo.selectedElement = target;
    v.divEidttingStateInfo.selectedElementParent = target.parentNode;
    v.divEidttingStateInfo.oldBorder = v.divEidttingStateInfo.selectedElement.style.border;
    v.divEidttingStateInfo.oldBoxShadow = v.divEidttingStateInfo.selectedElement.style.boxShadow;
    v.divEidttingStateInfo.selectedElement.style.border = DIV_EDIT_highlightBorder;
    v.divEidttingStateInfo.selectedElement.style.boxShadow = DIV_EDIT_highlightBoxshadow;
    showDivEditButtons(v.divEidttingStateInfo.selectedElement);

}


export function swithcToNormalMode() {
    if (window.editorVars.state === STATE_NORMAL) {
        return
    }
    const v = window.editorVars;
    if (v.state === STATE_EDIT_PICKING) {
        hideInspector();
        hideHoverHighlight();
    } else if (v.state === STATE_TEXT_EDITTING) {
        hideInspector();
        hideHoverHighlight();
    } else if (v.state === STATE_DIV_EDITTING) {
        v.divEidttingStateInfo.selectedElement.style.boxShadow = v.divEidttingStateInfo.oldBoxShadow;
        v.divEidttingStateInfo.selectedElement.style.border = v.divEidttingStateInfo.oldBorder;
        v.divEidttingStateInfo.duplicatedElements.forEach(element => {
            element.style.boxShadow = v.divEidttingStateInfo.oldBoxShadow;
            element.style.border = v.divEidttingStateInfo.oldBorder;
        })
        v.divEidttingStateInfo.selectedElementParent = null;
        v.divEidttingStateInfo.selectedElement = null;
        v.divEidttingStateInfo.oldBorder = null;
        v.divEidttingStateInfo.oldBoxShadow = null;
        v.divEidttingStateInfo.duplicatedElements = [];
        hideDivEditorButtons();
    } else if (v.state === STATE_TEXT_EDITTING) {
        window.editorVars.textEidttingStateInfo.edittingElement.blur();
        window.editorVars.textEidttingStateInfo.edittingElement = null;
    }
    v.saveBtn.style.visibility = 'hidden';
    v.state = STATE_NORMAL;
}

export function switchToInspectorMode() {
    if (currentModeType() === STATE_EDIT_PICKING) {
        return
    }
    swithcToNormalMode()
    const v = window.editorVars;
    v.saveBtn.className = '_aiyard_editor_saveBtn_nor';
    v.saveBtn.innerText = '保存';
    v.saveBtn.style.visibility = 'visible';
    window.editorVars.state = STATE_EDIT_PICKING;
}

// 显示检查器提示
function showInspector(x, y, element) {
    const v = window.editorVars;
    if (!element) {
        return;
    }
    const inspector = document.getElementById('_aiyard_editor_elementInspector');
    if (!inspector) {
        console.error('[ERROR] 找不到检查器元素');
        return;
    }

    let containingDiv = element;
    let info = '';
    if (containingDiv.tagName) {
        info = containingDiv.tagName.toLowerCase();

        if (containingDiv.id) {
            info += `#${containingDiv.id}`;
        }

        if (containingDiv.className && typeof containingDiv.className === 'string' && containingDiv.className.trim()) {
            const classNames = containingDiv.className.split(' ').filter(cls => cls.trim());
            if (classNames.length > 0) {
                info += `.${classNames.join('.')}`;
            }
        }
    }


    inspector.innerHTML = `<div><strong>${info}</strong></div>`;
    inspector.style.display = 'block';

    // 确保提示框在视窗内
    const inspectorRect = inspector.getBoundingClientRect();
    let left = x + 15;
    let top = y;

    if (left + inspectorRect.width > window.innerWidth) {
        left = x - inspectorRect.width - 5;
    }

    if (top + inspectorRect.height > window.innerHeight) {
        top = window.innerHeight - inspectorRect.height - 5;
    }

    inspector.style.left = `${left}px`;
    inspector.style.top = `${top}px`;

    const highlight = v.hoveredHighlightElement;
    const rect = containingDiv.getBoundingClientRect();
    highlight.style.top = (rect.top + window.scrollY) + 'px';
    highlight.style.left = (rect.left + window.scrollX) + 'px';
    highlight.style.width = rect.width + 'px';
    highlight.style.height = rect.height + 'px';
    highlight.style.display = 'block';
    if (element.tagName.toLowerCase() === 'div') {
        highlight.className = 'element-highlight-div-edit-hint';
    }else {
        highlight.className = 'element-highlight-nor';
    }
}

function hideInspector() {

    const inspector = document.getElementById('_aiyard_editor_elementInspector');
    if (inspector) {
        inspector.style.display = 'none';
    }
    hideHoverHighlight();
}

function hideHoverHighlight() {
    window.editorVars.hoveredHighlightElement.style.display = 'none';
}

function showDivEditButtons(element) {
    if (!element) return;
    const buttons = document.getElementById('_aiyard_editor_divEditorButtons');
    if (!buttons) {
        console.error('[ERROR] 找不到编辑按钮容器');
        return;
    }

    // 获取元素位置
    const rect = element.getBoundingClientRect();

    // 设置按钮位置到右下角
    buttons.style.display = 'flex';
    buttons.style.position = 'absolute';
    buttons.style.top = (rect.bottom + window.scrollY + 5) + 'px'; // 元素底部下方5px
    buttons.style.left = (rect.right + window.scrollX - 90) + 'px'; // 元素右侧偏左90px
}

function hideDivEditorButtons() {
    const buttons = document.getElementById('_aiyard_editor_divEditorButtons');
    if (buttons) {
        buttons.style.display = 'none';
    }
}
function onClickedDuplicateElementBtn(event) {
    const v = window.editorVars;
    const targetEle = v.divEidttingStateInfo.selectedElement;
    const targetEleParent = v.divEidttingStateInfo.selectedElementParent;
    event.preventDefault();
    event.stopPropagation();
    if (targetEle.parentNode === null) {
        targetEleParent.appendChild(targetEle);
    } else {
        const clone = targetEle.cloneNode(true);
        if (clone.id) {
            clone.id = clone.id + '-copy' + v.divEidttingStateInfo.duplicatedElements.length;
        }
        targetEleParent.insertBefore(clone, targetEle.nextSibling);
        v.divEidttingStateInfo.duplicatedElements.push(clone);
    }
}

function onClickedRemoveElement(event) {
    const v = window.editorVars;
    event.preventDefault();
    event.stopPropagation();
    const targetEleParent = v.divEidttingStateInfo.selectedElementParent;
    var toRemoveEle = null;
    if (v.divEidttingStateInfo.duplicatedElements.length > 0) {
        toRemoveEle = v.divEidttingStateInfo.duplicatedElements.pop();
    } else {
        toRemoveEle = v.divEidttingStateInfo.selectedElement;
    }
    if (toRemoveEle.parentNode) {
        targetEleParent.removeChild(toRemoveEle);
    }

}

export function currentModeType() {
    return window.editorVars.state;
}
