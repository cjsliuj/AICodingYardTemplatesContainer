import {swithcToNormalMode, switchToInspectorMode, switchToEditMode} from './main.js'
// 初始化编辑器
document.addEventListener('DOMContentLoaded', function () {
    addEditorButtons()
})



// 添加编辑器按钮
function addEditorButtons() {

    {
        const btn = document.createElement('button');
        btn.innerText = '启用区域编辑模式';
        btn.className = 'editor-button';
        btn.style.right = '180px';
        btn.onclick = function (e) {
            switchToEditMode(e)
        }
        document.body.appendChild(btn);
    }


    {
        const btn = document.createElement('button');
        btn.innerText = '启用元素检查';
        btn.className = 'editor-button';
        btn.style.right = '30px';
        btn.onclick = function (e) {
            switchToInspectorMode(e)

        }
        document.body.appendChild(btn);
    }

    {
        const btn = document.createElement('button');
        btn.innerText = 'Normal';
        btn.className = 'editor-button';
        btn.style.right = '330px';
        btn.onclick = function (e) {
            swithcToNormalMode(e)
        }
        document.body.appendChild(btn);
    }

}