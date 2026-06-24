import pandas as pd

REVIEW_COLUMNS = ['review', 'review text', 'review_text', 'comments', 'feedback', 'text']
RATING_COLUMNS = ['rating', 'ratings', 'score', 'stars']
PRODUCT_COLUMNS = ['product_name', 'product', 'class name', 'class_name', 'item', 'title', 'name']

def find_column(df, possible_names):
    df_columns_lower = {col.lower(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_columns_lower:
            return df_columns_lower[name.lower()]
    return None

def load_reviews(file):
    df = pd.read_csv(file);
    
    review_col = find_column(df, REVIEW_COLUMNS)
    rating_col = find_column(df, RATING_COLUMNS)
    product_col = find_column(df, PRODUCT_COLUMNS)
    
    if review_col is None:
        raise ValueError(f"Could not find a review column. Your columns are: {list(df.columns)}")
    
    rename_map = {}
    if review_col:
        rename_map[review_col] = 'review'
    if rating_col:
        rename_map[rating_col] = 'rating'
    if product_col:
        rename_map[product_col] = 'product_name'

    df = df.rename(columns=rename_map)
    
    df = df.dropna(subset=['review'])
    df['review'] = df['review'].str.strip()
    return df

def get_reviews_text(df, max_reviews=50):
    if len(df) > max_reviews:
        df = df.sample(n=max_reviews, random_state=42)

    reviews = []

    for index, row in df.iterrows():
        product = row.get('product_name', 'Unknown Product')
        rating = row.get('rating', 'N/A')
        review = row['review']

        review_entry = f"Product: {product}\nReview: {review}\nRating: {rating}/5"
        reviews.append(review_entry)

    all_reviews = "\n---\n".join(reviews)
    return all_reviews

