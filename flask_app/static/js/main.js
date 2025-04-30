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
}); 