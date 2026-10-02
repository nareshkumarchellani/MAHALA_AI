def run(category,latitude,longitude,existing_cases):
    if latitude is None or longitude is None: return {'case':None,'reason':'Location not supplied'}
    for c in existing_cases:
        if c.get('category')==category and c.get('latitude') is not None and ((latitude-c['latitude'])**2+(longitude-c['longitude'])**2)**0.5 < .015:
            return {'case':c,'reason':'Nearby similar community case'}
    return {'case':None,'reason':'No nearby matching case'}
