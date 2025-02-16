import pandas as pd
import random

def generate_realistic_product_names(data):
    # Read the data into a DataFrame
    lines = data.strip().split('\n')
    header = lines[0].split(',')
    records = [line.split(',') for line in lines[1:]]
    df = pd.DataFrame(records, columns=header)
    
    # Define category-specific product names
    category_products = {
        'Home & Kitchen': [
            'Coffee Maker', 'Food Processor', 'Blender', 'Toaster', 'Rice Cooker',
            'Kitchen Scale', 'Mixing Bowl', 'Cutting Board', 'Knife Set', 'Cookware Set',
            'Storage Container', 'Dish Rack', 'Paper Towel Holder', 'Trash Can', 'Vacuum Cleaner',
            'Air Purifier', 'Humidifier', 'Throw Pillow', 'Bath Towel', 'Shower Curtain'
        ],
        'Beauty': [
            'Face Cream', 'Lipstick', 'Mascara', 'Foundation', 'Eye Shadow Palette',
            'Hair Dryer', 'Nail Polish', 'Face Mask', 'Moisturizer', 'Shampoo',
            'Conditioner', 'Body Lotion', 'Perfume', 'Hair Straightener', 'Facial Cleanser',
            'Sunscreen', 'Hand Cream', 'Makeup Brush Set', 'Hair Serum', 'Face Scrub'
        ],
        'Electronics': [
            'Bluetooth Speaker', 'Wireless Earbuds', 'Power Bank', 'Smart Watch', 'USB Hub',
            'Webcam', 'Gaming Mouse', 'Keyboard', 'Monitor', 'Laptop Stand',
            'Phone Charger', 'Tablet Case', 'External Hard Drive', 'Wi-Fi Router', 'Security Camera',
            'LED Light Strip', 'Desk Lamp', 'Portable Fan', 'Digital Clock', 'Mini Projector'
        ],
        'Automotive': [
            'Car Phone Mount', 'Air Freshener', 'Dash Cam', 'Floor Mats', 'Car Vacuum',
            'Jump Starter', 'Tire Pressure Gauge', 'Car Cover', 'Windshield Wipers', 'Phone Holder',
            'Car Charger', 'Seat Covers', 'Air Compressor', 'Tool Kit', 'First Aid Kit',
            'Car Wash Kit', 'Touch Up Paint', 'Battery Charger', 'Oil Filter', 'LED Headlights'
        ],
        'Sports': [
            'Yoga Mat', 'Resistance Bands', 'Water Bottle', 'Gym Bag', 'Running Shoes',
            'Exercise Ball', 'Dumbbells', 'Jump Rope', 'Fitness Tracker', 'Tennis Racket',
            'Basketball', 'Soccer Ball', 'Cycling Gloves', 'Swimming Goggles', 'Knee Brace',
            'Weight Bench', 'Golf Gloves', 'Camping Tent', 'Hiking Backpack', 'Skateboard'
        ],
        'Toys': [
            'Building Blocks', 'Remote Car', 'Puzzle Set', 'Action Figure', 'Board Game',
            'Art Set', 'Plush Toy', 'Play Dough', 'Card Game', 'Educational Toy',
            'Robot Kit', 'Doll House', 'Science Kit', 'Musical Toy', 'Building Set',
            'Flying Drone', 'Magic Kit', 'Play Kitchen', 'Train Set', 'Drawing Tablet'
        ],
        'Books': [
            'Notebook', 'Planner', 'Journal', 'Coloring Book', 'Sketchbook',
            'Calendar', 'Address Book', 'Photo Album', 'Reading Light', 'Book Stand',
            'Bookmark Set', 'Desk Organizer', 'Filing Cabinet', 'Magazine Holder', 'Book Cover',
            'Dictionary Stand', 'Library Cart', 'Book Ends', 'Reading Glasses', 'Page Markers'
        ],
        'Clothing': [
            'T-Shirt', 'Backpack', 'Wallet', 'Sunglasses', 'Watch',
            'Belt', 'Scarf', 'Gloves', 'Socks', 'Hat',
            'Umbrella', 'Jewelry Box', 'Shoe Rack', 'Tie Holder', 'Dress Hanger',
            'Travel Bag', 'Coin Purse', 'Hair Tie', 'Shoe Horn', 'Garment Steamer'
        ]
    }
    
    # Generate unique product names
    used_names = set()
    new_names = []
    replacements = {}
    
    for _, row in df.iterrows():
        category = row['CATEGORY']
        original_name = row['PRODUCT_NAME']
        
        if original_name in replacements:
            new_names.append(replacements[original_name])
            continue
            
        while True:
            new_name = random.choice(category_products[category])
            if new_name not in used_names:
                used_names.add(new_name)
                replacements[original_name] = new_name
                new_names.append(new_name)
                break
                
        # If we run out of unique names for a category, reset the used names for that category
        if len(used_names.intersection(category_products[category])) == len(category_products[category]):
            used_names = used_names - set(category_products[category])
    
    # Create new DataFrame with updated names
    df['PRODUCT_NAME'] = new_names
    return df

# Function to format output as CSV
def format_as_csv(df):
    return df.to_csv(index=False)