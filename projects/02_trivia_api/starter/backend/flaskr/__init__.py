import os
from flask import Flask, json, request, abort, jsonify
from flask.json.tag import PassDict
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

# additional import
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    # paginates passed questions based on passed parameters
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app)

    @app.after_request
    def after_request(response):
        # sets CORS headers
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers',
                             'GET, POST, DELETE, OPTION')
        return response

    @app.route('/questions')
    def retrieve_questions():
        # GET endopoint for listing all questions
        selection = Question.query.order_by(Question.id).all()
        paginated_questions = paginate(request, selection)
        categories = Category.query.order_by(Category.id).all()

        # no questions or bad page path variable
        if len(paginated_questions) == 0:
            abort(404)

        return jsonify(
            {
                "questions": paginated_questions,
                "total_questions": len(Question.query.all()),
                "categories": {category.id: category.type for category in categories},
            }
        )

    @app.route('/categories')
    def retrieve_categories():
        # GET endpoint listing all categories
        categories = Category.query.order_by(Category.id).all()

        # no categories in database
        if len(categories) == 0:
            abort(404)

        return jsonify(
            {
                "categories": {category.id: category.type for category in categories}
            }
        )

    @app.route('/categories/<int:id>/questions')
    def retrieve_category_questions(id):
        # GET endpoint for listing questions from selected category, passed as path variable

        # category check
        if not Category.query.filter(Category.id == id).one_or_none():
            abort(404)

        selection = Question.query.filter(
            Question.category == id).order_by(Question.id).all()

        return jsonify(
            {
                'questions': [question.format() for question in selection],
                "total_questions": len(selection),
            }
        )

    @app.route('/questions', methods=['POST'])
    def add_question():
        # POST endpoint to search for a question OR add a question into database
        body = request.get_json()

        searchTerm = body.get('searchTerm', None)
        # if search term is passed into request, returns quenstions found
        if searchTerm:
            selection = Question.query.filter(Question.question.like(
                "%{}%".format(searchTerm))).order_by(Question.id).all()

            return jsonify(
                {
                    "questions": [question.format() for question in selection],
                    "total_questions": len(selection),
                }
            )

        # add a question, returns newly added question
        question = body.get('question', None)
        answer = body.get('answer', None)
        category = body.get('category', None)
        difficulty = body.get('difficulty', None)
        #print (question,answer,category,difficulty)
        # incomplete request
        if not(question and answer and category and difficulty):
            abort(422)

        # non existing category
        if not Category.query.filter(Category.id == category).one_or_none():
            abort(422)

        q = Question(question, answer, category, difficulty)
        q.insert()

        return jsonify(
            {
                'question': q.format()
            }
        )

    @app.route('/questions/<int:id>', methods=['DELETE'])
    def delete_question(id):
        # DELETE endpoint to delete a question with id passed as path variable
        question = Question.query.filter(Question.id == id).one_or_none()

        if question is None:
            abort(404)
        question.delete()
        return jsonify(
            {
                'id': id
            }
        )

    @app.route('/quizzes', methods=["POST"])
    def quizz():
        # POST endpoind, receiving category id (0 for all) and list of already answered questions, returns a random unanswered question
        body = request.get_json()
        category = body.get('quiz_category', None).get('id', None)
        previous_questions = body.get('previous_questions', None)

        all_questions = []
        if category == 0:
            all_questions = Question.query.all()
        else:
            if not Category.query.filter(Category.id == category).one_or_none():
                abort(422)
            all_questions = Question.query.filter(
                Question.category == category).all()

        unasnwered_questions = [
            q for q in all_questions if q.id not in previous_questions]

        if unasnwered_questions:
            return jsonify(
                {
                    'question': random.choice(unasnwered_questions).format()
                }
            )
        # when no question left
        return jsonify(
            {
                'question': None,
                'info': 'No more available questions'
            }
        )

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404,
                    "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422,
                    "message": "unprocessable"}),
            422,
        )

    @app.errorhandler(500)
    def internat_server_error(error):
        return (
            jsonify({"success": False, "error": 500,
                    "message": "runtime error, bad programming :)"}),
            500,
        )

    return app
