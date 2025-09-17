/**
 * Custom JavaScript for String-Multitool Documentation
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize custom features
    initPerformanceMetrics();
    initCodeCopyButtons();
    initAPIReferenceEnhancements();
    initSearchEnhancements();
    initThemeToggle();
    initTableEnhancements();
});

/**
 * Initialize performance metrics display
 */
function initPerformanceMetrics() {
    const performanceTables = document.querySelectorAll('table.docutils');

    performanceTables.forEach(table => {
        // Check if table contains performance data
        const headers = Array.from(table.querySelectorAll('th')).map(th => th.textContent.toLowerCase());
        if (headers.includes('execution time') || headers.includes('memory usage')) {
            table.classList.add('performance');

            // Add visual indicators for performance values
            const cells = table.querySelectorAll('td');
            cells.forEach(cell => {
                const text = cell.textContent.trim();

                // Highlight fast execution times
                if (text.includes('<1ms') || text.includes('<10ms')) {
                    cell.classList.add('performance-excellent');
                    cell.style.backgroundColor = '#e8f5e8';
                    cell.style.color = '#27ae60';
                    cell.style.fontWeight = 'bold';
                }

                // Highlight memory efficiency
                if (text.includes('65%') || text.includes('76%')) {
                    cell.classList.add('performance-improvement');
                    cell.style.backgroundColor = '#e1f5fe';
                    cell.style.color = '#2980b9';
                    cell.style.fontWeight = 'bold';
                }
            });
        }
    });
}

/**
 * Add copy buttons to code blocks
 */
function initCodeCopyButtons() {
    const codeBlocks = document.querySelectorAll('.highlight');

    codeBlocks.forEach((block, index) => {
        // Skip if already has copy button
        if (block.querySelector('.copy-button')) return;

        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.textContent = 'Copy';
        copyButton.title = 'Copy to clipboard';

        // Style the button
        copyButton.style.cssText = `
            position: absolute;
            top: 0.5em;
            right: 0.5em;
            background: #2980b9;
            color: white;
            border: none;
            padding: 0.3em 0.6em;
            border-radius: 3px;
            cursor: pointer;
            font-size: 0.8em;
            opacity: 0.7;
            transition: opacity 0.2s;
            z-index: 10;
        `;

        // Make parent relative for absolute positioning
        block.style.position = 'relative';

        // Add click handler
        copyButton.addEventListener('click', function() {
            const code = block.querySelector('pre').textContent;
            navigator.clipboard.writeText(code).then(() => {
                copyButton.textContent = 'Copied!';
                copyButton.style.backgroundColor = '#27ae60';

                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                    copyButton.style.backgroundColor = '#2980b9';
                }, 2000);
            }).catch(err => {
                console.error('Failed to copy code:', err);
                copyButton.textContent = 'Failed';
                setTimeout(() => {
                    copyButton.textContent = 'Copy';
                }, 2000);
            });
        });

        // Show/hide button on hover
        block.addEventListener('mouseenter', () => {
            copyButton.style.opacity = '1';
        });

        block.addEventListener('mouseleave', () => {
            copyButton.style.opacity = '0.7';
        });

        block.appendChild(copyButton);
    });
}

/**
 * Enhance API reference sections
 */
function initAPIReferenceEnhancements() {
    // Add anchors to function/class definitions
    const definitions = document.querySelectorAll('dl.class > dt, dl.function > dt, dl.method > dt');

    definitions.forEach(dt => {
        const id = dt.id;
        if (id) {
            // Add permalink icon
            const permalink = document.createElement('a');
            permalink.className = 'permalink';
            permalink.href = '#' + id;
            permalink.textContent = '¶';
            permalink.title = 'Permalink to this definition';
            permalink.style.cssText = `
                color: #ccc;
                font-size: 0.8em;
                margin-left: 0.5em;
                text-decoration: none;
                opacity: 0;
                transition: opacity 0.2s;
            `;

            dt.addEventListener('mouseenter', () => {
                permalink.style.opacity = '1';
            });

            dt.addEventListener('mouseleave', () => {
                permalink.style.opacity = '0';
            });

            dt.appendChild(permalink);
        }
    });

    // Enhance autosummary tables
    const autosummaryTables = document.querySelectorAll('table.autosummary');
    autosummaryTables.forEach(table => {
        // Add sortable functionality
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            if (index === 0) { // Only make first column sortable
                header.style.cursor = 'pointer';
                header.title = 'Click to sort';

                header.addEventListener('click', () => {
                    sortTable(table, index);
                });
            }
        });
    });
}

/**
 * Sort table by column
 */
function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    const sortedRows = rows.sort((a, b) => {
        const aText = a.cells[column].textContent.trim();
        const bText = b.cells[column].textContent.trim();
        return aText.localeCompare(bText);
    });

    // Re-append sorted rows
    sortedRows.forEach(row => tbody.appendChild(row));
}

/**
 * Enhance search functionality
 */
function initSearchEnhancements() {
    const searchInput = document.querySelector('input[name="q"]');
    if (!searchInput) return;

    // Add search suggestions
    let searchTimeout;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = this.value.toLowerCase();
            if (query.length > 2) {
                highlightSearchTerms(query);
            }
        }, 300);
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K to focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            searchInput.focus();
        }
    });
}

/**
 * Highlight search terms in content
 */
