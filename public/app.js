const storageKey = 'flowplan-static-tasks-v1';
const today = new Date();
today.setHours(0, 0, 0, 0);

function dateOffset(days) {
  const date = new Date(today);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function starterTasks() {
  return [
    { id: crypto.randomUUID(), title: 'Map out the week', description: 'Choose three things that matter most.', date: dateOffset(0), priority: 'High', done: false },
    { id: crypto.randomUUID(), title: 'Review project notes', description: 'Pull the open questions into one place.', date: dateOffset(0), priority: 'Medium', done: false },
    { id: crypto.randomUUID(), title: 'Take a proper lunch break', description: 'Step away from the desk for a while.', date: dateOffset(0), priority: 'Low', done: true },
    { id: crypto.randomUUID(), title: 'Send the weekly update', description: 'Share progress and any blockers.', date: dateOffset(1), priority: 'Medium', done: false },
    { id: crypto.randomUUID(), title: 'Read the research summary', description: 'Capture the useful takeaways.', date: dateOffset(2), priority: 'Low', done: false },
    { id: crypto.randomUUID(), title: 'Prepare Friday review', description: '', date: dateOffset(4), priority: 'High', done: false }
  ];
}

function loadTasks() {
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey));
    return Array.isArray(saved) ? saved : starterTasks();
  } catch {
    return starterTasks();
  }
}

let tasks = loadTasks();
const $ = (selector) => document.querySelector(selector);
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const prettyDate = (value, options = { month: 'short', day: 'numeric' }) => new Date(`${value}T12:00:00`).toLocaleDateString(undefined, options);

function persist() {
  localStorage.setItem(storageKey, JSON.stringify(tasks));
  render();
}

function taskMarkup(task) {
  const safeTitle = escapeHtml(task.title);
  const description = task.description ? `<p class="task-description">${escapeHtml(task.description)}</p>` : '';
  const doneClass = task.done ? ' is-done' : '';
  return `<article class="task-row${doneClass}">
    <input class="task-check" type="checkbox" aria-label="Mark ${safeTitle} complete" data-toggle="${task.id}" ${task.done ? 'checked' : ''}>
    <div><p class="task-title">${safeTitle}</p>${description}</div>
    <span class="priority ${task.priority.toLowerCase()}">${escapeHtml(task.priority)}</span>
    <span class="task-due">${prettyDate(task.date)}</span>
    <button class="delete-task" type="button" data-delete="${task.id}" aria-label="Delete ${safeTitle}">×</button>
  </article>`;
}

function updateSummary() {
  const todayTasks = tasks.filter((task) => task.date === dateOffset(0));
  const done = todayTasks.filter((task) => task.done).length;
  const open = todayTasks.filter((task) => !task.done);
  const percent = todayTasks.length ? Math.round(done / todayTasks.length * 100) : 0;
  $('#summary-grid').innerHTML = [
    ['On the list', todayTasks.length, '01'],
    ['In progress', open.length, '02'],
    ['Completed', done, '03']
  ].map(([label, value, mark]) => `<div class="summary-item"><div><span class="summary-label">${label}</span><strong class="summary-value">${value}</strong></div><span class="summary-mark">${mark}</span></div>`).join('');
  $('#progress-number').textContent = `${percent}%`;
  $('#progress-fill').style.width = `${percent}%`;
  $('#progress-done').textContent = `${done} finished`;
  $('#progress-left').textContent = `${open.length} to go`;
  const focus = open[0];
  $('#focus-content').innerHTML = focus
    ? `<div class="focus-task"><h3>${escapeHtml(focus.title)}</h3><p>${escapeHtml(focus.description || 'One step at a time.')}</p><div class="focus-meta"><span class="priority ${focus.priority.toLowerCase()}">${escapeHtml(focus.priority)} priority</span><span class="focus-time">Due ${prettyDate(focus.date)}</span></div></div>`
    : '<div class="focus-task"><h3>Room to breathe.</h3><p>Nothing urgent is waiting for you today.</p></div>';
  const todayList = $('#today-task-list');
  todayList.innerHTML = todayTasks.length ? todayTasks.map(taskMarkup).join('') : '<p class="empty-state">No tasks planned today. Add one when you are ready.</p>';
}

