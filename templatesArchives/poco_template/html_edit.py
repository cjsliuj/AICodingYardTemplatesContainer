#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
html_edit.py - HTML页面编辑工具

这个脚本可以为任何HTML页面添加四种编辑功能：
1. 元素检查：查看页面元素的结构和样式
2. 区域编辑：复制或删除页面上的区域
3. 文本编辑：直接编辑页面上的文本内容
4. 图片编辑：上传新图片替换现有图片

用法:
    python html_edit.py <input_html_file> [<output_html_file>]

如果没有指定输出文件，则会在输入文件名基础上添加"-editable"后缀
"""

import os
import sys
import re
from bs4 import BeautifulSoup

# 编辑工具的CSS样式
EDITOR_STYLES = """
<style id="editor-styles">
/* 编辑器按钮样式 */
.editor-button {
  position: fixed;
  bottom: 20px;
  z-index: 10000;
  padding: 10px 15px;
  background-color: #4285f4;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  box-shadow: 0 2px 5px rgba(0,0,0,0.3);
  font-size: 14px;
  font-weight: bold;
  transition: background-color 0.2s;
}

/* 元素高亮样式 */
.element-highlight {
  position: absolute;
  z-index: 9999;
  pointer-events: none;
  border: 2px solid #ea4335;
  background-color: rgba(234, 67, 53, 0.1);
  box-sizing: border-box;
}

/* 元素检查器样式 */
#elementInspector {
  position: fixed;
  display: none;
  z-index: 10000;
  padding: 10px 15px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2);
  font-size: 12px;
  max-width: 300px;
  word-break: break-all;
}

/* 编辑按钮容器 */
#divEditorButtons {
  position: absolute;
  display: none;
  z-index: 10000;
  gap: 5px;
}

/* 编辑按钮样式 */
#editDuplicateBtn {
  padding: 0 !important;
  background-color: #34a853 !important;
  color: white !important;
  font-weight: bold !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 36px !important;
  height: 36px !important;
  text-align: center !important;
  font-size: 20px !important;
  border-radius: 4px !important;
  margin: 0 4px !important;
  border: none !important;
}

#editRemoveBtn {
  padding: 0 !important;
  background-color: #ea4335 !important;
  color: white !important;
  font-weight: bold !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 36px !important;
  height: 36px !important;
  text-align: center !important;
  font-size: 20px !important;
  border-radius: 4px !important;
  margin: 0 4px !important;
  border: none !important;
}

/* 选中的div元素样式 */
.div-selected {
  outline: 2px dashed #4285f4 !important;
  outline-offset: 1px !important;
  position: relative;
}

/* 文本和图片编辑样式 - 完全不影响布局的版本 */
.text-editable:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  outline: 1px dashed #34a853;
  pointer-events: none;
  z-index: 9998;
}

.text-editable:hover:after {
  background-color: rgba(52, 168, 83, 0.1);
}

.text-editable:focus:after {
  outline: 1px solid #34a853;
  background-color: rgba(52, 168, 83, 0.05);
}

.text-editable {
  cursor: text !important;
}

.image-editable:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  outline: 2px dashed #fbbc05;
  pointer-events: none;
  z-index: 9998;
}

.image-editable:hover:after {
  background-color: rgba(251, 188, 5, 0.1);
}

.image-editable {
  cursor: pointer !important;
}

/* 带有背景图的可编辑元素样式 */
.bg-image-editable:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  outline: 2px dashed #fbbc05;
  pointer-events: none;
  z-index: 9998;
}

.bg-image-editable:hover:after {
  background-color: rgba(251, 188, 5, 0.1);
}

.bg-image-editable:before {
  content: "🖼️";
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: rgba(251, 188, 5, 0.8);
  color: #333;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 12px;
  z-index: 9999;
  pointer-events: none;
}

.bg-image-editable {
  cursor: pointer !important;
}

/* 轮播图容器样式 */
.carousel-container-editable:after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  outline: 2px dashed #4285f4;
  pointer-events: none;
  z-index: 9998;
}

.carousel-container-editable:hover:after {
  background-color: rgba(66, 133, 244, 0.1);
}

.carousel-container-editable:before {
  content: "🎞️";
  position: absolute;
  top: 5px;
  right: 5px;
  background-color: rgba(66, 133, 244, 0.8);
  color: white;
  padding: 2px 5px;
  border-radius: 3px;
  font-size: 12px;
  z-index: 9999;
  pointer-events: none;
}

.carousel-container-editable {
  cursor: pointer !important;
}

/* 图片上传模态框样式 */
#imageUploadModal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.7);
  display: none;
  align-items: center;
  justify-content: center;
  z-index: 10001;
}

.modal-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-title {
  margin-top: 0;
  color: #333;
}

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  gap: 10px;
}

.modal-button {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

#cancelImageUpload {
  background-color: #f2f2f2;
  color: #333;
}

#applyImageUpload {
  background-color: #4285f4;
  color: #fff;
}

#imagePreview {
  margin-top: 15px;
  text-align: center;
}

#imagePreview img {
  max-width: 100%;
  max-height: 300px;
  border: 1px solid #ddd;
}
</style>
"""

# 编辑工具的HTML元素
EDITOR_ELEMENTS = """
<!-- 元素检查器 -->
<div id="elementInspector"></div>

<!-- 区域编辑按钮容器 -->
<div id="divEditorButtons">
  <button id="editDuplicateBtn" style="font-size: 20px; font-weight: bold; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0; background-color: #34a853; color: white; border: none;">+</button>
  <button id="editRemoveBtn" style="font-size: 20px; font-weight: bold; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; padding: 0; background-color: #ea4335; color: white; border: none;">-</button>
</div>

<!-- 图片上传模态框 -->
<div id="imageUploadModal">
  <div class="modal-content">
    <h3 class="modal-title">上传新图片</h3>
    <p id="imageUploadDescription">选择一个图片文件上传替换当前图片。</p>
    <div id="uploadTypeToggle" style="margin-bottom: 15px; display: none;">
      <label><input type="radio" name="uploadType" value="single" checked> 单张上传</label>
      <label style="margin-left: 15px;"><input type="radio" name="uploadType" value="multiple"> 多张上传(轮播)</label>
    </div>
    <input type="file" id="imageFileInput" accept="image/*">
    <input type="file" id="multipleImageFileInput" accept="image/*" multiple style="display: none;">
    <div id="imagePreview"></div>
    <div id="multipleImagePreview" style="display: none; margin-top: 15px;"></div>
    <div class="modal-buttons">
      <button id="cancelImageUpload" class="modal-button">取消</button>
      <button id="applyImageUpload" class="modal-button">应用</button>
    </div>
  </div>
</div>
"""

# 编辑工具的JavaScript代码
EDITOR_SCRIPTS = """
<script id="editor-script">
// 全局共享变量
window.editorVars = {
  isTextEditMode: false,
  isImageEditMode: false,
  isInspecting: false,
  isEditMode: false,
  editedTextElements: {},
  editedImages: {},
  editedBackgroundImages: {},
  editedCarouselImages: {},
  currentEditingImage: null,
  currentEditingElement: null,
  currentEditingType: 'single', // 'single', 'background', 'carousel', 'container'
  selectedElement: null,
  hoverElement: null,
  hoveredHighlight: null,
  highlightElement: null,
  uploadedMultipleImages: [],
  containerImages: [], // 存储容器内的所有图片
  selectedImageIndex: -1, // 当前选中的图片索引
  selectedSingleFile: null, // 存储单个选择的文件
  selectedMultipleFiles: null, // 存储多个选择的文件
  buttons: null // 存储编辑器按钮引用
};

// 获取元素路径的函数
function getElementPath(element) {
  if (!element) return '';
  
  let path = [];
  let current = element;
  
  while (current && current !== document.documentElement) {
    let selector = current.tagName.toLowerCase();
    
    if (current.id) {
      selector += '#' + current.id;
    } else {
      // 获取元素在其父元素中的索引
      let index = 0;
      let sibling = current;
      while (sibling) {
        if (sibling.tagName === current.tagName) {
          index++;
        }
        sibling = sibling.previousElementSibling;
      }
      selector += `:nth-of-type(${index})`;
    }
    
    path.unshift(selector);
    current = current.parentElement;
  }
  
  return path.join(' > ');
}

// 保存页面状态函数
function savePageState() {
  localStorage.setItem('pageLastModified', new Date().getTime().toString());
}

// 添加编辑器按钮
function addEditorButtons() {
  // 文本编辑按钮
  const toggleTextEditButton = document.createElement('button');
  toggleTextEditButton.innerText = '启用文本编辑';
  toggleTextEditButton.className = 'editor-button';
  toggleTextEditButton.style.right = '350px';
  document.body.appendChild(toggleTextEditButton);
  
  // 图片编辑按钮
  const toggleImageEditButton = document.createElement('button');
  toggleImageEditButton.innerText = '启用图片编辑';
  toggleImageEditButton.className = 'editor-button';
  toggleImageEditButton.style.right = '580px';
  document.body.appendChild(toggleImageEditButton);
  
  // 区域编辑按钮
  const toggleEditButton = document.createElement('button');
  toggleEditButton.innerText = '启用区域编辑模式';
  toggleEditButton.className = 'editor-button';
  toggleEditButton.style.right = '180px';
  document.body.appendChild(toggleEditButton);
  
  // 元素检查按钮
  const toggleInspectButton = document.createElement('button');
  toggleInspectButton.innerText = '启用元素检查';
  toggleInspectButton.className = 'editor-button';
  toggleInspectButton.style.right = '30px';
  document.body.appendChild(toggleInspectButton);
  
  return {
    textEditBtn: toggleTextEditButton,
    imageEditBtn: toggleImageEditButton,
    editBtn: toggleEditButton,
    inspectBtn: toggleInspectButton
  };
}

// 初始化编辑器功能
function initEditor() {
  console.log('[DEBUG] 开始初始化编辑器');
  const v = window.editorVars;
  console.log('[DEBUG] 编辑器变量状态:', JSON.stringify({
    isTextEditMode: v.isTextEditMode,
    isImageEditMode: v.isImageEditMode,
    isInspecting: v.isInspecting,
    isEditMode: v.isEditMode
  }));
  
  // 获取DOM元素
  const inspector = document.getElementById('elementInspector');
  const editorButtons = document.getElementById('divEditorButtons');
  const duplicateBtn = document.getElementById('editDuplicateBtn');
  const removeBtn = document.getElementById('editRemoveBtn');
  const imageUploadModal = document.getElementById('imageUploadModal');
  const imageFileInput = document.getElementById('imageFileInput');
  const imagePreview = document.getElementById('imagePreview');
  const cancelImageUploadBtn = document.getElementById('cancelImageUpload');
  const applyImageUploadBtn = document.getElementById('applyImageUpload');
  
  console.log('[DEBUG] DOM元素加载状态:', {
    inspector: !!inspector,
    editorButtons: !!editorButtons,
    duplicateBtn: !!duplicateBtn,
    removeBtn: !!removeBtn,
    imageUploadModal: !!imageUploadModal
  });
  
  // 添加编辑器按钮
  const buttons = addEditorButtons();
  // 保存按钮到全局变量
  v.buttons = buttons;
  
  console.log('[DEBUG] 编辑器按钮创建:', {
    textEditBtn: !!buttons.textEditBtn,
    imageEditBtn: !!buttons.imageEditBtn,
    editBtn: !!buttons.editBtn,
    inspectBtn: !!buttons.inspectBtn
  });
  
  // 初始化高亮元素
  ensureHighlightElementsCreated();
  
  // 绑定按钮事件
  bindButtonEvents();
  
  // 确保复制和删除按钮文本显示正确
  function fixActionButtons() {
    if (duplicateBtn) {
      duplicateBtn.innerHTML = '+';
      duplicateBtn.style.fontSize = '20px';
      duplicateBtn.style.backgroundColor = '#34a853';
      duplicateBtn.style.color = 'white';
    }
    
    if (removeBtn) {
      removeBtn.innerHTML = '-';
      removeBtn.style.fontSize = '20px';
      removeBtn.style.backgroundColor = '#ea4335';
      removeBtn.style.color = 'white';
    }
  }
  
  // 定期执行确保按钮显示正确
  fixActionButtons();
  setInterval(fixActionButtons, 500);
  
  // 复制按钮点击事件
  duplicateBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (v.selectedElement) {
      duplicateElement(v.selectedElement);
    }
  });
  
  // 删除按钮点击事件
  removeBtn.addEventListener('click', function(e) {
    e.preventDefault();
    e.stopPropagation();
    
    if (v.selectedElement) {
      removeElement(v.selectedElement);
    }
  });
  
  // 阻止编辑按钮冒泡
  editorButtons.addEventListener('click', function(e) {
    e.stopPropagation();
  });
  
  // 在页面加载时应用保存的修改
  document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] DOM内容加载完成');
    setTimeout(() => {
      console.log('[DEBUG] 开始应用保存的修改');
      try {
        // 加载文本编辑
        v.editedTextElements = JSON.parse(localStorage.getItem('editedTexts') || '{}');
        applyTextEdits();
        
        // 加载图片编辑
        v.editedImages = JSON.parse(localStorage.getItem('editedImages') || '{}');
        v.editedBackgroundImages = JSON.parse(localStorage.getItem('editedBackgroundImages') || '{}');
        v.editedCarouselImages = JSON.parse(localStorage.getItem('editedCarouselImages') || '{}');
        applyImageEdits();
        
        // 应用页面修改
        applyPageModifications();
        
        // 确保高亮元素已创建
        ensureHighlightElementsCreated();
        console.log('[DEBUG] 保存的修改应用完成');
      } catch (error) {
        console.error('[ERROR] 应用保存的修改失败:', error);
      }
    }, 500);
  });

  console.log('[DEBUG] 编辑器初始化完成');
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

