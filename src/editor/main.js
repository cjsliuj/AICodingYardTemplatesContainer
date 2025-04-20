const MODE_TYPE_NORMAL = 0;
const MODE_TYPE_EDIT = 1;
const MODE_TYPE_INSPECTING = 2;
const MODE_TYPE_TEXT_EDITTING = 3;
window.editorVars = {
    modeType: MODE_TYPE_NORMAL,
    // MODE_TYPE_TEXT_EDITTING only
    textEdittingTargetElement:null,
    selectedElement: null,
    hoverElement: null,
    editHoveredHighlightElement: null,
    inspectHoveredHighlightElement: null,
    saveBtn: null
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
        if (dstModeType === MODE_TYPE_NORMAL) {
            swithcToNormalMode();
        } else if (dstModeType === MODE_TYPE_EDIT) {
            switchToEditMode();
        } else if (dstModeType === MODE_TYPE_INSPECTING) {
            switchToInspectorMode()
        }
    });

    document.addEventListener('click', function (event) {
        handleClickOnDocument(event);

    });

    window.parent.postMessage({
        "msgType": "requestEditMode"
    }, '*');
});

// 初始化编辑器功能
function initEditor() {
    const v = window.editorVars;
    initialEditorElements();
}

function initialEditorElements() {
    const divElement = document.createElement("div");
    divElement.id = "elementInspector";
    document.body.appendChild(divElement);

    const divEditBtnsCtn = document.createElement("div");
    divEditBtnsCtn.id = "divEditorButtons";
    divEditBtnsCtn.innerHTML = `
    <button id="editDuplicateBtn" style="font-size: 20px; font-weight: bold; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0; background-color: #34a853; color: white; border: none;">+</button>
    <button id="editRemoveBtn" style="font-size: 20px; font-weight: bold; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0; background-color: #ea4335; color: white; border: none;">-</button>
    `;
    document.body.appendChild(divEditBtnsCtn);
    // 复制按钮点击事件
    const duplicateBtn = document.getElementById('editDuplicateBtn');
    duplicateBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();
        if (v.selectedElement) {
            duplicateElement(v.selectedElement);
        }
    });

    // 删除按钮点击事件
    const removeBtn = document.getElementById('editRemoveBtn');
    removeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (v.selectedElement) {
            removeElement(v.selectedElement);
        }
    });

    // 阻止编辑按钮冒泡
    const editorButtons = document.getElementById('divEditorButtons');
    editorButtons.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    const v = window.editorVars;
    // 检查检查高亮元素
    if (!document.querySelector('.element-highlight[data-highlight-type="inspect"]')) {
        const highlight = document.createElement('div');
        highlight.className = 'element-highlight';
        highlight.setAttribute('data-highlight-type', 'inspect');
        highlight.style.position = 'absolute';
        highlight.style.zIndex = '9999';
        highlight.style.pointerEvents = 'none';
        highlight.style.border = '2px solid #ea4335';
        highlight.style.backgroundColor = 'rgba(234, 67, 53, 0.1)';
        highlight.style.boxSizing = 'border-box';
        highlight.style.display = 'none';
        document.body.appendChild(highlight);
    }
    v.inspectHoveredHighlightElement = document.querySelector('.element-highlight[data-highlight-type="inspect"]');

    // 检查悬停高亮元素
    if (!document.querySelector('.element-highlight[data-highlight-type="hover"]')) {
        const hover = document.createElement('div');
        hover.className = 'element-highlight';
        hover.setAttribute('data-highlight-type', 'hover');
        hover.style.position = 'absolute';
        hover.style.zIndex = '9998';
        hover.style.pointerEvents = 'none';
        hover.style.backgroundColor = 'rgba(66, 133, 244, 0.2)';
        hover.style.border = '2px solid #4285f4';
        hover.style.boxSizing = 'border-box';
        hover.style.display = 'none';
        document.body.appendChild(hover);
    }
    v.editHoveredHighlightElement = document.querySelector('.element-highlight[data-highlight-type="hover"]');

    // 保存按钮
    const saveCtn = document.createElement('div');
    saveCtn.id = 'editor-savebtn-ctn';
    const saveBtn = document.createElement('button');
    saveBtn.id = 'editor-savebtn'
    saveBtn.className = 'float-btn';
    saveBtn.innerHTML = '🚀'; // 使用emoji作为按钮图标
    saveBtn.addEventListener('click', (e) => {
        handleClickOnSave(e);
    });
    saveCtn.appendChild(saveBtn);
    document.body.appendChild(saveCtn);
    window.editorVars.saveBtn = saveBtn;
}
function handleClickOnSave(event) {
    swithcToNormalMode()
    console.log(document.body.innerHTML)
}
function handleClickOnDocument(event) {
    if (currentModeType() === MODE_TYPE_INSPECTING) {
        event.preventDefault();
        event.stopPropagation();
        const target = event.target;
        const editableTags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'span', 'li', 'td', 'th', 'button', 'a'];

        if (editableTags.includes(target.tagName.toLowerCase()) && !target.hasAttribute('contentEditable')) {
            window.editorVars.modeType = MODE_TYPE_TEXT_EDITTING;
            window.editorVars.textEdittingTargetElement = target;
            target.contentEditable = true;
            target.focus();
            target.addEventListener('blur', (e) => {
                target.removeAttribute('contentEditable');
            });
        }
    }

    // window.parent.postMessage({
    //     "msgType": "edit",
    //     "prototype": Object.prototype.toString.call(event.target),
    //     "outerHTML": target.outerHTML,
    //     "tagName": target.tagName,
    //     "textContent": target.textContent,
    //     "baseURI": target.baseURI
    // }, '*');
}


