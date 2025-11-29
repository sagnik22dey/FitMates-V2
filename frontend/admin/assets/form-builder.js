// Form Builder Module
// This handles the dynamic form creation with all field types

let currentFormData = null;
let currentFormId = null;

const FIELD_TYPES = {
  text: { label: 'Text', icon: '📝', hasTarget: false },
  number: { label: 'Number', icon: '🔢', hasTarget: true },
  date: { label: 'Date', icon: '📅', hasTarget: false },
  dropdown: { label: 'Dropdown', icon: '📋', hasTarget: false },
  checkbox: { label: 'Checkbox', icon: '☑️', hasTarget: false },
  textarea: { label: 'Long Text', icon: '📄', hasTarget: false },
  dynamic_table: { label: 'Dynamic Table', icon: '📊', hasTarget: false },
};

function showFormBuilder(form = null) {
  currentFormData = form ? JSON.parse(JSON.stringify(form)) : { data: { fields: [] } };
  currentFormId = form ? form.id : null;

  // Create overlay wrapper
  const overlay = document.createElement('div');
  overlay.className = 'modal-overlay active';
  overlay.id = 'form-builder-modal';
  window.currentFormBuilderModal = overlay;

  // Create modal content
  overlay.innerHTML = `
        <div class="modal" style="max-width: 900px; width: 95%; max-height: 90vh; display: flex; flex-direction: column;">
            <div class="modal-header">
                <h3 class="modal-title">${form ? 'Edit Form' : 'Create New Form'}</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">✕</button>
            </div>
            <div class="modal-body" style="overflow-y: auto; flex: 1;">
                <div class="form-group">
                    <label class="input-label">Form Title</label>
                    <input type="text" id="form-title" class="input" value="${form ? form.title : ''}" placeholder="e.g., Weekly Check-in">
                </div>

                <div id="form-fields-container" style="margin: 20px 0; display: flex; flex-direction: column; gap: 16px;">
                    <!-- Fields will be rendered here -->
                </div>

                <div class="add-field-controls" style="border: 2px dashed rgba(255,255,255,0.1); padding: 20px; text-align: center; border-radius: 8px;">
                    <p style="margin-bottom: 10px; color: var(--color-text-secondary);">Add a new field:</p>
                    <div style="display: flex; gap: 8px; justify-content: center; flex-wrap: wrap;">
                        ${Object.entries(FIELD_TYPES).map(([type, config]) => `
                            <button class="btn btn-sm btn-outline" onclick="addNewField('${type}')">
                                ${config.icon} ${config.label}
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
            <div class="modal-footer" style="margin-top: 20px; padding-top: 20px; border-top: 1px solid var(--color-border); display: flex; justify-content: flex-end; gap: 10px;">
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">Cancel</button>
                <button class="btn btn-primary" onclick="saveForm()">Save Form</button>
            </div>
        </div>
    `;

  document.body.appendChild(overlay);
  renderFields();
}

function renderFields() {
  const container = document.getElementById('form-fields-container');
  if (!container) return;

  container.innerHTML = currentFormData.data.fields.map((field, index) => renderFieldEditor(field, index)).join('');
}

function renderFieldEditor(field, index) {
  const typeConfig = FIELD_TYPES[field.type];

  return `
    <div class="field-editor" id="field-${index}" style="background: var(--color-surface); padding: 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span style="font-size: 1.2em;">${typeConfig.icon}</span>
                <span style="font-weight: 500; color: var(--color-text-secondary);">${typeConfig.label}</span>
            </div>
            <div style="display: flex; gap: 8px;">
                <button class="btn-icon" onclick="moveField(${index}, -1)" ${index === 0 ? 'disabled' : ''}>↑</button>
                <button class="btn-icon" onclick="moveField(${index}, 1)" ${index === currentFormData.data.fields.length - 1 ? 'disabled' : ''}>↓</button>
                <button class="btn-icon text-danger" onclick="removeField(${index})">🗑️</button>
            </div>
        </div>

        <div class="row">
            <div class="col-md-8">
                <label>Field Label</label>
                <input type="text" class="input field-label" value="${field.label || ''}" placeholder="Question or Label">
            </div>
            <div class="col-md-4">
                <label>Required</label>
                <div style="margin-top: 8px;">
                    <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                        <input type="checkbox" class="field-required" ${field.required ? 'checked' : ''}>
                        <span>Required field</span>
                    </label>
                </div>
            </div>
        </div>

        ${field.type === 'dropdown' ? renderOptionsEditor(field, index) : ''}
        ${field.type === 'dynamic_table' ? renderDynamicTableEditor(field, index) : ''}
    </div>
    `;
}

function renderOptionsEditor(field, index) {
  const options = field.options || [];
  return `
    <div style="margin-top: 12px;">
        <label>Options (comma separated)</label>
        <input type="text" class="input field-options" value="${options.join(', ')}" placeholder="Option 1, Option 2, Option 3">
    </div>
    `;
}

// --- Dynamic Table Logic ---

function renderDynamicTableEditor(field, fieldIndex) {
  const columns = field.columns || [];
  const rows = field.rows || [];

  return `
    <div style="grid-column: 1 / -1; margin-top: var(--spacing-md); background: rgba(0,0,0,0.2); padding: var(--spacing-md); border-radius: var(--radius-md);">
        
        <!-- Columns Configuration -->
        <h6 style="margin-bottom: var(--spacing-sm);">Table Columns</h6>
        <div id="table-columns-${fieldIndex}" style="display: grid; gap: 8px; margin-bottom: 16px;">
            ${columns.map((col, colIndex) => renderTableColumn(col, fieldIndex, colIndex)).join('')}
        </div>
        <button class="btn btn-sm btn-outline" onclick="addTableColumn(${fieldIndex})">
            ➕ Add Column
        </button>

        <hr style="border-color: rgba(255,255,255,0.1); margin: 16px 0;">

        <!-- Initial Rows -->
        <h6 style="margin-bottom: var(--spacing-sm);">Initial Rows (Admin Pre-fill)</h6>
        <div id="table-rows-${fieldIndex}" style="overflow-x: auto;">
            ${renderTableRowsEditor(columns, rows, fieldIndex)}
        </div>
        <button class="btn btn-sm btn-outline" style="margin-top: var(--spacing-sm);" onclick="addTableRow(${fieldIndex})">
            ➕ Add Row
        </button>
    </div>
    `;
}

function renderTableColumn(column, fieldIndex, colIndex) {
  return `
    <div class="table-column-config" style="display: grid; grid-template-columns: 2fr 1fr 1fr auto; gap: 8px; align-items: center;">
        <input type="text" class="input col-label" value="${column.label}" placeholder="Column Name" onchange="refreshTableRows(${fieldIndex})">
        <select class="input col-type" onchange="refreshTableRows(${fieldIndex})">
            <option value="text" ${column.type === 'text' ? 'selected' : ''}>Text</option>
            <option value="number" ${column.type === 'number' ? 'selected' : ''}>Number</option>
            <option value="checkbox" ${column.type === 'checkbox' ? 'selected' : ''}>Checkbox</option>
            <option value="dropdown" ${column.type === 'dropdown' ? 'selected' : ''}>Dropdown</option>
        </select>
        <select class="input col-access">
            <option value="admin" ${column.access === 'admin' ? 'selected' : ''}>Admin Only</option>
            <option value="client" ${column.access === 'client' ? 'selected' : ''}>Client Editable</option>
        </select>
        <button class="btn-icon text-danger" onclick="removeTableColumn(${fieldIndex}, ${colIndex})">✕</button>
    </div>
    `;
}

function renderTableRowsEditor(columns, rows, fieldIndex) {
  if (columns.length === 0) return '<p style="color: var(--color-text-secondary); font-style: italic;">Add columns first</p>';

  return `
    <table style="width: 100%; border-collapse: collapse; min-width: 600px;">
        <thead>
            <tr style="background: rgba(255,255,255,0.05);">
                ${columns.map(col => `<th style="padding: 8px; text-align: left; font-size: 0.9em;">${col.label || '(No Label)'}</th>`).join('')}
                <th style="width: 40px;"></th>
            </tr>
        </thead>
        <tbody>
            ${rows.map((row, rowIndex) => `
                <tr class="table-row-data">
                    ${columns.map((col, colIndex) => `
                        <td style="padding: 4px;">
                            <input type="${col.type === 'number' ? 'number' : 'text'}" 
                                   class="input row-cell" 
                                   data-col-index="${colIndex}"
                                   value="${row[`col_${colIndex}`] || ''}"
                                   placeholder="${col.label}">
                        </td>
                    `).join('')}
                    <td>
                        <button class="btn-icon text-danger" onclick="removeTableRow(${fieldIndex}, ${rowIndex})">✕</button>
                    </td>
                </tr>
            `).join('')}
        </tbody>
    </table>
    `;
}

function addTableColumn(fieldIndex) {
  // Save current state first
  currentFormData.data.fields = collectFieldsData();

  currentFormData.data.fields[fieldIndex].columns = currentFormData.data.fields[fieldIndex].columns || [];
  currentFormData.data.fields[fieldIndex].columns.push({
    label: 'New Column',
    type: 'text',
    access: 'client'
  });

  renderFields();
}

function removeTableColumn(fieldIndex, colIndex) {
  currentFormData.data.fields = collectFieldsData();
  currentFormData.data.fields[fieldIndex].columns.splice(colIndex, 1);
  renderFields();
}

function addTableRow(fieldIndex) {
  currentFormData.data.fields = collectFieldsData();
  currentFormData.data.fields[fieldIndex].rows = currentFormData.data.fields[fieldIndex].rows || [];
  currentFormData.data.fields[fieldIndex].rows.push({});
  renderFields();
}

function removeTableRow(fieldIndex, rowIndex) {
  currentFormData.data.fields = collectFieldsData();
  currentFormData.data.fields[fieldIndex].rows.splice(rowIndex, 1);
  renderFields();
}

function refreshTableRows(fieldIndex) {
  // Just re-render to update headers/types, but need to save data first
  currentFormData.data.fields = collectFieldsData();
  renderFields();
}

// --- General Field Operations ---

function addNewField(type) {
  currentFormData.data.fields.push({
    id: crypto.randomUUID(),
    type: type,
    label: '',
    required: false,
    options: type === 'dropdown' ? [] : undefined,
    columns: type === 'dynamic_table' ? [] : undefined,
    rows: type === 'dynamic_table' ? [] : undefined
  });
  renderFields();
}

function removeField(index) {
  currentFormData.data.fields.splice(index, 1);
  renderFields();
}

function moveField(index, direction) {
  const newIndex = index + direction;
  if (newIndex >= 0 && newIndex < currentFormData.data.fields.length) {
    const temp = currentFormData.data.fields[index];
    currentFormData.data.fields[index] = currentFormData.data.fields[newIndex];
    currentFormData.data.fields[newIndex] = temp;
    renderFields();
  }
}

function collectFieldsData() {
  const container = document.getElementById('form-fields-container');
  if (!container) return [];

  return Array.from(container.children).map((item, index) => {
    const field = currentFormData.data.fields[index];
    field.label = item.querySelector('.field-label').value;
    field.required = item.querySelector('.field-required').checked;

    if (field.type === 'dropdown') {
      const optionsStr = item.querySelector('.field-options').value;
      field.options = optionsStr.split(',').map(o => o.trim()).filter(o => o);
    }

    if (field.type === 'dynamic_table') {
      field.columns = [];
      const colsContainer = item.querySelector(`#table-columns-${index}`);
      if (colsContainer) {
        colsContainer.querySelectorAll('.table-column-config').forEach(col => {
          field.columns.push({
            label: col.querySelector('.col-label').value,
            type: col.querySelector('.col-type').value,
            access: col.querySelector('.col-access').value
          });
        });
      }

      field.rows = [];
      const rowsContainer = item.querySelector(`#table-rows-${index}`);
      if (rowsContainer) {
        rowsContainer.querySelectorAll('.table-row-data').forEach(row => {
          const rowData = {};
          row.querySelectorAll('.row-cell').forEach(cell => {
            const colIndex = cell.getAttribute('data-col-index');
            rowData[`col_${colIndex}`] = cell.value;
          });
          field.rows.push(rowData);
        });
      }
    }

    return field;
  });
}

