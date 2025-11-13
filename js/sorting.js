document.addEventListener('DOMContentLoaded', function() {
    // 1. Функция-обработчик клика
    function toggleFolder(folderNameSpan) {
        const folderEntryLi = folderNameSpan.closest('.folder-entry');
        const folderContentUl = folderEntryLi.querySelector('.folder-content');
        const togglerSpan = folderNameSpan.querySelector('.toggler');

        if (folderContentUl && togglerSpan) {
            // Переключаем класс для скрытия/отображения
            folderContentUl.classList.toggle('collapsed');
            
            // Обновляем символ тогглера и класс
            if (folderContentUl.classList.contains('collapsed')) {
                togglerSpan.textContent = '[+]';
                folderEntryLi.classList.remove('expanded');
            } else {
                togglerSpan.textContent = '[-]';
                folderEntryLi.classList.add('expanded');
            }
        }
    }

    // 2. Используем делегирование событий
    const fileTreeRoot = document.querySelector('.file-tree-root');

    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            // Проверяем, был ли клик по элементу с классом .folder-name
            const folderNameElement = event.target.closest('.folder-name');
            
            if (folderNameElement) {
                // Если да, вызываем нашу функцию toggleFolder, передавая найденный элемент
                toggleFolder(folderNameElement);
            }
        });
    }
});