document.addEventListener('DOMContentLoaded', function() {
    console.log("sorting.js: Инициализация.");
    
    // 1. ФУНКЦИЯ СОРТИРОВКИ (Папки вверх)
    function sortFoldersFirst() {
        // Находим все списки (корневой и вложенные)
        const allLists = document.querySelectorAll('.file-tree-root, .folder-content');
        
        allLists.forEach(ul => {
            // Превращаем живую коллекцию children в массив
            const items = Array.from(ul.children);
            
            // Отделяем папки от файлов
            const folders = items.filter(li => li.classList.contains('folder-entry'));
            const files = items.filter(li => li.classList.contains('file-entry'));
            
            // Если порядок уже правильный, можно не трогать, но для надежности передобавим:
            // Сначала добавляем все папки
            folders.forEach(folder => ul.appendChild(folder));
            // Затем добавляем все файлы
            files.forEach(file => ul.appendChild(file));
        });
    }

    // Запускаем сортировку сразу
    sortFoldersFirst();

    // 2. ЛОГИКА ОТКРЫТИЯ/ЗАКРЫТИЯ (Твой старый код с небольшими правками)
    const fileTreeRoot = document.querySelector('.file-tree-root');
    if (fileTreeRoot) {
        fileTreeRoot.addEventListener('click', function(event) {
            const folderNameSpan = event.target.closest('.folder-name');
            
            if (folderNameSpan) {
                event.stopImmediatePropagation(); 
                
                const folderEntryLi = folderNameSpan.closest('.folder-entry');
                const folderContentUl = folderEntryLi.querySelector('.folder-content');
                // Ищем тогглер внутри нажатого элемента
                const togglerSpan = folderNameSpan.querySelector('.toggler');

                if (folderContentUl && togglerSpan) {
                    folderContentUl.classList.toggle('collapsed');
                    
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