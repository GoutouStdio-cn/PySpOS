document.addEventListener('DOMContentLoaded', function() {
    // 主题切换功能
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = themeToggle?.querySelector('i');
    const body = document.body;
    
    // 从 localStorage 读取主题偏好
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.add('light-theme');
        if (themeIcon) {
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }
    
    // 主题切换按钮点击事件
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const icon = themeToggle.querySelector('i');
            
            // 添加过渡效果
            if (icon) {
                // 先缩小消失
                icon.classList.add('icon-transition');
                
                // 等图标消失后切换，然后再淡入
                setTimeout(() => {
                    body.classList.toggle('light-theme');
                    
                    // 更新图标
                    const isLight = body.classList.contains('light-theme');
                    if (icon) {
                        icon.className = isLight ? 'far fa-sun' : 'far fa-moon';
                    }
                    
                    // 保存到 localStorage
                    localStorage.setItem('theme', isLight ? 'light' : 'dark');
                    
                    // 移除过渡类，让图标重新显示
                    icon.classList.remove('icon-transition');
                }, 150);
            } else {
                // 如果没有图标，直接切换
                body.classList.toggle('light-theme');
                const isLight = body.classList.contains('light-theme');
                localStorage.setItem('theme', isLight ? 'light' : 'dark');
            }
        });
    }
    
    // Mobile Navigation Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const navIndicator = document.getElementById('nav-indicator');

    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            const isActive = navMenu.classList.toggle('active');
            if (isActive) {
                navToggle.classList.add('active');
                body.style.overflow = 'hidden';
            } else {
                navToggle.classList.remove('active');
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
                navToggle.classList.remove('active');
                body.style.overflow = '';
            }
        }
    });

    // 毛玻璃效果通过 CSS 的 backdrop-filter 实现，无需额外 JavaScript
});
