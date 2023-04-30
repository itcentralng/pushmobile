mainland1 = {'areas':"Ebute Metta, Akoka, Fola Agoro, Shomolu, ljora, lganmu, Costain, Surulere, Yaba, Jibowu, Onipanu, Obanikoro, lkorodu road, llupeju, Anthony, Festac", "cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
mainland2 = {'areas':"Gbagada, Ogudu, lyana-Oworo, Magodo, Shangisha, Alausa, Omole 1, Ojota, Ogba, Ketu, lkeja, Maryland, Lagos Airport [MM1&MM2J, Oshodi, Apapa, Ojodu Berger", "cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
mainland3 = {'areas':"Okota, Isolo, Egbeda, Dopemu, Iyana Ipaja, Abule Egba, Agbado Ijaiye", "cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
island1 = {'areas':"Victoria Island, Ikoyi, Obalende, Dolphin Estate, Osborne Estate, Park View Estate, Banana Island, Marina, CMS, Lagos Island","cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
island2 = {'areas':"Oniru, Lekki Phase 1,2 Roundabout -Marwa,3'0 Roundabout, Elf","cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
island3 = {'areas':"Chisco, lkate, Jakande First gate, Jakande Roundabout, Femi Okunu, Agungi, lgbo Efon, Alpha Beach, lkota, VGC","cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}},
island4 = {'areas':"Abraham Adesanya, Ajah, Badore, Oqombo, Oqidan, Sanqotedo, Abijo, Awoyaya","cost":{"mainland1":"1500-2000", "mainland2":"1000-1500", "mainland3":"1000-2000", "island1":"1500-2000", "island2":"1500-2000", "island3":"1500-2000", "island4":"1500-2000"}}

locations = {
    'mainland1':mainland1,
    'mainland2':mainland2,
    'mainland3':mainland3,
    'island1':island1,
    'island2':island2,
    'island3':island3,
    'island4':island4,
}

def delivery_cost(_from, _to):
    # Extract relevant information from input addresses
    from_address_parts = _from.split(',')
    from_city = from_address_parts[-2].strip()
    from_area = from_address_parts[-3].strip()
    from_island_or_mainland = None
    for key, value in locations.items():
        if from_area in value['areas']:
            from_island_or_mainland = key
            break
    if from_island_or_mainland is None:
        raise ValueError(f"Invalid address: {_from}")

    to_address_parts = _to.split(',')
    to_city = to_address_parts[-2].strip()
    to_area = to_address_parts[-3].strip()
    to_island_or_mainland = None
    for key, value in locations.items():
        if to_area in value['areas']:
            to_island_or_mainland = key
            break
    if to_island_or_mainland is None:
        raise ValueError(f"Invalid address: {_to}")

    # Look up delivery cost in locations dictionary
    cost = locations[from_island_or_mainland]['cost'][to_island_or_mainland]
    return cost
