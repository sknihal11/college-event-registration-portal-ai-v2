from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Event, Registration


def get_recommendations(user):
    events = Event.objects.all()
    if not events:
        return []

    # Prepare event category list
    event_categories = [event.category for event in events]

    # Create vectorizer
    vectorizer = TfidfVectorizer()
    event_vectors = vectorizer.fit_transform(event_categories)

    # Get user's registered categories
    user_regs = Registration.objects.filter(user=user)
    if not user_regs:
        return []

    user_categories = [reg.event.category for reg in user_regs]
    user_vector = vectorizer.transform([" ".join(user_categories)])

    similarity = cosine_similarity(user_vector, event_vectors)

    scores = list(enumerate(similarity[0]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    recommended_events = []
    for index, score in scores:
        event = list(events)[index]
        if event not in [reg.event for reg in user_regs]:
            recommended_events.append(event)

    return recommended_events[:3]