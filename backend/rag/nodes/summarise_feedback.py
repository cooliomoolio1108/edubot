from rag.graph.state import FeedbackState
from database import feedback_collection
from . import llm_stream

def load_feedback(state: FeedbackState) -> FeedbackState:
    feedbacks = list(feedback_collection.find())
    print("success_response:", feedbacks)
    return {**state,"feedback": feedbacks}
    
def summarise_feedback(state: FeedbackState)-> FeedbackState:
    print("Summarising feedback:", state)
    feedback = state.get("feedback", [])
    if not feedback:
        return {"summary": "No feedback available."}

    comments = [f.get("comment", "") for f in feedback if f.get("comment")]
    ratings = [f.get("rating") for f in feedback if f.get("rating") is not None]
    avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else "N/A"
    print("AVG:", avg_rating)
    # Build summarisation prompt
    prompt = f"""
    You are analyzing feedback from users.

    Average rating: {avg_rating}
    Total responses: {len(feedback)}

    Comments:
    {chr(10).join("- " + c for c in comments)}

    Please:
    - Summarize positives, negatives, and suggestions in 3–5 bullet points.
    - State overall sentiment (positive/neutral/negative).
    - Keep it concise and clear for an admin dashboard.
    """

    response = llm_stream.invoke(prompt)
    summary = getattr(response, "content", str(response))
    return {
        **state,
        "summary": summary
    }