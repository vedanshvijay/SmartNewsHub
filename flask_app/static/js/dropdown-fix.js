// Fix for Bootstrap dropdown menu issues
document.addEventListener('DOMContentLoaded', function() {
    // Manual handling for dropdown menus
    const dropdownToggle = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggle.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Find the dropdown-menu associated with this button
            const parent = this.closest('.dropdown');
            const menu = parent.querySelector('.dropdown-menu');
            
            // Toggle the menu
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            } else {
                // Close all other menus first
                document.querySelectorAll('.dropdown-menu').forEach(m => {
                    m.style.display = 'none';
                });
                
                // Calculate position
                const buttonRect = this.getBoundingClientRect();
                menu.style.position = 'absolute';
                menu.style.top = (buttonRect.bottom + window.scrollY) + 'px';
                menu.style.left = (buttonRect.left + window.scrollX) + 'px';
                
                // Check if we need to align right
                if (menu.classList.contains('dropdown-menu-end')) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                }
                
                menu.style.display = 'block';
                menu.style.zIndex = '1030';
            }
        });
    });
    
    // Close menus when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.style.display = 'none';
            });
        }
    });
}); 