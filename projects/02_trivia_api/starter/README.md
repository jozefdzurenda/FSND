# Udacity Trivia

This project is a simple Trivia game. Users are able list questions by category, to add own questions and, the main part, play the game/quiz. 

All backend code follows [PEP8 style guidelines](https://www.python.org/dev/peps/pep-0008/). 

## Getting Started

### Pre-requisites and Local Development 
Developers using this project should already have Python3, pip and node installed on their local machines.

#### Backend

From the backend folder run `pip install requirements.txt`. All required packages are included in the requirements file. 

To run the application run the following commands: 
```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

These commands put the application in development and directs our application to use the `__init__.py` file in our flaskr folder. Working in development mode shows an interactive debugger in the console and restarts the server whenever changes are made. Currently, the database access is password protected - user *postgres*, password *postgress*, which is set in *models.py* and *test_flaskr.py* .
The application is run on `http://127.0.0.1:5000/` by default and is a proxy in the frontend configuration. 

#### Frontend

From the frontend folder, run the following commands to start the client: 
```
npm install // only once to install dependencies
npm start 
```

By default, the frontend will run on localhost:3000. 

### Tests
In order to run tests navigate to the backend folder and run the following commands: 

```
dropdb trivia_test
createdb tiriva_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

The first time you run the tests, omit the dropdb command. 

All tests are kept in that file and should be maintained as updates are made to app functionality. 

## API Reference

### Getting Started
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: This version of the application does not require authentication or API keys. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 

### Endpoints 
#### GET /questions
- General:
    - Returns a list of questions and total number of questions, also lists categories
    - Results are paginated in groups of 10. Include a request argument to choose page number, starting from 1. 
- Sample: `curl http://127.0.0.1:5000/questions`
- Sample: `curl http://127.0.0.1:5000/questions?page=2`

``` {
  "questions": [
    {
      "question": "Sample question",
      "answer": "Sample answer",
      "difficulty": 1,
      "category": 1
    },
    ...
  ],
"total_questions": 100,
"categories": { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
}
```

#### GET /categories
- General:
    - Returns a list of categories
- Sample: `curl http://127.0.0.1:5000/categories`

``` {
    'categories': { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" }
}
```

#### GET /categories/{category_id}/questions
- General:
    - Returns a list of questions for selected category
- Sample: `curl http://127.0.0.1:5000/categories/1/questions`

``` {
  "questions": [
    {
      "question": "Sample question",
      "answer": "Sample answer",
      "difficulty": 1,
      "category": 1
    },
    ...
  ],
"total_questions": 100,
"categories": { '1' : "Science",
    '2' : "Art",
    '3' : "Geography",
    '4' : "History",
    '5' : "Entertainment",
    '6' : "Sports" },
}
```

#### DELETE /questions/{question_id}
- General:
    - Deletes the question of the given ID if it exists. Returns the id of the deleted question
- Sample: `curl -X DELETE http://127.0.0.1:5000/questions/1`
```
{
  "id": 1
}
```

#### POST /questions
- General:
    - If provided with search term object, it returns list of questions that match the search term. Otherwise it adds new question to the database and returns it as a question object.
- Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"search_term": "Tom"}'`
```
{
  "questions": [
    {
      "question": "Who does Tom Handks do for living",
      "answer": "Actor",
      "difficulty": 1,
      "category": 1
    },
    ...
  ],
"total_questions": 10
```
- Sample: `curl http://127.0.0.1:5000/questions -X POST -H "Content-Type: application/json" -d '{"question": "TEST Q", "answer": "TEST A", 'category': 3, "difficulty": 5}' `
```
{
  "question":
    {
      "question": "TEST Q",
      "answer": "TEST A",
      "difficulty": 5,
      "category": 3
    }
}
```

#### POST /quizz
- General:
    - Accepts category object (category id 0 for all) and list of question ids that were already played, returns a random question from a valid pool
	- Returns and empty object when there is no available question left

- Sample: `curl http://127.0.0.1:5000/quizz -X POST -H "Content-Type: application/json" -d '{{"previous_questions":  [1, 4, 20, 15], "quiz_category": { "id" : 1, "category" : "Science" }}'`
```
{
  "question": [
    {
      "question": "Who does Tom Handks do for living",
      "answer": "Actor",
      "difficulty": 1,
      "category": 1
    }
}
```


## Deployment N/A

## Authors
Jozef Dzurenda 

## Acknowledgements 
Thank god for google and stackoverflow