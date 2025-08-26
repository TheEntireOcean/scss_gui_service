# app/api/persons/routes.py
from flask import Blueprint
from flask_restful import Api, Resource, request
from app.models.person import Person
from app import db
from app.api.persons.serializers import PersonSchema, PersonCreateSchema
from app.utils.response_helpers import success_response, error_response, paginated_response
from app.api.middleware.auth import token_required

persons_bp = Blueprint('persons', __name__, url_prefix='/api/persons')
persons_api = Api(persons_bp)

class PersonListResource(Resource):
    @token_required
    def get(self, current_user):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        search = request.args.get('search')
        
        query = Person.query
        if search:
            query = query.filter(Person.name.ilike(f'%{search}%'))
        
        total = query.count()
        persons = query.offset((page - 1) * per_page).limit(per_page).all()
        
        schema = PersonSchema(many=True)
        return paginated_response(
            items={'persons': schema.dump(persons)},
            page=page,
            per_page=per_page,
            total=total
        )
    
    @token_required
    def post(self, current_user):
        schema = PersonCreateSchema()
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return error_response("Validation error", details=e.messages)
        
        person = Person(**data)
        db.session.add(person)
        db.session.commit()
        
        result_schema = PersonSchema()
        return success_response({
            'person': result_schema.dump(person)
        }, status_code=201)

class PersonDetailResource(Resource):
    @token_required
    def get(self, current_user, person_id):
        person = Person.query.get_or_404(person_id)
        schema = PersonSchema()
        return success_response({
            'person': schema.dump(person)
        })
    
    @token_required
    def put(self, current_user, person_id):
        person = Person.query.get_or_404(person_id)
        schema = PersonCreateSchema()
        
        try:
            data = schema.load(request.get_json() or {})
        except Exception as e:
            return error_response("Validation error", details=e.messages)
        
        for key, value in data.items():
            setattr(person, key, value)
        
        db.session.commit()
        
        result_schema = PersonSchema()
        return success_response({
            'person': result_schema.dump(person)
        })
    
    @token_required
    def delete(self, current_user, person_id):
        person = Person.query.get_or_404(person_id)
        db.session.delete(person)
        db.session.commit()
        return success_response(message="Person deleted successfully")

persons_api.add_resource(PersonListResource, '')
persons_api.add_resource(PersonDetailResource, '/<int:person_id>')