// 绑定按钮事件处理
function bindButtonEvents() {
  const v = window.editorVars;
  const buttons = v.buttons;
  
  if (!buttons) {
    console.error('[ERROR] 按钮未定义，无法绑定事件');
    return;
  }
  
  console.log('[DEBUG] 开始绑定按钮事件');

  // 切换元素检查模式
  buttons.inspectBtn.addEventListener('click', function(e) {
    console.log('[DEBUG] 元素检查按钮被点击', e.type);
    console.log('[DEBUG] 点击前状态:', { 
      isInspecting: v.isInspecting,
      isTextEditMode: v.isTextEditMode,
      isImageEditMode: v.isImageEditMode,
      isEditMode: v.isEditMode
    });
    
    // 清除可能的旧事件处理程序
    document.removeEventListener('mousemove', handleInspectorMouseMove);
    document.removeEventListener('mousemove', handleMouseMove);
    console.log('[DEBUG] 旧事件处理程序已清除');
    
    // 如果其他模式已开启，先关闭
    if (v.isTextEditMode) {
      console.log('[DEBUG] 关闭文本编辑模式');
      v.isTextEditMode = false;
      removeTextEditability();
      buttons.textEditBtn.innerText = '启用文本编辑';
      buttons.textEditBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isImageEditMode) {
      console.log('[DEBUG] 关闭图片编辑模式');
      v.isImageEditMode = false;
      completelyRemoveImageEditability();
      buttons.imageEditBtn.innerText = '启用图片编辑';
      buttons.imageEditBtn.style.backgroundColor = '#4285f4';
      buttons.imageEditBtn.style.color = '#fff';
    }
    
    if (v.isEditMode) {
      console.log('[DEBUG] 关闭区域编辑模式');
      v.isEditMode = false;
      removeEditModeFromDivs();
      buttons.editBtn.innerText = '启用区域编辑模式';
      buttons.editBtn.style.backgroundColor = '#4285f4';
    }
    
    // 切换检查模式状态
    v.isInspecting = !v.isInspecting;
    console.log('[DEBUG] 检查模式切换为:', v.isInspecting);
    
    if (v.isInspecting) {
      console.log('[DEBUG] 启用元素检查');
      this.innerText = '禁用元素检查';
      this.style.backgroundColor = '#ea4335';
      
      try {
        // 绑定鼠标移动事件处理程序
        console.log('[DEBUG] 尝试绑定检查器鼠标移动事件');
        document.addEventListener('mousemove', handleInspectorMouseMove);
        console.log('[DEBUG] 检查器鼠标移动事件绑定成功');
      } catch (error) {
        console.error('[ERROR] 绑定检查器鼠标移动事件失败:', error);
      }
    } else {
      console.log('[DEBUG] 禁用元素检查');
      this.innerText = '启用元素检查';
      this.style.backgroundColor = '#4285f4';
      
      try {
        // 隐藏检查器和高亮
        console.log('[DEBUG] 尝试隐藏检查器和高亮');
        hideInspector();
        hideHighlight();
        console.log('[DEBUG] 检查器和高亮隐藏成功');
        
        // 解绑鼠标移动事件处理程序
        document.removeEventListener('mousemove', handleInspectorMouseMove);
        console.log('[DEBUG] 检查器鼠标移动事件解绑成功');
      } catch (error) {
        console.error('[ERROR] 隐藏检查器或解绑事件失败:', error);
      }
    }
    console.log('[DEBUG] 元素检查模式切换完成');
  });
  
  // 切换区域编辑模式
  buttons.editBtn.addEventListener('click', function(e) {
    console.log('[DEBUG] 区域编辑按钮被点击', e.type);
    console.log('[DEBUG] 点击前状态:', { 
      isEditMode: v.isEditMode,
      isInspecting: v.isInspecting, 
      isTextEditMode: v.isTextEditMode,
      isImageEditMode: v.isImageEditMode
    });
    
    // 清除可能的旧事件处理程序
    document.removeEventListener('mousemove', handleInspectorMouseMove);
    document.removeEventListener('mousemove', handleMouseMove);
    console.log('[DEBUG] 旧事件处理程序已清除');
    
    // 如果其他模式已开启，先关闭
    if (v.isInspecting) {
      console.log('[DEBUG] 关闭元素检查模式');
      v.isInspecting = false;
      hideInspector();
      hideHighlight();
      buttons.inspectBtn.innerText = '启用元素检查';
      buttons.inspectBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isTextEditMode) {
      console.log('[DEBUG] 关闭文本编辑模式');
      v.isTextEditMode = false;
      removeTextEditability();
      buttons.textEditBtn.innerText = '启用文本编辑';
      buttons.textEditBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isImageEditMode) {
      console.log('[DEBUG] 关闭图片编辑模式');
      v.isImageEditMode = false;
      completelyRemoveImageEditability();
      buttons.imageEditBtn.innerText = '启用图片编辑';
      buttons.imageEditBtn.style.backgroundColor = '#4285f4';
      buttons.imageEditBtn.style.color = '#fff';
    }
    
    // 切换区域编辑状态
    v.isEditMode = !v.isEditMode;
    console.log('[DEBUG] 区域编辑模式切换为:', v.isEditMode);
    
    if (v.isEditMode) {
      console.log('[DEBUG] 启用区域编辑模式');
      this.innerText = '禁用区域编辑模式';
      this.style.backgroundColor = '#ea4335';
      
      try {
        // 应用区域编辑模式
        console.log('[DEBUG] 尝试应用区域编辑模式');
        applyEditModeToDivs();
        console.log('[DEBUG] 区域编辑模式应用成功');
        
        // 绑定鼠标移动事件处理程序
        console.log('[DEBUG] 尝试绑定鼠标移动事件');
        document.addEventListener('mousemove', handleMouseMove);
        console.log('[DEBUG] 鼠标移动事件绑定成功');
      } catch (error) {
        console.error('[ERROR] 应用区域编辑模式失败:', error);
      }
    } else {
      console.log('[DEBUG] 禁用区域编辑模式');
      this.innerText = '启用区域编辑模式';
      this.style.backgroundColor = '#4285f4';
      
      try {
        // 移除区域编辑模式
        console.log('[DEBUG] 尝试移除区域编辑模式');
        removeEditModeFromDivs();
        console.log('[DEBUG] 区域编辑模式移除成功');
        
        // 解绑鼠标移动事件处理程序
        document.removeEventListener('mousemove', handleMouseMove);
        console.log('[DEBUG] 鼠标移动事件解绑成功');
      } catch (error) {
        console.error('[ERROR] 移除区域编辑模式失败:', error);
      }
    }
    console.log('[DEBUG] 区域编辑模式切换完成');
  });
  
  // 切换文本编辑模式
  buttons.textEditBtn.addEventListener('click', function() {
    // 清除可能的旧事件处理程序
    document.removeEventListener('mousemove', handleInspectorMouseMove);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mousemove', handleImageEditMouseMove);
    
    // 清理所有样式残留
    clearAllEditModes();
    
    // 如果其他模式已开启，先关闭
    if (v.isImageEditMode) {
      v.isImageEditMode = false;
      completelyRemoveImageEditability();
      buttons.imageEditBtn.innerText = '启用图片编辑';
      buttons.imageEditBtn.style.backgroundColor = '#4285f4';
      buttons.imageEditBtn.style.color = '#fff';
    }
    
    if (v.isInspecting) {
      v.isInspecting = false;
      hideInspector();
      hideHighlight();
      buttons.inspectBtn.innerText = '启用元素检查';
      buttons.inspectBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isEditMode) {
      v.isEditMode = false;
      removeEditModeFromDivs();
      buttons.editBtn.innerText = '启用区域编辑模式';
      buttons.editBtn.style.backgroundColor = '#4285f4';
    }
    
    v.isTextEditMode = !v.isTextEditMode;
    
    if (v.isTextEditMode) {
      // 启用文本编辑模式
      this.innerText = '禁用文本编辑';
      this.style.backgroundColor = '#34a853';
      
      // 使所有文本元素可编辑
      makeElementEditable(document.body);
    } else {
      // 禁用文本编辑模式
      this.innerText = '启用文本编辑';
      this.style.backgroundColor = '#4285f4';
      
      // 移除可编辑属性
      removeTextEditability();
    }
  });
  
  // 切换图片编辑模式
  buttons.imageEditBtn.addEventListener('click', function() {
    // 清除可能的旧事件处理程序
    document.removeEventListener('mousemove', handleInspectorMouseMove);
    document.removeEventListener('mousemove', handleMouseMove);
    document.removeEventListener('mousemove', handleImageEditMouseMove);
    
    // 清理所有样式残留
    clearAllEditModes();
    
    // 如果其他模式已开启，先关闭
    if (v.isTextEditMode) {
      v.isTextEditMode = false;
      removeTextEditability();
      buttons.textEditBtn.innerText = '启用文本编辑';
      buttons.textEditBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isInspecting) {
      v.isInspecting = false;
      hideInspector();
      hideHighlight();
      buttons.inspectBtn.innerText = '启用元素检查';
      buttons.inspectBtn.style.backgroundColor = '#4285f4';
    }
    
    if (v.isEditMode) {
      v.isEditMode = false;
      removeEditModeFromDivs();
      buttons.editBtn.innerText = '启用区域编辑模式';
      buttons.editBtn.style.backgroundColor = '#4285f4';
    }
    
    v.isImageEditMode = !v.isImageEditMode;
    
    if (v.isImageEditMode) {
      // 启用图片编辑模式
      this.innerText = '禁用图片编辑';
      this.style.backgroundColor = '#fbbc05';
      this.style.color = '#000';
      
      console.log('[DEBUG] 正在启用图片编辑模式...');
      
      // 使所有图片元素可编辑
      makeImagesEditable();
      
      // 阻止链接点击事件
      document.querySelectorAll('a[data-image-editable-container="true"]').forEach(link => {
        link.addEventListener('click', preventLinkClick);
      });
      
      // 显示容器编辑图标
      document.querySelectorAll('[data-container-editable="true"] .container-edit-icon').forEach(icon => {
        if (icon) {
          icon.style.display = 'block';
        }
      });
      
      // 添加鼠标移动事件来高亮div
      document.addEventListener('mousemove', handleImageEditMouseMove);
      
      console.log('[DEBUG] 图片编辑模式已启用，可以点击div或图片');
    } else {
      // 禁用图片编辑模式
      this.innerText = '启用图片编辑';
      this.style.backgroundColor = '#4285f4';
      this.style.color = '#fff';
      
      // 使用增强的清理函数
      completelyRemoveImageEditability();
      
      // 恢复链接点击行为
      document.querySelectorAll('a[data-image-editable-container="true"]').forEach(link => {
        link.removeEventListener('click', preventLinkClick);
        link.removeAttribute('data-image-editable-container');
      });
      
      // 移除鼠标移动事件监听
      document.removeEventListener('mousemove', handleImageEditMouseMove);
      
      // 隐藏高亮
      hideHoverHighlight();
      
      // 移除所有div-hover-highlight类
      document.querySelectorAll('.div-hover-highlight').forEach(div => {
        div.classList.remove('div-hover-highlight');
        div.style.cursor = '';
      });
      
      // 移除所有div-image-container类
      document.querySelectorAll('.div-image-container').forEach(div => {
        div.classList.remove('div-image-container');
        div.removeAttribute('data-images-count');
      });
    }
  });
  
  console.log('[DEBUG] 按钮事件绑定完成');
}

