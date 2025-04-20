const MODE_TYPE_NORMAL = 0;
const MODE_TYPE_EDIT = 1;
const MODE_TYPE_INSPECTING = 2;
window.editorVars = {
    modeType: MODE_TYPE_NORMAL,
    selectedElement: null,
    hoverElement: null,
    hoveredHighlight: null,
    highlightElement: null,
};

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function () {
    console.log('初始化编辑器...');

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
        if (currentModeType() === MODE_TYPE_INSPECTING) {
            event.preventDefault();
            event.stopPropagation();
        }
        const target = event.target;
        window.parent.postMessage({
            "msgType": "edit",
            "prototype": Object.prototype.toString.call(event.target),
            "outerHTML": target .outerHTML,
            "tagName": target.tagName,
            "textContent": target.textContent,
            "baseURI": target.baseURI
        }, '*');
    });

    window.parent.postMessage({
        "msgType": "requestEditMode"
    }, '*');
});

// 初始化编辑器功能
function initEditor() {
    const v = window.editorVars;
    // 获取DOM元素
    const editorButtons = document.getElementById('divEditorButtons');
    const duplicateBtn = document.getElementById('editDuplicateBtn');
    const removeBtn = document.getElementById('editRemoveBtn');

    // 初始化高亮元素
    ensureHighlightElementsCreated();

    // 复制按钮点击事件
    duplicateBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (v.selectedElement) {
            duplicateElement(v.selectedElement);
        }
    });

    // 删除按钮点击事件
    removeBtn.addEventListener('click', function (e) {
        e.preventDefault();
        e.stopPropagation();

        if (v.selectedElement) {
            removeElement(v.selectedElement);
        }
    });

    // 阻止编辑按钮冒泡
    editorButtons.addEventListener('click', function (e) {
        e.stopPropagation();
    });
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
        hideHighlight();
        document.removeEventListener('mousemove', handleInspectorMouseMove);
    } else if (v.modeType === MODE_TYPE_EDIT) {
        removeEditModeFromDivs();
        document.removeEventListener('mousemove', handleEditMouseMove);
    }
    v.modeType = MODE_TYPE_NORMAL;
}

export function switchToEditMode() {
    if (currentModeType() === MODE_TYPE_EDIT) {
        return
    }
    swithcToNormalMode()
    applyEditModeToDivs();
    document.addEventListener('mousemove', handleEditMouseMove);
    window.editorVars.modeType = MODE_TYPE_EDIT;
}
export function switchToInspectorMode(e){
    if (currentModeType() === MODE_TYPE_INSPECTING) {
        return
    }
    swithcToNormalMode()
    document.addEventListener('mousemove', handleInspectorMouseMove);
    window.editorVars.modeType = MODE_TYPE_INSPECTING;
}
// 确保创建和显示高亮元素
function ensureHighlightElementsCreated() {
    console.log('[DEBUG] 确保高亮元素已创建');
    const v = window.editorVars;
    // 检查检查高亮元素
    if (!document.querySelector('.element-highlight[data-highlight-type="inspect"]')) {
        console.log('[DEBUG] 创建检查高亮元素');
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
        v.highlightElement = highlight;
        console.log('[DEBUG] 检查高亮元素已创建');
    } else {
        console.log('[DEBUG] 检查高亮元素已存在');
        v.highlightElement = document.querySelector('.element-highlight[data-highlight-type="inspect"]');
    }

    // 检查悬停高亮元素
    if (!document.querySelector('.element-highlight[data-highlight-type="hover"]')) {
        console.log('[DEBUG] 创建悬停高亮元素');
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
        v.hoveredHighlight = hover;
        console.log('[DEBUG] 悬停高亮元素已创建');
    } else {
        console.log('[DEBUG] 悬停高亮元素已存在');
        v.hoveredHighlight = document.querySelector('.element-highlight[data-highlight-type="hover"]');
    }

    console.log('[DEBUG] 高亮元素创建完成', {
        highlightElement: !!v.highlightElement,
        hoveredHighlight: !!v.hoveredHighlight
    });
}

// 显示检查器提示
function showInspector(x, y, element) {
    const v = window.editorVars;
    console.log('[DEBUG] 显示检查器:', {x, y, element: element ? element.tagName : 'null'});

    if (!element) {
        console.log('[DEBUG] 无元素可检查');
        return;
    }

    // 获取DOM元素
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

    console.log('[DEBUG] 找到包含元素:', containingDiv ? containingDiv.tagName : 'null');

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

    console.log('[DEBUG] 元素信息:', info);

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

    try {
        // 高亮显示div元素
        console.log('[DEBUG] 尝试高亮显示元素');
        highlightTargetElement(containingDiv);
        console.log('[DEBUG] 元素高亮成功');
    } catch (error) {
        console.error('[ERROR] 元素高亮失败:', error);
    }
}

