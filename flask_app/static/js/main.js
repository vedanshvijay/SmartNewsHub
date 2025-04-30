// Add any custom JavaScript here
console.log('SmartNewsHub is running!');

document.addEventListener('DOMContentLoaded', function() {
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
    
    // Fact card interactions
    const factCard = document.querySelector('.fact-card');
    const refreshButton = document.querySelector('.fact-refresh');
    const shareButton = document.querySelector('.fact-share');

    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            // Add spinning animation
            this.classList.add('spinning');
            
            // Fetch new fact
            fetch('/api/fact/random')
                .then(response => response.json())
                .then(data => {
                    // Update fact content
                    document.querySelector('.fact-text').textContent = data.text;
                    document.querySelector('.fact-source span').textContent = data.source;
                    
                    // Update source link if available
                    const sourceLink = document.querySelector('.fact-link');
                    if (data.permalink) {
                        sourceLink.href = data.permalink;
                        sourceLink.style.display = 'flex';
                    } else {
                        sourceLink.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Error fetching new fact:', error);
                })
                .finally(() => {
                    // Remove spinning animation
                    this.classList.remove('spinning');
                });
        });
    }

    if (shareButton) {
        shareButton.addEventListener('click', function() {
            const factText = document.querySelector('.fact-text').textContent;
            const shareData = {
                title: 'Did You Know?',
                text: factText,
                url: window.location.href
            };

            if (navigator.share) {
                navigator.share(shareData)
                    .catch(error => console.error('Error sharing:', error));
            } else {
                // Fallback for browsers that don't support Web Share API
                const tempInput = document.createElement('input');
                tempInput.value = `${shareData.text}\n\n${shareData.url}`;
                document.body.appendChild(tempInput);
                tempInput.select();
                document.execCommand('copy');
                document.body.removeChild(tempInput);
                
                // Show copied notification
                const originalText = this.innerHTML;
                this.innerHTML = '<i class="fas fa-check"></i> Copied!';
                setTimeout(() => {
                    this.innerHTML = originalText;
                }, 2000);
            }
        });
    }

    // Add hover effect to fact card
    if (factCard) {
        factCard.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });

        factCard.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    }

    // Handle Load More for Global News
    const loadMoreGlobalBtn = document.getElementById('load-more-global');
    if (loadMoreGlobalBtn) {
        loadMoreGlobalBtn.addEventListener('click', function() {
            loadMoreNews('global');
        });
    }

    // Handle Load More for Indian News
    const loadMoreIndianBtn = document.getElementById('load-more-indian');
    if (loadMoreIndianBtn) {
        loadMoreIndianBtn.addEventListener('click', function() {
            loadMoreNews('indian');
        });
    }

    // Function to load more news
    function loadMoreNews(type) {
        const url = `/api/news/${type}`;
        const loadBtn = document.getElementById(`load-more-${type}`);
        const container = document.getElementById(`${type}-news-container`);
        
        // Show loading state
        loadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        loadBtn.disabled = true;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.articles && data.articles.length > 0) {
                    data.articles.forEach(article => {
                        const articleDiv = document.createElement('div');
                        articleDiv.className = 'news-article mb-4';
                        
                        let html = '';
                        
                        if (article.image_url) {
                            html += `<img src="${article.image_url}" alt="${article.title}" class="img-fluid mb-2 rounded">`;
                        }
                        
                        html += `
                            <h4 class="h5"><a href="${article.url}" target="_blank" class="text-decoration-none">${article.title}</a></h4>
                            <p class="text-muted small">
                                <i class="fas fa-newspaper me-1"></i>${article.source} 
                                <i class="far fa-clock ms-2 me-1"></i>${article.published_at || 'N/A'}
                            </p>
                        `;
                        
                        if (article.description) {
                            html += `<p class="card-text">${article.description.length > 150 ? article.description.substring(0, 150) + '...' : article.description}</p>`;
                        } else {
                            html += `<p class="card-text text-muted">No description available.</p>`;
                        }
                        
                        // Add read more button matching the styling of the existing articles
                        const btnClass = type === 'global' ? 'btn-outline-primary' : 'btn-outline-success';
                        html += `
                            <a href="${article.url}" class="btn btn-sm ${btnClass}" target="_blank">
                                Read More <i class="fas fa-external-link-alt ms-1"></i>
                            </a>
                            <hr class="my-3">
                        `;
                        
                        articleDiv.innerHTML = html;
                        container.appendChild(articleDiv);
                    });
                    
                    // Restore button if there are more results
                    if (data.has_more) {
                        loadBtn.innerHTML = '<i class="fas fa-plus-circle me-1"></i>Load More';
                        loadBtn.disabled = false;
                    } else {
                        loadBtn.innerHTML = 'No More Articles';
                        loadBtn.disabled = true;
                    }
                } else {
                    loadBtn.innerHTML = 'No More Articles';
                    loadBtn.disabled = true;
                }
            })
            .catch(error => {
                console.error(`Error loading more ${type} news:`, error);
                loadBtn.innerHTML = '<i class="fas fa-exclamation-circle me-1"></i>Try Again';
                loadBtn.disabled = false;
            });
    }
}); 