export function currentModeType() {
    return window.editorVars.modeType;
}

export function swithcToNormalMode() {
    if (window.editorVars.modeType === MODE_TYPE_NORMAL) {
        return
    }
    const v = window.editorVars;
    if (v.modeType === MODE_TYPE_INSPECTING) {
        hideInspector();
        hideInspectorHighlight();
        document.removeEventListener('mousemove', handleInspectorMouseMove);
    } else if (v.modeType === MODE_TYPE_EDIT) {
        removeEditModeFromDivs();
        document.removeEventListener('mousemove', handleEditMouseMove);
    } else if (v.modeType === MODE_TYPE_TEXT_EDITTING) {
        window.editorVars.textEdittingTargetElement.blur();
        window.editorVars.textEdittingTargetElement = null;
    }
    v.saveBtn.style.visibility = 'hidden';
    v.modeType = MODE_TYPE_NORMAL;
}

export function switchToEditMode() {
    if (currentModeType() === MODE_TYPE_EDIT) {
        return
    }
    swithcToNormalMode()
    applyEditModeToDivs();
    document.addEventListener('mousemove', handleEditMouseMove);
    window.editorVars.saveBtn.style.visibility = 'visible';
    window.editorVars.modeType = MODE_TYPE_EDIT;
}

export function switchToInspectorMode() {
    if (currentModeType() === MODE_TYPE_INSPECTING) {
        return
    }
    swithcToNormalMode()

    window.editorVars.saveBtn.style.visibility = 'visible';
    document.addEventListener('mousemove', handleInspectorMouseMove);
    window.editorVars.modeType = MODE_TYPE_INSPECTING;
}

// 显示检查器提示
function showInspector(x, y, element) {
    const v = window.editorVars;
    if (!element) {
        return;
    }
    const inspector = document.getElementById('elementInspector');
    if (!inspector) {
        console.error('[ERROR] 找不到检查器元素');
        return;
    }

    // 查找元素所在的最近的div
    let containingDiv = element;
    while (containingDiv && containingDiv.tagName.toLowerCase() !== 'div' && containingDiv !== document.body) {
        containingDiv = containingDiv.parentElement;
    }

    if (!containingDiv || containingDiv === document.body) {
        containingDiv = element; // 如果找不到包含的div，则显示元素本身
    }

    // 获取元素名称
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

    highlightInspectorHoverToTargetElement(containingDiv);
}

