import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

# to load env. variables
from dotenv import load_dotenv
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(os.environ.get('DB_USER'), os.environ.get('DB_PASSWORD'),'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question_valid = {"question": "TEST Q", "answer": "TEST A", 'category': 3, "difficulty": 5}
        self.new_question_invalid_category = {"question": "TEST Q", "answer": "TEST Q", 'category': 300, "difficulty": 5}
        self.new_question_missing_question = {"question": None, "answer": "TEST Q", 'category': 3, "difficulty": 5}

            
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_paginated_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
    
    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get("/questions?page=1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
    
    def test_get_category_questions(self):
        res = self.client().get("/categories/1/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])

    def test_404_sent_requesting_beyond_valid_category(self):
        res = self.client().get("/categories/10000/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
    
    def test_post_new_question(self):
        res = self.client().post("/questions", json=self.new_question_valid)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
    
    def test_post_new_question_invalid_category(self):
        res = self.client().post("/questions", json=self.new_question_invalid_category)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    def test_post_new_question_missing_question(self):
        res = self.client().post("/questions", json=self.new_question_missing_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)

    def test_delete_question(self):
        res = self.client().delete("/questions/5")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['id'], 5)
    
    def test_delete_non_existing_question(self):
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_quiz_question_all_categories(self):
        res = self.client().post("/quizzes", json={'quiz_category': {'id': 0}, 'previous_questions' : []})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])

    def test_quiz_no_more_questions(self):
        res = self.client().post("/quizzes", json={'quiz_category': {'id': 1}, 'previous_questions' : [i for i in range(1000)]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertFalse(data['question'])
    

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()