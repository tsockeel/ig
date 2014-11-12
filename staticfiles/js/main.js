$(document).ready(function () {

    $(function () { $("[data-toggle='popover']").popover(); });


    $(".mysettings").popover({
        html : true,
        content: function() {
          var content = $(this).attr("data-popover-content");
          return $(content).children(".popover-body").html();
        },
        title: function() {
          var title = $(this).attr("data-popover-content");
          return $(title).children(".popover-heading").html();
        }
    });


    var sync1 = $("#sync1");
    var sync2 = $("#sync2");

    sync1.owlCarousel({
        singleItem: true,
        slideSpeed: 500,
        navigation: false,
        pagination: false,
      	autoPlay : parseInt($(".parameters .autoplay").text()),
        afterAction: syncPosition,
	lazyLoad : true,
	transitionStyle : "fade",
    });

    sync2.owlCarousel({
        items: 10,
        itemsDesktop: [1199, 10],
        itemsDesktopSmall: [979, 8],
        itemsTablet: [768, 6],
        itemsMobile: [479, 4],
        pagination: false,
        responsiveRefreshRate: 100,
	lazyLoad : true,
        afterInit: function (el) {
            el.find(".owl-item").eq(0).addClass("synced");
        }
    });

    function syncPosition(el) {
        var current = this.currentItem;
        $("#sync2")
            .find(".owl-item")
            .removeClass("synced")
            .eq(current)
            .addClass("synced")
        if ($("#sync2").data("owlCarousel") !== undefined) {
            center(current)
        }

	$(".currentItem").text(current+1);
	$(".nbitems").text(this.itemsAmount);

    }
	
	function refresh () {
		var tagname_sub =  $(".subscribe-input").val();
		var most_recent_post = $(".most_recent_post").text();
		console.log("refresh date : " + most_recent_post);
		var data_parameters;
		if (most_recent_post) {data_parameters = {tagname: tagname_sub, start_date: most_recent_post};}
		else { data_parameters = {tagname: tagname_sub}}
		if (tagname_sub)
		{
		$.ajax({
			url: 'http://66.228.61.74:8001/ig/viewerupdate/',
			data: data_parameters,
		        success: function(data) {

			        var source1   = $("#sync1-template").html();
			        var template1 = Handlebars.compile(source1);
			        var result1 = template1(data);

			        var source2   = $("#sync2-template").html();
			        var template2 = Handlebars.compile(source2);
			        var result2 = template2(data);

			        if (data["most_recent_post"])
			        {
			              $(".most_recent_post").text(data["most_recent_post"])
			        }
				if( $.isArray(data["posts"]) &&  data["posts"].length>0 ) 
				{
			        	var currentItem = parseInt($(".currentItem").text());

				        $(".owl-carousel").hide();/*addClass("hidden");*/
				        sync1.data('owlCarousel').addItem(result1,currentItem+1);
				        sync2.data('owlCarousel').addItem(result2,currentItem+1);
				        sync1.trigger('owl.jumpTo', currentItem-1);
			        	$(".owl-carousel").show();/*removeClass("hidden");*/
				}
			},
			failure: function(data) {
			        console.log('refresh failed');
			}
		});
		}
	}

	setInterval(refresh, 10000);

    $("#sync2").on("click", ".owl-item", function (e) {
        e.preventDefault();
        var number = $(this).data("owlItem");
        sync1.trigger("owl.goTo", number);
    });



    $(".first").click(function(){
      sync1.trigger('owl.goTo', 0);
    })
    
    $(".prev").click(function(){
      sync1.trigger('owl.prev');
    })
    
    $(".next").click(function(){
      sync1.trigger('owl.next');
    })
        
    $(".last").click(function(){
      sync1.trigger('owl.goTo', sync1.data('owlCarousel').itemsAmount-1);
    })

    $(".refresh").click(refresh);

    $(".mysettings").on('hide.bs.popover', function () {
  	var autoplayValue = parseInt($(".popover-content .autoplayvalue").val(), 10) * 1000;
        $(".parameters .autoplay").text(autoplayValue);
        sync1.data('owlCarousel').reinit(
                {autoPlay : autoplayValue});
    })

    $(".mysettings").on('shown.bs.popover', function () {
	var autoplayValue = parseInt($(".parameters .autoplay").text(), 10) /1000;
 	$(".popover-content .autoplayvalue").val(autoplayValue);
    })



$(".subscribe").click(function(){
	var tagname_sub = $(".subscribe-input").val();
	$(".most_recent_post").text(Date.now());

      $.ajax({
        url: 'http://66.228.61.74:8001/ig/subtag/',
	data: {tagname: tagname_sub},
        success: function(data) {
	
	console.log(data);
    },
    failure: function(data) {
	alert('Got an error dude');
    }
});
})


  
    function center(number) {
        var sync2visible = sync2.data("owlCarousel").owl.visibleItems;
        var num = number;
        var found = false;
        for (var i in sync2visible) {
            if (num === sync2visible[i]) {
                var found = true;
            }
        }

        if (found === false) {
            if (num > sync2visible[sync2visible.length - 1]) 
		{
		/* When "num" is greater the highest visible index, e.g. go to last index */
                sync2.trigger("owl.jumpTo", num - sync2visible.length + 2)
            	
		} else {
                if (num - 1 === -1) {
                    num = 0;
                }
		/* When "num" is less than the lowest visible index, e.g. go to first index */
                sync2.trigger("owl.goTo", num);
            }
       	    } else if (num === sync2visible[sync2visible.length - 1]) 
		{
		/* When "num" index is equal to the highest visible index, so we move the first visible item to plus one */
            	sync2.trigger("owl.goTo", sync2visible[1]);
       		
		} else if (num === sync2visible[0]) 
		{
		/* When "num" index is equal to the lowest visible index, so we move the first visible item to less one */
            	sync2.trigger("owl.goTo", num - 1)
        	}
    	   }
  });
