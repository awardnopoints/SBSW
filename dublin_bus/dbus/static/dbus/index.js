/*var map = new GMaps({
    div: '#map',
    lat: 53.350140,
    lng: -6.266155,
    zoom: 10,
});

var markerCluster = new MarkerClusterer(map, markers,
            {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
      }

GMaps.geolocate({
  success: function(position) {
    map.setCenter(position.coords.latitude, position.coords.longitude);
  },
});

$(document).ready(function(){    
    $('#busButton').html('it works');
})

function initMap() {

var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 10,
          center: {lat: 53.3498, lng: -6.2603}
        });

markers = [];

 {% for item in contents %}
                var name = "{{item.stop_name}}"
                var latitude = "{{item.latitude}}"
                var longitude = "{{item.longitude}}"
                
                var marker = new google.maps.Marker({
                        position: {lat: Number(latitude), lng: Number(longitude)},
                        map: map,
                        title: name
                });
		markers.push(marker);
        {% endfor %}


	var markerCluster = new MarkerClusterer(map, markers,
            {imagePath: 'https://developers.google.com/maps/documentation/javascript/examples/markerclusterer/m'});
      };
};*\
