window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(map, lat, lon, zoom) {
            map.flyTo([lat, lon], zoom);
        }
    }
});