async function saveForm() {
  const title = document.getElementById('form-title').value;
  if (!title) {
    ui.showToast('Please enter a form title', 'error');
    return;
  }

  const fields = collectFieldsData();

  if (fields.length === 0) {
    ui.showToast('Please add at least one field', 'error');
    return;
  }

  const formData = {
    client_id: clientId, // Assumes clientId is available globally or in scope
    title,
    data: { fields },
    status: 'draft',
    is_template: false,
  };

  try {
    if (currentFormId) {
      // Update existing form
      await api.put(`/api/forms/${currentFormId}`, {
        title,
        data: { fields },
      });
      ui.showToast('Form updated successfully!', 'success');
    } else {
      // Create new form
      await api.post('/api/forms', formData);
      ui.showToast('Form created successfully!', 'success');
    }

    // Close modal and reload forms
    if (window.currentFormBuilderModal) {
      window.currentFormBuilderModal.classList.remove('active');
      setTimeout(() => window.currentFormBuilderModal.remove(), 300);
    }

    if (window.loadForms) {
      loadForms();
    }
  } catch (error) {
    console.error(error);
    ui.showToast(error.message || 'Failed to save form', 'error');
  }
}

function editForm(form) {
  showFormBuilder(form);
}

// Export functions to global scope
window.showFormBuilder = showFormBuilder;
window.editForm = editForm;
window.addNewField = addNewField;
window.removeField = removeField;
window.addTableColumn = addTableColumn;
window.removeTableColumn = removeTableColumn;
window.addTableRow = addTableRow;
window.removeTableRow = removeTableRow;
window.refreshTableRows = refreshTableRows;
window.saveForm = saveForm;
