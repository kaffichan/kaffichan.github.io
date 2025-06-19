$(window).on('load', function() {
	$('.video-container').isotope({
		itemSelector: '.video-block',
		layoutMode: 'masonry',
		percentPosition: true,
		masonry: {
			columnWidth: '.video-block'
		}
	});
});