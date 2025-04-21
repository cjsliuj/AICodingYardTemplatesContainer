import {swithcToNormalMode, switchToInspectorMode, switchToEditMode} from './main.js'
// 初始化编辑器
document.addEventListener('DOMContentLoaded', function () {
    addEditorButtons()
})



// 添加编辑器按钮
function addEditorButtons() {

    {
        const btn = document.createElement('button');
        btn.id = '_aiyard_editor_editbtn';
        btn.innerText = 'div edit';
        btn.className = 'editor-button';
        btn.style.right = '180px';
        btn.onclick = function (e) {
            switchToEditMode(e)
        }
        document.body.appendChild(btn);
    }


    {
        const btn = document.createElement('button');
        btn.id = '_aiyard_editor_inspectorbtn';
        btn.innerText = 'inspector';
        btn.className = 'editor-button';
        btn.style.right = '30px';
        btn.onclick = function (e) {
            switchToInspectorMode(e)

        }
        document.body.appendChild(btn);
    }

    {
        const btn = document.createElement('button');
        btn.id = '_aiyard_editor_normalbtn';
        btn.innerText = 'normal';
        btn.className = 'editor-button';
        btn.style.right = '330px';
        btn.onclick = function (e) {
            swithcToNormalMode(e)
        }
        document.body.appendChild(btn);
    }

}