// Advanced Custom Dropdown Implementation
// Moves the dropdown menu to the body and positions it below the button

document.addEventListener('DOMContentLoaded', function() {
    const dropdownButtons = document.querySelectorAll('.category-btn');
    let openDropdown = null;
    let openButton = null;

    function positionDropdown(content, button) {
        const rect = button.getBoundingClientRect();
        content.style.left = rect.left + window.scrollX + 'px';
        content.style.top = rect.bottom + window.scrollY + 'px';
        content.style.minWidth = rect.width + 'px';
    }

    dropdownButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();

            // Find the parent dropdown container
            const dropdown = this.closest('.category-dropdown');
            const content = dropdown.querySelector('.category-content');

            // Close any open dropdowns
            document.querySelectorAll('.category-content.open').forEach(el => {
                el.classList.remove('open');
                if (el.parentNode === document.body && el !== content) {
                    if (el._originalParent) {
                        el._originalParent.appendChild(el);
                        el._originalParent = null;
                    }
                }
            });

            if (content.classList.contains('open')) {
                content.classList.remove('open');
                if (content.parentNode === document.body && content._originalParent) {
                    content._originalParent.appendChild(content);
                    content._originalParent = null;
                }
                openDropdown = null;
                openButton = null;
                return;
            }

            // Move the dropdown to the body
            if (content.parentNode !== document.body) {
                content._originalParent = content.parentNode;
                document.body.appendChild(content);
            }

            // Position the dropdown
            positionDropdown(content, this);
            content.classList.add('open');
            openDropdown = content;
            openButton = this;
        });
    });

    // Only close dropdowns when clicking outside
    document.addEventListener('mousedown', function(e) {
        if (openDropdown && !e.target.closest('.category-content') && !e.target.closest('.category-btn')) {
            openDropdown.classList.remove('open');
            if (openDropdown.parentNode === document.body && openDropdown._originalParent) {
                openDropdown._originalParent.appendChild(openDropdown);
                openDropdown._originalParent = null;
            }
            openDropdown = null;
            openButton = null;
        }
    });

    // On window scroll/resize, reposition the dropdown if open
    window.addEventListener('scroll', function() {
        if (openDropdown && openButton) {
            positionDropdown(openDropdown, openButton);
        }
    });
    window.addEventListener('resize', function() {
        if (openDropdown && openButton) {
            positionDropdown(openDropdown, openButton);
        }
    });
}); 