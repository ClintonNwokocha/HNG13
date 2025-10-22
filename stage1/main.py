from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import hashlib
from collections import Counter
from typing import Optional
import re

app = FastAPI()


database = {}

class StringInput(BaseModel):
    value: str

def analyze_string(value: str):
    clean_value = value.strip()
    freq = Counter(clean_value) 
    sha256_hash = hashlib.sha256(clean_value.encode()).hexdigest()

    return{
        "length": len(clean_value),
        "is_palindrome": clean_value.lower() == clean_value[::-1].lower(),
        "uniq": len(freq),
        "word_count": len(clean_value.split()),
        "sha256_hash": sha256_hash,
        "character_frequency_map": dict(freq)
    }
@app.get("/")
def home():
    return {"message": "String Analyzer API is running"}


@app.post("/strings", status_code=201)
def create_string(item: StringInput):
    value = item.value

    sha256_hash = hashlib.sha256(value.encode()).hexdigest()

    if sha256_hash in database:
        raise HTTPException(status_code=409, detail="String already exists")
    

    analysis = analyze_string(value)

    record = {
        "id" : sha256_hash,
        "value" : value,
        "properties" : analysis,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }

    database[sha256_hash] = record

    return record

@app.get("/strings/filter-by-natural-language")
def filter_by_natural_language(query: str):
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    query = query.lower()
    filters = {}

    if "palindromic" in query or "palindrome" in query:
        filters["is_palindrome"] = True

    if "single word" in query or "one word" in query:
        filters["word_count"] = 1
    elif "two word" in query:
        filters["word_count"] = 2
    elif "three word" in query:
        filters["word_count"] = 3

    match_longer = re.search(r"longer than (\d+)", query)
    if match_longer:
        filters["min_length"] = int(match_longer.group(1)) + 1

    match_shorter = re.search(r"shorter than (\d+)", query)
    if match_shorter:
        filters["max_length"] = int(match_shorter.group(1)) - 1

    match_at_least = re.search(r"at least (\d+) characters?", query)
    if match_at_least:
        filters["min_length"] = int(match_at_least.group(1))

    match_at_most = re.search(r"at most (\d+) characters?", query)
    if match_at_most:
        filters["max_length"] = int(match_at_most.group(1))

    match_letter = re.search(r"letter\s+([a-zA-Z])", query)
    if match_letter:
        filters["contains_character"] = match_letter.group(1)

    match_contains = re.search(r"contain(?:ing|s)?\s+(?:the\s+)?(?:letter\s+|character\s+)?([a-zA-Z])", query)
    if match_contains:
        filters["contains_character"] = match_contains.group(1)

    if "first vowel" in query or re.search(r"\bvowel\s+a\b", query):
        filters["contains_character"] = "a"

    if not filters:
        raise HTTPException(status_code=400, detail="Unable to parse natural language")
    
    results = list(database.values())

    if "is_palindrome" in filters:
        results = [r for r in results
                   if r["properties"]["is_palindrome"]
                   == filters["is_palindrome"]]
        
    if "word_count" in filters:
        results = [r for r in results
                   if r["properties"]["word_count"]
                   == filters["word_count"]]
        
    if "min_length" in filters:
        results = [r for r in results
                   if r["properties"]["length"]
                   >= filters["min_length"]]
        
    if "max_length" in filters:
        results = [r for r in results
                   if r["properties"]["length"]
                   <= filters["max_length"]]
        
    if "contains_character" in filters:
        results = [r for r in results
                   if filters["contains_character"].lower() in r["value"].lower()]

    if not results:
        raise HTTPException(status_code=404, details="No strings matched your query")

    return {
        "data": results,
        "count": len(results),
        "interpreted_query": {
            "original": query,
            "parsed_filters": filters
        }
    }

@app.get("/strings")
def get_all_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None
):
    if not database:
        return {"data": [], "count": 0, "filters_applied": {}}
    

    results = list(database.values())
    
    if is_palindrome is not None:
        results = [
            r for r in results
            if r["properties"]["is_palindrome"] == is_palindrome
        ]

    if min_length is not None:
        results = [
            r for r in results
            if r["properties"]["length"] >= min_length
        ]
    
    if max_length is not None:
        results = [
            r for r in results
            if r["properties"]["length"] <= max_length
        ]

    if word_count is not None:
        results = [
            r for r in results
            if r["properties"]["word_count"] == word_count
        ]

    if contains_character is not None:
        results = [
            r for r in results
            if contains_character.lower() in r["value"].lower()
        ]

    return {
        "data" : results,
        "count": len(results),
        "filters_applied": {
            "is_palindrome": is_palindrome,
            "min_length": min_length,
            "max_length": max_length,
            "word_count": word_count,
            "contains_character": contains_character
        }
    }

@app.get("/strings/{string_value}")
def get_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.strip().encode()).hexdigest()


    if sha256_hash not in database:
        raise HTTPException(status_code=404, detail="string not found")
    
    return database[sha256_hash]




@app.delete("/strings/{string_value}", status_code=204)
def delete_string(string_value: str):
    sha256_hash = hashlib.sha256(string_value.strip().encode()).hexdigest()

    if sha256_hash not in database:
        raise HTTPException(status_code=404, detail="string not found")
    

    del database[sha256_hash]

    return None