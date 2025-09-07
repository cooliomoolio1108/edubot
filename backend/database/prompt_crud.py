from . import prompt_collection, serialize_id
from bson import ObjectId

def get_all_prompts():
    prompt_list = list(prompt_collection.find({}))
    return [serialize_id(p) for p in prompt_list]

def get_prompt(prompt_id):
    doc = prompt_collection.find_one({"_id": ObjectId(prompt_id)})
    if not doc:
        return None  # or False if you prefer

    return serialize_id(doc)