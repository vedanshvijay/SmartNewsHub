// Advanced Custom Dropdown Implementation
// Moves the dropdown menu to the body and positions it below the button

document.addEventListener('DOMContentLoaded', function() {
    // Handle category dropdown
    const categoryBtn = document.querySelector('.category-btn');
    const categoryContent = document.querySelector('.category-content');
    
    if (categoryBtn && categoryContent) {
        categoryBtn.addEventListener('click', function(e) {
            e.preventDefault();
            categoryContent.classList.toggle('show');
            
            // Toggle chevron icon
            const chevron = this.querySelector('.fa-chevron-down');
            chevron.classList.toggle('fa-chevron-up');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(e) {
            if (!categoryBtn.contains(e.target) && !categoryContent.contains(e.target)) {
                categoryContent.classList.remove('show');
                const chevron = categoryBtn.querySelector('.fa-chevron-down');
                chevron.classList.remove('fa-chevron-up');
            }
        });
        
        // Handle category selection
        const categoryItems = categoryContent.querySelectorAll('.category-item');
        categoryItems.forEach(item => {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                const category = this.textContent.trim();
                
                // Update button text
                categoryBtn.querySelector('span').textContent = category;
                
                // Close dropdown
                categoryContent.classList.remove('show');
                const chevron = categoryBtn.querySelector('.fa-chevron-down');
                chevron.classList.remove('fa-chevron-up');
                
                // Here you would typically make an AJAX call to filter news by category
                console.log(`Filtering news by category: ${category}`);
                
                // Show loading state
                const newsContainer = document.querySelector('#global-news-container, #indian-news-container');
                if (newsContainer) {
                    newsContainer.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
                }
            });
        });
    }
    
    // Add fade-in animation to news articles
    const newsArticles = document.querySelectorAll('.news-article');
    newsArticles.forEach((article, index) => {
        article.style.animationDelay = `${index * 0.1}s`;
        article.classList.add('fade-in');
    });
    
    // Handle responsive adjustments
    function handleResponsive() {
        const navbar = document.querySelector('.navbar');
        const searchForm = document.querySelector('.navbar .d-flex');
        
        if (window.innerWidth < 768) {
            if (searchForm) {
                searchForm.classList.add('mt-3');
            }
        } else {
            if (searchForm) {
                searchForm.classList.remove('mt-3');
            }
        }
    }
    
    // Initial call and event listener for responsive adjustments
    handleResponsive();
    window.addEventListener('resize', handleResponsive);

    // Initialize all Bootstrap dropdowns
    const dropdownElementList = document.querySelectorAll('.dropdown-toggle');
    const dropdownList = [...dropdownElementList].map(dropdownToggleEl => {
        return new bootstrap.Dropdown(dropdownToggleEl, {
            autoClose: true
        });
    });
    
    // Dropdown show/hide handling for better positioning
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const menu = dropdown.querySelector('.dropdown-menu');
        
        if (toggle && menu) {
            toggle.addEventListener('click', function(e) {
                // Toggle visibility with proper positioning
                if (menu.classList.contains('show')) {
                    menu.classList.remove('show');
                } else {
                    // Close any open dropdowns
                    document.querySelectorAll('.dropdown-menu.show').forEach(openMenu => {
                        openMenu.classList.remove('show');
                    });
                    
                    // Position and show this dropdown
                    menu.classList.add('show');
                    
                    // Ensure dropdown is fully visible
                    const rect = menu.getBoundingClientRect();
                    const windowHeight = window.innerHeight;
                    
                    if (rect.bottom > windowHeight) {
                        menu.style.maxHeight = (windowHeight - rect.top - 20) + 'px';
                    }
                }
                
                e.stopPropagation();
            });
        }
    });
    
    // Close dropdowns when clicking elsewhere on the page
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}); 