// TaskRebuild Floating In-Page Quick-Capture Script
// Mounts an isolated Shadow DOM UI for zero style interference with task selection support.

(function () {
  console.log('TaskRebuild quick-capture content script active');

  let hostElement: HTMLDivElement | null = null;
  let shadowRoot: ShadowRoot | null = null;
  let triggerBubble: HTMLButtonElement | null = null;
  let captureModal: HTMLDivElement | null = null;
  let toastEl: HTMLDivElement | null = null;

  let currentSelectedText = '';
  let availableTasks: Array<{ id: string; name: string }> = [];
  let selectedTaskId: string | null = null;
  let selectedTaskName: string | null = null;

  // 1. Initialize Root & Shadow DOM
  function initHost() {
    if (document.getElementById('taskrebuild-floating-root')) return;

    hostElement = document.createElement('div');
    hostElement.id = 'taskrebuild-floating-root';
    hostElement.style.position = 'absolute';
    hostElement.style.top = '0';
    hostElement.style.left = '0';
    hostElement.style.zIndex = '2147483647';
    hostElement.style.pointerEvents = 'none';

    shadowRoot = hostElement.attachShadow({ mode: 'open' });

    // Stylesheet inside Shadow DOM
    const style = document.createElement('style');
    style.textContent = `
      * {
        box-sizing: border-box;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      }
      .tr-pointer {
        pointer-events: auto;
      }
      .tr-bubble {
        position: absolute;
        display: none;
        align-items: center;
        gap: 6px;
        background: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 9999px;
        padding: 6px 12px;
        font-size: 12px;
        font-weight: 600;
        cursor: pointer;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -4px rgba(0, 0, 0, 0.2);
        transition: transform 0.15s ease, background 0.15s ease;
        user-select: none;
      }
      .tr-bubble:hover {
        background: #0f172a;
        transform: translateY(-2px);
      }
      .tr-bubble svg {
        width: 14px;
        height: 14px;
        fill: #38bdf8;
      }
      .tr-card {
        position: absolute;
        display: none;
        flex-direction: column;
        width: 340px;
        background: #0f172a;
        color: #f1f5f9;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 14px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.3);
      }
      .tr-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 10px;
      }
      .tr-header-title {
        font-size: 13px;
        font-weight: 700;
        color: #38bdf8;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .tr-header-title svg {
        width: 15px;
        height: 15px;
        fill: #38bdf8;
      }
      .tr-close {
        background: none;
        border: none;
        color: #94a3b8;
        font-size: 16px;
        cursor: pointer;
        padding: 2px 6px;
        line-height: 1;
      }
      .tr-close:hover {
        color: #f1f5f9;
      }
      .tr-label {
        font-size: 11px;
        font-weight: 600;
        color: #94a3b8;
        margin-bottom: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
      }
      .tr-input, .tr-select, .tr-textarea {
        width: 100%;
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 6px;
        color: #f8fafc;
        font-size: 12px;
        padding: 6px 10px;
        margin-bottom: 8px;
        outline: none;
      }
      .tr-input:focus, .tr-select:focus, .tr-textarea:focus {
        border-color: #38bdf8;
      }
      .tr-textarea {
        height: 60px;
        resize: none;
      }
      .tr-row {
        display: flex;
        gap: 8px;
      }
      .tr-row > div {
        flex: 1;
      }
      .tr-actions {
        display: flex;
        gap: 8px;
        margin-top: 4px;
      }
      .tr-btn {
        flex: 1;
        padding: 8px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        cursor: pointer;
        border: none;
        transition: opacity 0.15s, background 0.15s;
        text-align: center;
      }
      .tr-btn-primary {
        background: #0284c7;
        color: white;
      }
      .tr-btn-primary:hover {
        background: #0369a1;
      }
      .tr-btn-secondary {
        background: #334155;
        color: #f1f5f9;
      }
      .tr-btn-secondary:hover {
        background: #475569;
      }
      .tr-toast {
        position: fixed;
        bottom: 24px;
        right: 24px;
        background: #059669;
        color: white;
        padding: 10px 16px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 600;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
        display: none;
        align-items: center;
        gap: 8px;
        z-index: 2147483647;
      }
    `;
    shadowRoot.appendChild(style);

    // Floating Bubble Trigger
    triggerBubble = document.createElement('button');
    triggerBubble.className = 'tr-bubble tr-pointer';
    triggerBubble.innerHTML = `
      <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
      <span>Capture Knowledge</span>
    `;
    triggerBubble.addEventListener('click', (e) => {
      e.stopPropagation();
      openModal();
    });
    shadowRoot.appendChild(triggerBubble);

    // Capture Modal Card with Task Chooser
    captureModal = document.createElement('div');
    captureModal.className = 'tr-card tr-pointer';
    captureModal.innerHTML = `
      <div class="tr-header">
        <div class="tr-header-title">
          <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/></svg>
          <span>TaskRebuild Quick-Capture</span>
        </div>
        <button class="tr-close" id="tr-btn-close">&times;</button>
      </div>

      <div class="tr-label">Target Task</div>
      <select class="tr-select" id="tr-task-select">
        <option value="">(Loading tasks...)</option>
      </select>

      <div class="tr-row">
        <div>
          <div class="tr-label">Type</div>
          <select class="tr-select" id="tr-type-select">
            <option value="insight">Insight</option>
            <option value="concept">Concept</option>
            <option value="note" selected>Note</option>
            <option value="question">Question</option>
            <option value="resource">Resource</option>
          </select>
        </div>
      </div>

      <div class="tr-label">Title</div>
      <input type="text" class="tr-input" id="tr-title-input" placeholder="Title or Summary" />

      <div class="tr-label">Selected Content</div>
      <textarea class="tr-textarea" id="tr-content-input"></textarea>

      <div class="tr-actions">
        <button class="tr-btn tr-btn-primary" id="tr-btn-save-knowledge">Save Knowledge</button>
        <button class="tr-btn tr-btn-secondary" id="tr-btn-save-resource">Save as URL</button>
      </div>
    `;

    shadowRoot.appendChild(captureModal);

    // Toast
    toastEl = document.createElement('div');
    toastEl.className = 'tr-toast tr-pointer';
    toastEl.innerHTML = `<span>✓</span> <span id="tr-toast-msg">Saved to TaskRebuild</span>`;
    shadowRoot.appendChild(toastEl);

    // Attach event listeners
    const closeBtn = captureModal.querySelector('#tr-btn-close');
    closeBtn?.addEventListener('click', hideAll);

    const taskSelect = captureModal.querySelector('#tr-task-select') as HTMLSelectElement;
    taskSelect?.addEventListener('change', (e: any) => {
      selectedTaskId = e.target.value || null;
      const found = availableTasks.find((t) => t.id === selectedTaskId);
      selectedTaskName = found ? found.name : null;
    });

    const saveKnowledgeBtn = captureModal.querySelector('#tr-btn-save-knowledge');
    saveKnowledgeBtn?.addEventListener('click', handleSaveKnowledge);

    const saveResourceBtn = captureModal.querySelector('#tr-btn-save-resource');
    saveResourceBtn?.addEventListener('click', handleSaveResource);

    document.body.appendChild(hostElement);
  }

  function showToast(message: string) {
    if (!toastEl) return;
    const msgSpan = toastEl.querySelector('#tr-toast-msg');
    if (msgSpan) msgSpan.textContent = message;
    toastEl.style.display = 'flex';
    setTimeout(() => {
      if (toastEl) toastEl.style.display = 'none';
    }, 3000);
  }

  function hideAll() {
    if (triggerBubble) triggerBubble.style.display = 'none';
    if (captureModal) captureModal.style.display = 'none';
  }

  function populateTaskOptions(taskSelect: HTMLSelectElement) {
    taskSelect.innerHTML = '';

    if (!availableTasks || availableTasks.length === 0) {
      const opt = document.createElement('option');
      opt.value = '';
      opt.textContent = 'No tasks found (General / Standalone)';
      taskSelect.appendChild(opt);
      return;
    }

    // Optional General / Standalone choice
    const genOpt = document.createElement('option');
    genOpt.value = '';
    genOpt.textContent = '-- General / None --';
    taskSelect.appendChild(genOpt);

    availableTasks.forEach((task) => {
      const opt = document.createElement('option');
      opt.value = task.id;
      opt.textContent = task.name;
      if (task.id === selectedTaskId) {
        opt.selected = true;
      }
      taskSelect.appendChild(opt);
    });
  }

  function openModal() {
    if (!captureModal || !triggerBubble) return;

    const taskSelect = captureModal.querySelector('#tr-task-select') as HTMLSelectElement;
    const titleInput = captureModal.querySelector('#tr-title-input') as HTMLInputElement;
    const contentInput = captureModal.querySelector('#tr-content-input') as HTMLTextAreaElement;

    // Load available tasks and current active task context
    chrome.runtime.sendMessage({ action: 'GET_ACTIVE_CONTEXT' }, (res) => {
      if (res) {
        availableTasks = res.tasks || [];
        selectedTaskId = res.activeTaskId || (availableTasks[0] ? availableTasks[0].id : null);
        selectedTaskName = res.activeTaskName || (availableTasks[0] ? availableTasks[0].name : null);
        if (taskSelect) {
          populateTaskOptions(taskSelect);
        }
      }
    });

    // Auto-suggest concise title
    const firstLine = currentSelectedText.split('\n')[0].trim();
    const suggestedTitle = firstLine.length > 50 ? firstLine.substring(0, 47) + '...' : firstLine || document.title;

    if (titleInput) titleInput.value = suggestedTitle;
    if (contentInput) contentInput.value = currentSelectedText;

    // Position modal at the bubble's coordinates
    captureModal.style.top = triggerBubble.style.top;
    captureModal.style.left = triggerBubble.style.left;
    captureModal.style.display = 'flex';

    triggerBubble.style.display = 'none';
  }

  function handleSaveKnowledge() {
    if (!captureModal) return;
    const typeSelect = captureModal.querySelector('#tr-type-select') as HTMLSelectElement;
    const titleInput = captureModal.querySelector('#tr-title-input') as HTMLInputElement;
    const contentInput = captureModal.querySelector('#tr-content-input') as HTMLTextAreaElement;

    const payload = {
      type: typeSelect?.value || 'note',
      title: titleInput?.value.trim() || 'Untitled Knowledge',
      content: contentInput?.value.trim() || currentSelectedText,
      url: window.location.href,
      pageTitle: document.title,
      taskId: selectedTaskId,
      taskName: selectedTaskName
    };

    chrome.runtime.sendMessage({ action: 'SAVE_KNOWLEDGE_CAPTURE', payload }, (response) => {
      if (response && response.success) {
        hideAll();
        showToast('✓ Saved to Knowledge!');
      } else {
        alert(response?.error || 'Failed to save knowledge. Please ensure you are logged in.');
      }
    });
  }

  function handleSaveResource() {
    if (!selectedTaskId) {
      alert('Please select a target task from the dropdown first.');
      return;
    }

    const payload = {
      taskId: selectedTaskId,
      url: window.location.href,
      title: document.title
    };

    chrome.runtime.sendMessage({ action: 'SAVE_RESOURCE_CAPTURE', payload }, (response) => {
      if (response && response.success) {
        hideAll();
        showToast('✓ Saved as Resource!');
      } else {
        alert(response?.error || 'Failed to save resource.');
      }
    });
  }

  // 2. Selection Event Handling
  function onSelectionChange() {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) {
      if (captureModal && captureModal.style.display === 'flex') return;
      if (triggerBubble) triggerBubble.style.display = 'none';
      return;
    }

    const text = selection.toString().trim();
    if (text.length < 3) {
      if (triggerBubble) triggerBubble.style.display = 'none';
      return;
    }

    currentSelectedText = text;

    try {
      const range = selection.getRangeAt(0);
      const rect = range.getBoundingClientRect();

      initHost();

      if (triggerBubble) {
        const top = window.scrollY + rect.top - 40;
        const left = window.scrollX + rect.left + rect.width / 2 - 60;

        triggerBubble.style.top = `${Math.max(10, top)}px`;
        triggerBubble.style.left = `${Math.max(10, left)}px`;
        triggerBubble.style.display = 'flex';
      }
    } catch (e) {
      console.debug('Selection range error', e);
    }
  }

  // Mouse & Keyboard Event Listeners
  document.addEventListener('mouseup', (e) => {
    if (hostElement && e.composedPath().includes(hostElement)) return;
    setTimeout(onSelectionChange, 20);
  });

  document.addEventListener('keyup', (e) => {
    if (hostElement && e.composedPath().includes(hostElement)) return;
    setTimeout(onSelectionChange, 20);
  });

  document.addEventListener('mousedown', (e) => {
    if (hostElement && e.composedPath().includes(hostElement)) return;
    if (captureModal && captureModal.style.display === 'flex') {
      hideAll();
    }
  });
})();
