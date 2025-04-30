// Add any custom JavaScript here
console.log('SmartNewsHub is running!');

document.addEventListener('DOMContentLoaded', function() {
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
            const page = parseInt(this.getAttribute('data-page'));
            loadMoreNews('global', page);
            this.setAttribute('data-page', page + 1);
        });
    }

    // Handle Load More for Indian News
    const loadMoreIndianBtn = document.getElementById('load-more-indian');
    if (loadMoreIndianBtn) {
        loadMoreIndianBtn.addEventListener('click', function() {
            const page = parseInt(this.getAttribute('data-page'));
            loadMoreNews('indian', page);
            this.setAttribute('data-page', page + 1);
        });
    }

    // Function to load more news
    function loadMoreNews(type, page) {
        const url = `/api/news/${type}?page=${page}&page_size=10`;
        const loadBtn = document.getElementById(`load-more-${type}`);
        loadBtn.textContent = 'Loading...';
        loadBtn.disabled = true;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                const container = document.getElementById(`${type}-news-container`);
                
                if (data.articles && data.articles.length > 0) {
                    data.articles.forEach(article => {
                        const articleDiv = document.createElement('div');
                        articleDiv.className = 'news-article mb-4';
                        
                        let html = '';
                        
                        if (article.image_url) {
                            html += `<img src="${article.image_url}" alt="${article.title}" class="img-fluid mb-2 rounded">`;
                        }
                        
                        html += `
                            <h4><a href="${article.url}" target="_blank">${article.title}</a></h4>
                            <p class="text-muted">
                                <small>Source: ${article.source} | ${article.published_at || 'N/A'}</small>
                            </p>
                        `;
                        
                        if (article.description) {
                            html += `<p>${article.description.length > 150 ? article.description.substring(0, 150) + '...' : article.description}</p>`;
                        } else {
                            html += `<p>No description available.</p>`;
                        }
                        
                        articleDiv.innerHTML = html;
                        container.appendChild(articleDiv);
                    });
                    
                    loadBtn.textContent = 'Load More';
                    loadBtn.disabled = false;
                    
                    if (!data.has_more) {
                        loadBtn.textContent = 'No More Articles';
                        loadBtn.disabled = true;
                    }
                } else {
                    loadBtn.textContent = 'No More Articles';
                    loadBtn.disabled = true;
                }
            })
            .catch(error => {
                console.error(`Error loading more ${type} news:`, error);
                loadBtn.textContent = 'Try Again';
                loadBtn.disabled = false;
            });
    }
}); 