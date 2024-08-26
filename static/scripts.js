// scripts.js

document.getElementById('lang-toggle').addEventListener('click', () => {
    const button = document.getElementById('lang-toggle');
    if (button.textContent === 'English') {
        button.textContent = 'हिन्दी'; // Change to Hindi text
    } else {
        button.textContent = 'English'; // Change back to English text
    }
});

document.getElementById('more-examples-btn').addEventListener('click', () => {
    alert('More examples coming soon!');
});
