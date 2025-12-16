// app/web/static/js/script.js
document.addEventListener('DOMContentLoaded', () => {
    const sandbox = document.getElementById('website-sandbox');
    if (sandbox) {
        // ✅ Use /sandbox/index.html (not /sandbox_static/)
        // ✅ Add cache-busting query param
        const cacheBuster = Date.now();
        sandbox.src = `/sandbox/index.html?t=${cacheBuster}`;
        console.log("✅ Sandbox refreshed:", sandbox.src);
    }

    // Optional: auto-resize iframe height (improves UX)
    window.addEventListener('resize', () => {
        if (sandbox) sandbox.style.height = (window.innerHeight - 200) + 'px';
    });
    if (sandbox) sandbox.style.height = (window.innerHeight - 200) + 'px';
});