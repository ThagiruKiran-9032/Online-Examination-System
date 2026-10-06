from app.db.session import SessionLocal, engine, Base
from app.models.exam import Exam
from app.models.question import Question

SAMPLE_EXAMS = [
    {
        "title": "Numerical Ability & Mathematics Quiz",
        "description": "Test your speed calculation, arithmetic, and problem solving skills.",
        "category": "Numeric",
        "duration_minutes": 15,
        "passing_marks": 2,
        "max_attempts": 2,
        "is_published": True,
        "questions": [
            {
                "question_text": "What is 15 * 12?",
                "question_type": "mcq",
                "options": ["160", "180", "190", "200"],
                "correct_answer": "1",  # 180
                "marks": 1
            },
            {
                "question_text": "What is the square root of 256?",
                "question_type": "mcq",
                "options": ["14", "16", "18", "24"],
                "correct_answer": "1",  # 16
                "marks": 1
            },
            {
                "question_text": "If a car travels at 60 km/h for 2.5 hours, how far does it travel?",
                "question_type": "mcq",
                "options": ["120 km", "140 km", "150 km", "160 km"],
                "correct_answer": "2",  # 150 km
                "marks": 1
            }
        ]
    },
    {
        "title": "Logical Reasoning Challenge",
        "description": "Analytical thinking, pattern recognition, and deductive logic test.",
        "category": "Logic & Reasoning",
        "duration_minutes": 15,
        "passing_marks": 2,
        "max_attempts": 2,
        "is_published": True,
        "questions": [
            {
                "question_text": "Complete the sequence: 2, 4, 8, 16, ?",
                "question_type": "mcq",
                "options": ["24", "28", "32", "64"],
                "correct_answer": "2",  # 32
                "marks": 1
            },
            {
                "question_text": "If ALL A are B, and ALL B are C, then ALL A are C.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "0",  # True
                "marks": 1
            },
            {
                "question_text": "Which word does NOT belong with the others: Apple, Banana, Carrot, Orange?",
                "question_type": "mcq",
                "options": ["Apple", "Banana", "Carrot", "Orange"],
                "correct_answer": "2",  # Carrot
                "marks": 1
            }
        ]
    },
    {
        "title": "English Proficiency & Grammar Assessment",
        "description": "Vocabulary, synonyms, and grammatical rules test.",
        "category": "English",
        "duration_minutes": 15,
        "passing_marks": 2,
        "max_attempts": 2,
        "is_published": True,
        "questions": [
            {
                "question_text": "Identify the correct synonym for 'ABUNDANT':",
                "question_type": "mcq",
                "options": ["Scarce", "Plentiful", "Rare", "Tiny"],
                "correct_answer": "1",  # Plentiful
                "marks": 1
            },
            {
                "question_text": "She _____ to the market yesterday.",
                "question_type": "mcq",
                "options": ["go", "went", "gone", "going"],
                "correct_answer": "1",  # went
                "marks": 1
            },
            {
                "question_text": "Is 'Receive' spelled correctly?",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "0",  # True
                "marks": 1
            }
        ]
    },
    {
        "title": "World General Knowledge Quiz",
        "description": "Geography, science facts, and world awareness assessment.",
        "category": "General Knowledge",
        "duration_minutes": 10,
        "passing_marks": 2,
        "max_attempts": 2,
        "is_published": True,
        "questions": [
            {
                "question_text": "Which planet is known as the Red Planet?",
                "question_type": "mcq",
                "options": ["Venus", "Mars", "Jupiter", "Saturn"],
                "correct_answer": "1",  # Mars
                "marks": 1
            },
            {
                "question_text": "What is the capital city of France?",
                "question_type": "mcq",
                "options": ["London", "Berlin", "Paris", "Madrid"],
                "correct_answer": "2",  # Paris
                "marks": 1
            },
            {
                "question_text": "The Pacific Ocean is the largest ocean on Earth.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "0",  # True
                "marks": 1
            }
        ]
    },
    {
        "title": "Python Programming & Data Structures Quiz",
        "description": "Core technical concepts, Python syntax, and fundamental algorithms.",
        "category": "Technical",
        "duration_minutes": 15,
        "passing_marks": 2,
        "max_attempts": 2,
        "is_published": True,
        "questions": [
            {
                "question_text": "Which keyword is used to define a function in Python?",
                "question_type": "mcq",
                "options": ["func", "def", "function", "lambda"],
                "correct_answer": "1",  # def
                "marks": 1
            },
            {
                "question_text": "In Python, lists are immutable.",
                "question_type": "true_false",
                "options": ["True", "False"],
                "correct_answer": "1",  # False
                "marks": 1
            },
            {
                "question_text": "What data structure operates on a First In, First Out (FIFO) basis?",
                "question_type": "mcq",
                "options": ["Stack", "Queue", "Tree", "Graph"],
                "correct_answer": "1",  # Queue
                "marks": 1
            }
        ]
    }
]

def seed_exams():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        for exam_data in SAMPLE_EXAMS:
            existing = db.query(Exam).filter(Exam.title == exam_data["title"]).first()
            if not existing:
                questions_data = exam_data.pop("questions")
                exam = Exam(**exam_data)
                db.add(exam)
                db.commit()
                db.refresh(exam)
                
                for q_data in questions_data:
                    q = Question(exam_id=exam.id, **q_data)
                    db.add(q)
                db.commit()
                print(f"[Seed] Created Published Exam: '{exam.title}' ({exam.category}) with {len(questions_data)} questions.")
            else:
                print(f"[Seed] Exam '{exam_data['title']}' already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_exams()
