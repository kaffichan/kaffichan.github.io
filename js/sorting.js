document.addEventListener('DOMContentLoaded', function() {
    
    // Используем делегирование событий на корневом элементе
    const fileTreeRoot = document.querySelector('.file-tree-root');

    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            
            // Ищем элемент, который должен быть кликабельным: <span class="folder-name">
            const folderNameSpan = event.target.closest('.folder-name');
            
            if (folderNameSpan) {
                // Если клик был на названии папки (или внутри него),
                // находим все связанные элементы:
                
                const folderEntryLi = folderNameSpan.closest('.folder-entry');
                // Контент папки - это следующий элемент <ul>
                const folderContentUl = folderEntryLi.querySelector('.folder-content');
                // Тогглер - это элемент внутри названия папки
                const togglerSpan = folderNameSpan.querySelector('.toggler');

                // Убедимся, что все элементы найдены, прежде чем что-то менять
                if (folderContentUl && togglerSpan) {
                    
                    // 1. Переключаем класс для скрытия/отображения
                    folderContentUl.classList.toggle('collapsed');
                    
                    // 2. Обновляем символ тогглера и класс родительского LI
                    if (folderContentUl.classList.contains('collapsed')) {
                        togglerSpan.textContent = '[+]';
                        folderEntryLi.classList.remove('expanded');
                    } else {
                        togglerSpan.textContent = '[-]';
                        folderEntryLi.classList.add('expanded');
                    }
                }
            }
        });
    }
});