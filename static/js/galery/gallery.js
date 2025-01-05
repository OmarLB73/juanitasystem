"use strict";

(function ($) {

	$.fn.masonry_gallery = function () {

		// Seleccionamos todas las galerías
		this.each(function () {

			var $grid_gallery = $(this);  // Cada galería específica
			var $filters = $grid_gallery.siblings('#gallery-filters');  // Filtros para esta galería

			// Iniciar Isotope con la galería específica
			$grid_gallery.imagesLoaded(function () {
				$grid_gallery.isotope({
					itemSelector: '.gallery-grid-item',
					layoutMode: 'masonry'
				});
			});

			// Filtrar imágenes según el tipo
			var filterFns = {};

			// Asociar filtros a la galería específica
			$filters.on('click', 'button', function () {
				var filterValue = $(this).attr('data-filter');
				// Usar filterFn si corresponde
				filterValue = filterFns[filterValue] || filterValue;
				$grid_gallery.isotope({ filter: filterValue });
				// Cambiar la clase 'is-checked' en los botones de filtro
				$(this).siblings().removeClass('is-checked'); // Remueve la clase de los demás botones
				$(this).addClass('is-checked'); // Añade la clase al botón clickeado

			});

			// Inicializar Fancybox para el zoom de imágenes dentro de esta galería
			$grid_gallery.find(".grid-image-zoom").fancybox({
				'transitionIn': 'elastic',
				'transitionOut': 'elastic',
				'speedIn': 600,
				'speedOut': 200,
				'overlayShow': false
			});

		});

	};


})(jQuery);