// 高亮显示元素
function highlightTargetElement(element) {
    const v = window.editorVars;
    console.log('[DEBUG] 高亮显示元素:', element ? element.tagName : 'null');

    if (!element) {
        console.log('[DEBUG] 无元素可高亮');
        return;
    }

    if (!v.highlightElement) {
        console.log('[DEBUG] 高亮元素不存在，尝试创建');
        ensureHighlightElementsCreated();
    }

    const highlight = v.highlightElement;
    console.log('[DEBUG] 高亮元素状态:', !!highlight);

    if (!highlight) {
        console.error('[ERROR] 高亮元素创建失败');
        return;
    }

    const rect = element.getBoundingClientRect();
    console.log('[DEBUG] 元素位置:', {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
    });

    highlight.style.top = (rect.top + window.scrollY) + 'px';
    highlight.style.left = (rect.left + window.scrollX) + 'px';
    highlight.style.width = rect.width + 'px';
    highlight.style.height = rect.height + 'px';
    highlight.style.display = 'block';
}

// 处理鼠标移动事件 - 元素检查模式
function handleInspectorMouseMove(e) {
    console.log('[DEBUG] 处理检查器鼠标移动:', {x: e.clientX, y: e.clientY});
    const x = e.clientX;
    const y = e.clientY;
    const element = document.elementFromPoint(x, y);
    console.log('[DEBUG] 鼠标下元素:', element ? element.tagName : 'null');

    // 忽略编辑器自身的元素
    if (element && (
        element.id === 'elementInspector' ||
        element.classList.contains('element-highlight') ||
        element.classList.contains('editor-button'))) {
        console.log('[DEBUG] 忽略编辑器自身元素');
        return;
    }

    try {
        console.log('[DEBUG] 尝试显示检查器');
        showInspector(x, y, element);
        console.log('[DEBUG] 检查器显示成功');
    } catch (error) {
        console.error('[ERROR] 显示检查器失败:', error);
    }
}

// 隐藏高亮
function hideHighlight() {
    console.log('[DEBUG] 隐藏高亮元素');
    if (window.editorVars.highlightElement) {
        window.editorVars.highlightElement.style.display = 'none';
        console.log('[DEBUG] 高亮元素已隐藏');
    } else {
        console.log('[DEBUG] 无高亮元素可隐藏');
    }
}

// 隐藏检查器提示
function hideInspector() {
    console.log('[DEBUG] 隐藏检查器');
    const inspector = document.getElementById('elementInspector');
    if (inspector) {
        inspector.style.display = 'none';
        console.log('[DEBUG] 检查器已隐藏');
    } else {
        console.log('[DEBUG] 无检查器可隐藏');
    }
    hideHighlight();
}

// 鼠标移动事件处理
function handleEditMouseMove(e) {
    console.log('[DEBUG] 处理鼠标移动事件');

    if (!window.editorVars.modeType === MODE_TYPE_EDIT) {
        console.log('[DEBUG] 编辑模式未启用，不处理鼠标移动');
        return;
    }

    const element = document.elementFromPoint(e.clientX, e.clientY);
    console.log('[DEBUG] 鼠标下元素:', element ? element.tagName : 'null');

    // 忽略我们的UI元素
    if (element && (
        element.id === 'elementInspector' ||
        element.id === 'divEditorButtons' ||
        element.classList.contains('element-highlight') ||
        element.classList.contains('editor-button') ||
        element === document.getElementById('editDuplicateBtn') ||
        element === document.getElementById('editRemoveBtn'))) {
        console.log('[DEBUG] 忽略UI元素');
        hideHoverHighlight();
        return;
    }

    // 查找最近的div元素
    let targetDiv = element;
    while (targetDiv && targetDiv.tagName.toLowerCase() !== 'div' && targetDiv !== document.body) {
        targetDiv = targetDiv.parentElement;
    }

    console.log('[DEBUG] 目标DIV:', targetDiv ? targetDiv.tagName : 'null');

    if (!targetDiv || targetDiv === document.body || targetDiv === window.editorVars.selectedElement) {
        console.log('[DEBUG] 无效目标或已选中，隐藏高亮');
        hideHoverHighlight();
        return;
    }

    // 更新当前悬停元素
    window.editorVars.hoverElement = targetDiv;
    console.log('[DEBUG] 更新悬停元素:', window.editorVars.hoverElement.tagName);

    try {
        // 显示高亮
        console.log('[DEBUG] 尝试高亮悬停元素');
        highlightHoverElement(window.editorVars.hoverElement);
        console.log('[DEBUG] 悬停元素高亮成功');
    } catch (error) {
        console.error('[ERROR] 悬停元素高亮失败:', error);
    }
}

// 隐藏悬停高亮
function hideHoverHighlight() {
    console.log('[DEBUG] 隐藏悬停高亮');
    if (window.editorVars.hoveredHighlight) {
        window.editorVars.hoveredHighlight.style.display = 'none';
        console.log('[DEBUG] 悬停高亮已隐藏');
    } else {
        console.log('[DEBUG] 无悬停高亮可隐藏');
    }
}

