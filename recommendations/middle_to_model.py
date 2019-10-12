class RealEstate:
    def __init__(self, json):
        self.id = json['id']
        self.promotionId = json['promotionId']
        self.multimedia = list(map(lambda x: x['url'], json['multimedias']))
        #self.features = {}
        self.rooms = None
        self.bathrooms = None
        self.surface = None
        for feature in json['features']:
            v = feature['value']
            assert len(v) == 1
            v = v[0]
            k = feature['key']
            #self.features[feature['key']] = v[0]
            if 'rooms' in k:
                self.rooms = v
            elif 'bathrooms' in k:
                self.bathrooms = v
            elif 'surface' in k:
                self.surface = v
            else:
                print('Unexpected feature: ', k)
                raise Exception()

        self.ubication = json['address']['ubication']
        self.locations = []
        for location in json['address']['location']:
            for k in location:
                if not ('country' in k or k.startswith('level')):
                    continue
                self.locations.append(location[k])
        self.latitude = json['address']['coordinates']['latitude']
        self.longitude = json['address']['coordinates']['longitude']
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __hash__(self):
        return hash(self.id)
    
    def __str__(self):
        return f'<RealEstate id={self.id}>'
    
    def __repr__(self):
        return str(self)
    
    def as_dict(self):
        return {
            'id': self.id,
            'promotionId': self.promotionId,
            'multimedia': self.multimedia,
            'rooms': self.rooms,
            'bathrooms': self.bathrooms,
            'surface': self.surface,
            'ubication': self.ubication,
            'locations': self.locations,
            'latitude': self.latitude,
            'longitude': self.longitude
        }
