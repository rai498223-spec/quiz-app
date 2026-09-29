document.addEventListener('DOMContentLoaded', function () {
    const countdownEls = document.querySelectorAll('[data-end]');
    function formatTimeLeft(seconds) {
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hrs).padStart(2, '0')}:${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    countdownEls.forEach(el => {
        const target = new Date(el.dataset.end);
        const value = el.querySelector('.countdown-value');
        if (!value) return;

        function update() {
            const now = new Date();
            const diff = Math.max(0, Math.floor((target - now) / 1000));
            value.textContent = formatTimeLeft(diff);
        }

        update();
        setInterval(update, 1000);
    });
});
