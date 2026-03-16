/**
 * AutoService Pro — Modal System
 * Animated modal popups with backdrop blur.
 */

function openModal(modalId) {
    const overlay = document.getElementById(modalId);
    if (!overlay) return;
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';

    // Close on backdrop click
    overlay.addEventListener('click', function handler(e) {
        if (e.target === overlay) {
            closeModal(modalId);
            overlay.removeEventListener('click', handler);
        }
    });

    // Close on Escape
    document.addEventListener('keydown', function handler(e) {
        if (e.key === 'Escape') {
            closeModal(modalId);
            document.removeEventListener('keydown', handler);
        }
    });
}

function closeModal(modalId) {
    const overlay = document.getElementById(modalId);
    if (!overlay) return;
    overlay.classList.remove('active');
    document.body.style.overflow = '';
}

/**
 * Create a dynamic confirmation modal
 */
function confirmAction(message, onConfirm) {
    // Create modal dynamically
    const id = 'confirmModal_' + Date.now();
    const overlay = document.createElement('div');
    overlay.id = id;
    overlay.className = 'modal-overlay active';
    overlay.innerHTML = `
        <div class="modal" style="max-width:420px; text-align:center;">
            <div style="margin-bottom:20px;">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--accent-orange)" stroke-width="1.5" style="margin-bottom:12px;">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <h3 style="margin-bottom:8px;">Подтверждение</h3>
                <p style="color: var(--text-secondary); font-size:14px;">${message}</p>
            </div>
            <div style="display:flex; gap:12px; justify-content:center;">
                <button class="btn btn-secondary" onclick="closeModal('${id}'); this.closest('.modal-overlay').remove();">Отмена</button>
                <button class="btn btn-danger" id="${id}_confirm">Подтвердить</button>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);

    document.getElementById(`${id}_confirm`).addEventListener('click', () => {
        overlay.remove();
        document.body.style.overflow = '';
        if (typeof onConfirm === 'function') onConfirm();
    });

    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.remove();
            document.body.style.overflow = '';
        }
    });
}
