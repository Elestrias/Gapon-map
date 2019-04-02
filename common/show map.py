def show_map(ll_spn=None, map_type="map", add_params=None):
    if ll_spn:
        map_request = "http://static-maps.yandex.ru/1.x/?{ll_spn}&l={map_type}".format(**locals())
    else:
        map_request = "http://static-maps.yandex.ru/1.x/?l={map_type}".format(**locals())

    if add_params:
        map_request += "&" + add_params
    response = requests.get(map_request)
