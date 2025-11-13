document.addEventListener('DOMContentLoaded', function() {
    console.log("sorting.js: Файл загружен. Инициализация делегирования событий.");
    
    // Используем делегирование событий на корневом элементе
    const fileTreeRoot = document.querySelector('.file-tree-root');

    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            
            // Ищем элемент, который должен быть кликабельным: <span class="folder-name">
            const folderNameSpan = event.target.closest('.folder-name');
            
            if (folderNameSpan) {
                console.log("sorting.js: Клик обнаружен. Запуск операции...");

                const folderEntryLi = folderNameSpan.closest('.folder-entry');
                const folderContentUl = folderEntryLi.querySelector('.folder-content');
                const togglerSpan = folderNameSpan.querySelector('.toggler');

                if (folderContentUl && togglerSpan) {
                    
                    // Переключаем класс
                    folderContentUl.classList.toggle('collapsed');
                    
                    // Обновляем тогглер
                    if (folderContentUl.classList.contains('collapsed')) {
                        togglerSpan.textContent = '[+]';
                        folderEntryLi.classList.remove('expanded');
                        console.log("sorting.js: Папка СКРЫТА. Класс .collapsed добавлен, тогглер: [+]");
                    } else {
                        togglerSpan.textContent = '[-]';
                        folderEntryLi.classList.add('expanded');
                        console.log("sorting.js: Папка ОТКРЫТА. Класс .collapsed удален, тогглер: [-]");
                    }
                } else {
                    console.error("sorting.js: Ошибка! Не найдены folderContentUl или togglerSpan.");
                }
            }
        });
    } else {
        console.error("sorting.js: Ошибка! Элемент .file-tree-root не найден.");
    }
});