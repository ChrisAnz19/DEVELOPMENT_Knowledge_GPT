/**
 * Avatar Component for LinkedIn Photo Initials Fallback
 * 
 * This component handles rendering of both LinkedIn profile photos and initials avatars
 * with automatic fallback behavior when photos fail to load.
 */

class AvatarRenderer {
    constructor() {
        this.defaultSize = 200;
        this.retryAttempts = 2;
        this.retryDelay = 1000; // 1 second
    }

    /**
     * Render an avatar based on candidate data
     * @param {Object} candidate - Candidate data with avatar information
     * @param {Object} options - Rendering options (size, className, etc.)
     * @returns {HTMLElement} - Avatar DOM element
     */
    renderAvatar(candidate, options = {}) {
        const {
            size = this.defaultSize,
            className = 'candidate-avatar',
            showTooltip = true,
            onClick = null
        } = options;

        const container = document.createElement('div');
        container.className = `avatar-container ${className}`;
        container.style.width = `${size}px`;
        container.style.height = `${size}px`;
        
        // Add click handler if provided
        if (onClick && typeof onClick === 'function') {
            container.style.cursor = 'pointer';
            container.addEventListener('click', () => onClick(candidate));
        }

        // Determine avatar type and render accordingly
        const avatar = candidate.avatar || {};
        
        if (avatar.type === 'photo' && avatar.photo_url) {
            this.renderPhotoAvatar(container, avatar, candidate, size, showTooltip);
        } else if (avatar.type === 'initials' && avatar.initials) {
            this.renderInitialsAvatar(container, avatar, candidate, size, showTooltip);
        } else {
            // Fallback for missing or invalid avatar data
            this.renderFallbackAvatar(container, candidate, size, showTooltip);
        }

        return container;
    }

    /**
     * Render a photo avatar with fallback to initials
     */
    renderPhotoAvatar(container, avatar, candidate, size, showTooltip) {
        const img = document.createElement('img');
        img.className = 'avatar-photo';
        img.src = avatar.photo_url;
        img.alt = `${candidate.name || 'Candidate'} profile photo`;
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'cover';
        img.style.borderRadius = '50%';
        img.style.display = 'block';

        // Add loading state
        container.classList.add('avatar-loading');

        // Handle successful photo load
        img.onload = () => {
            container.classList.remove('avatar-loading');
            container.classList.add('avatar-photo-loaded');
        };

        // Handle photo load failure - fallback to initials
        img.onerror = () => {
            console.log(`Photo failed to load for ${candidate.name}, falling back to initials`);
            container.classList.remove('avatar-loading');
            container.innerHTML = ''; // Clear the failed image
            
            // Generate initials avatar as fallback
            const fallbackAvatar = this.generateInitialsFromCandidate(candidate);
            this.renderInitialsAvatar(container, fallbackAvatar, candidate, size, showTooltip);
        };

        container.appendChild(img);

        // Add tooltip if enabled
        if (showTooltip) {
            container.title = candidate.name || 'Candidate profile photo';
        }
    }

    /**
     * Render an initials avatar
     */
    renderInitialsAvatar(container, avatar, candidate, size, showTooltip) {
        container.className += ' avatar-initials';
        container.style.backgroundColor = avatar.background_color || '#3B82F6';
        container.style.borderRadius = '50%';
        container.style.display = 'flex';
        container.style.alignItems = 'center';
        container.style.justifyContent = 'center';
        container.style.position = 'relative';
        container.style.overflow = 'hidden';

        // Create initials text element
        const initialsText = document.createElement('span');
        initialsText.className = 'avatar-initials-text';
        initialsText.textContent = avatar.initials || '?';
        initialsText.style.color = 'white';
        initialsText.style.fontSize = `${Math.round(size * 0.4)}px`;
        initialsText.style.fontWeight = '600';
        initialsText.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        initialsText.style.textAlign = 'center';
        initialsText.style.lineHeight = '1';
        initialsText.style.userSelect = 'none';

        container.appendChild(initialsText);

        // Add tooltip if enabled
        if (showTooltip) {
            const tooltipText = avatar.initials === '?' 
                ? 'Photo unavailable' 
                : `${candidate.name || 'Candidate'} - Photo unavailable`;
            container.title = tooltipText;
        }

        // Add accessibility attributes
        container.setAttribute('role', 'img');
        container.setAttribute('aria-label', `${candidate.name || 'Candidate'} avatar with initials ${avatar.initials}`);
    }