function updateTaskView() {
  const query = $('#task-search').value.trim().toLowerCase();
  const filter = $('#task-filter').value;
  const visible = tasks.filter((task) => {
    const matchesText = `${task.title} ${task.description}`.toLowerCase().includes(query);
    const matchesStatus = filter === 'all' || (filter === 'done' ? task.done : !task.done);
    return matchesText && matchesStatus;
  }).sort((a, b) => a.date.localeCompare(b.date));
  $('#all-task-list').innerHTML = visible.length ? visible.map(taskMarkup).join('') : '<p class="empty-state">Nothing matches that view. Try another search or add a task.</p>';
}

function updateWeek() {
  const days = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(today);
    date.setDate(date.getDate() + index);
    const key = date.toISOString().slice(0, 10);
    const items = tasks.filter((task) => task.date === key);
    const label = index === 0 ? 'Today' : index === 1 ? 'Tomorrow' : date.toLocaleDateString(undefined, { weekday: 'long' });
    const markup = items.length ? items.map((task) => `<div class="week-task">${escapeHtml(task.title)}${task.done ? ' <span>(done)</span>' : ''}</div>`).join('') : '<span class="week-empty">Open space</span>';
    return `<article class="week-day"><div class="week-date">${prettyDate(key, { month: 'long', day: 'numeric' })}<strong>${label}</strong></div><div class="week-items">${markup}</div></article>`;
  });
  $('#week-list').innerHTML = days.join('');
}

function updateInsights() {
  const completed = tasks.filter((task) => task.done).length;
  const total = tasks.length;
  const upcoming = tasks.filter((task) => !task.done && task.date >= dateOffset(0)).length;
  const rate = total ? Math.round(completed / total * 100) : 0;
  $('#insights-content').innerHTML = [
    ['FINISHED', completed, 'Tasks you have already moved forward.'],
    ['STILL IN PLAY', upcoming, 'Open tasks on today or later.'],
    ['COMPLETION RATE', `${rate}%`, 'A snapshot of your current list.']
  ].map(([label, value, caption]) => `<article class="insight-panel"><p class="eyebrow">${label}</p><div class="insight-value">${value}</div><p>${caption}</p></article>`).join('');
}

function render() {
  updateSummary();
  updateTaskView();
  updateWeek();
  updateInsights();
}

function setView(name) {
  document.querySelectorAll('.view').forEach((view) => {
    const active = view.id === `view-${name}`;
    view.hidden = !active;
    view.classList.toggle('active', active);
  });
  document.querySelectorAll('.nav-link').forEach((button) => button.classList.toggle('active', button.dataset.view === name));
  const labels = { dashboard: 'OVERVIEW', tasks: 'MY TASKS', calendar: 'THIS WEEK', insights: 'INSIGHTS' };
  $('#section-name').textContent = labels[name] || labels.dashboard;
  history.replaceState(null, '', `#${name}`);
}

document.addEventListener('click', (event) => {
  const nav = event.target.closest('[data-view], [data-go]');
  if (nav) setView(nav.dataset.view || nav.dataset.go);
  if (event.target.closest('[data-open-task]')) {
    const dialog = $('#task-dialog');
    $('#task-form').elements.date.value = dateOffset(0);
    dialog.showModal();
    $('#task-form').elements.title.focus();
  }
  if (event.target.closest('[data-close-task]')) $('#task-dialog').close();
  const toggle = event.target.closest('[data-toggle]');
  if (toggle) {
    tasks = tasks.map((task) => task.id === toggle.dataset.toggle ? { ...task, done: toggle.checked } : task);
    persist();
  }
  const remove = event.target.closest('[data-delete]');
  if (remove) {
    tasks = tasks.filter((task) => task.id !== remove.dataset.delete);
    persist();
  }
});

$('#task-form').addEventListener('submit', (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const values = new FormData(form);
  tasks.unshift({ id: crypto.randomUUID(), title: values.get('title').trim(), description: values.get('description').trim(), date: values.get('date'), priority: values.get('priority'), done: false });
  persist();
  $('#task-dialog').close();
  form.reset();
  setView('tasks');
});

$('#task-search').addEventListener('input', updateTaskView);
$('#task-filter').addEventListener('change', updateTaskView);
$('#date-stamp').textContent = today.toLocaleDateString(undefined, { weekday: 'long', month: 'long', day: 'numeric' });
$('#today-label').textContent = today.toLocaleDateString(undefined, { weekday: 'long', month: 'long' }).toUpperCase();
render();
const requestedView = location.hash.slice(1);
setView(['dashboard', 'tasks', 'calendar', 'insights'].includes(requestedView) ? requestedView : 'dashboard');