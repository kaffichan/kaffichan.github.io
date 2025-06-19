$(function() {
  let isMenuVisible = false; // Флаг для отслеживания состояния меню
  let catImages = [
    'content/mainpage/kitty1.gif',
    'content/mainpage/kitty2.gif',
    'content/mainpage/lovecatemoji.gif' // Добавьте больше путей к изображениям котиков
  ];

  $("#button").click(function(event) {
    event.preventDefault(); // Предотвращаем стандартное поведение ссылки

    if (!isMenuVisible) {
      // Показать меню в первый раз
      $("#mainDiv").toggle();
      isMenuVisible = true;
    } else {
      // Создать падающего котика
      createFallingCat();
    }
  });

  function createFallingCat() {
    let catImage = catImages[Math.floor(Math.random() * catImages.length)]; // Случайный котик
    let cat = $('<img src="' + catImage + '" class="falling-cat">');

    // Рандомная позиция по горизонтали
    let randomX = Math.random() * (window.innerWidth - 50); // 50 - ширина изображения

    // Случайный размер
    let randomSize = 30 + Math.random() * 40; // Размер от 30px до 70px

    // Случайный поворот
    let randomRotation = (Math.random() * 90) - 45; // Угол от -45 до 45 градусов

    cat.css({
      position: 'fixed',
      left: randomX + 'px',
      top: '-50px', // Начинаем за пределами видимости сверху
      width: randomSize + 'px',
      height: randomSize + 'px',
      zIndex: 1000, // Чтобы были поверх других элементов
      transform: 'rotate(' + randomRotation + 'deg)' // Поворот
    });

    $('body').append(cat);

    // Анимация падения
    cat.animate({
      top: window.innerHeight + 'px' // Падают до низа экрана
    }, {
      duration: 3000, // Длительность падения
      easing: 'easeInQuad',
      complete: function() {
        $(this).remove(); // Удаляем после падения
      }
    });
  }
});
