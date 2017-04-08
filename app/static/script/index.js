$(document).ready(function() {
	var ph = $(window).height() - 80;
	$(".page-content").css("height", ph);
	$(".nav-list-item a").click(function() {
		$(this).parent(".nav-list-item").toggleClass("active");
		$(this).next(".sub-list").toggle(200);
		if ($(this).parent(".nav-list-item").hasClass('active')) {
			$(this).parent(".nav-list-item").siblings(".nav-list-item").removeClass("active").children(".sub-list").slideUp(200);
		}
	});

	$(".tab-nav li").click(function() {
		$(".nav-list li").removeClass('active');
	});

	$(".sub-list").on('click', 'li', function() {
		$(this).addClass('active');
		$(this).siblings().removeClass('active');
	});

	$(window).resize(function() {
		var ph = $(window).height() - 80;
		$(".page-content").css("height", ph);
	});
});

$(document).ready(function() {
	// $(".tab-nav").on('click', 'li', function() {
	// 	$(".nav-list li").removeClass('active');
	// });
	// $(".tab-nav").on('dblclick', 'li', function() {
	// 	closeApp($(this).attr('data-id'));
	// });
	// $(".tab-arrow-l").click(function() {
	// 	var left = parseInt($('.tab-nav > ul').css('left'));
	// 	left = left + 70 > 0 ? 0 : left + 70;
	// 	$(".tab-nav > ul").animate({
	// 		left: left + "px"
	// 	}, 200);
	// });
	// $(".tab-arrow-r").click(function() {
	// 	var left = parseInt($('.tab-nav > ul').css('left'));
	// 	left = left - 70 > -$(".tab-nav").width() + 10 ? left - 70 : left;
	// 	$(".tab-nav > ul").animate({
	// 		left: left + "px"
	// 	}, 100);
	// });
	// $(window).resize(function() {
	// 	throttle(tabResponse, window);
	// });
});

// function throttle(fn, context) {
// 	clearTimeout(fn.tid);
// 	fn.tid = setTimeout(function() {
// 		fn.call(context);
// 	}, 200);
// }

function openapp(url, appid, title, subTitle, refesh) {
	var i, len, flag = 0;
	var iframeList = $(".page-content iframe");
	$(".title").text(title);
	$(".sub-title").text(subTitle);

	$(".page-content iframe").addClass("none").removeClass("current");
	for (i = 0, len = iframeList.length; i < len; i++) {
		if ($(iframeList[i]).attr("data-id") == appid) {
			$(iframeList[i]).addClass("current").removeClass("none");
			flag = 1;
			break;
		}
	}

	console.log(flag);
	console.log(url);
	if (flag === 0) {
		$("<iframe class='current'></iframe>").attr("data-id", appid).prop("src", url).appendTo($(".page-content"));
	} else if (refesh) {
		iframeList[i].contentWindow.location.reload(true);
	}
}