// 高亮显示悬停元素
function highlightHoverElement(element) {
    const v = window.editorVars;
    console.log('[DEBUG] 高亮显示悬停元素:', element ? element.tagName : 'null');

    if (!element) {
        console.log('[DEBUG] 无元素可高亮');
        return;
    }

    if (!v.hoveredHighlight) {
        console.log('[DEBUG] 悬停高亮元素不存在，尝试创建');
        ensureHighlightElementsCreated();
    }

    const hover = v.hoveredHighlight;
    console.log('[DEBUG] 悬停高亮元素状态:', !!hover);

    if (!hover) {
        console.error('[ERROR] 悬停高亮元素创建失败');
        return;
    }

    const rect = element.getBoundingClientRect();
    console.log('[DEBUG] 元素位置:', {
        top: rect.top,
        left: rect.left,
        width: rect.width,
        height: rect.height
    });

    hover.style.top = (rect.top + window.scrollY) + 'px';
    hover.style.left = (rect.left + window.scrollX) + 'px';
    hover.style.width = rect.width + 'px';
    hover.style.height = rect.height + 'px';
    hover.style.display = 'block';
}

// 应用编辑模式到所有div
function applyEditModeToDivs() {
    console.log('[DEBUG] 应用编辑模式到所有DIV');
    const v = window.editorVars;
    const divs = document.querySelectorAll('div');
    console.log('[DEBUG] 找到DIV元素数量:', divs.length);

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
    console.log('[DEBUG] 处理元素点击事件');

    if (window.editorVars.modeType !== MODE_TYPE_EDIT) {
        console.log('[DEBUG] 编辑模式未启用，不处理点击');
        return;
    }

    // 阻止默认行为和事件冒泡
    e.preventDefault();
    e.stopPropagation();

    // 确保高亮元素存在
    ensureHighlightElementsCreated();

    // 如果点击的是编辑器元素，不做任何处理
    if (e.target.id === 'elementInspector' ||
        e.target.id === 'divEditorButtons' ||
        e.target.classList.contains('element-highlight') ||
        e.target.classList.contains('editor-button') ||
        e.target === document.getElementById('editDuplicateBtn') ||
        e.target === document.getElementById('editRemoveBtn')) {
        console.log('[DEBUG] 点击的是编辑器元素，忽略');
        return;
    }

    // 获取点击的div
    const clickedElement = e.currentTarget;
    console.log('[DEBUG] 点击的元素:', clickedElement.tagName);

    // 如果已经有选中的元素，移除选中状态
    if (v.selectedElement) {
        v.selectedElement.style.border = '';
        v.selectedElement.style.boxShadow = '';

        // 隐藏编辑按钮
        const editorButtons = document.getElementById('divEditorButtons');
        if (editorButtons) {
            editorButtons.style.display = 'none';
        }

        console.log('[DEBUG] 移除先前选中元素的样式');
    }

    // 更新选中的元素
    if (v.selectedElement === clickedElement) {
        // 如果再次点击同一个元素，取消选择
        v.selectedElement = null;
        hideEditorButtons();
        console.log('[DEBUG] 取消选择元素');
        return;
    }

    // 设置新选中的元素
    v.selectedElement = clickedElement;

    // 高亮显示选中的元素
    v.selectedElement.style.border = '2px solid #34a853';
    v.selectedElement.style.boxShadow = '0 0 10px rgba(52, 168, 83, 0.5)';

    // 显示编辑按钮
    showEditorButtons(v.selectedElement);

    console.log('[DEBUG] 选中新元素，应用样式和显示按钮');
}

// 显示编辑按钮
function showEditorButtons(element) {
    console.log('[DEBUG] 显示编辑按钮');
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

    console.log('[DEBUG] 编辑按钮已显示');
}

// 隐藏编辑按钮
function hideEditorButtons() {
    console.log('[DEBUG] 隐藏编辑按钮');
    const buttons = document.getElementById('divEditorButtons');
    if (buttons) {
        buttons.style.display = 'none';
        console.log('[DEBUG] 编辑按钮已隐藏');
    }
}

// 复制元素
function duplicateElement(element) {
    console.log('[DEBUG] 复制元素');
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
            console.log('[DEBUG] 元素已成功复制');

        }
    } catch (error) {
        console.error('[ERROR] 复制元素失败:', error);
    }
}

// 移除元素
function removeElement(element) {
    console.log('[DEBUG] 移除元素');
    if (!element) return;

    try {
        // 隐藏编辑按钮
        hideEditorButtons();

        // 移除元素（不再需要确认）
        if (element.parentNode) {
            element.parentNode.removeChild(element);
            console.log('[DEBUG] 元素已成功移除');

            // 重置选中的元素
            window.editorVars.selectedElement = null;
        }
    } catch (error) {
        console.error('[ERROR] 移除元素失败:', error);
    }
}

// 移除区域编辑模式
function removeEditModeFromDivs() {
    console.log('[DEBUG] 移除所有DIV的编辑模式');

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

    // 隐藏高亮
    hideHighlight();
    hideHoverHighlight();

    console.log('[DEBUG] 区域编辑模式已移除');
}
