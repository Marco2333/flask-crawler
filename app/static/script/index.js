$(document).ready(function() {
	var ph = $(window).height() - 46;
	$(".page-wrap").css("height", ph);
	$(".page-content").css("height", ph - 60);
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

	$(".sub-list a").dblclick(function() {
		var href = $(this).attr('href').split(":")[1];
		href = href.substring(0, href.length - 1) + ", true)";
		eval(href);
		// openapp('/tweets_search', $(this).attr('data-id'), '推文查询', '基于人物名称查询推文信息', true);
	});

	$(window).resize(function() {
		var ph = $(window).height() - 46;
		$(".page-wrap").css("height", ph);
		$(".page-content").css("height", ph - 60);
	});
});

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

	if (flag === 0) {
		$("<iframe class='current'></iframe>").attr("data-id", appid).prop("src", url).appendTo($(".page-content"));
	} else if (refesh) {
		iframeList[i].contentWindow.location.reload(true);
	}
	$(".page-top").removeClass('hidden');
}