document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const navIndicator = document.getElementById('nav-indicator');
    const body = document.body;

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            const isActive = navMenu.classList.toggle('active');
            navToggle.classList.toggle('active', isActive);
            
            // 防止背景滚动
            if (isActive) {
                body.style.overflow = 'hidden';
            } else {
                body.style.overflow = '';
            }
        });
    }

    // Navigation Link Active State
    if (navLinks.length > 0) {
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navLinks.forEach(l => l.classList.remove('active'));
                this.classList.add('active');
                
                // 在移动端点击链接后关闭菜单
                if (navMenu.classList.contains('active')) {
                    navMenu.classList.remove('active');
                    navToggle.classList.remove('active');
                    body.style.overflow = '';
                }
            });
        });
    }

    // Navigation Indicator (Desktop only)
    if (navIndicator && window.innerWidth > 768) {
        const updateIndicator = (element) => {
            if (!element) return;
            const rect = element.getBoundingClientRect();
            const parentRect = element.parentElement.getBoundingClientRect();
            navIndicator.style.transform = `translateX(${rect.left - parentRect.left}px)`;
            navIndicator.style.width = `${rect.width}px`;
        };

        navLinks.forEach(link => {
            link.addEventListener('mouseenter', () => updateIndicator(link));
        });

        // Initialize with active link
        const activeLink = document.querySelector('.nav-link.active');
        if (activeLink) {
            updateIndicator(activeLink);
        }

        // Update on window resize
        let resizeTimer;
        window.addEventListener('resize', () => {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(() => {
                if (window.innerWidth <= 768) {
                    navIndicator.style.display = 'none';
                } else {
                    navIndicator.style.display = 'block';
                    updateIndicator(activeLink);
                }
            }, 250);
        });
    }

    // Smooth Scroll for Buttons
    const heroButtons = document.querySelectorAll('.btn');
    heroButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href && href.startsWith('#')) {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });

    // Scroll-based Header Shadow
    let ticking = false;
    window.addEventListener('scroll', function() {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                const header = document.querySelector('header');
                if (header) {
                    const scrollPosition = window.scrollY;
                    header.style.boxShadow = scrollPosition > 100 
                        ? '0 4px 30px rgba(0, 0, 0, 0.5)' 
                        : '0 4px 30px rgba(0, 0, 0, 0.3)';
                }
                ticking = false;
            });
            ticking = true;
        }
    });

    // Footer Logo Click to Top
    const footerLogo = document.querySelector('.footer-logo');
    if (footerLogo) {
        footerLogo.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Close mobile menu when clicking outside
    document.addEventListener('click', function(e) {
        if (navMenu && navMenu.classList.contains('active')) {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('active');
            }
        }
    });
});
