var map = new GMaps({
    div: '#map',
    lat: 53.350140,
    lng: -6.266155,
    zoom: 13,
});

map.addMarker({
    lat:53.349432, 
    lng:-6.260506,
    title:'GPO',
    infoWindow: {
        content: '<div id="busInfo"><p>Bus Information</p><button id="busButton">Click Here</button></div>'
    }
})

GMaps.geolocate({
  success: function(position) {
    map.setCenter(position.coords.latitude, position.coords.longitude);
  },
});

map.drawRoute({
    origin: [53.345557, -6.255142],
    destination: [53.352711, -6.264208],
    travelMode: 'driving',
    strokeColor: '#131540',
    strokeOpacity: 0.6,
    strokeWeight: 6
})

$(document).ready(function(){    
    $('#busButton').html('it works');
})
