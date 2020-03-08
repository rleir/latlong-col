

document.addEventListener("DOMContentLoaded", function(event) { 


	var map = L.map('map').setView([30.5, -0.09], 2);

	L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);

	function onEachFeature(feature, layer) {
		var popupContent = "";

		if (feature.properties) {
            if( feature.properties.place) {
			    popupContent += feature.properties.place;
			    popupContent += "<br>";
            }
            if( feature.properties.popupContent) {
			    popupContent += "<ul>";
                for(var key in feature.properties.popupContent) {
                    popupContent += "<li>";
			        popupContent += feature.properties.popupContent[key] + " - ";
			        popupContent += key;
			        popupContent += "</li>";
                };
			    popupContent += "</ul>";
			}
        }
		layer.bindTooltip(popupContent); // or bindPopup
	}

	L.geoJSON([bicycleRental], {

		style: function (feature) {
			return feature.properties && feature.properties.style;
		},

		onEachFeature: onEachFeature,

		pointToLayer: function (feature, latlng) {
			return L.marker(latlng);
		}
	}).addTo(map);

    const params = new URLSearchParams(document.location.search);
    const l = params.get("l");
    var para_name = "";
    if(l === "fr"){
        //display:none
        para_name = "fr_para";
    } else {
        para_name = "en_para";
    }
    var x = document.getElementById(para_name);
    x.style.display = "block";
});

    
