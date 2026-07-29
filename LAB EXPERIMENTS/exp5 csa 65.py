from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Two sample documents
doc1 = "Artificial Intelligence is transforming technology."
doc2 = "Artificial Intelligence is changing modern technology."

# Convert text into numerical vectors
vectorizer = CountVectorizer()
vectors = vectorizer.fit_transform([doc1, doc2])

# Calculate cosine similarity
similarity = cosine_similarity(vectors)

print("Cosine Similarity Matrix:")
print(similarity)

print("\nSimilarity Score:", similarity[0][1])

# Interpretation
if similarity[0][1] > 0.8:
    print("Interpretation: The documents are highly similar.")
elif similarity[0][1] > 0.5:
    print("Interpretation: The documents are moderately similar.")
else:
    print("Interpretation: The documents are not very similar.")