function highlightSearchTerms(query) {
    // Remove existing highlights
    const existingHighlights = document.querySelectorAll('.search-highlight');
    existingHighlights.forEach(el => {
        el.outerHTML = el.innerHTML;
    });

    if (query.length < 3) return;

    // Find and highlight new terms
    const content = document.querySelector('.rst-content');
    if (!content) return;

    const walker = document.createTreeWalker(
        content,
        NodeFilter.SHOW_TEXT,
        {
            acceptNode: function(node) {
                // Skip script and style nodes
                if (node.parentNode.tagName === 'SCRIPT' ||
                    node.parentNode.tagName === 'STYLE') {
                    return NodeFilter.FILTER_REJECT;
                }
                return NodeFilter.FILTER_ACCEPT;
            }
        }
    );

    const textNodes = [];
    let node;
    while (node = walker.nextNode()) {
        if (node.textContent.toLowerCase().includes(query)) {
            textNodes.push(node);
        }
    }

    textNodes.forEach(textNode => {
        const regex = new RegExp(`(${query})`, 'gi');
        const highlighted = textNode.textContent.replace(regex, '<span class="search-highlight" style="background-color: yellow; padding: 0.1em 0.2em;">$1</span>');

        if (highlighted !== textNode.textContent) {
            const span = document.createElement('span');
            span.innerHTML = highlighted;
            textNode.parentNode.replaceChild(span, textNode);
        }
    });
}

/**
 * Initialize theme toggle
 */
function initThemeToggle() {
    // Create theme toggle button
    const toggleButton = document.createElement('button');
    toggleButton.innerHTML = '🌓';
    toggleButton.title = 'Toggle dark/light theme';
    toggleButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        border: none;
        background: #2980b9;
        color: white;
        font-size: 1.2em;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 1000;
        transition: all 0.3s;
    `;

    toggleButton.addEventListener('click', () => {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');

        // Update button
        toggleButton.innerHTML = isDark ? '☀️' : '🌙';
        toggleButton.style.transform = 'rotate(360deg)';
        setTimeout(() => {
            toggleButton.style.transform = 'rotate(0deg)';
        }, 300);
    });

    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        toggleButton.innerHTML = '☀️';
    }

    document.body.appendChild(toggleButton);
}

/**
 * Enhance table functionality
 */
function initTableEnhancements() {
    const tables = document.querySelectorAll('table.docutils');

    tables.forEach(table => {
        // Add responsive wrapper
        if (!table.parentNode.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            wrapper.style.cssText = `
                overflow-x: auto;
                margin: 1em 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            `;

            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }

        // Add row hover effects
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            row.addEventListener('mouseenter', function() {
                this.style.backgroundColor = '#f5f5f5';
            });

            row.addEventListener('mouseleave', function() {
                this.style.backgroundColor = '';
            });
        });

        // Add column highlighting for performance tables
        if (table.classList.contains('performance')) {
            const cells = table.querySelectorAll('td, th');
            cells.forEach(cell => {
                cell.addEventListener('mouseenter', function() {
                    const columnIndex = Array.from(this.parentNode.children).indexOf(this);
                    const columnCells = table.querySelectorAll(`td:nth-child(${columnIndex + 1}), th:nth-child(${columnIndex + 1})`);

                    columnCells.forEach(c => {
                        c.style.backgroundColor = '#e3f2fd';
                    });
                });

                cell.addEventListener('mouseleave', function() {
                    const columnIndex = Array.from(this.parentNode.children).indexOf(this);
                    const columnCells = table.querySelectorAll(`td:nth-child(${columnIndex + 1}), th:nth-child(${columnIndex + 1})`);

                    columnCells.forEach(c => {
                        c.style.backgroundColor = '';
                    });
                });
            });
        }
    });
}

/**
 * Add smooth scrolling for internal links
 */
document.addEventListener('click', function(e) {
    if (e.target.tagName === 'A' && e.target.getAttribute('href').startsWith('#')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });

            // Update URL
            history.pushState(null, null, '#' + targetId);
        }
    }
});

/**
 * Initialize table of contents enhancements
 */
function initTOCEnhancements() {
    const tocLinks = document.querySelectorAll('.wy-menu a');

    tocLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            tocLinks.forEach(l => l.classList.remove('current'));

            // Add active class to clicked link
            this.classList.add('current');

            // Store in session storage
            sessionStorage.setItem('activeTOCLink', this.href);
        });
    });

    // Restore active link on page load
    const activeLink = sessionStorage.getItem('activeTOCLink');
    if (activeLink) {
        const link = document.querySelector(`.wy-menu a[href="${activeLink}"]`);
        if (link) {
            link.classList.add('current');
        }
    }
}

// Initialize TOC enhancements
document.addEventListener('DOMContentLoaded', initTOCEnhancements);

/**
 * Performance monitoring for page load
 */
window.addEventListener('load', function() {
    // Log performance metrics
    if ('performance' in window) {
        const loadTime = performance.now();
        console.log(`Documentation page loaded in ${loadTime.toFixed(2)}ms`);

        // Add performance info to footer if available
        const footer = document.querySelector('.rst-footer-buttons');
        if (footer && loadTime > 1000) {
            const perfInfo = document.createElement('div');
            perfInfo.style.cssText = `
                font-size: 0.8em;
                color: #666;
                text-align: center;
                margin-top: 1em;
            `;
            perfInfo.textContent = `Page loaded in ${(loadTime / 1000).toFixed(2)}s`;
            footer.appendChild(perfInfo);
        }
    }
});