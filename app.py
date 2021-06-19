import logging, requests
from math import cos
from typing import Sequence
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:15432/campsite_finder'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

ma = Marshmallow(app)

class Facility(db.Model):
    facility_id = db.Column(db.Text, primary_key=True)
    facility_name = db.Column(db.Text)
    facility_type_description = db.Column(db.Text)
    facility_reservation_url = db.Column(db.Text)
    facility_map_url = db.Column(db.Text)
    facility_longitude = db.Column(db.Float)
    facility_latitude = db.Column(db.Float)
    reservable = db.Column(db.Boolean)
    enabled = db.Column(db.Boolean)
    medias = db.relationship('Media', backref='facility', lazy='joined')

    def __repr__(self) -> str:
        return '<Facility ID: %r>' % self.facility_id

class Media(db.Model):
    media_id = db.Column(db.Text, primary_key=True)
    media_type = db.Column(db.Text)
    entity_id = db.Column(db.Text, db.ForeignKey('facility.facility_id'))
    entity_type = db.Column(db.Text)
    height = db.Column(db.Float)
    width = db.Column(db.Float)
    url = db.Column(db.Text)
    is_gallery = db.Column(db.Boolean)

    def __repr__(self) -> str:
        return '<Media ID: %r>' % self.media_id

class FacilitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Facility
    medias = ma.Nested('MediaSchema', many=True)

class MediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Media

facility_schema = FacilitySchema()
facilities_schema = FacilitySchema(many=True)

media_schema = MediaSchema()
medias_schema = MediaSchema(many=True)

@app.route('/api/search', methods=['POST'])
def search():
    try:
        date = request.get_json()['dates'][0]
        lat = request.get_json()['latitude']
        lng = request.get_json()['longitude']
        base = 111.3
        radius = 36.00

        min_lat = lat - radius/base
        max_lat = lat + radius/base
        min_lng = lng - radius/(base * cos(lat))
        max_lng = lng + radius/(base * cos(lat))

        results = Facility.query.filter(Facility.facility_type_description=='Campground')

        if min_lat > 0:
            results = results.filter(Facility.facility_latitude>=min_lat)
        else:
            results = results.filter(Facility.facility_latitude<=min_lat)
        if max_lat > 0:
            results = results.filter(Facility.facility_latitude<=max_lat)
        else:
            results = results.filter(Facility.facility_latitude>=max_lat)
        if min_lng > 0:
            results = results.filter(Facility.facility_longitude>=min_lng)
        else:
            results = results.filter(Facility.facility_longitude<=min_lng)
        if max_lng > 0:
            results = results.filter(Facility.facility_longitude<=max_lng)
        else:
            results = results.filter(Facility.facility_longitude>=max_lng)

        results = results.limit(11).all()

        params = { 'start_date': datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-01T00:00:00.000Z") }
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Host': 'www.recreation.gov',
            'User-Agent': 'PostmanRuntime/7.26.10',
        }

        campgrounds = []

        for result in results:
            url = 'https://www.recreation.gov/api/camps/availability/campground/{id}/month'.format(id=result.facility_id)
            response = requests.get(url, params=params, headers=headers)
            res = response.json()

            if res['count'] and res['count'] > 0:
                site = { 'facility': facility_schema.dump(result), 'sites': {} }
                available = False
                for id, data in res['campsites'].items():
                    for date, status in data['availabilities'].items():
                        if status == 'Available':
                            available = True
                            if id in site['sites']:
                                site['sites'][id].append(date)
                            else:
                                site['sites'][id] = [date]
                if available:
                    campgrounds.append(site)

        return jsonify({ 'status': True, 'campgrounds': campgrounds })
    except Exception as e:
        logging.error(__name__, exc_info=e)
        return jsonify({ 'status': False })

if __name__ == "__main__":
    app.run()
