import pickle
import random
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).parent.parent


def load_character_works() -> dict:
    df = pd.read_csv(DATA_DIR / "data" / "characters_works.csv")
    return dict(zip(df["character"], df["work"]))


def load_statements() -> dict:
    df = pd.read_csv(DATA_DIR / "personality_statements.csv")
    return dict(zip(df["id"], df["statement"]))


def load_model_and_graph():
    with open(DATA_DIR / "small_graph.pkl", "rb") as f:
        graph = pickle.load(f)
    with open(DATA_DIR / "model.pkl", "rb") as f:
        model = pickle.load(f)
    return model, graph


def get_random_questions(statements: dict, count: int = 10) -> list:
    return random.sample(list(statements.keys()), count)


def calculate_user_vector(answers: dict, model) -> np.ndarray:
    user_vector = np.zeros(model.vector_size)
    valid_count = 0
    for axis, answer in answers.items():
        node = f"A:{answer}:{axis}"
        if node in model.wv:
            user_vector += model.wv[node]
            valid_count += 1
    if valid_count > 0:
        user_vector /= valid_count
    return user_vector


def find_matching_character(answers: dict) -> tuple[str, float]:
    model, graph = load_model_and_graph()
    user_vector = calculate_user_vector(answers, model)
    
    character_nodes = [n for n in graph.nodes if n.startswith("C:")]
    best_character = None
    best_similarity = -1

    for node in character_nodes:
        if node in model.wv:
            vec = model.wv[node]
            sim = cosine_similarity([vec], [user_vector]).flatten()[0]
            if sim > best_similarity:
                best_similarity = sim
                best_character = node

    character_name = best_character.replace("C:", "") if best_character else "Unknown"
    return character_name, best_similarity
