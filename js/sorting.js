document.addEventListener('DOMContentLoaded', function() {
    // Функция для обработки клика по тогглеру
    function toggleFolder(event) {
        const folderNameSpan = event.currentTarget;
        const folderEntryLi = folderNameSpan.closest('.folder-entry');
        const folderContentUl = folderEntryLi.querySelector('.folder-content');
        const togglerSpan = folderNameSpan.querySelector('.toggler');

        if (folderContentUl && togglerSpan) {
            // Переключаем класс для скрытия/отображения
            folderContentUl.classList.toggle('collapsed');
            
            // Обновляем символ тогглера
            if (folderContentUl.classList.contains('collapsed')) {
                togglerSpan.textContent = '[+]';
                folderEntryLi.classList.remove('expanded');
            } else {
                togglerSpan.textContent = '[-]';
                folderEntryLi.classList.add('expanded');
            }
        }
    }

    // Находим все элементы с названием папки и прикрепляем обработчик
    const folderNames = document.querySelectorAll('.folder-name');
    folderNames.forEach(name => {
        name.addEventListener('click', toggleFolder);
    });
});