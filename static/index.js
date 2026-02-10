const modal = document.getElementById('modal');
const backdrop = modal.querySelector('.modal-backdrop');

let lastFocusedElement;

function openModal() {
  lastFocusedElement = document.activeElement;
  modal.classList.add('active');
  modal.setAttribute('aria-hidden', 'false');

  // focus the modal content if present
  const content = modal.querySelector('.modal-content');
  if (content) content.focus();
}

function closeModal() {
  modal.classList.remove('active');
  modal.setAttribute('aria-hidden', 'true');

  // Optional: clear modal content so old forms/errors don't linger
  const content = document.getElementById('modal-content');
  if (content) content.innerHTML = "";

  lastFocusedElement?.focus();
}

/**
 * OPEN:
 * We won't bind to a specific #openModal button anymore.
 * Instead, any element with data-open-modal will open the modal.
 * (Your HTMX "Add task" buttons can include data-open-modal.)
 */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-open-modal]');
  if (btn) openModal();
});

/**
 * CLOSE:
 * Close button is inside dynamically loaded modal content.
 * So use event delegation: any element with data-close-modal closes it.
 */
document.addEventListener('click', (e) => {
  const btn = e.target.closest('[data-close-modal]');
  if (btn) closeModal();
});

backdrop.addEventListener('click', closeModal);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape' && modal.classList.contains('active')) {
    closeModal();
  }
});

// focus trap stays the same
modal.addEventListener('keydown', (e) => {
  if (e.key !== 'Tab') return;

  const focusable = modal.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  if (!focusable.length) return;

  const first = focusable[0];
  const last = focusable[focusable.length - 1];

  if (e.shiftKey && document.activeElement === first) {
    e.preventDefault();
    last.focus();
  } else if (!e.shiftKey && document.activeElement === last) {
    e.preventDefault();
    first.focus();
  }
});

/**
 * HTMX integration:
 * When modal content is loaded into #modal-content, open the modal.
 */
document.body.addEventListener('htmx:afterSwap', (e) => {
  if (e.detail.target && e.detail.target.id === 'modal-content') {
    openModal();
  }
});

/**
 * Server-triggered close (recommended):
 * Flask can respond with header: HX-Trigger: closeModal
 */
document.body.addEventListener('closeModal', closeModal);