    /**
     * Render a fallback avatar when no avatar data is available
     */
    renderFallbackAvatar(container, candidate, size, showTooltip) {
        const fallbackAvatar = this.generateInitialsFromCandidate(candidate);
        this.renderInitialsAvatar(container, fallbackAvatar, candidate, size, showTooltip);
    }

    /**
     * Generate initials avatar data from candidate information
     */
    generateInitialsFromCandidate(candidate) {
        const name = candidate.name || '';
        const nameParts = name.trim().split(/\s+/);
        
        let initials = '?';
        if (nameParts.length >= 2) {
            initials = `${nameParts[0][0]}${nameParts[nameParts.length - 1][0]}`.toUpperCase();
        } else if (nameParts.length === 1 && nameParts[0].length >= 2) {
            initials = nameParts[0].substring(0, 2).toUpperCase();
        } else if (nameParts.length === 1 && nameParts[0].length === 1) {
            initials = nameParts[0].toUpperCase();
        }

        // Generate a simple color based on name
        const colors = [
            '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
            '#06B6D4', '#84CC16', '#F97316', '#EC4899', '#6366F1'
        ];
        
        const nameHash = this.simpleHash(name.toLowerCase());
        const backgroundColor = colors[nameHash % colors.length];

        return {
            type: 'initials',
            photo_url: null,
            initials: initials,
            background_color: backgroundColor
        };
    }

    /**
     * Simple hash function for consistent color generation
     */
    simpleHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    /**
     * Batch render avatars for multiple candidates
     * @param {Array} candidates - Array of candidate objects
     * @param {HTMLElement} container - Container element to append avatars to
     * @param {Object} options - Rendering options
     */
    renderAvatarList(candidates, container, options = {}) {
        const fragment = document.createDocumentFragment();
        
        candidates.forEach((candidate, index) => {
            const avatarElement = this.renderAvatar(candidate, {
                ...options,
                className: `${options.className || 'candidate-avatar'} avatar-${index}`
            });
            fragment.appendChild(avatarElement);
        });

        container.appendChild(fragment);
    }

    /**
     * Update an existing avatar element with new candidate data
     */
    updateAvatar(avatarElement, candidate, options = {}) {
        const newAvatar = this.renderAvatar(candidate, options);
        avatarElement.parentNode.replaceChild(newAvatar, avatarElement);
        return newAvatar;
    }
}

// CSS styles for the avatar component
const avatarStyles = `
.avatar-container {
    position: relative;
    display: inline-block;
    border-radius: 50%;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.avatar-container:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
}

.avatar-container.avatar-loading {
    background: linear-gradient(45deg, #f0f0f0 25%, transparent 25%), 
                linear-gradient(-45deg, #f0f0f0 25%, transparent 25%), 
                linear-gradient(45deg, transparent 75%, #f0f0f0 75%), 
                linear-gradient(-45deg, transparent 75%, #f0f0f0 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    animation: loading-shimmer 1.5s infinite linear;
}

@keyframes loading-shimmer {
    0% { background-position: 0 0, 0 10px, 10px -10px, -10px 0px; }
    100% { background-position: 20px 20px, 20px 30px, 30px 10px, 10px 20px; }
}

.avatar-photo {
    transition: opacity 0.2s ease;
}

.avatar-initials {
    border: 2px solid rgba(255, 255, 255, 0.2);
}

.avatar-initials-text {
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Responsive sizing */
@media (max-width: 768px) {
    .avatar-container {
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
    }
    
    .avatar-container:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
        transform: none; /* Disable hover transform on mobile */
    }
}

/* High contrast mode support */
@media (prefers-contrast: high) {
    .avatar-container {
        border: 2px solid currentColor;
    }
    
    .avatar-initials {
        border: 3px solid currentColor;
    }
}

/* Reduced motion support */
@media (prefers-reduced-motion: reduce) {
    .avatar-container,
    .avatar-photo {
        transition: none;
    }
    
    .avatar-container:hover {
        transform: none;
    }
    
    @keyframes loading-shimmer {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
}
`;

// Inject styles into the document
function injectAvatarStyles() {
    if (!document.getElementById('avatar-component-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'avatar-component-styles';
        styleSheet.textContent = avatarStyles;
        document.head.appendChild(styleSheet);
    }
}

// Auto-inject styles when the script loads
if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectAvatarStyles);
    } else {
        injectAvatarStyles();
    }
}

// Export for use in different environments
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AvatarRenderer;
} else if (typeof window !== 'undefined') {
    window.AvatarRenderer = AvatarRenderer;
}