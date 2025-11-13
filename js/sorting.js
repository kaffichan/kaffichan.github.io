document.addEventListener('DOMContentLoaded', function() {
    console.log("sorting.js: Файл загружен. Инициализация делегирования событий.");
    
    // Используем делегирование событий на корневом элементе
    const fileTreeRoot = document.querySelector('.file-tree-root');

    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            
            // 1. Ищем элемент, который должен быть кликабельным: <span class="folder-name">
            const folderNameSpan = event.target.closest('.folder-name');
            
            if (folderNameSpan) {
                console.log("sorting.js: Клик обнаружен на названии папки.");

                const folderEntryLi = folderNameSpan.closest('.folder-entry');
                const folderContentUl = folderEntryLi.querySelector('.folder-content');
                const togglerSpan = folderNameSpan.querySelector('.toggler');

                // 2. Убедимся, что все элементы найдены
                if (folderContentUl && togglerSpan) {
                    console.log("sorting.js: Все элементы найдены. Переключение класса...");
                    
                    // Переключаем класс (ДОЛЖЕН УДАЛИТЬ .collapsed при втором клике)
                    folderContentUl.classList.toggle('collapsed');
                    
                    // Обновляем символ тогглера и класс
                    if (folderContentUl.classList.contains('collapsed')) {
                        togglerSpan.textContent = '[+]'; // Скрыто
                        folderEntryLi.classList.remove('expanded');
                        console.log("sorting.js: Папка СКРЫТА. Класс .collapsed добавлен, тогглер: [+]");
                    } else {
                        togglerSpan.textContent = '[-]'; // Открыто
                        folderEntryLi.classList.add('expanded');
                        console.log("sorting.js: Папка ОТКРЫТА. Класс .collapsed удален, тогглер: [-]");
                    }
                } else {
                    // Это может случиться, если структура HTML не соответствует ожидаемой
                    console.error("sorting.js: Ошибка! Не удалось найти folderContentUl или togglerSpan.");
                    console.log("folderContentUl:", folderContentUl);
                    console.log("togglerSpan:", togglerSpan);
                }
            }
        });
    } else {
        console.error("sorting.js: Ошибка! Элемент .file-tree-root не найден.");
    }
});