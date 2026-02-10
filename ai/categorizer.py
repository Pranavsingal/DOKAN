from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import os

# Load and train once
products_file = 'data/products.csv'

if os.path.exists(products_file):
    products = pd.read_csv(products_file)

    if not products.empty and 'name' in products.columns and 'category' in products.columns:
        vectorizer = CountVectorizer()
        x = vectorizer.fit_transform(products['name'])  # lowercase 'x'
        y = products['category']

        model = MultinomialNB()
        model.fit(x, y)
    else:
        model = None
        vectorizer = None
else:
    model = None
    vectorizer = None


def categorize_product(product_name):
    if not model or not vectorizer:
        return "Unknown"

    product_vector = vectorizer.transform([product_name])
    category_prediction = model.predict(product_vector)

    return category_prediction[0]
