/**
 * AutoService Pro — Animations Module
 * Smooth entrance, hover and page-transition animations.
 */

(function () {
    'use strict';

    /* ---- Intersection Observer: fade-slide-in on scroll ---- */
    const animatedEls = document.querySelectorAll(
        '.card, .stat-card, .table-container, .form-container, .detail-section'
    );

    if ('IntersectionObserver' in window) {
        const io = new IntersectionObserver((entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.08 });

        animatedEls.forEach((el, i) => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(24px)';
            el.style.transitionDelay = `${i * 60}ms`;
            io.observe(el);
        });
    } else {
        // fallback — show everything immediately
        animatedEls.forEach((el) => el.classList.add('animate-in'));
    }

    /* ---- CSS class for the observer ---- */
    const style = document.createElement('style');
    style.textContent = `
        .animate-in {
            opacity: 1 !important;
            transform: translateY(0) !important;
            transition: opacity .5s cubic-bezier(.22,1,.36,1),
                        transform .5s cubic-bezier(.22,1,.36,1);
        }
    `;
    document.head.appendChild(style);

    /* ---- Magnetic hover for buttons ---- */
    document.querySelectorAll('.btn').forEach((btn) => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const dx = e.clientX - (rect.left + rect.width / 2);
            const dy = e.clientY - (rect.top + rect.height / 2);
            btn.style.transform = `translate(${dx * 0.15}px, ${dy * 0.15}px)`;
        });
        btn.addEventListener('mouseleave', () => {
            btn.style.transform = '';
        });
    });

    /* ---- Parallax tilt for cards on hover ---- */
    document.querySelectorAll('.stat-card').forEach((card) => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;
            card.style.transform = `perspective(600px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) scale(1.02)`;
        });
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
        });
    });

    /* ---- Ripple effect on button click ---- */
    document.querySelectorAll('.btn').forEach((btn) => {
        btn.style.position = 'relative';
        btn.style.overflow = 'hidden';
        btn.addEventListener('click', (e) => {
            const circle = document.createElement('span');
            const d = Math.max(btn.clientWidth, btn.clientHeight);
            const rect = btn.getBoundingClientRect();
            circle.style.cssText = `
                width:${d}px; height:${d}px;
                left:${e.clientX - rect.left - d / 2}px;
                top:${e.clientY - rect.top - d / 2}px;
                position:absolute; border-radius:50%;
                background:rgba(255,255,255,0.25);
                transform:scale(0); pointer-events:none;
                animation:ripple-anim .5s ease-out forwards;
            `;
            btn.appendChild(circle);
            setTimeout(() => circle.remove(), 600);
        });
    });

    const rippleStyle = document.createElement('style');
    rippleStyle.textContent = `
        @keyframes ripple-anim {
            to { transform: scale(2.5); opacity: 0; }
        }
    `;
    document.head.appendChild(rippleStyle);

    /* ---- Smooth page transition on navigation ---- */
    document.querySelectorAll('a:not([target="_blank"]):not([href^="#"]):not([href^="javascript"])').forEach((a) => {
        a.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (!href || href.startsWith('#')) return;
            e.preventDefault();
            document.body.style.transition = 'opacity .2s ease';
            document.body.style.opacity = '0';
            setTimeout(() => { window.location.href = href; }, 200);
        });
    });

    window.addEventListener('pageshow', () => {
        document.body.style.transition = 'opacity .3s ease';
        document.body.style.opacity = '1';
    });
})();
