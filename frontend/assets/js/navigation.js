/**
 * Navigation JavaScript
 * Handles responsive navigation, hamburger menu, and mobile sidebar
 */

class Navigation {
    constructor() {
        this.hamburgerBtn = null;
        this.mobileOverlay = null;
        this.mobileSidebar = null;
        this.isOpen = false;

        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        // Get elements
        this.hamburgerBtn = document.getElementById('hamburgerBtn');
        this.mobileOverlay = document.getElementById('mobileMenuOverlay');
        this.mobileSidebar = document.getElementById('mobileSidebar');

        if (!this.hamburgerBtn || !this.mobileOverlay || !this.mobileSidebar) {
            return; // Elements not found, navigation not needed on this page
        }

        // Add event listeners
        this.hamburgerBtn.addEventListener('click', () => this.toggle());
        this.mobileOverlay.addEventListener('click', () => this.close());

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 768 && this.isOpen) {
                this.close();
            }
        });

        // Add navbar scroll effect
        this.setupScrollEffect();

        // Set active menu item
        this.setActiveMenuItem();
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        this.isOpen = true;
        this.hamburgerBtn.classList.add('active');
        this.mobileOverlay.classList.add('active');
        this.mobileSidebar.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent background scroll
    }

    close() {
        this.isOpen = false;
        this.hamburgerBtn.classList.remove('active');
        this.mobileOverlay.classList.remove('active');
        this.mobileSidebar.classList.remove('active');
        document.body.style.overflow = ''; // Restore scroll
    }

    setupScrollEffect() {
        const navbar = document.querySelector('.top-navbar');
        if (!navbar) return;

        let lastScroll = 0;

        window.addEventListener('scroll', () => {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScroll = currentScroll;
        });
    }

    setActiveMenuItem() {
        const currentPath = window.location.pathname;

        // Desktop menu
        const desktopLinks = document.querySelectorAll('.navbar-menu-link');
        desktopLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath ||
                currentPath.includes(link.getAttribute('href'))) {
                link.classList.add('active');
            }
        });

        // Mobile menu
        const mobileLinks = document.querySelectorAll('.mobile-menu-link');
        mobileLinks.forEach(link => {
            if (link.getAttribute('href') === currentPath ||
                currentPath.includes(link.getAttribute('href'))) {
                link.classList.add('active');
            }
        });
    }
}

// Initialize navigation
const nav = new Navigation();

// Export for use in other scripts if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Navigation;
}
