import pandas as pd

REVIEW_COLUMNS  = ['review', 'review text', 'review_text', 'comments', 'feedback', 'text']
RATING_COLUMNS  = ['rating', 'ratings', 'rate', 'score', 'stars']
PRODUCT_COLUMNS = ['product_name', 'product', 'class name', 'class_name', 'item', 'title', 'name']

MAX_REVIEW_CHARS = 500 


def find_column(df, possible_names):
    df_lower = {col.lower(): col for col in df.columns}
    for name in possible_names:
        if name.lower() in df_lower:
            return df_lower[name.lower()]
    return None


def load_reviews(file):
    
    df = None
    for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        try:
            df = pd.read_csv(
                file,
                encoding=encoding,
                on_bad_lines='skip', 
                engine='python'       
            )
            break
        except UnicodeDecodeError:
            try:
                file.seek(0)        
            except AttributeError:
                pass
            continue
        except Exception:
            break

    if df is None or df.empty:
        raise ValueError("Could not read the CSV file. Please check the file and try again.")

    review_col  = find_column(df, REVIEW_COLUMNS)
    rating_col  = find_column(df, RATING_COLUMNS)
    product_col = find_column(df, PRODUCT_COLUMNS)

    if review_col is None:
        raise ValueError(
            f"No review column found. Your CSV has these columns: {list(df.columns)}\n"
            f"Expected one of: {REVIEW_COLUMNS}"
        )

    rename_map = {review_col: 'review'}
    if rating_col:
        rename_map[rating_col] = 'rating'
    if product_col:
        rename_map[product_col] = 'product_name'

    df = df.rename(columns=rename_map)

    df = df.dropna(subset=['review'])          
    df['review'] = df['review'].str.strip()   
    df = df[df['review'] != '']                
    df = df.drop_duplicates(subset=['review'])  

    if 'rating' in df.columns:
        df['rating'] = pd.to_numeric(df['rating'], errors='coerce')

    if 'product_name' in df.columns:
        df['product_name'] = df['product_name'].fillna('Unknown Product')
        df['product_name'] = df['product_name'].astype(str).str.strip()

    if df.empty:
        raise ValueError("No valid reviews found after cleaning. The CSV may only contain empty rows.")

    return df


def get_reviews_text(df, max_reviews=50):
    """
    Returns a formatted string of reviews to send to the AI.

    Uses stratified sampling when the dataset is large:
      - Half the sample from low-rated reviews (≤2) so negatives aren't missed
      - Half from the rest
    This prevents a dataset dominated by positive reviews from hiding return risks.
    """
    if len(df) > max_reviews:
        df = _stratified_sample(df, max_reviews)

    reviews = []
    for _, row in df.iterrows():
        product = row.get('product_name', 'Unknown Product')
        review  = str(row['review'])[:MAX_REVIEW_CHARS]
        rating  = row.get('rating', 'N/A')

        reviews.append(f"Product: {product}\nReview: {review}\nRating: {rating}/5")

    return "\n---\n".join(reviews)


def _stratified_sample(df, n):
    """
    Splits sample evenly between low-rated (≤2) and higher-rated reviews.
    Falls back to pure random sample if no rating column exists.
    """
    if 'rating' not in df.columns:
        return df.sample(n=n, random_state=42)

    low  = df[df['rating'] <= 2]
    high = df[df['rating'] > 2]

    n_low  = min(len(low),  n // 2)
    n_high = min(len(high), n - n_low)

    parts = []
    if n_low  > 0: parts.append(low.sample( n=n_low,  random_state=42))
    if n_high > 0: parts.append(high.sample(n=n_high, random_state=42))

    return pd.concat(parts).sample(frac=1, random_state=42) 