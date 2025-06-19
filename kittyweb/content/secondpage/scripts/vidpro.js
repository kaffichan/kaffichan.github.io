$(document).ready(function() {
	
	function loadVideo(element) {
		var video = element.find('video');
		var source = video.attr('data-src');
		if (source) {
			video.attr('src', source);
			video.removeAttr('data-src');
			setTimeout(function() {
				video[0].load();
			}, 50);
		}
	}
	
	function checkVisible() {
		$('.video-block:not(.loaded)').each(function() {
			if ($(this).isInViewport()) {
				loadVideo($(this));
				$(this).addClass('loaded');
			}
		});
	}
	
	$.fn.isInViewport = function() {
		var elementTop = $(this).offset().top;
		var elementBottom = elementTop + $(this).outerHeight();
		
		var viewportTop = $(window).scrollTop();
		var viewportBottom = viewportTop + $(window).height();
		
		return elementBottom > viewportTop && elementTop < viewportBottom;
	};
	
	checkVisible();
	
	$(window).on('resize scroll', checkVisible);
	
	$('.video-block video').on('loadeddata', function() {
		$(this).closest('.video-block').addClass('loaded');
		$('.video-container').isotope('layout');
	});
	
	$('.video-block video').on('error', function() {
		console.log('Ошибка загрузки: ' + $(this).attr('src'));
		$(this).closest('.video-block').addClass('loaded');
		$(this).replaceWith('<p style="color: #FFD9FF; text-align: center;">Ошибка загрузки</p>');
		$('.video-container').isotope('layout');
	});
	
	function triggerResize() {
		var currentWidth = $(window).width();
		var currentHeight = $(window).height();
		
		var newWidth = currentWidth + 1;
		
		$(window).width(newWidth);
		
		setTimeout(function() {
			$(window).width(currentWidth);
		}, 50);
	}
	
	$(window).on('load', function() {
		$('.video-container').isotope('layout');
		triggerResize();
	});
	
});