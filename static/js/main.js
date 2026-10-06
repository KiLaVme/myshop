document.addEventListener('DOMContentLoaded', function() {

    // --- Logic for the Main Page (catalog.html) ---
    const homePageContent = document.querySelector('.main-content-grid');
    if (homePageContent) {
        // Sort Options Logic: косметичне миттєве підсвічування активної кнопки
        // сортування (без очікування перезавантаження сторінки).
        const sortButtons = document.querySelectorAll('.sort-options .sort-button');
        sortButtons.forEach(button => {
            button.addEventListener('click', function() {
                sortButtons.forEach(btn => btn.classList.remove('active-sort'));
                this.classList.add('active-sort');
            });
        });
    }
});