// 显示检查器提示
function showInspector(x, y, element) {
  const v = window.editorVars;
  console.log('[DEBUG] 显示检查器:', { x, y, element: element ? element.tagName : 'null' });
  
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
  console.log('[DEBUG] 处理检查器鼠标移动:', { x: e.clientX, y: e.clientY });
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
function handleMouseMove(e) {
  console.log('[DEBUG] 处理鼠标移动事件');
  
  if (!window.editorVars.isEditMode) {
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
      
      // 如果图片编辑模式和区域编辑模式同时开启，添加图片编辑功能
      if (v.isImageEditMode) {
        div.addEventListener('click', function(e) {
          // 只有在选中状态下才允许编辑图片
          if (v.selectedElement === this) {
            handleImageEditClick.call(this, e);
          }
        });
      }
      
      // 添加样式
      div.style.cursor = 'pointer';
      appliedCount++;
    } catch (error) {
      console.error('[ERROR] 为DIV应用编辑模式失败:', error);
    }
  });
}

// 完全移除图片编辑功能
function completelyRemoveImageEditability() {
  const v = window.editorVars;
  console.log('[DEBUG] 完全移除图片编辑功能');
  
  try {
    // 移除所有图片的可编辑状态
    document.querySelectorAll('img.image-editable').forEach(img => {
      img.classList.remove('image-editable');
      img.style.cursor = '';
      img.style.border = '';
      img.style.padding = '';
      img.style.margin = '';
      img.style.outline = '';
      img.removeEventListener('click', handleImageEditClick);
    });
    
    // 移除所有背景图片的可编辑状态
    document.querySelectorAll('.bg-image-editable, [data-bg-editable]').forEach(el => {
      el.classList.remove('bg-image-editable');
      el.removeAttribute('data-bg-editable');
      el.style.cursor = '';
      el.style.outline = '';
      el.removeEventListener('click', handleImageEditClick);
    });
    
    // 移除轮播图容器的可编辑状态
    document.querySelectorAll('.carousel-container-editable, [data-carousel-editable]').forEach(carousel => {
      carousel.classList.remove('carousel-container-editable');
      carousel.removeAttribute('data-carousel-editable');
      carousel.style.outline = '';
      
      // 移除提示标记
      const hint = carousel.querySelector('[data-carousel-hint]');
      if (hint && hint.parentElement) {
        hint.parentElement.removeChild(hint);
      }
    });
    
    // 移除容器编辑标记和事件
    document.querySelectorAll('[data-container-editable="true"]').forEach(container => {
      container.removeAttribute('data-container-editable');
      
      // 移除编辑图标
      const icon = container.querySelector('.container-edit-icon');
      if (icon) {
        icon.style.display = 'none';
      }
    });
    
    // 移除所有容器提示
    document.querySelectorAll('[data-container-hint]').forEach(hint => {
      if (hint.parentElement) {
        hint.parentElement.removeChild(hint);
      }
    });
    
    // 移除所有div-image-container类和高亮
    document.querySelectorAll('.div-image-container, .div-hover-highlight').forEach(div => {
      div.classList.remove('div-image-container');
      div.classList.remove('div-hover-highlight');
      div.style.cursor = '';
      div.style.outline = '';
      div.style.border = '';
      div.removeAttribute('data-images-count');
    });
    
    // 恢复链接点击行为
    document.querySelectorAll('a[data-image-editable-container="true"]').forEach(link => {
      link.removeEventListener('click', preventLinkClick);
      link.removeAttribute('data-image-editable-container');
    });
    
    // 为所有div移除点击事件
    document.querySelectorAll('div').forEach(div => {
      div.removeEventListener('click', handleImageEditClick);
    });
    
    // 关闭图片上传模态框
    closeImageUploadModal();
    
    // 重置变量
    v.currentEditingImage = null;
    v.currentEditingElement = null;
    v.currentEditingType = 'single';
    v.containerImages = [];
    v.selectedSingleFile = null;
    v.selectedMultipleFiles = null;
    v.currentImageIndex = 0;
    
    // 隐藏高亮
    hideHighlight();
    hideHoverHighlight();
    
    console.log('[DEBUG] 图片编辑功能已完全移除');
  } catch (error) {
    console.error('[ERROR] 移除图片编辑功能时出错:', error);
  }
}

// 移除图片编辑功能
function removeImageEditability() {
  // 移除所有图片的编辑状态
  document.querySelectorAll('img.image-editable').forEach(img => {
    img.classList.remove('image-editable');
    img.style.cursor = '';
    img.style.border = '';
    img.style.padding = '';
    img.style.margin = '';
    img.style.outline = '';
    img.removeEventListener('click', handleImageEditClick);
  });
  
  // 移除所有背景图片的编辑状态
  document.querySelectorAll('.bg-image-editable, [data-bg-editable]').forEach(el => {
    el.classList.remove('bg-image-editable');
    el.removeAttribute('data-bg-editable');
    el.style.cursor = '';
    el.style.outline = '';
    el.removeEventListener('click', handleImageEditClick);
  });
  
  // 移除轮播图容器的编辑状态
  document.querySelectorAll('.carousel-container-editable, [data-carousel-editable]').forEach(carousel => {
    carousel.classList.remove('carousel-container-editable');
    carousel.removeAttribute('data-carousel-editable');
    
    // 移除提示标记
    const hint = carousel.querySelector('[data-carousel-hint]');
    if (hint) {
      carousel.removeChild(hint);
    }
  });
  
  // 移除区域容器中的图片编辑提示
  document.querySelectorAll('[data-container-hint]').forEach(hint => {
    if (hint.parentElement) {
      hint.parentElement.removeChild(hint);
    }
  });
  
  // 关闭图片上传模态框
  const imageUploadModal = document.getElementById('imageUploadModal');
  if (imageUploadModal) {
    imageUploadModal.style.display = 'none';
  }
  
  console.log('[DEBUG] 已移除所有图片编辑功能');
}

// 处理图片编辑点击事件
function handleImageEditClick(e) {
  const v = window.editorVars;
  console.log('[DEBUG] 处理图片编辑点击事件', e.currentTarget.tagName);
  
  if (!v.isImageEditMode) {
    console.log('[DEBUG] 图片编辑模式未启用，不处理点击');
    return;
  }
  
  // 阻止事件冒泡和默认行为
  e.preventDefault();
  e.stopPropagation();
  
  // 获取点击的元素
  const element = e.currentTarget;
  console.log('[DEBUG] 点击的元素类型:', element.tagName);
  
  // 记录当前编辑的元素
  v.currentEditingElement = element;
  
  // 确定编辑类型
  if (element.tagName === 'IMG') {
    v.currentEditingType = 'single';
    v.currentEditingImage = element; // 保存当前编辑的图片元素
    console.log('[DEBUG] 识别为单图片编辑');
  } else if (element.classList.contains('bg-image-editable')) {
    v.currentEditingType = 'background';
    console.log('[DEBUG] 识别为背景图片编辑');
  } else if (element.classList.contains('carousel-container-editable')) {
    v.currentEditingType = 'carousel';
    console.log('[DEBUG] 识别为轮播图编辑');
    
    // 找到容器内的所有图片
    v.containerImages = Array.from(element.querySelectorAll('img'));
  } else if (element.tagName.toLowerCase() === 'div') {
    // div容器中的图片 - 不再需要v.isEditMode检查，因为现在直接在图片编辑模式下可以点击div
    v.currentEditingType = 'container';
    console.log('[DEBUG] 识别为容器图片编辑');
    
    // 清空之前的容器图片列表
    v.containerImages = [];
    
    // 直接找到当前div内的所有图片
    const images = element.querySelectorAll('img');
    console.log('[DEBUG] 找到原始图片数量:', images.length);
    
    // 转为数组并过滤掉编辑器自身的图片
    v.containerImages = Array.from(images).filter(img => {
      // 检查图片是否属于编辑器元素
      const isEditorElement = img.closest('#elementInspector') || 
                            img.closest('#divEditorButtons') || 
                            img.closest('#imageUploadModal') ||
                            img.closest('.editor-button');
      return !isEditorElement;
    });
    
    console.log('[DEBUG] 过滤后的图片数量:', v.containerImages.length);
    
    if (v.containerImages.length === 0) {
      alert('所选区域内没有可替换的图片');
      return;
    }
    
    console.log(`[DEBUG] 发现区域内有 ${v.containerImages.length} 张图片可替换`);
  }
  
  // 显示上传模态框
  console.log('[DEBUG] 准备显示上传模态框');
  createImageUploadModal();
}

// 阻止链接点击事件函数
function preventLinkClick(e) {
  const v = window.editorVars;
  if (v.isImageEditMode) {
    e.preventDefault();
    e.stopPropagation();
    return false;
  }
}