// 高亮显示元素
function highlightInspectorHoverToTargetElement(targetElement) {
    const v = window.editorVars;
    const highlight = v.inspectHoveredHighlightElement;
    const rect = targetElement.getBoundingClientRect();
    highlight.style.top = (rect.top + window.scrollY) + 'px';
    highlight.style.left = (rect.left + window.scrollX) + 'px';
    highlight.style.width = rect.width + 'px';
    highlight.style.height = rect.height + 'px';
    highlight.style.display = 'block';
}

// 处理鼠标移动事件 - 元素检查模式
function handleInspectorMouseMove(e) {
    const x = e.clientX;
    const y = e.clientY;
    const element = document.elementFromPoint(x, y);
    // 忽略编辑器自身的元素
    if (element && (
        element.id === 'elementInspector' || element.id === 'editor-savebtn' ||  element.id === 'editor-savebtn-ctn' ||
        element.classList.contains('element-highlight') ||
        element.classList.contains('editor-button'))) {
        return;
    }
    showInspector(x, y, element);
}

// 隐藏高亮
function hideInspectorHighlight() {

    if (window.editorVars.inspectHoveredHighlightElement) {
        window.editorVars.inspectHoveredHighlightElement.style.display = 'none';
    } else {

    }
}

// 隐藏检查器提示
function hideInspector() {

    const inspector = document.getElementById('elementInspector');
    if (inspector) {
        inspector.style.display = 'none';

    } else {

    }
    hideInspectorHighlight();
}

// 鼠标移动事件处理
function handleEditMouseMove(e) {
    if (!window.editorVars.modeType === MODE_TYPE_EDIT) {
        return;
    }
    const element = document.elementFromPoint(e.clientX, e.clientY);
    // 忽略我们的UI元素
    if (element && (
        element.id === 'elementInspector' ||
        element.id === 'divEditorButtons' ||
        element.classList.contains('element-highlight') ||
        element.classList.contains('editor-button') ||
        element === document.getElementById('editDuplicateBtn') ||
        element === document.getElementById('editRemoveBtn'))) {

        hideEditHoverHighlight();
        return;
    }

    // 查找最近的div元素
    let targetDiv = element;
    while (targetDiv && targetDiv.tagName.toLowerCase() !== 'div' && targetDiv !== document.body) {
        targetDiv = targetDiv.parentElement;
    }
    if (!targetDiv || targetDiv === document.body || targetDiv === window.editorVars.selectedElement) {
        hideEditHoverHighlight();
        return;
    }

    // 更新当前悬停元素
    window.editorVars.hoverElement = targetDiv;
    highlightHoverElement(window.editorVars.hoverElement);
}

// 隐藏悬停高亮
function hideEditHoverHighlight() {
    window.editorVars.editHoveredHighlightElement.style.display = 'none';
}

// 高亮显示悬停元素
function highlightHoverElement(element) {
    const v = window.editorVars;
    if (!element) {
        return;
    }

    const hover = v.editHoveredHighlightElement;
    if (!hover) {
        console.error('[ERROR] 悬停高亮元素创建失败');
        return;
    }

    const rect = element.getBoundingClientRect();
    hover.style.top = (rect.top + window.scrollY) + 'px';
    hover.style.left = (rect.left + window.scrollX) + 'px';
    hover.style.width = rect.width + 'px';
    hover.style.height = rect.height + 'px';
    hover.style.display = 'block';
}

// 应用编辑模式到所有div
function applyEditModeToDivs() {

    const v = window.editorVars;
    const divs = document.querySelectorAll('div');


    let appliedCount = 0;
    divs.forEach(div => {
        // 排除我们自己的元素
        if (div.id === 'elementInspector' ||
            div.id === 'divEditorButtons' ||
            div.classList.contains('element-highlight') ||
            div.classList.contains('editor-button')) {
            return;
        }

        try {
            // 移除可能存在的旧事件监听器
            div.removeEventListener('click', handleElementClick);

            // 添加点击事件
            div.addEventListener('click', handleElementClick);
            // 添加样式
            div.style.cursor = 'pointer';
            appliedCount++;
        } catch (error) {
            console.error('[ERROR] 为DIV应用编辑模式失败:', error);
        }
    });
}


