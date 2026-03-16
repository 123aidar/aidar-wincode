/**
 * AutoService Pro — Core Application JavaScript
 * Handles: sidebar toggle, loading screen, dropdown menus, form validation,
 * smooth page transitions, and general UI interactivity.
 */

document.addEventListener('DOMContentLoaded', function () {

    // ════════════════════════════════════════════════════════════════
    // Loading Screen — fade out after page load
    // ════════════════════════════════════════════════════════════════
    const loader = document.getElementById('loadingOverlay');
    if (loader) {
        setTimeout(() => {
            loader.classList.add('hidden');
        }, 400);
    }

    // ════════════════════════════════════════════════════════════════
    // Sidebar Toggle (mobile & desktop)
    // ════════════════════════════════════════════════════════════════
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebarToggle');
    const collapseBtn = document.getElementById('sidebarCollapseBtn');

    // Restore saved state
    if (sidebar && localStorage.getItem('sidebarCollapsed') === '1') {
        sidebar.classList.add('collapsed');
    }

    function toggleSidebar() {
        if (!sidebar) return;
        sidebar.classList.toggle('collapsed');
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed') ? '1' : '0');
    }

    if (toggleBtn) toggleBtn.addEventListener('click', toggleSidebar);
    if (collapseBtn) collapseBtn.addEventListener('click', toggleSidebar);

    // ════════════════════════════════════════════════════════════════
    // Animated Card Entry — Intersection Observer
    // ════════════════════════════════════════════════════════════════
    const animatedCards = document.querySelectorAll('.glass-card, .stat-card, .chart-card');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });

        animatedCards.forEach(card => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(card);
        });
    }

    // ════════════════════════════════════════════════════════════════
    // Form Validation — highlight invalid fields with glow
    // ════════════════════════════════════════════════════════════════
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = 'var(--accent-red)';
                    field.style.boxShadow = '0 0 0 3px rgba(239,68,68,0.2)';
                    // Shake animation
                    field.style.animation = 'shake 0.4s ease';
                    setTimeout(() => { field.style.animation = ''; }, 400);
                } else {
                    field.style.borderColor = '';
                    field.style.boxShadow = '';
                }
            });
            if (!isValid) {
                e.preventDefault();
            }
        });
    });

    // Clear validation styles on input
    document.querySelectorAll('.form-input, .form-select, .form-textarea').forEach(input => {
        input.addEventListener('input', function () {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    });

    // ════════════════════════════════════════════════════════════════
    // Table Row Hover Glow
    // ════════════════════════════════════════════════════════════════
    document.querySelectorAll('.data-table tbody tr').forEach(row => {
        row.addEventListener('mouseenter', function () {
            this.style.background = 'rgba(59, 130, 246, 0.05)';
        });
        row.addEventListener('mouseleave', function () {
            this.style.background = '';
        });
    });

    // ════════════════════════════════════════════════════════════════
    // Keyboard shortcut — Ctrl+K for search focus
    // ════════════════════════════════════════════════════════════════
    document.addEventListener('keydown', function (e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-bar input');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
    });

    // ════════════════════════════════════════════════════════════════
    // Smooth number counter animation for stat values
    // ════════════════════════════════════════════════════════════════
    document.querySelectorAll('.stat-value').forEach(el => {
        const text = el.textContent.trim();
        const numMatch = text.match(/[\d,]+/);
        if (numMatch) {
            const target = parseInt(numMatch[0].replace(/,/g, ''));
            const prefix = text.substring(0, text.indexOf(numMatch[0]));
            const suffix = text.substring(text.indexOf(numMatch[0]) + numMatch[0].length);
            if (target > 0 && target < 1000000) {
                el.textContent = prefix + '0' + suffix;
                animateCounter(el, 0, target, 800, prefix, suffix);
            }
        }
    });

    function animateCounter(element, start, end, duration, prefix, suffix) {
        const startTime = performance.now();
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = Math.floor(start + (end - start) * eased);
            element.textContent = prefix + current.toLocaleString() + suffix;
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        requestAnimationFrame(update);
    }
});
