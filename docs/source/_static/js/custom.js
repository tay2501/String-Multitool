// Custom JavaScript for String-Multitool documentation

document.addEventListener('DOMContentLoaded', function() {
    console.log('String-Multitool documentation loaded');
    
    // Add copy buttons to code blocks
    addCopyButtons();
    
    // Improve external link handling
    handleExternalLinks();
    
    // Add scroll-to-top functionality
    addScrollToTop();
});

function addCopyButtons() {
    // Add copy buttons to code blocks
    const codeBlocks = document.querySelectorAll('.highlight pre');
    
    codeBlocks.forEach(function(block) {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = 'Copy';
        button.style.cssText = `
            position: absolute;
            top: 8px;
            right: 8px;
            background: #2980b9;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 3px;
            cursor: pointer;
            font-size: 12px;
        `;
        
        // Make parent relative for absolute positioning
        block.parentElement.style.position = 'relative';
        block.parentElement.appendChild(button);
        
        button.addEventListener('click', function() {
            const code = block.textContent;
            navigator.clipboard.writeText(code).then(function() {
                button.textContent = 'Copied!';
                button.style.background = '#27ae60';
                
                setTimeout(function() {
                    button.textContent = 'Copy';
                    button.style.background = '#2980b9';
                }, 2000);
            });
        });
    });
}

function handleExternalLinks() {
    // Open external links in new tab
    const links = document.querySelectorAll('a[href^="http"]');
    
    links.forEach(function(link) {
        if (!link.hostname.includes(window.location.hostname)) {
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
        }
    });
}

function addScrollToTop() {
    // Create scroll-to-top button
    const scrollButton = document.createElement('button');
    scrollButton.innerHTML = '↑';
    scrollButton.className = 'scroll-to-top';
    scrollButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: #2980b9;
        color: white;
        border: none;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        cursor: pointer;
        font-size: 18px;
        display: none;
        z-index: 1000;
        transition: opacity 0.3s;
    `;
    
    document.body.appendChild(scrollButton);
    
    // Show/hide button based on scroll position
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.style.display = 'block';
        } else {
            scrollButton.style.display = 'none';
        }
    });
    
    // Smooth scroll to top
    scrollButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + / for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        const searchInput = document.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
});