// 处理元素点击事件
function handleElementClick(e) {
    const v = window.editorVars;


    if (window.editorVars.modeType !== MODE_TYPE_EDIT) {

        return;
    }

    // 阻止默认行为和事件冒泡
    e.preventDefault();
    e.stopPropagation();

    // 如果点击的是编辑器元素，不做任何处理
    if (e.target.id === 'elementInspector' ||
        e.target.id === 'divEditorButtons' ||
        e.target.classList.contains('element-highlight') ||
        e.target.classList.contains('editor-button') ||
        e.target === document.getElementById('editDuplicateBtn') ||
        e.target === document.getElementById('editRemoveBtn')) {

        return;
    }

    // 获取点击的div
    const clickedElement = e.currentTarget;


    // 如果已经有选中的元素，移除选中状态
    if (v.selectedElement) {
        v.selectedElement.style.border = '';
        v.selectedElement.style.boxShadow = '';

        // 隐藏编辑按钮
        const editorButtons = document.getElementById('divEditorButtons');
        if (editorButtons) {
            editorButtons.style.display = 'none';
        }


    }

    // 更新选中的元素
    if (v.selectedElement === clickedElement) {
        // 如果再次点击同一个元素，取消选择
        v.selectedElement = null;
        hideEditorButtons();

        return;
    }

    // 设置新选中的元素
    v.selectedElement = clickedElement;

    // 高亮显示选中的元素
    v.selectedElement.style.border = '2px solid #34a853';
    v.selectedElement.style.boxShadow = '0 0 10px rgba(52, 168, 83, 0.5)';

    // 显示编辑按钮
    showEditorButtons(v.selectedElement);


}

// 显示编辑按钮
function showEditorButtons(element) {

    if (!element) return;

    const buttons = document.getElementById('divEditorButtons');
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

// 隐藏编辑按钮
function hideEditorButtons() {

    const buttons = document.getElementById('divEditorButtons');
    if (buttons) {
        buttons.style.display = 'none';

    }
}

// 复制元素
function duplicateElement(element) {

    if (!element) return;

    try {
        // 创建元素的副本
        const clone = element.cloneNode(true);

        // 移除可能的ID以避免重复ID
        if (clone.id) {
            clone.id = clone.id + '-copy';
        }

        // 插入副本到原元素之后
        if (element.parentNode) {
            element.parentNode.insertBefore(clone, element.nextSibling);


        }
    } catch (error) {
        console.error('[ERROR] 复制元素失败:', error);
    }
}

// 移除元素
function removeElement(element) {

    if (!element) return;

    try {
        // 隐藏编辑按钮
        hideEditorButtons();

        // 移除元素（不再需要确认）
        if (element.parentNode) {
            element.parentNode.removeChild(element);


            // 重置选中的元素
            window.editorVars.selectedElement = null;
        }
    } catch (error) {
        console.error('[ERROR] 移除元素失败:', error);
    }
}

// 移除区域编辑模式
function removeEditModeFromDivs() {


    // 清除选中样式和事件监听器
    document.querySelectorAll('div').forEach(div => {
        // 移除事件监听器和样式
        div.removeEventListener('click', handleElementClick);
        div.style.cursor = '';

        // 清除div上可能的高亮样式
        if (div.classList.contains('div-selected')) {
            div.classList.remove('div-selected');
        }

        div.style.outline = '';
        div.style.border = '';
        div.style.boxShadow = '';
    });

    // 重置选中元素
    if (window.editorVars.selectedElement) {
        window.editorVars.selectedElement.style.outline = '';
        window.editorVars.selectedElement.style.border = '';
        window.editorVars.selectedElement.style.boxShadow = '';
        window.editorVars.selectedElement = null;
    }

    // 隐藏编辑按钮
    hideEditorButtons();
    hideEditHoverHighlight();
}
