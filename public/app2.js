const tg = window.Telegram.WebApp;
tg.ready();
tg.expand();

let currentTab = 'notes';

// Отправка данных боту
function sendToBot(data) {
    tg.sendData(JSON.stringify(data));
}

// Загрузка заметок
function loadNotes() {
    sendToBot({ action: "get_notes" });
}

// Загрузка задач
function loadTasks() {
    sendToBot({ action: "get_tasks" });
}

// Рендер заметок
function renderNotes(notes) {
    const content = document.getElementById('content');
    if (!notes || notes.length === 0) {
        content.innerHTML = '<p style="color: var(--text-secondary); padding: 20px;">Нет заметок</p>';
        return;
    }
    let html = '';
    notes.forEach(note => {
        html += `
            <div class="note-card">
                <h3>${escapeHtml(note.title)}</h3>
                <p>${escapeHtml(note.content || '')}</p>
                <span class="note-date">${note.created_at}</span>
                <button class="delete-btn" data-id="${note.id}">🗑</button>
            </div>
        `;
    });
    content.innerHTML = html;
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteNote(parseInt(btn.dataset.id));
        });
    });
}

// Рендер задач
function renderTasks(tasks) {
    const content = document.getElementById('content');
    if (!tasks || tasks.length === 0) {
        content.innerHTML = '<p style="color: var(--text-secondary); padding: 20px;">Нет задач</p>';
        return;
    }
    let html = '';
    tasks.forEach(task => {
        html += `
            <div class="note-card">
                <h3>${task.done ? '✅ ' : ''}${escapeHtml(task.title)}</h3>
                <p>${escapeHtml(task.description || '')}</p>
                <span class="note-date">${task.created_at}</span>
                <button class="delete-btn" data-id="${task.id}">🗑</button>
            </div>
        `;
    });
    content.innerHTML = html;
    document.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            deleteTask(parseInt(btn.dataset.id));
        });
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Форма создания заметки
function showNoteForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="form">
            <input type="text" id="noteTitle" placeholder="Название заметки" class="input">
            <textarea id="noteContent" placeholder="Содержимое" class="textarea" rows="4"></textarea>
            <div class="form-buttons">
                <button class="btn btn-primary" id="saveNoteBtn">Сохранить</button>
                <button class="btn btn-secondary" id="cancelNoteBtn">Отмена</button>
            </div>
        </div>
    `;
    document.getElementById('saveNoteBtn').addEventListener('click', () => {
        const title = document.getElementById('noteTitle').value.trim();
        const content = document.getElementById('noteContent').value.trim();
        if (title) {
            sendToBot({ action: "create_note", title, content });
        }
    });
    document.getElementById('cancelNoteBtn').addEventListener('click', loadNotes);
}

// Форма создания задачи
function showTaskForm() {
    const content = document.getElementById('content');
    content.innerHTML = `
        <div class="form">
            <input type="text" id="taskTitle" placeholder="Название задачи" class="input">
            <textarea id="taskDescription" placeholder="Описание" class="textarea" rows="4"></textarea>
            <div class="form-buttons">
                <button class="btn btn-primary" id="saveTaskBtn">Сохранить</button>
                <button class="btn btn-secondary" id="cancelTaskBtn">Отмена</button>
            </div>
        </div>
    `;
    document.getElementById('saveTaskBtn').addEventListener('click', () => {
        const title = document.getElementById('taskTitle').value.trim();
        const description = document.getElementById('taskDescription').value.trim();
        if (title) {
            sendToBot({ action: "create_task", title, description });
        }
    });
    document.getElementById('cancelTaskBtn').addEventListener('click', loadTasks);
}

// Удаление
function deleteNote(id) {
    tg.showConfirm('Удалить заметку?', (ok) => {
        if (ok) sendToBot({ action: "delete_note", id });
    });
}

function deleteTask(id) {
    tg.showConfirm('Удалить задачу?', (ok) => {
        if (ok) sendToBot({ action: "delete_task", id });
    });
}

// Вкладки
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        currentTab = tab.dataset.tab;
        currentTab === 'notes' ? loadNotes() : loadTasks();
    });
});

// Кнопка +
document.getElementById('addBtn').addEventListener('click', () => {
    currentTab === 'notes' ? showNoteForm() : showTaskForm();
});

// Получение ответов от бота
window.addEventListener('message', (event) => {
    try {
        const data = JSON.parse(event.data);
        if (data.notes) renderNotes(data.notes);
        if (data.tasks) renderTasks(data.tasks);
        if (data.ok) {
            tg.showAlert('Готово!');
            currentTab === 'notes' ? loadNotes() : loadTasks();
        }
    } catch(e) {}
});

// Старт
loadNotes();