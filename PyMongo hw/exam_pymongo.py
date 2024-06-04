from pymongo import MongoClient

from pprint import pprint

client = MongoClient(
    host="127.0.0.1",
    port = 27017,
    username = "admin",
    password = "pass"
)

#b
database_names = client.list_database_names()
pprint(database_names)

#c
sample_db = client.sample
collection_names = sample_db.list_collection_names()
pprint(collection_names)
#d

collection = sample_db["books"]

# Retrieve one document from the collection
document = collection.find_one()

# Display the document
pprint(document)

#e
document_count = collection.count_documents({})
print("Number of documents in the collection:", document_count)

#exlpore
# a
num_books_gt_400_pages = collection.count_documents({"pageCount": {"$gt": 400}})
num_books_gt_400_pages_published = collection.count_documents({
    "pageCount": {"$gt": 400},
    "status": "PUBLISH"
})
print("Number of books with more than 400 pages:", num_books_gt_400_pages)
print("Number of books with more than 400 pages and are published:", num_books_gt_400_pages_published)

#b
num_books_android_keyword = collection.count_documents({
    "$or": [
        {"shortDescription": {"$regex": "Android", "$options": "i"}},
        {"longDescription": {"$regex": "Android", "$options": "i"}}
    ]
})

# Display the result
print("Number of books with the keyword 'Android' in their description:", num_books_android_keyword)
#c
pipeline = [
    {
        "$group": {
            "_id": None,
            "categories_0": {"$addToSet": {"$arrayElemAt": ["$categories.name", 0]}},
            "categories_1": {"$addToSet": {"$arrayElemAt": ["$categories.name", 1]}}
        }
    },
    {
        "$project": {
            "_id": 0,
            "categories_0": 1,
            "categories_1": 1
        }
    }
]
distinct_categories = list(collection.aggregate(pipeline))

# Extract the category lists
categories_0 = distinct_categories[0]["categories_0"] if distinct_categories else []
categories_1 = distinct_categories[0]["categories_1"] if distinct_categories else []

# Display the result
print(f"Distinct categories at index 0: {categories_0}")
print(f"Distinct categories at index 1: {categories_1}")

#d
languages = ["Python", "Java", "C++", "Scala"]

# Construct the regular expression pattern
regex_pattern = "|".join(languages)

# Perform aggregation to count books containing the language names
pipeline = [
    {"$match": {"longDescription": {"$regex": regex_pattern, "$options": "i"}}},
    {"$count": "total_books"}
]
result = list(collection.aggregate(pipeline))

# Display the result
if result:
    print(f"Number of books containing the language names in their long description: {result[0]['total_books']}")
else:
    print("No books found containing the specified language names in their long description.")

#e
    
pipeline = [
    {"$unwind": "$categories"},  # Deconstruct the categories array
    {"$group": {
        "_id": "$categories",  # Group by category
        "max_pages": {"$max": "$pageCount"},  # Calculate maximum number of pages
        "min_pages": {"$min": "$pageCount"},  # Calculate minimum number of pages
        "avg_pages": {"$avg": "$pageCount"}   # Calculate average number of pages
    }}
]
statistics = list(collection.aggregate(pipeline))

# Display the result
for stat in statistics:
    category = stat['_id']  # Get the category name
    max_pages = stat['max_pages']
    min_pages = stat['min_pages']
    avg_pages = stat['avg_pages']
    print(f"Category: {category}")
    print(f"Maximum number of pages: {max_pages}")
    print(f"Minimum number of pages: {min_pages}")
    print(f"Average number of pages: {avg_pages}")
    print()



#f
    
pipeline = [
    {
        "$project": {
            "year": {"$year": "$publishedDate"},
            "month": {"$month": "$publishedDate"},
            "day": {"$dayOfMonth": "$publishedDate"}
        }
    },
    {
        "$match": {"year": {"$gt": 2009}}
    },
    {
        "$limit": 20
    }
]
results = list(collection.aggregate(pipeline))

# Display the result
for result in results:
    print(result)

#g
pipeline = [
    {
        "$project": {
            "author1": {"$arrayElemAt": ["$authors", 0]},
            "author2": {"$arrayElemAt": ["$authors", 1]},
            "author3": {"$arrayElemAt": ["$authors", 2]},
            # Continue with additional authors as needed
        }
    },
    {
        "$limit": 20
    }
]
results = list(collection.aggregate(pipeline))

# Display the result
for result in results:
    print(result)

#h
pipeline = [
    {"$unwind": "$categories"},  # Deconstruct the categories array
    {"$group": {
        "_id": "$categories",  # Group by category
        "max_pages": {"$max": "$pageCount"},  # Calculate maximum number of pages
        "min_pages": {"$min": "$pageCount"},  # Calculate minimum number of pages
        "avg_pages": {"$avg": "$pageCount"},   # Calculate average number of pages
        "first_author": {"$arrayElemAt": ["$authors", 0]}  # Extract the first author
    }},
    {"$project": {
        "category": "$_id",
        "max_pages": 1,
        "min_pages": 1,
        "avg_pages": 1,
        "first_author": 1,
        "total_publications": 1,
        "new_column": {"$arrayElemAt": ["$first_author", 0]}  # Create a new column containing the name of the first author
    }},
    {"$group": {
        "_id": "$new_column",
        "total_publications": {"$sum": 1}  # Count the number of publications for each first author
    }},
    {"$sort": {"total_publications": -1}},  # Sort by total publications in descending order
    {"$limit": 10}  # Limit the result to the top 10 most prolific authors
]
result = list(collection.aggregate(pipeline))

# Display the result
for entry in result:
    author_name = entry['_id']
    publications = entry['total_publications']
    print(f"Author: {author_name}, Total Publications: {publications}")