// 创建图片上传模态框
function createImageUploadModal() {
  const v = window.editorVars;
  
  const modal = document.getElementById('imageUploadModal');
  const description = document.getElementById('imageUploadDescription');
  const uploadTypeToggle = document.getElementById('uploadTypeToggle');
  const singleFileInput = document.getElementById('imageFileInput');
  const multipleFileInput = document.getElementById('multipleImageFileInput');
  const imagePreview = document.getElementById('imagePreview');
  const multipleImagePreview = document.getElementById('multipleImagePreview');
  const cancelBtn = document.getElementById('cancelImageUpload');
  const applyBtn = document.getElementById('applyImageUpload');
  
  // 清空文件输入和预览
  singleFileInput.value = '';
  multipleFileInput.value = '';
  imagePreview.innerHTML = '';
  multipleImagePreview.innerHTML = '';
  v.selectedSingleFile = null;
  v.selectedMultipleFiles = null;
  
  // 移除之前的图片预览区域
  const oldDivPreview = document.getElementById('divImagesPreview');
  if (oldDivPreview) {
    oldDivPreview.remove();
  }
  
  // 移除之前的选择器
  const oldSelector = document.getElementById('carousel-image-selector');
  if (oldSelector) {
    oldSelector.remove();
  }
  
  // 根据编辑类型设置描述和显示/隐藏元素
  if (v.currentEditingType === 'single') {
    description.textContent = '选择一个图片文件上传替换当前图片。';
    uploadTypeToggle.style.display = 'none';
    singleFileInput.style.display = 'block';
    multipleFileInput.style.display = 'none';
    imagePreview.style.display = 'block';
    multipleImagePreview.style.display = 'none';
  } else if (v.currentEditingType === 'background') {
    description.textContent = '选择一个图片文件上传替换当前背景图片。';
    uploadTypeToggle.style.display = 'none';
    singleFileInput.style.display = 'block';
    multipleFileInput.style.display = 'none';
    imagePreview.style.display = 'block';
    multipleImagePreview.style.display = 'none';
  } else if (v.currentEditingType === 'carousel' || v.currentEditingType === 'container') {
    let containerType = v.currentEditingType === 'carousel' ? '轮播图' : '区域';
    let title = document.querySelector('.modal-title');
    title.textContent = `上传图片替换${containerType}内容`;
    
    description.textContent = `选择图片上传替换${containerType}中的图片（共有${v.containerImages.length}张图片）。`;
    uploadTypeToggle.style.display = 'block';
    
    // 验证containerImages是否正确
    console.log(`[DEBUG] 准备替换的图片数量: ${v.containerImages.length}`);
    
    // 默认选择多张上传模式，更符合批量替换的场景
    document.querySelector('input[name="uploadType"][value="multiple"]').checked = true;
    singleFileInput.style.display = 'none';
    multipleFileInput.style.display = 'block';
    imagePreview.style.display = 'none';
    multipleImagePreview.style.display = 'block';
    
    // 创建图片选择器 - 仅在单张模式下才需要
    createImageSelector(v.containerImages);
    
    // 显示div中的所有图片预览
    const divPreview = document.createElement('div');
    divPreview.id = 'divImagesPreview';
    divPreview.style.marginBottom = '15px';
    divPreview.style.border = '1px solid #ddd';
    divPreview.style.borderRadius = '4px';
    divPreview.style.padding = '10px';
    
    const previewTitle = document.createElement('h4');
    previewTitle.textContent = `${containerType}中的图片:`;
    previewTitle.style.margin = '0 0 10px 0';
    divPreview.appendChild(previewTitle);
    
    const imagesWrapper = document.createElement('div');
    imagesWrapper.style.display = 'flex';
    imagesWrapper.style.flexWrap = 'wrap';
    imagesWrapper.style.gap = '10px';
    
    v.containerImages.forEach((img, index) => {
      const imgContainer = document.createElement('div');
      imgContainer.style.textAlign = 'center';
      
      const imgEl = document.createElement('img');
      imgEl.src = img.src;
      imgEl.style.maxHeight = '80px';
      imgEl.style.maxWidth = '120px';
      imgEl.style.objectFit = 'contain';
      imgEl.style.border = '1px solid #eee';
      
      const imgLabel = document.createElement('div');
      imgLabel.textContent = `图片 ${index + 1}`;
      imgLabel.style.fontSize = '12px';
      imgLabel.style.marginTop = '5px';
      
      imgContainer.appendChild(imgEl);
      imgContainer.appendChild(imgLabel);
      imagesWrapper.appendChild(imgContainer);
    });
    
    divPreview.appendChild(imagesWrapper);
    
    // 在模态框的描述下方添加图片预览
    description.parentNode.insertBefore(divPreview, description.nextSibling);
  }
  
  // 显示模态框
  modal.style.display = 'flex';
  
  // 绑定事件
  cancelBtn.onclick = closeImageUploadModal;
  applyBtn.onclick = applyImageUpload;
  
  // 单个文件输入变化事件
  singleFileInput.onchange = function(e) {
    const file = e.target.files[0];
    if (file) {
      v.selectedSingleFile = file;
      
      const reader = new FileReader();
      reader.onload = function(e) {
        imagePreview.innerHTML = '';
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.maxHeight = '200px';
        img.style.marginBottom = '10px';
        imagePreview.appendChild(img);
        
        // 显示替换信息
        const info = document.createElement('p');
        
        if (v.currentEditingType === 'single' && v.currentEditingImage) {
          const originalSrc = v.currentEditingImage.src.split('/').pop();
          info.innerHTML = `将替换: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        } else if (v.currentEditingType === 'background') {
          const bgUrl = getBackgroundImageUrl(v.currentEditingElement);
          const originalSrc = bgUrl ? bgUrl.split('/').pop() : '背景图';
          info.innerHTML = `将替换背景图: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        } else if ((v.currentEditingType === 'carousel' || v.currentEditingType === 'container') && v.selectedImageIndex >= 0) {
          const originalImg = v.containerImages[v.selectedImageIndex];
          const originalSrc = originalImg.src.split('/').pop();
          info.innerHTML = `将替换第 ${v.selectedImageIndex + 1} 张图片: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        }
        
        imagePreview.appendChild(info);
      };
      
      reader.readAsDataURL(file);
    }
  };
  
  // 多个文件输入变化事件
  multipleFileInput.onchange = function(e) {
    const files = e.target.files;
    if (files && files.length > 0) {
      v.selectedMultipleFiles = files;
      
      multipleImagePreview.innerHTML = '';
      
      // 检查文件数量
      if (files.length > v.containerImages.length) {
        const warning = document.createElement('p');
        warning.style.color = 'red';
        warning.textContent = `警告: 您选择了${files.length}张图片，但${v.currentEditingType === 'carousel' ? '轮播图' : '区域'}中只有${v.containerImages.length}张图片。只有前${v.containerImages.length}张将被使用。`;
        multipleImagePreview.appendChild(warning);
      }
      
      // 显示替换预览
      const previewContainer = document.createElement('div');
      previewContainer.style.display = 'flex';
      previewContainer.style.flexDirection = 'column';
      previewContainer.style.gap = '15px';
      
      const maxToShow = Math.min(files.length, v.containerImages.length);
      
      // 添加标题
      const title = document.createElement('h4');
      title.textContent = '替换预览:';
      title.style.margin = '10px 0';
      previewContainer.appendChild(title);
      
      for (let i = 0; i < maxToShow; i++) {
        const file = files[i];
        const originalImg = v.containerImages[i];
        
        const itemContainer = document.createElement('div');
        itemContainer.style.width = '100%';
        itemContainer.style.padding = '10px';
        itemContainer.style.border = '1px solid #ddd';
        itemContainer.style.borderRadius = '4px';
        itemContainer.style.backgroundColor = '#f9f9f9';
        
        const originalSrc = originalImg.src.split('/').pop();
        
        const reader = new FileReader();
        reader.onload = (function(index, origSrc, f) {
          return function(e) {
            const content = `
              <div style="display: flex; align-items: center; gap: 15px;">
                <div style="flex: 1; text-align: center;">
                  <img src="${originalImg.src}" style="max-height: 100px; max-width: 100%; border: 1px solid #ddd;">
                  <p style="margin: 5px 0 0 0; font-size: 12px; font-weight: bold;">${origSrc}</p>
                </div>
                <div style="font-size: 24px; color: #4285f4;">→</div>
                <div style="flex: 1; text-align: center;">
                  <img src="${e.target.result}" style="max-height: 100px; max-width: 100%; border: 1px solid #ddd;">
                  <p style="margin: 5px 0 0 0; font-size: 12px; font-weight: bold;">${f.name}</p>
                </div>
              </div>
              <p style="margin: 10px 0 0 0; text-align: center; background-color: #e8f0fe; padding: 5px; border-radius: 4px;">
                替换第 ${index + 1} 张图片
              </p>
            `;
            
            itemContainer.innerHTML = content;
          };
        })(i, originalSrc, file);
        
        reader.readAsDataURL(file);
        previewContainer.appendChild(itemContainer);
      }
      
      multipleImagePreview.appendChild(previewContainer);
    }
  };
  
  // 上传类型切换
  const radioButtons = document.querySelectorAll('input[name="uploadType"]');
  radioButtons.forEach(radio => {
    radio.onchange = function() {
      if (this.value === 'single') {
        singleFileInput.style.display = 'block';
        multipleFileInput.style.display = 'none';
        imagePreview.style.display = 'block';
        multipleImagePreview.style.display = 'none';
        
        // 显示图片选择器
        const selector = document.getElementById('carousel-image-selector');
        if (selector) selector.style.display = 'block';
        
        // 清空已选文件
        multipleFileInput.value = '';
        multipleImagePreview.innerHTML = '';
        v.selectedMultipleFiles = null;
      } else {
        singleFileInput.style.display = 'none';
        multipleFileInput.style.display = 'block';
        imagePreview.style.display = 'none';
        multipleImagePreview.style.display = 'block';
        
        // 隐藏图片选择器
        const selector = document.getElementById('carousel-image-selector');
        if (selector) selector.style.display = 'none';
        
        // 清空已选文件
        singleFileInput.value = '';
        imagePreview.innerHTML = '';
        v.selectedSingleFile = null;
      }
    };
  });
  
  // 如果是多张上传模式，触发change事件以初始化界面
  if (v.currentEditingType === 'carousel' || v.currentEditingType === 'container') {
    document.querySelector('input[name="uploadType"]:checked').dispatchEvent(new Event('change'));
  }
}

// 创建轮播图选择器
function createImageSelector(images) {
  if (!images || images.length === 0) return;
  
  const v = window.editorVars;
  const imagePreview = document.getElementById('imagePreview');
  
  // 清空选择器
  const existingSelector = document.getElementById('carousel-image-selector');
  if (existingSelector) {
    existingSelector.remove();
  }
  
  // 创建选择器容器
  const selectorContainer = document.createElement('div');
  selectorContainer.id = 'carousel-image-selector';
  selectorContainer.style.marginBottom = '15px';
  
  // 添加标题
  const title = document.createElement('p');
  title.textContent = '选择要替换的图片:';
  selectorContainer.appendChild(title);
  
  // 创建图片选择区
  const selector = document.createElement('div');
  selector.style.display = 'flex';
  selector.style.flexWrap = 'wrap';
  selector.style.gap = '10px';
  
  // 添加图片选项
  images.forEach((img, index) => {
    const option = document.createElement('div');
    option.style.border = '2px solid transparent';
    option.style.padding = '5px';
    option.style.cursor = 'pointer';
    option.style.borderRadius = '4px';
    option.dataset.index = index;
    
    const thumbnail = document.createElement('img');
    thumbnail.src = img.src;
    thumbnail.style.height = '60px';
    thumbnail.style.maxWidth = '100px';
    thumbnail.style.objectFit = 'contain';
    
    const label = document.createElement('div');
    label.textContent = `图片 ${index + 1}`;
    label.style.fontSize = '12px';
    label.style.textAlign = 'center';
    label.style.marginTop = '5px';
    
    option.appendChild(thumbnail);
    option.appendChild(label);
    
    // 点击事件
    option.onclick = function() {
      // 移除所有选中样式
      selector.querySelectorAll('div[data-index]').forEach(el => {
        el.style.border = '2px solid transparent';
        el.style.backgroundColor = 'transparent';
      });
      
      // 设置选中样式
      this.style.border = '2px solid #4285f4';
      this.style.backgroundColor = 'rgba(66, 133, 244, 0.1)';
      
      // 保存选中的索引
      v.selectedImageIndex = parseInt(this.dataset.index);
      
      // 清空已选文件
      document.getElementById('imageFileInput').value = '';
      imagePreview.innerHTML = '';
      v.selectedSingleFile = null;
    };
    
    selector.appendChild(option);
  });
  
  // 添加选择器到容器
  selectorContainer.appendChild(selector);
  
  // 插入到模态框中
  const uploadTypeToggle = document.getElementById('uploadTypeToggle');
  uploadTypeToggle.parentNode.insertBefore(selectorContainer, uploadTypeToggle.nextSibling);
  
  // 默认选择第一张图片
  selector.querySelector('div[data-index="0"]').click();
}

// 关闭图片上传模态框
function closeImageUploadModal() {
  const modal = document.getElementById('imageUploadModal');
  if (modal) {
    modal.style.display = 'none';
  }
  
  // 清空临时变量
  const v = window.editorVars;
  v.selectedSingleFile = null;
  v.selectedMultipleFiles = null;
  
  // 移除选择器
  const selector = document.getElementById('carousel-image-selector');
  if (selector) {
    selector.remove();
  }
}

// 应用图片上传事件
function applyImageUpload() {
  const v = window.editorVars;
  const imageFileInput = document.getElementById('imageFileInput');
  const multipleImageFileInput = document.getElementById('multipleImageFileInput');
  
  // 获取选中的单选按钮
  const uploadType = document.querySelector('input[name="uploadType"]:checked')?.value || 'single';
  
  // 验证是否有选择文件
  if (uploadType === 'single') {
    // 使用v.selectedSingleFile而不是检查文件输入，因为我们已经在onchange中设置了它
    if (!v.selectedSingleFile) {
      alert('请选择图片');
      return;
    }
    
    const reader = new FileReader();
    
    reader.onload = function(e) {
      if (v.currentEditingType === 'single' && v.currentEditingImage) {
        // 保存原始图片路径
        const originalSrc = v.currentEditingImage.src;
        // 更新图片
        v.currentEditingImage.src = e.target.result;
        console.log(`已成功替换图片: ${originalSrc} -> ${v.selectedSingleFile.name}`);
        
        // 保存编辑的图片到本地存储
        saveEditedImage(originalSrc, v.selectedSingleFile);
      } else if (v.currentEditingType === 'background') {
        // 更新背景图
        v.currentEditingElement.style.backgroundImage = `url('${e.target.result}')`;
        
        // 保存编辑的背景图到本地存储
        const bgUrl = getBackgroundImageUrl(v.currentEditingElement);
        saveEditedImage(bgUrl, v.selectedSingleFile);
        
        console.log(`已成功替换背景图`);
      } else if ((v.currentEditingType === 'carousel' || v.currentEditingType === 'container') && v.selectedImageIndex >= 0) {
        // 保存原始图片路径
        const originalSrc = v.containerImages[v.selectedImageIndex].src;
        // 更新图片
        v.containerImages[v.selectedImageIndex].src = e.target.result;
        console.log(`已成功替换第 ${v.selectedImageIndex + 1} 张图片: ${originalSrc} -> ${v.selectedSingleFile.name}`);
        
        // 保存编辑的图片到本地存储
        saveEditedImage(originalSrc, v.selectedSingleFile);
      }
      
      // 关闭模态框
      closeImageUploadModal();
    };
    
    reader.readAsDataURL(v.selectedSingleFile);
    
  } else if (uploadType === 'multiple') {
    // 检查是否有选中的多个文件
    const files = multipleImageFileInput.files;
    
    if (!files || files.length === 0) {
      alert('请选择图片');
      return;
    }
    
    // 检查选择的图片数量是否与容器图片数量匹配
    if (files.length > v.containerImages.length) {
      alert(`您选择了${files.length}张图片，但${v.currentEditingType === 'carousel' ? '轮播图' : '区域'}中只有${v.containerImages.length}张图片，只会使用前${v.containerImages.length}张图片`);
    }
    
    // 处理多张图片上传
    let processedCount = 0;
    for (let i = 0; i < Math.min(files.length, v.containerImages.length); i++) {
      const file = files[i];
      const reader = new FileReader();
      
      reader.onload = (function(index) {
        return function(e) {
          // 保存原始图片路径
          const originalSrc = v.containerImages[index].src;
          // 更新图片
          v.containerImages[index].src = e.target.result;
          console.log(`已成功替换图片 ${index + 1}: ${originalSrc} -> ${files[index].name}`);
          
          // 保存编辑的图片到本地存储
          saveEditedImage(originalSrc, files[index]);
          
          processedCount++;
          // 如果所有图片都处理完毕，关闭模态框
          if (processedCount === Math.min(files.length, v.containerImages.length)) {
            closeImageUploadModal();
          }
        };
      })(i);
      
      reader.readAsDataURL(file);
    }
  }
}

// 获取背景图URL
function getBackgroundImageUrl(element) {
  if (!element) return null;
  
  const bgImage = window.getComputedStyle(element).backgroundImage;
  if (bgImage && bgImage !== 'none') {
    // 提取url中的实际链接
    const match = bgImage.match(/url\(['"]?(.*?)['"]?\)/);
    if (match && match[1]) {
      return match[1];
    }
  }
  
  return null;
}

// 初始化编辑器
document.addEventListener('DOMContentLoaded', function() {
  console.log('初始化编辑器...');
  initEditor();
});

function makeElementEditable(root) {
  console.log('[DEBUG] 使元素可编辑:', root ? root.tagName : 'null');
  
  if (!root) {
    console.error('[ERROR] 无法使空元素可编辑');
    return;
  }
  
  // 获取所有文本元素
  const textElements = root.querySelectorAll('p, h1, h2, h3, h4, h5, h6, span, div > strong, div > em, div > u, li, td, th, button, a');
  console.log('[DEBUG] 找到文本元素数量:', textElements.length);
  
  // 保存元素原始样式以便恢复
  const originalStyles = new Map();
  
  textElements.forEach(el => {
    // 排除已经是可编辑的元素或编辑器自身的元素
    if (el.contentEditable === 'true' || 
        el.classList.contains('editor-button') ||
        el.id === 'elementInspector' ||
        el.id === 'imageUploadModal' ||
        el.id === 'divEditorButtons' ||
        el.parentElement && (
          el.parentElement.id === 'elementInspector' ||
          el.parentElement.id === 'imageUploadModal' ||
          el.parentElement.id === 'divEditorButtons' ||
          el.parentElement.classList.contains('editor-button')
        )) {
      return;
    }
    
    // 检查元素是否包含实际文本内容（排除空白内容或只包含HTML元素的情况）
    const text = el.textContent.trim();
    if (!text) {
      return; // 跳过没有文本内容的元素
    }
    
    // 跳过包含大量子元素但自身文本内容很少的元素（可能是容器而非文本元素）
    if (el.children.length > 5 && el.childNodes.length > 10 && text.length < 20) {
      return;
    }
    
    // 跳过包含表单元素的元素
    if (el.querySelector('input, select, textarea, button')) {
      return;
    }
    
    try {
      // 确保元素是相对定位，以支持伪元素
      ensureRelativePosition(el);
      
      // 使元素可编辑，不修改其布局
      el.contentEditable = 'true';
      el.classList.add('text-editable');
      
      // 添加输入事件处理
      el.addEventListener('input', function() {
        // 保存编辑后的文本
        const v = window.editorVars;
        const path = getElementPath(this);
        v.editedTextElements[path] = this.innerHTML;
        localStorage.setItem('editedTexts', JSON.stringify(v.editedTextElements));
        
        // 更新页面修改时间
        savePageState();
      });
      
      // 添加焦点事件处理
      el.addEventListener('focus', function() {
        this.dataset.originalText = this.innerHTML;
      });
      
      el.addEventListener('blur', function() {
        // 如果文本已更改，记录更改
        if (this.dataset.originalText !== this.innerHTML) {
          console.log('[DEBUG] 文本已更改:', this.innerHTML);
        }
      });
    } catch (error) {
      console.error('[ERROR] 使元素可编辑失败:', error);
    }
  });
  
  // 保存原始样式以便稍后恢复
  window.editorVars.originalTextStyles = originalStyles;
  
  console.log('[DEBUG] 文本编辑已启用');
}

// 移除文本编辑功能
function removeTextEditability() {
  console.log('[DEBUG] 移除文本编辑功能');
  
  // 获取所有可编辑的文本元素（包括可能遗漏的元素）
  const editableElements = document.querySelectorAll('[contenteditable="true"], .text-editable');
  console.log('[DEBUG] 找到可编辑文本元素数量:', editableElements.length);
  
  editableElements.forEach(el => {
    try {
      // 移除可编辑属性
      el.contentEditable = 'false';
      el.classList.remove('text-editable');
      
      // 清除所有样式修改
      el.style.outline = '';
      el.style.border = '';
      el.style.padding = '';
      el.style.margin = '';
      el.style.cursor = '';
      el.style.backgroundColor = '';
      
      // 移除所有事件监听器
      const clone = el.cloneNode(true);
      if (el.parentNode) {
        el.parentNode.replaceChild(clone, el);
      }
      
      // 确保克隆后的元素也不是可编辑的
      clone.contentEditable = 'false';
      clone.removeAttribute('contenteditable');
    } catch (error) {
      console.error('[ERROR] 移除文本编辑功能失败:', error);
    }
  });
  
  // 强制全局清除
  document.querySelectorAll('[contenteditable], [style*="outline"], [style*="border"]').forEach(el => {
    // 排除编辑器自身的元素
    if (el.id === 'elementInspector' || 
        el.classList.contains('editor-button') ||
        el.id === 'imageUploadModal' ||
        el.id === 'divEditorButtons' ||
        el.closest('#imageUploadModal')) {
      return;
    }
    
    el.removeAttribute('contenteditable');
    el.contentEditable = 'false';
    
    // 检查并清除可能影响布局的样式
    if (el.getAttribute('style') && 
        (el.getAttribute('style').includes('outline') || 
         el.getAttribute('style').includes('border') || 
         el.getAttribute('style').includes('margin') || 
         el.getAttribute('style').includes('padding'))) {
      el.style.outline = '';
      el.style.border = '';
      el.style.padding = '';
      el.style.margin = '';
    }
  });
  
  console.log('[DEBUG] 文本编辑功能已移除');
}

// 应用保存的文本编辑
function applyTextEdits() {
  const v = window.editorVars;
  console.log('[DEBUG] 应用保存的文本编辑');
  
  try {
    // 遍历所有保存的文本编辑
    for (const path in v.editedTextElements) {
      try {
        // 查找元素
        const elements = document.querySelectorAll(path);
        if (elements && elements.length > 0) {
          // 更新第一个匹配的元素的内容
          elements[0].innerHTML = v.editedTextElements[path];
          console.log('[DEBUG] 已更新文本元素:', path);
        } else {
          console.warn('[WARN] 找不到路径对应的元素:', path);
        }
      } catch (error) {
        console.error('[ERROR] 应用文本编辑失败:', error, path);
      }
    }
  } catch (error) {
    console.error('[ERROR] 应用保存的文本编辑失败:', error);
  }
}

// 处理元素点击事件
function handleElementClick(e) {
  const v = window.editorVars;
  console.log('[DEBUG] 处理元素点击事件');
  
  if (!v.isEditMode) {
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
      
      // 保存页面修改状态
      savePageState();
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
      
      // 保存页面修改状态
      savePageState();
    }
  } catch (error) {
    console.error('[ERROR] 移除元素失败:', error);
  }
}

// 应用页面修改
function applyPageModifications() {
  // 实现保存的页面修改逻辑
  console.log('[DEBUG] 应用页面修改');
}

// 使所有图片可编辑
function makeImagesEditable() {
  console.log('[DEBUG] 使所有图片可编辑');
  
  // 清除之前的事件监听器
  document.querySelectorAll('.image-editable').forEach(img => {
    img.removeEventListener('click', handleImageEditClick);
    img.classList.remove('image-editable');
  });
  
  document.querySelectorAll('.bg-image-editable').forEach(el => {
    el.removeEventListener('click', handleImageEditClick);
    el.classList.remove('bg-image-editable');
    el.removeAttribute('data-bg-editable');
  });
  
  document.querySelectorAll('div').forEach(div => {
    div.removeEventListener('click', handleImageEditClick);
  });
  
  // 处理普通图片
  let imageCount = 0;
  document.querySelectorAll('img').forEach(img => {
    // 排除编辑器元素的图片
    if (img.closest('#elementInspector') || 
        img.closest('#divEditorButtons') || 
        img.closest('#imageUploadModal') ||
        img.closest('.editor-button')) {
      return;
    }
    
    // 确保图片父元素是相对定位，以支持伪元素
    if (img.parentElement) {
      ensureRelativePosition(img.parentElement);
    }
    
    // 仅添加类和事件监听器，不修改直接样式
    img.classList.add('image-editable');
    img.addEventListener('click', handleImageEditClick);
    imageCount++;
  });
  
  console.log(`[DEBUG] 添加了 ${imageCount} 张可编辑图片`);
  
  // 处理背景图片
  let bgImageCount = 0;
  document.querySelectorAll('*').forEach(el => {
    // 排除已处理的元素和编辑器元素
    if (el.classList.contains('bg-image-editable') || 
        el.id === 'elementInspector' || 
        el.id === 'divEditorButtons' ||
        el.classList.contains('element-highlight') ||
        el.classList.contains('editor-button') ||
        el.closest('#imageUploadModal')) {
      return;
    }
    
    const style = window.getComputedStyle(el);
    const bgImage = style.backgroundImage;
    
    if (bgImage && bgImage !== 'none' && !bgImage.includes('gradient')) {
      // 确保元素是相对定位，以支持伪元素
      ensureRelativePosition(el);
      
      el.classList.add('bg-image-editable');
      el.setAttribute('data-bg-editable', 'true');
      el.addEventListener('click', handleImageEditClick);
      bgImageCount++;
    }
  });
  
  console.log(`[DEBUG] 添加了 ${bgImageCount} 个可编辑背景`);
  
  // 处理轮播图容器
  const carouselContainers = [];
  
  // 查找可能的轮播图容器
  document.querySelectorAll('.carousel, .swiper, .slider, [id*="carousel"], [id*="slider"], [class*="carousel"], [class*="slider"]').forEach(container => {
    // 排除编辑器元素
    if (container.closest('#elementInspector') || 
        container.closest('#divEditorButtons') || 
        container.closest('#imageUploadModal') ||
        container.classList.contains('editor-button')) {
      return;
    }
    
    if (container.querySelectorAll('img').length > 1) {
      carouselContainers.push(container);
    }
  });
  
  console.log(`[DEBUG] 找到 ${carouselContainers.length} 个轮播图`);
  
  // 标记轮播图容器
  carouselContainers.forEach(container => {
    container.classList.add('carousel-container-editable');
    container.setAttribute('data-carousel-editable', 'true');
    container.addEventListener('click', handleImageEditClick);
    
    // 添加提示标记
    if (!container.querySelector('[data-carousel-hint]')) {
      const hint = document.createElement('div');
      hint.setAttribute('data-carousel-hint', 'true');
      hint.style.position = 'absolute';
      hint.style.top = '5px';
      hint.style.right = '5px';
      hint.style.backgroundColor = 'rgba(66, 133, 244, 0.8)';
      hint.style.color = 'white';
      hint.style.padding = '2px 5px';
      hint.style.borderRadius = '3px';
      hint.style.fontSize = '12px';
      hint.style.zIndex = '1000';
      hint.textContent = '轮播图 - 点击编辑';
      
      // 如果容器是相对定位，直接添加提示；否则，先设置相对定位
      const containerStyle = window.getComputedStyle(container);
      if (containerStyle.position === 'static') {
        container.style.position = 'relative';
      }
      
      container.appendChild(hint);
    }
  });
  
  // 处理包含图片的div容器 - 添加可点击编辑功能
  let divWithImagesCount = 0;
  document.querySelectorAll('div').forEach(div => {
    // 排除已处理的元素和编辑器元素
    if (div.id === 'elementInspector' || 
        div.id === 'divEditorButtons' ||
        div.classList.contains('element-highlight') ||
        div.classList.contains('editor-button') ||
        div.id === 'imageUploadModal' ||
        div.closest('#imageUploadModal')) {
      return;
    }
    
    // 检查div是否包含图片
    const images = div.querySelectorAll('img');
    if (images.length === 0) {
      return; // 没有图片的div直接跳过
    }
    
    // 过滤出非编辑器的图片
    const validImages = Array.from(images).filter(img => {
      return !(img.closest('#elementInspector') || 
              img.closest('#divEditorButtons') || 
              img.closest('#imageUploadModal') ||
              img.closest('.editor-button'));
    });
    
    if (validImages.length > 0) {
      // 加上特殊标记类，方便调试
      div.classList.add('div-image-container');
      div.setAttribute('data-images-count', validImages.length);
      
      // 直接使用简单的点击处理函数
      div.addEventListener('click', function(e) {
        console.log('[DEBUG] div点击事件触发', this.tagName, '包含图片数:', validImages.length);
        // 防止冒泡
        e.stopPropagation();
        // 调用处理函数
        handleImageEditClick.call(this, e);
      });
      
      divWithImagesCount++;
    }
  });
  
  console.log(`[DEBUG] 添加了 ${divWithImagesCount} 个包含图片的div`);
  
  // 处理包含多个图片的链接容器
  document.querySelectorAll('a').forEach(link => {
    const images = link.querySelectorAll('img');
    if (images.length > 0) {
      link.setAttribute('data-image-editable-container', 'true');
    }
  });
  
  console.log('[DEBUG] 图片编辑已启用');
}

// 保存编辑的图片到本地存储
function saveEditedImage(originalSrc, file) {
  const v = window.editorVars;
  
  try {
    // 读取文件为DataURL
    const reader = new FileReader();
    reader.onload = function(e) {
      const dataUrl = e.target.result;
      
      // 根据编辑类型保存到不同的存储对象
      if (v.currentEditingType === 'single') {
        v.editedImages[originalSrc] = dataUrl;
        localStorage.setItem('editedImages', JSON.stringify(v.editedImages));
      } else if (v.currentEditingType === 'background') {
        v.editedBackgroundImages[originalSrc] = dataUrl;
        localStorage.setItem('editedBackgroundImages', JSON.stringify(v.editedBackgroundImages));
      } else if (v.currentEditingType === 'carousel' || v.currentEditingType === 'container') {
        v.editedCarouselImages[originalSrc] = dataUrl;
        localStorage.setItem('editedCarouselImages', JSON.stringify(v.editedCarouselImages));
      }
      
      // 更新页面修改时间
      savePageState();
      
      console.log('[DEBUG] 图片编辑已保存:', originalSrc);
    };
    
    reader.readAsDataURL(file);
  } catch (error) {
    console.error('[ERROR] 保存编辑的图片失败:', error);
  }
}

// 应用图片编辑
function applyImageEdits() {
  const v = window.editorVars;
  console.log('[DEBUG] 应用保存的图片编辑');
  
  try {
    // 应用普通图片编辑
    for (const originalSrc in v.editedImages) {
      document.querySelectorAll(`img[src="${originalSrc}"]`).forEach(img => {
        img.src = v.editedImages[originalSrc];
      });
    }
    
    // 应用背景图片编辑
    for (const originalSrc in v.editedBackgroundImages) {
      document.querySelectorAll('*').forEach(el => {
        const style = window.getComputedStyle(el);
        const bgImage = style.backgroundImage;
        
        if (bgImage && bgImage.includes(originalSrc)) {
          el.style.backgroundImage = `url('${v.editedBackgroundImages[originalSrc]}')`;
        }
      });
    }
    
    // 应用轮播图/容器图片编辑
    for (const originalSrc in v.editedCarouselImages) {
      document.querySelectorAll(`img[src="${originalSrc}"]`).forEach(img => {
        img.src = v.editedCarouselImages[originalSrc];
      });
    }
    
    console.log('[DEBUG] 图片编辑已应用');
  } catch (error) {
    console.error('[ERROR] 应用图片编辑失败:', error);
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

// 处理图片编辑模式下的鼠标移动事件
function handleImageEditMouseMove(e) {
  const v = window.editorVars;
  
  if (!v.isImageEditMode) {
    return;
  }
  
  const element = document.elementFromPoint(e.clientX, e.clientY);
  
  // 忽略编辑器自身的元素
  if (element && (
      element.id === 'elementInspector' || 
      element.id === 'divEditorButtons' || 
      element.classList.contains('element-highlight') ||
      element.classList.contains('editor-button') ||
      element === document.getElementById('editDuplicateBtn') ||
      element === document.getElementById('editRemoveBtn') ||
      element.closest('#imageUploadModal'))) {
    hideHoverHighlight();
    return;
  }
  
  // 查找最近的div元素
  let targetDiv = element;
  while (targetDiv && targetDiv.tagName.toLowerCase() !== 'div' && targetDiv !== document.body) {
    targetDiv = targetDiv.parentElement;
  }
  
  if (!targetDiv || targetDiv === document.body) {
    hideHoverHighlight();
    return;
  }
  
  // 检查div是否包含图片（排除编辑器元素的图片）
  const images = targetDiv.querySelectorAll('img');
  let containsImages = false;
  
  for (const img of images) {
    // 检查图片是否属于编辑器元素
    const isEditorElement = img.closest('#elementInspector') || 
                           img.closest('#divEditorButtons') || 
                           img.closest('#imageUploadModal') ||
                           img.closest('.editor-button');
    if (!isEditorElement) {
      containsImages = true;
      break;
    }
  }
  
  if (!containsImages) {
    hideHoverHighlight();
    return;
  }
  
  // 更新当前悬停元素
  v.hoverElement = targetDiv;
  
  // 特殊标记，标明此div可编辑图片
  if (!targetDiv.classList.contains('div-hover-highlight')) {
    targetDiv.classList.add('div-hover-highlight');
    targetDiv.style.cursor = 'pointer';
  }
  
  // 显示高亮
  highlightHoverElement(v.hoverElement);
}

// 全局清理函数 - 确保退出所有编辑模式后没有样式残留
function clearAllEditModes() {
  console.log('[DEBUG] 清理所有编辑模式样式残留');
  
  // 清除所有可能的高亮和样式改变
  document.querySelectorAll('*').forEach(el => {
    // 排除编辑器自身的元素
    if (el.id === 'elementInspector' || 
        el.classList.contains('editor-button') ||
        el.id === 'imageUploadModal' ||
        el.id === 'divEditorButtons' ||
        el.closest('#imageUploadModal')) {
      return;
    }
    
    // 移除可能的类
    if (el.classList.contains('text-editable')) el.classList.remove('text-editable');
    if (el.classList.contains('image-editable')) el.classList.remove('image-editable');
    if (el.classList.contains('bg-image-editable')) el.classList.remove('bg-image-editable');
    if (el.classList.contains('carousel-container-editable')) el.classList.remove('carousel-container-editable');
    if (el.classList.contains('div-selected')) el.classList.remove('div-selected');
    if (el.classList.contains('div-image-container')) el.classList.remove('div-image-container');
    if (el.classList.contains('div-hover-highlight')) el.classList.remove('div-hover-highlight');
    
    // 移除可能的属性
    if (el.getAttribute('contenteditable')) el.removeAttribute('contenteditable');
    if (el.getAttribute('data-bg-editable')) el.removeAttribute('data-bg-editable');
    if (el.getAttribute('data-carousel-editable')) el.removeAttribute('data-carousel-editable');
    if (el.getAttribute('data-container-editable')) el.removeAttribute('data-container-editable');
    if (el.getAttribute('data-images-count')) el.removeAttribute('data-images-count');
    
    // 清除可能的内联样式
    if (el.style) {
      if (el.style.outline) el.style.outline = '';
      if (el.style.border) el.style.border = '';
      if (el.style.boxShadow) el.style.boxShadow = '';
      if (el.style.backgroundColor && el.style.backgroundColor.includes('rgba(')) el.style.backgroundColor = '';
    }
  });
  
  // 隐藏所有编辑器UI
  hideEditorButtons();
  hideInspector();
  hideHighlight();
  hideHoverHighlight();
  
  // 关闭模态框
  closeImageUploadModal();
  
  console.log('[DEBUG] 所有编辑模式样式已清理');
}

// 切换文本编辑模式
buttons.textEditBtn.addEventListener('click', function() {
  // 清除可能的旧事件处理程序
  document.removeEventListener('mousemove', handleInspectorMouseMove);
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mousemove', handleImageEditMouseMove);
  
  // 清理所有样式残留
  clearAllEditModes();
  
  // 如果其他模式已开启，先关闭
  if (v.isImageEditMode) {
    v.isImageEditMode = false;
    completelyRemoveImageEditability();
    buttons.imageEditBtn.innerText = '启用图片编辑';
    buttons.imageEditBtn.style.backgroundColor = '#4285f4';
    buttons.imageEditBtn.style.color = '#fff';
  }
  
  if (v.isInspecting) {
    v.isInspecting = false;
    hideInspector();
    hideHighlight();
    buttons.inspectBtn.innerText = '启用元素检查';
    buttons.inspectBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isEditMode) {
    v.isEditMode = false;
    removeEditModeFromDivs();
    buttons.editBtn.innerText = '启用区域编辑模式';
    buttons.editBtn.style.backgroundColor = '#4285f4';
  }
  
  v.isTextEditMode = !v.isTextEditMode;
  
  if (v.isTextEditMode) {
    // 启用文本编辑模式
    this.innerText = '禁用文本编辑';
    this.style.backgroundColor = '#34a853';
    
    // 使所有文本元素可编辑
    makeElementEditable(document.body);
  } else {
    // 禁用文本编辑模式
    this.innerText = '启用文本编辑';
    this.style.backgroundColor = '#4285f4';
    
    // 移除可编辑属性
    removeTextEditability();
  }
});

// 切换区域编辑模式
buttons.editBtn.addEventListener('click', function(e) {
  console.log('[DEBUG] 区域编辑按钮被点击', e.type);
  console.log('[DEBUG] 点击前状态:', { 
    isEditMode: v.isEditMode,
    isInspecting: v.isInspecting, 
    isTextEditMode: v.isTextEditMode,
    isImageEditMode: v.isImageEditMode
  });
  
  // 清除可能的旧事件处理程序
  document.removeEventListener('mousemove', handleInspectorMouseMove);
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mousemove', handleImageEditMouseMove);
  
  // 清理所有样式残留
  clearAllEditModes();
  
  // 如果其他模式已开启，先关闭
  if (v.isInspecting) {
    console.log('[DEBUG] 关闭元素检查模式');
    v.isInspecting = false;
    hideInspector();
    hideHighlight();
    buttons.inspectBtn.innerText = '启用元素检查';
    buttons.inspectBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isTextEditMode) {
    console.log('[DEBUG] 关闭文本编辑模式');
    v.isTextEditMode = false;
    removeTextEditability();
    buttons.textEditBtn.innerText = '启用文本编辑';
    buttons.textEditBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isImageEditMode) {
    console.log('[DEBUG] 关闭图片编辑模式');
    v.isImageEditMode = false;
    completelyRemoveImageEditability();
    buttons.imageEditBtn.innerText = '启用图片编辑';
    buttons.imageEditBtn.style.backgroundColor = '#4285f4';
    buttons.imageEditBtn.style.color = '#fff';
  }
  
  // 切换区域编辑状态
  v.isEditMode = !v.isEditMode;
  console.log('[DEBUG] 区域编辑模式切换为:', v.isEditMode);
  
  if (v.isEditMode) {
    console.log('[DEBUG] 启用区域编辑模式');
    this.innerText = '禁用区域编辑模式';
    this.style.backgroundColor = '#ea4335';
    
    try {
      // 应用区域编辑模式
      console.log('[DEBUG] 尝试应用区域编辑模式');
      applyEditModeToDivs();
      console.log('[DEBUG] 区域编辑模式应用成功');
      
      // 绑定鼠标移动事件处理程序
      console.log('[DEBUG] 尝试绑定鼠标移动事件');
      document.addEventListener('mousemove', handleMouseMove);
      console.log('[DEBUG] 鼠标移动事件绑定成功');
    } catch (error) {
      console.error('[ERROR] 应用区域编辑模式失败:', error);
    }
  } else {
    console.log('[DEBUG] 禁用区域编辑模式');
    this.innerText = '启用区域编辑模式';
    this.style.backgroundColor = '#4285f4';
    
    try {
      // 移除区域编辑模式
      console.log('[DEBUG] 尝试移除区域编辑模式');
      removeEditModeFromDivs();
      console.log('[DEBUG] 区域编辑模式移除成功');
      
      // 解绑鼠标移动事件处理程序
      document.removeEventListener('mousemove', handleMouseMove);
      console.log('[DEBUG] 鼠标移动事件解绑成功');
    } catch (error) {
      console.error('[ERROR] 移除区域编辑模式失败:', error);
    }
  }
  console.log('[DEBUG] 区域编辑模式切换完成');
});

// 切换图片编辑模式
buttons.imageEditBtn.addEventListener('click', function() {
  // 清除可能的旧事件处理程序
  document.removeEventListener('mousemove', handleInspectorMouseMove);
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mousemove', handleImageEditMouseMove);
  
  // 清理所有样式残留
  clearAllEditModes();
  
  // 如果其他模式已开启，先关闭
  if (v.isTextEditMode) {
    v.isTextEditMode = false;
    removeTextEditability();
    buttons.textEditBtn.innerText = '启用文本编辑';
    buttons.textEditBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isInspecting) {
    v.isInspecting = false;
    hideInspector();
    hideHighlight();
    buttons.inspectBtn.innerText = '启用元素检查';
    buttons.inspectBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isEditMode) {
    v.isEditMode = false;
    removeEditModeFromDivs();
    buttons.editBtn.innerText = '启用区域编辑模式';
    buttons.editBtn.style.backgroundColor = '#4285f4';
  }
  
  v.isImageEditMode = !v.isImageEditMode;
  
  if (v.isImageEditMode) {
    // 启用图片编辑模式
    this.innerText = '禁用图片编辑';
    this.style.backgroundColor = '#fbbc05';
    this.style.color = '#000';
    
    console.log('[DEBUG] 正在启用图片编辑模式...');
    
    // 使所有图片元素可编辑
    makeImagesEditable();
    
    // 阻止链接点击事件
    document.querySelectorAll('a[data-image-editable-container="true"]').forEach(link => {
      link.addEventListener('click', preventLinkClick);
    });
    
    // 显示容器编辑图标
    document.querySelectorAll('[data-container-editable="true"] .container-edit-icon').forEach(icon => {
      if (icon) {
        icon.style.display = 'block';
      }
    });
    
    // 添加鼠标移动事件来高亮div
    document.addEventListener('mousemove', handleImageEditMouseMove);
    
    console.log('[DEBUG] 图片编辑模式已启用，可以点击div或图片');
  } else {
    // 禁用图片编辑模式
    this.innerText = '启用图片编辑';
    this.style.backgroundColor = '#4285f4';
    this.style.color = '#fff';
    
    // 使用增强的清理函数
    completelyRemoveImageEditability();
    
    // 恢复链接点击行为
    document.querySelectorAll('a[data-image-editable-container="true"]').forEach(link => {
      link.removeEventListener('click', preventLinkClick);
      link.removeAttribute('data-image-editable-container');
    });
    
    // 移除鼠标移动事件监听
    document.removeEventListener('mousemove', handleImageEditMouseMove);
    
    // 隐藏高亮
    hideHoverHighlight();
    
    // 移除所有div-hover-highlight类
    document.querySelectorAll('.div-hover-highlight').forEach(div => {
      div.classList.remove('div-hover-highlight');
      div.style.cursor = '';
    });
    
    // 移除所有div-image-container类
    document.querySelectorAll('.div-image-container').forEach(div => {
      div.classList.remove('div-image-container');
      div.removeAttribute('data-images-count');
    });
  }
});

// 切换元素检查模式
buttons.inspectBtn.addEventListener('click', function(e) {
  console.log('[DEBUG] 元素检查按钮被点击', e.type);
  console.log('[DEBUG] 点击前状态:', { 
    isInspecting: v.isInspecting,
    isTextEditMode: v.isTextEditMode,
    isImageEditMode: v.isImageEditMode,
    isEditMode: v.isEditMode
  });
  
  // 清除可能的旧事件处理程序
  document.removeEventListener('mousemove', handleInspectorMouseMove);
  document.removeEventListener('mousemove', handleMouseMove);
  document.removeEventListener('mousemove', handleImageEditMouseMove);
  
  // 清理所有样式残留
  clearAllEditModes();
  
  // 如果其他模式已开启，先关闭
  if (v.isTextEditMode) {
    console.log('[DEBUG] 关闭文本编辑模式');
    v.isTextEditMode = false;
    removeTextEditability();
    buttons.textEditBtn.innerText = '启用文本编辑';
    buttons.textEditBtn.style.backgroundColor = '#4285f4';
  }
  
  if (v.isImageEditMode) {
    console.log('[DEBUG] 关闭图片编辑模式');
    v.isImageEditMode = false;
    completelyRemoveImageEditability();
    buttons.imageEditBtn.innerText = '启用图片编辑';
    buttons.imageEditBtn.style.backgroundColor = '#4285f4';
    buttons.imageEditBtn.style.color = '#fff';
  }
  
  if (v.isEditMode) {
    console.log('[DEBUG] 关闭区域编辑模式');
    v.isEditMode = false;
    removeEditModeFromDivs();
    buttons.editBtn.innerText = '启用区域编辑模式';
    buttons.editBtn.style.backgroundColor = '#4285f4';
  }
  
  // 切换检查模式状态
  v.isInspecting = !v.isInspecting;
  console.log('[DEBUG] 检查模式切换为:', v.isInspecting);
  
  if (v.isInspecting) {
    console.log('[DEBUG] 启用元素检查');
    this.innerText = '禁用元素检查';
    this.style.backgroundColor = '#ea4335';
    
    try {
      // 绑定鼠标移动事件处理程序
      console.log('[DEBUG] 尝试绑定检查器鼠标移动事件');
      document.addEventListener('mousemove', handleInspectorMouseMove);
      console.log('[DEBUG] 检查器鼠标移动事件绑定成功');
    } catch (error) {
      console.error('[ERROR] 绑定检查器鼠标移动事件失败:', error);
    }
  } else {
    console.log('[DEBUG] 禁用元素检查');
    this.innerText = '启用元素检查';
    this.style.backgroundColor = '#4285f4';
    
    try {
      // 隐藏检查器和高亮
      console.log('[DEBUG] 尝试隐藏检查器和高亮');
      hideInspector();
      hideHighlight();
      console.log('[DEBUG] 检查器和高亮隐藏成功');
      
      // 解绑鼠标移动事件处理程序
      document.removeEventListener('mousemove', handleInspectorMouseMove);
      console.log('[DEBUG] 检查器鼠标移动事件解绑成功');
    } catch (error) {
      console.error('[ERROR] 隐藏检查器或解绑事件失败:', error);
    }
  }
  console.log('[DEBUG] 元素检查模式切换完成');
});

// 确保图片元素相对定位，以支持伪元素
function ensureRelativePosition(element) {
  // 获取当前computed样式
  const computedStyle = window.getComputedStyle(element);
  
  // 只有当元素不是relative、absolute或fixed时才设置relative
  if (computedStyle.position === 'static') {
    element.style.position = 'relative';
  }
}

// 图片上传模态框代码
function setupImageUploadModal() {
  const modal = document.createElement('div');
  modal.id = 'imageUploadModal';
  
  modal.innerHTML = `
    <div class="modal-content">
      <h3 class="modal-title">上传图片</h3>
      
      <div id="imageUploadSelection">
        <label>
          <input type="radio" name="uploadType" value="single" checked> 替换单张图片
        </label>
        <label>
          <input type="radio" name="uploadType" value="multiple"> 批量替换多张图片
        </label>
      </div>
      
      <div id="singleUploadSection">
        <input type="file" id="imageFileInput" accept="image/*">
      </div>
      
      <div id="multipleUploadSection" style="display: none;">
        <input type="file" id="multipleImageFileInput" accept="image/*" multiple>
      </div>
      
      <div id="imageList" style="margin-top: 15px; max-height: 200px; overflow-y: auto;"></div>
      
      <div id="imagePreview"></div>
      
      <div class="modal-buttons">
        <button id="cancelImageUpload" class="modal-button">取消</button>
        <button id="applyImageUpload" class="modal-button">应用</button>
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  
  // 获取元素引用
  const singleUploadSection = document.getElementById('singleUploadSection');
  const multipleUploadSection = document.getElementById('multipleUploadSection');
  const uploadTypeRadios = document.querySelectorAll('input[name="uploadType"]');
  const singleFileInput = document.getElementById('imageFileInput');
  const multipleFileInput = document.getElementById('multipleImageFileInput');
  const imagePreview = document.getElementById('imagePreview');
  const imageList = document.getElementById('imageList');
  const cancelButton = document.getElementById('cancelImageUpload');
  const applyButton = document.getElementById('applyImageUpload');
  
  console.log('[DEBUG] 图片上传模态框设置完成');
  console.log('[DEBUG] 单文件输入元素:', singleFileInput ? 'OK' : 'NOT FOUND');
  console.log('[DEBUG] 多文件输入元素:', multipleFileInput ? 'OK' : 'NOT FOUND');
  
  // 切换上传类型
  uploadTypeRadios.forEach(radio => {
    radio.addEventListener('change', function() {
      console.log('[DEBUG] 切换上传类型:', this.value);
      if (this.value === 'single') {
        singleUploadSection.style.display = 'block';
        multipleUploadSection.style.display = 'none';
      } else {
        singleUploadSection.style.display = 'none';
        multipleUploadSection.style.display = 'block';
      }
    });
  });
  
  // 单个文件输入变化事件 - 完全重写
  singleFileInput.addEventListener('change', function(e) {
    console.log('[DEBUG] 单文件输入变化, 文件数量:', e.target.files.length);
    
    const file = e.target.files[0];
    if (file) {
      console.log('[DEBUG] 已选择文件:', file.name, file.type, file.size);
      
      // 显式设置全局变量
      window.editorVars.selectedSingleFile = file;
      console.log('[DEBUG] 已设置 selectedSingleFile:', file.name);
      
      // 创建预览
      const reader = new FileReader();
      reader.onload = function(e) {
        console.log('[DEBUG] 文件读取完成');
        imagePreview.innerHTML = '';
        
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.maxHeight = '200px';
        img.style.marginBottom = '10px';
        imagePreview.appendChild(img);
        
        // 显示替换信息
        const info = document.createElement('p');
        const v = window.editorVars;
        
        if (v.currentEditingType === 'single' && v.currentEditingImage) {
          const originalSrc = v.currentEditingImage.src.split('/').pop();
          info.innerHTML = `将替换: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        } else if (v.currentEditingType === 'background') {
          const bgUrl = getBackgroundImageUrl(v.currentEditingElement);
          const originalSrc = bgUrl ? bgUrl.split('/').pop() : '背景图';
          info.innerHTML = `将替换背景图: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        } else if ((v.currentEditingType === 'carousel' || v.currentEditingType === 'container') && v.selectedImageIndex >= 0) {
          const originalImg = v.containerImages[v.selectedImageIndex];
          const originalSrc = originalImg.src.split('/').pop();
          info.innerHTML = `将替换第 ${v.selectedImageIndex + 1} 张图片: <strong>${originalSrc}</strong> → <strong>${file.name}</strong>`;
        }
        
        imagePreview.appendChild(info);
      };
      
      reader.readAsDataURL(file);
    } else {
      console.log('[DEBUG] 没有选择文件');
      imagePreview.innerHTML = '';
      window.editorVars.selectedSingleFile = null;
    }
  });
  
  // 多个文件输入变化事件
  multipleFileInput.addEventListener('change', function(e) {
    console.log('[DEBUG] 多文件输入变化, 文件数量:', e.target.files.length);
    
    const files = e.target.files;
    if (files && files.length > 0) {
      imagePreview.innerHTML = '';
      
      // 显示预览
      const previewContainer = document.createElement('div');
      previewContainer.style.display = 'flex';
      previewContainer.style.flexWrap = 'wrap';
      previewContainer.style.gap = '10px';
      
      for (let i = 0; i < Math.min(files.length, 5); i++) {
        const file = files[i];
        const reader = new FileReader();
        
        reader.onload = (function(file, index) {
          return function(e) {
            const imgContainer = document.createElement('div');
            imgContainer.style.textAlign = 'center';
            
            const img = document.createElement('img');
            img.src = e.target.result;
            img.style.maxHeight = '100px';
            img.style.marginBottom = '5px';
            
            const label = document.createElement('div');
            label.textContent = file.name.length > 15 ? file.name.substring(0, 12) + '...' : file.name;
            label.style.fontSize = '12px';
            
            imgContainer.appendChild(img);
            imgContainer.appendChild(label);
            previewContainer.appendChild(imgContainer);
          };
        })(file, i);
        
        reader.readAsDataURL(file);
      }
      
      imagePreview.appendChild(previewContainer);
      
      if (files.length > 5) {
        const moreInfo = document.createElement('p');
        moreInfo.textContent = `还有 ${files.length - 5} 张图片未显示预览`;
        imagePreview.appendChild(moreInfo);
      }
    } else {
      imagePreview.innerHTML = '';
    }
  });
  
  // 取消按钮
  cancelButton.addEventListener('click', function() {
    console.log('[DEBUG] 取消图片上传');
    closeImageUploadModal();
  });
  
  // 应用按钮
  applyButton.addEventListener('click', function() {
    console.log('[DEBUG] 应用图片上传');
    applyImageUpload();
  });
  
  // 点击模态框背景关闭
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      console.log('[DEBUG] 点击背景关闭模态框');
      closeImageUploadModal();
    }
  });
  
  return modal;
}

// 显示图片上传模态框
function showImageUploadModal(type, element, index) {
  console.log('[DEBUG] 显示图片上传模态框:', type, element, index);
  
  const v = window.editorVars;
  
  // 重置模态框状态
  v.currentEditingType = type;
  v.currentEditingElement = element;
  v.currentEditingImage = type === 'single' ? element : null;
  v.selectedImageIndex = index;
  v.selectedSingleFile = null;
  
  // 创建模态框（如果不存在）
  let modal = document.getElementById('imageUploadModal');
  if (!modal) {
    console.log('[DEBUG] 创建新的图片上传模态框');
    modal = setupImageUploadModal();
  }
  
  // 清空预览
  const imagePreview = document.getElementById('imagePreview');
  if (imagePreview) {
    imagePreview.innerHTML = '';
  }
  
  // 清空文件输入
  const singleFileInput = document.getElementById('imageFileInput');
  const multipleFileInput = document.getElementById('multipleImageFileInput');
  
  if (singleFileInput) {
    singleFileInput.value = ''; // 清空文件输入
    console.log('[DEBUG] 单文件输入重置');
  }
  
  if (multipleFileInput) {
    multipleFileInput.value = '';
    console.log('[DEBUG] 多文件输入重置');
  }
  
  // 根据类型设置上传选项
  const singleRadio = document.querySelector('input[name="uploadType"][value="single"]');
  const multipleRadio = document.querySelector('input[name="uploadType"][value="multiple"]');
  const singleUploadSection = document.getElementById('singleUploadSection');
  const multipleUploadSection = document.getElementById('multipleUploadSection');
  
  if (type === 'single' || type === 'background') {
    // 单图模式
    if (singleRadio) singleRadio.checked = true;
    if (singleUploadSection) singleUploadSection.style.display = 'block';
    if (multipleUploadSection) multipleUploadSection.style.display = 'none';
    console.log('[DEBUG] 设置为单图上传模式');
  } else {
    // 多图模式（轮播或容器）
    if (multipleRadio) multipleRadio.checked = true;
    if (singleUploadSection) singleUploadSection.style.display = 'none';
    if (multipleUploadSection) multipleUploadSection.style.display = 'block';
    console.log('[DEBUG] 设置为多图上传模式');
  }
  
  // 显示模态框
  modal.style.display = 'flex';
}

// 关闭图片上传模态框
function closeImageUploadModal() {
  console.log('[DEBUG] 关闭图片上传模态框');
  
  const modal = document.getElementById('imageUploadModal');
  if (modal) {
    modal.style.display = 'none';
  }
  
  // 清空状态
  const v = window.editorVars;
  v.currentEditingType = null;
  v.currentEditingElement = null;
  v.currentEditingImage = null;
  v.selectedImageIndex = -1;
  v.selectedSingleFile = null;
}

// 应用图片上传
function applyImageUpload() {
  console.log('[DEBUG] 开始应用图片上传');
  
  const v = window.editorVars;
  const imageFileInput = document.getElementById('imageFileInput');
  const multipleImageFileInput = document.getElementById('multipleImageFileInput');
  
  // 获取选中的单选按钮
  const uploadType = document.querySelector('input[name="uploadType"]:checked')?.value || 'single';
  console.log('[DEBUG] 上传类型:', uploadType);
  
  if (uploadType === 'single') {
    // 检查是否有选中的单个文件
    console.log('[DEBUG] 检查单个文件: selectedSingleFile =', v.selectedSingleFile ? v.selectedSingleFile.name : 'null');
    
    if (!v.selectedSingleFile) {
      console.log('[ERROR] 未选择单个文件!');
      
      // 检查input中是否有文件
      if (imageFileInput && imageFileInput.files && imageFileInput.files.length > 0) {
        v.selectedSingleFile = imageFileInput.files[0];
        console.log('[DEBUG] 从input获取文件:', v.selectedSingleFile.name);
      } else {
        console.log('[DEBUG] input中也没有文件');
        alert('请选择图片');
        return;
      }
    }
    
    console.log('[DEBUG] 准备处理单个文件:', v.selectedSingleFile.name);
    
    const reader = new FileReader();
    
    reader.onload = function(e) {
      console.log('[DEBUG] 文件读取完成，准备替换图片');
      
      if (v.currentEditingType === 'single' && v.currentEditingImage) {
        // 保存原始图片路径
        const originalSrc = v.currentEditingImage.src;
        console.log('[DEBUG] 单图替换: 原路径 =', originalSrc);
        
        // 更新图片
        v.currentEditingImage.src = e.target.result;
        console.log('[DEBUG] 单图替换成功:', v.selectedSingleFile.name);
        
        // 保存编辑的图片到本地存储
        saveEditedImage(originalSrc, v.selectedSingleFile);
      } else if (v.currentEditingType === 'background') {
        // 更新背景图
        console.log('[DEBUG] 背景图替换');
        v.currentEditingElement.style.backgroundImage = `url('${e.target.result}')`;
        
        // 保存编辑的背景图到本地存储
        const bgUrl = getBackgroundImageUrl(v.currentEditingElement);
        saveEditedImage(bgUrl, v.selectedSingleFile);
        
        console.log('[DEBUG] 背景图替换成功');
      } else if ((v.currentEditingType === 'carousel' || v.currentEditingType === 'container') && v.selectedImageIndex >= 0) {
        console.log('[DEBUG] 轮播/容器图片替换: 索引 =', v.selectedImageIndex);
        
        // 保存原始图片路径
        const originalImg = v.containerImages[v.selectedImageIndex];
        const originalSrc = originalImg.src;
        console.log('[DEBUG] 轮播/容器原图路径 =', originalSrc);
        
        // 更新图片
        originalImg.src = e.target.result;
        console.log('[DEBUG] 轮播/容器图片替换成功:', v.selectedSingleFile.name);
        
        // 保存编辑的图片到本地存储
        saveEditedImage(originalSrc, v.selectedSingleFile);
      } else {
        console.log('[ERROR] 无法确定要替换的图片类型或元素');
      }
      
      // 关闭模态框
      closeImageUploadModal();
    };
    
    reader.onerror = function(error) {
      console.error('[ERROR] 文件读取失败:', error);
      alert('图片读取失败，请重试');
    };
    
    console.log('[DEBUG] 开始读取文件...');
    reader.readAsDataURL(v.selectedSingleFile);
    
  } else if (uploadType === 'multiple') {
    // 检查是否有选中的多个文件
    const files = multipleImageFileInput.files;
    console.log('[DEBUG] 多文件数量:', files ? files.length : 0);
    
    if (!files || files.length === 0) {
      console.log('[ERROR] 未选择多个文件!');
      alert('请选择图片');
      return;
    }
    
    // 检查选择的图片数量是否与容器图片数量匹配
    if (files.length > v.containerImages.length) {
      console.log('[WARN] 选择的图片数量超过容器图片数量');
      alert(`您选择了${files.length}张图片，但${v.currentEditingType === 'carousel' ? '轮播图' : '区域'}中只有${v.containerImages.length}张图片，只会使用前${v.containerImages.length}张图片`);
    }
    
    // 处理多张图片上传
    let processedCount = 0;
    const totalToProcess = Math.min(files.length, v.containerImages.length);
    console.log('[DEBUG] 准备处理多文件, 总数:', totalToProcess);
    
    for (let i = 0; i < totalToProcess; i++) {
      const file = files[i];
      console.log('[DEBUG] 处理第', i+1, '个文件:', file.name);
      
      const reader = new FileReader();
      
      reader.onload = (function(index) {
        return function(e) {
          // 保存原始图片路径
          const originalSrc = v.containerImages[index].src;
          console.log('[DEBUG] 多图替换 #', index+1, ': 原路径 =', originalSrc);
          
          // 更新图片
          v.containerImages[index].src = e.target.result;
          console.log('[DEBUG] 多图替换 #', index+1, '成功');
          
          // 保存编辑的图片到本地存储
          saveEditedImage(originalSrc, files[index]);
          
          processedCount++;
          console.log('[DEBUG] 已处理:', processedCount, '/', totalToProcess);
          
          // 如果所有图片都处理完毕，关闭模态框
          if (processedCount === totalToProcess) {
            console.log('[DEBUG] 所有图片处理完毕，关闭模态框');
            closeImageUploadModal();
          }
        };
      })(i);
      
      reader.onerror = (function(index) {
        return function(error) {
          console.error('[ERROR] 文件', index+1, '读取失败:', error);
          
          processedCount++;
          if (processedCount === totalToProcess) {
            closeImageUploadModal();
          }
        };
      })(i);
      
      reader.readAsDataURL(file);
    }
  }
}

// 初始化编辑器变量
function initEditorVars() {
  // 创建全局变量对象
  window.editorVars = {
    elementInspectorVisible: false,
    selectedElement: null,
    editModeActive: false,
    textEditModeActive: false,
    imageEditModeActive: false,
    elementInspectModeActive: false,
    editedElements: {},
    editedTextElements: {},
    editedImages: {},
    editedOrder: [],
    undoStack: [],
    redoStack: [],
    originalTextStyles: new Map(),
    currentEditingType: null,        // 'single', 'background', 'carousel', 'container'
    currentEditingElement: null,     // 当前正在编辑的元素
    currentEditingImage: null,       // 当前正在编辑的图片
    containerImages: [],             // 容器或轮播图中的所有图片
    selectedImageIndex: -1,          // 选中的图片索引
    selectedSingleFile: null,        // 选中的单个文件
    divHoverHighlightActive: false,  // div hover高亮是否激活
  };
  
  console.log('[DEBUG] 编辑器变量已初始化');
}
</script>
"""

# 主函数
def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python html_edit.py <input_html_file> [<output_html_file>]")
        sys.exit(1)
    
    # 获取输入文件路径
    input_path = sys.argv[1]
    
    # 如果没有指定输出文件，则使用默认名称
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
    else:
        # 提取基本文件名并添加-editable后缀
        base_name, ext = os.path.splitext(input_path)
        output_path = f"{base_name}-editable{ext}"
    
    # 读取输入文件
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
    except Exception as e:
        print(f"读取文件时出错: {e}")
        sys.exit(1)
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 添加编辑工具样式
    head = soup.find('head')
    if not head:
        head = soup.new_tag('head')
        if soup.html:
            soup.html.insert(0, head)
        else:
            html = soup.new_tag('html')
            html.append(head)
            soup.append(html)
    
    # 添加样式
    head.append(BeautifulSoup(EDITOR_STYLES, 'html.parser'))
    
    # 添加HTML元素和脚本
    body = soup.find('body')
    if not body:
        body = soup.new_tag('body')
        if soup.html:
            soup.html.append(body)
        else:
            html = soup.new_tag('html')
            html.append(body)
            soup.append(html)
    
    # 添加编辑器元素
    body.append(BeautifulSoup(EDITOR_ELEMENTS, 'html.parser'))
    
    # 添加脚本
    body.append(BeautifulSoup(EDITOR_SCRIPTS, 'html.parser'))
    
    # 写入输出文件
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"已成功生成可编辑HTML文件: {output_path}")
        print("原始文件: {0}".format(input_path))
        print("可编辑文件: {0}".format(output_path))
        print("\n在浏览器中打开可编辑文件，使用以下功能:")
        print("1. 元素检查: 查看页面元素的结构和样式")
        print("2. 区域编辑: 复制或删除页面上的区域")
        print("3. 文本编辑: 直接编辑页面上的文本内容")
        print("4. 图片编辑: 上传新图片替换现有图片")
    except Exception as e:
        print(f"写入文件时出错: {e}")
        sys.exit(1)

# 运行主函数
if __name__ == "__main__":
    main()
