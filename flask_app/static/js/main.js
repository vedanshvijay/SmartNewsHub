// Add any custom JavaScript here
console.log('PlanetPulse is running!');

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

    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Handle news filtering
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('[data-filter]');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const filterType = this.dataset.filter;
            const newsContainer = this.closest('.card').querySelector('.card-body');
            
            // Remove active class from all buttons in the same container
            this.closest('.news-filters').querySelectorAll('button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Here you would typically make an AJAX call to get filtered news
            // For now, we'll just show a loading state
            newsContainer.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            // Simulate API call
            setTimeout(() => {
                // Replace with actual API call
                console.log(`Filtering news by: ${filterType}`);
            }, 1000);
        });
    });
});

// Handle article actions (save and share)
document.addEventListener('DOMContentLoaded', function() {
    const articleActions = document.querySelectorAll('.article-actions');
    
    articleActions.forEach(actions => {
        // Save for later functionality
        const saveButton = actions.querySelector('[title="Save for later"]');
        if (saveButton) {
            saveButton.addEventListener('click', function() {
                const article = this.closest('.news-article');
                const articleId = article.dataset.articleId; // You'll need to add this data attribute
                
                // Toggle save state
                this.classList.toggle('active');
                this.querySelector('i').classList.toggle('far');
                this.querySelector('i').classList.toggle('fas');
                
                // Here you would typically make an AJAX call to save/unsave the article
                console.log(`Article ${articleId} saved/unsaved`);
            });
        }
        
        // Share functionality
        const shareButton = actions.querySelector('[title="Share"]');
        if (shareButton) {
            shareButton.addEventListener('click', function() {
                const article = this.closest('.news-article');
                const articleUrl = article.querySelector('a[target="_blank"]').href;
                const articleTitle = article.querySelector('h4').textContent;
                
                // Create share options
                const shareOptions = {
                    title: articleTitle,
                    url: articleUrl
                };
                
                // Use Web Share API if available
                if (navigator.share) {
                    navigator.share(shareOptions)
                        .catch(error => console.log('Error sharing:', error));
                } else {
                    // Fallback to copying to clipboard
                    navigator.clipboard.writeText(articleUrl)
                        .then(() => {
                            const tooltip = new bootstrap.Tooltip(this, {
                                title: 'Link copied to clipboard!',
                                trigger: 'manual'
                            });
                            tooltip.show();
                            setTimeout(() => tooltip.dispose(), 2000);
                        })
                        .catch(err => console.error('Failed to copy:', err));
                }
            });
        }
    });
});

// Handle newsletter subscription
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const emailInput = this.querySelector('input[type="email"]');
            const email = emailInput.value;
            
            // Here you would typically make an AJAX call to subscribe
            // For now, we'll just show a success message
            emailInput.value = '';
            const alert = document.createElement('div');
            alert.className = 'alert alert-success mt-3';
            alert.textContent = 'Thank you for subscribing!';
            this.appendChild(alert);
            
            setTimeout(() => alert.remove(), 3000);
        });
    }
});

// Load More functionality
document.addEventListener('DOMContentLoaded', function() {
    const loadMoreButtons = {
        'global': document.getElementById('load-more-global'),
        'indian': document.getElementById('load-more-indian')
    };

    Object.entries(loadMoreButtons).forEach(([type, button]) => {
        if (button) {
            button.addEventListener('click', function() {
                const page = parseInt(this.dataset.page);
                const container = document.getElementById(`${type}-news-container`);
                
                fetch(`/api/news/${type}?page=${page}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.articles && data.articles.length > 0) {
                            data.articles.forEach(article => {
                                const articleHtml = `
                                    <div class="news-article mb-4">
                                        <div class="article-image-container" style="height: 200px; overflow: hidden; margin-bottom: 1rem;">
                                            ${article.image_url ? 
                                                `<img src="${article.image_url}" alt="${article.title}" class="img-fluid rounded" style="width: 100%; height: 100%; object-fit: cover;">` :
                                                `<div class="no-image-placeholder bg-light rounded d-flex align-items-center justify-content-center" style="width: 100%; height: 100%;">
                                                    <i class="fas fa-newspaper fa-3x text-muted"></i>
                                                </div>`
                                            }
                                        </div>
                                        <h4 class="h5"><a href="${article.url}" target="_blank" class="text-decoration-none">${article.title}</a></h4>
                                        <p class="text-muted small">
                                            <i class="fas fa-newspaper me-1"></i>${article.source} 
                                            <i class="far fa-clock ms-2 me-1"></i>${article.published_at}
                                        </p>
                                        <p class="card-text">${article.description ? article.description.substring(0, 150) + '...' : 'No description available.'}</p>
                                        <div class="d-flex justify-content-between align-items-center">
                                            <a href="${article.url}" class="btn btn-sm btn-outline-${type === 'global' ? 'primary' : 'success'}" target="_blank">
                                                Read More <i class="fas fa-external-link-alt ms-1"></i>
                                            </a>
                                            <div class="article-actions">
                                                <button class="btn btn-sm btn-outline-secondary me-2" title="Save for later">
                                                    <i class="far fa-bookmark"></i>
                                                </button>
                                                <button class="btn btn-sm btn-outline-secondary" title="Share">
                                                    <i class="fas fa-share-alt"></i>
                                                </button>
                                            </div>
                                        </div>
                                        <hr class="my-3">
                                    </div>
                                `;
                                container.insertAdjacentHTML('beforeend', articleHtml);
                            });
                            
                            this.dataset.page = page + 1;
                            if (!data.has_more) {
                                this.style.display = 'none';
                            }
                        }
                    })
                    .catch(error => console.error('Error loading more news:', error));
            });
        }
    });
});

// Fix hover issues for buttons
document.addEventListener('DOMContentLoaded', function() {
    // Add hover effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.opacity = '0.8';
        });
        button.addEventListener('mouseleave', function() {
            this.style.opacity = '1';
        });
    });

    // Make sure icons are clickable
    const iconButtons = document.querySelectorAll('.article-actions button');
    iconButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            // Add your click handling logic here
            console.log('Button clicked:', this.title);
        });
    });
});

// Handle trending topics
document.addEventListener('DOMContentLoaded', function() {
    const trendingTopics = document.querySelectorAll('.trending-topics .badge');
    
    trendingTopics.forEach(topic => {
        topic.addEventListener('click', function(e) {
            const topicName = this.textContent.replace('#', '');
            
            // Update active state
            trendingTopics.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}); 