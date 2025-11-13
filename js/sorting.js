document.addEventListener('DOMContentLoaded', function() {
    console.log("sorting.js: Файл загружен. Инициализация.");
    
    // Используем делегирование событий на корневом элементе
    const fileTreeRoot = document.querySelector('.file-tree-root');

    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            
            // Ищем элемент, который должен быть кликабельным: <span class="folder-name">
            const folderNameSpan = event.target.closest('.folder-name');
            
            if (folderNameSpan) {
                // Если мы обработали клик, немедленно останавливаем его дальнейшее распространение.
                // Это устраняет проблему двойного срабатывания.
                event.stopImmediatePropagation(); 
                
                // console.log("sorting.js: Клик на папке обработан."); // Убираем логи для чистоты

                const folderEntryLi = folderNameSpan.closest('.folder-entry');
                const folderContentUl = folderEntryLi.querySelector('.folder-content');
                const togglerSpan = folderNameSpan.querySelector('.toggler');

                if (folderContentUl && togglerSpan) {
                    
                    // Переключаем класс
                    folderContentUl.classList.toggle('collapsed');
                    
                    // Обновляем тогглер
                    if (folderContentUl.classList.contains('collapsed')) {
                        togglerSpan.textContent = '[+]'; // Скрыто
                        folderEntryLi.classList.remove('expanded');
                    } else {
                        togglerSpan.textContent = '[-]'; // Открыто
                        folderEntryLi.classList.add('expanded');
                    }
                }
            }
        });
    }
});