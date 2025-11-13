document.addEventListener('DOMContentLoaded', function() {
    function toggleFolder(event) {
        const folderNameSpan = event.currentTarget;
        const folderEntryLi = folderNameSpan.closest('.folder-entry');
        const folderContentUl = folderEntryLi.querySelector('.folder-content');
        // Убрали const togglerSpan - он нам не нужен

        if (folderContentUl) {
            folderContentUl.classList.toggle('collapsed');
            
            // Вместо изменения текста тогглера, меняем класс на li:
            if (folderContentUl.classList.contains('collapsed')) {
                folderEntryLi.classList.remove('expanded');
                // Добавляем класс для закрытой папки, чтобы CSS мог применить иконку [+]
                folderEntryLi.classList.add('collapsed-icon'); 
            } else {
                folderEntryLi.classList.add('expanded');
                // Убираем класс закрытой папки, чтобы CSS мог применить иконку [-]
                folderEntryLi.classList.remove('collapsed-icon');
            }
        }
    }

    const folderNames = document.querySelectorAll('.folder-name');
    folderNames.forEach(name => {
        name.addEventListener('click', toggleFolder);
    });
    
    // Инициализация: убедимся, что все папки начинаются с иконкой [+]
    document.querySelectorAll('.folder-entry').forEach(li => {
        li.classList.add('collapsed-icon');
    });
});