from flask import Blueprint, jsonify, g
from models import db, Feature, FeatureDetail
from utils import token_required

feature_bp = Blueprint('feature', __name__, url_prefix='/features')

@feature_bp.route('/', methods=['GET'])
#@token_required
def list_features():
    features = Feature.query.filter_by(active=True).all()
    return jsonify([f.to_dict() for f in features]), 200

@feature_bp.route('/<string:key>', methods=['GET'])
#@token_required
def feature_detail(key):
    feature = Feature.query.filter_by(key=key, active=True).first()
    if not feature:
        return jsonify({'error': f'Feature with key {key} not found'}), 404

    detail = FeatureDetail.query.filter_by(feature_id=feature.id).first()
    if not detail:
        return jsonify({'error': f'Detail for feature_id {feature.id} not found'}), 404

    return jsonify(detail.to_dict()), 200

