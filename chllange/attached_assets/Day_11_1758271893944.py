"""
Retro Restaurant - Complete Streamlit Web Application
A comprehensive restaurant ordering system with cart, checkout, reviews, and WhatsApp integration.
"""

import streamlit as st
import json
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, TypedDict
from dataclasses import dataclass
import uuid

# Configuration
GST_RATE = 0.18  # 18% GST
RESTAURANT_PHONE = "+918056443430"

# Data Models
class MenuItem(TypedDict):
    id: str
    name: str
    description: str
    price: float
    category: str
    imageUrl: str
    available: bool

class CartItem(TypedDict):
    menuItem: MenuItem
    quantity: int

class Customer(TypedDict):
    name: str
    phone: str
    email: str
    address: str

class OrderItem(TypedDict):
    menuItemId: str
    quantity: int
    unitPrice: float
    totalPrice: float

class Order(TypedDict):
    id: str
    customer: Customer
    orderType: str  # 'dine-in' or 'takeaway'
    paymentMethod: str
    subtotal: float
    gstAmount: float
    total: float
    orderItems: List[OrderItem]
    createdAt: str

class Review(TypedDict):
    id: str
    customerName: str
    rating: int
    comment: str
    createdAt: str

# Tamil Nadu Menu Data
MENU_ITEMS: List[MenuItem] = [
    # Biryani
    {
        "id": "1", "name": "Retro Restaurant Mutton Biryani", "description": "Signature mutton biryani with aromatic spices and basmati rice",
        "price": 280.0, "category": "Biryani", "imageUrl": "https://images.unsplash.com/photo-1563379091339-03246963d29c", "available": True
    },
    {
        "id": "2", "name": "Chicken Biryani", "description": "Tender chicken pieces cooked with fragrant biryani rice",
        "price": 240.0, "category": "Biryani", "imageUrl": "https://images.unsplash.com/photo-1563379091339-03246963d29c", "available": True
    },
    {
        "id": "3", "name": "Prawn Biryani", "description": "Fresh prawns layered with aromatic biryani rice",
        "price": 320.0, "category": "Biryani", "imageUrl": "https://images.unsplash.com/photo-1563379091339-03246963d29c", "available": True
    },
    {
        "id": "4", "name": "Egg Biryani", "description": "Boiled eggs cooked with flavorful biryani rice",
        "price": 180.0, "category": "Biryani", "imageUrl": "https://images.unsplash.com/photo-1563379091339-03246963d29c", "available": True
    },
    
    # Starters
    {
        "id": "5", "name": "Chicken 65", "description": "Spicy deep-fried chicken with curry leaves and chilies",
        "price": 220.0, "category": "Starters", "imageUrl": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8", "available": True
    },
    {
        "id": "6", "name": "Mutton Pepper Fry", "description": "Tender mutton pieces tossed with black pepper and spices",
        "price": 280.0, "category": "Starters", "imageUrl": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8", "available": True
    },
    {
        "id": "7", "name": "Fish Fry", "description": "Marinated fish fillets fried to golden perfection",
        "price": 250.0, "category": "Starters", "imageUrl": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8", "available": True
    },
    {
        "id": "8", "name": "Prawn Roast", "description": "Prawns roasted with onions and South Indian spices",
        "price": 300.0, "category": "Starters", "imageUrl": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8", "available": True
    },
    
    # Soups
    {
        "id": "9", "name": "Mutton Bone Soup", "description": "Rich and nutritious soup made from mutton bones",
        "price": 120.0, "category": "Soups", "imageUrl": "https://images.unsplash.com/photo-1547592166-23ac45744acd", "available": True
    },
    {
        "id": "10", "name": "Chicken Soup", "description": "Clear chicken soup with vegetables and herbs",
        "price": 100.0, "category": "Soups", "imageUrl": "https://images.unsplash.com/photo-1547592166-23ac45744acd", "available": True
    },
    {
        "id": "11", "name": "Tomato Soup", "description": "Fresh tomato soup with aromatic spices",
        "price": 80.0, "category": "Soups", "imageUrl": "https://images.unsplash.com/photo-1547592166-23ac45744acd", "available": True
    },
    
    # Curries
    {
        "id": "12", "name": "Chettinad Chicken", "description": "Spicy chicken curry with Chettinad spices",
        "price": 260.0, "category": "Curries", "imageUrl": "https://images.unsplash.com/photo-1565557623262-b51c2513a641", "available": True
    },
    {
        "id": "13", "name": "Mutton Curry", "description": "Traditional Tamil mutton curry with coconut and spices",
        "price": 300.0, "category": "Curries", "imageUrl": "https://images.unsplash.com/photo-1565557623262-b51c2513a641", "available": True
    },
    {
        "id": "14", "name": "Fish Curry", "description": "Tangy fish curry cooked in coconut milk",
        "price": 240.0, "category": "Curries", "imageUrl": "https://images.unsplash.com/photo-1565557623262-b51c2513a641", "available": True
    },
    {
        "id": "15", "name": "Prawn Curry", "description": "Fresh prawns in spicy tamarind curry",
        "price": 280.0, "category": "Curries", "imageUrl": "https://images.unsplash.com/photo-1565557623262-b51c2513a641", "available": True
    },
    {
        "id": "16", "name": "Dal Tadka", "description": "Yellow lentils tempered with cumin and mustard seeds",
        "price": 120.0, "category": "Curries", "imageUrl": "https://images.unsplash.com/photo-1565557623262-b51c2513a641", "available": True
    },
    
    # Parottas & Breads
    {
        "id": "17", "name": "Kerala Parotta", "description": "Flaky layered bread served with curry",
        "price": 15.0, "category": "Parottas & Breads", "imageUrl": "https://images.unsplash.com/photo-1606491956689-2ea866880c84", "available": True
    },
    {
        "id": "18", "name": "Kothu Parotta", "description": "Shredded parotta stir-fried with egg and vegetables",
        "price": 140.0, "category": "Parottas & Breads", "imageUrl": "https://images.unsplash.com/photo-1606491956689-2ea866880c84", "available": True
    },
    {
        "id": "19", "name": "Naan", "description": "Soft leavened bread baked in tandoor",
        "price": 25.0, "category": "Parottas & Breads", "imageUrl": "https://images.unsplash.com/photo-1606491956689-2ea866880c84", "available": True
    },
    {
        "id": "20", "name": "Garlic Naan", "description": "Naan bread topped with fresh garlic and herbs",
        "price": 35.0, "category": "Parottas & Breads", "imageUrl": "https://images.unsplash.com/photo-1606491956689-2ea866880c84", "available": True
    },
    {
        "id": "21", "name": "Chapati", "description": "Whole wheat flatbread cooked on tawa",
        "price": 12.0, "category": "Parottas & Breads", "imageUrl": "https://images.unsplash.com/photo-1606491956689-2ea866880c84", "available": True
    },
    
    # Beverages
    {
        "id": "22", "name": "Filter Coffee", "description": "Traditional South Indian filter coffee",
        "price": 30.0, "category": "Beverages", "imageUrl": "https://images.unsplash.com/photo-1509042239860-f550ce710b93", "available": True
    },
    {
        "id": "23", "name": "Masala Tea", "description": "Spiced tea with cardamom and ginger",
        "price": 25.0, "category": "Beverages", "imageUrl": "https://images.unsplash.com/photo-1509042239860-f550ce710b93", "available": True
    },
    {
        "id": "24", "name": "Fresh Lime Soda", "description": "Refreshing lime soda with mint",
        "price": 40.0, "category": "Beverages", "imageUrl": "https://images.unsplash.com/photo-1509042239860-f550ce710b93", "available": True
    }
]

CATEGORIES = ["Biryani", "Starters", "Soups", "Curries", "Parottas & Breads", "Beverages"]
ORDER_TYPES = ["dine-in", "takeaway"]
PAYMENT_METHODS = ["cash", "upi-gpay", "upi-phonepe", "credit-card", "debit-card"]

# Helper Functions
def init_session_state():
    """Initialize session state variables"""
    if 'cart' not in st.session_state:
        st.session_state.cart = {}
    if 'orders' not in st.session_state:
        st.session_state.orders = load_orders()
    if 'reviews' not in st.session_state:
        st.session_state.reviews = load_reviews()
    if 'customer' not in st.session_state:
        st.session_state.customer = {"name": "", "phone": "", "email": "", "address": ""}

def load_orders() -> List[Order]:
    """Load orders from JSON file"""
    try:
        if os.path.exists('orders.json'):
            with open('orders.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_orders():
    """Save orders to JSON file"""
    try:
        with open('orders.json', 'w') as f:
            json.dump(st.session_state.orders, f, indent=2)
    except:
        pass

def load_reviews() -> List[Review]:
    """Load reviews from JSON file"""
    try:
        if os.path.exists('reviews.json'):
            with open('reviews.json', 'r') as f:
                return json.load(f)
    except:
        pass
    return []

def save_reviews():
    """Save reviews to JSON file"""
    try:
        with open('reviews.json', 'w') as f:
            json.dump(st.session_state.reviews, f, indent=2)
    except:
        pass

def add_to_cart(item: MenuItem):
    """Add item to cart"""
    item_id = item['id']
    if item_id in st.session_state.cart:
        st.session_state.cart[item_id]['quantity'] += 1
    else:
        st.session_state.cart[item_id] = {'menuItem': item, 'quantity': 1}

def update_cart_quantity(item_id: str, quantity: int):
    """Update item quantity in cart"""
    if quantity <= 0:
        if item_id in st.session_state.cart:
            del st.session_state.cart[item_id]
    else:
        st.session_state.cart[item_id]['quantity'] = quantity

def remove_from_cart(item_id: str):
    """Remove item from cart"""
    if item_id in st.session_state.cart:
        del st.session_state.cart[item_id]

def clear_cart():
    """Clear entire cart"""
    st.session_state.cart = {}

def get_cart_total():
    """Calculate cart totals"""
    subtotal = sum(item['menuItem']['price'] * item['quantity'] for item in st.session_state.cart.values())
    gst_amount = subtotal * GST_RATE
    total = subtotal + gst_amount
    return subtotal, gst_amount, total

def get_cart_count():
    """Get total items in cart"""
    return sum(item['quantity'] for item in st.session_state.cart.values())

def normalize_phone(phone: str) -> str:
    """Normalize phone number for WhatsApp"""
    # Remove all non-digits
    phone_digits = re.sub(r'[^0-9]', '', phone)
    
    # Add country code if missing (Indian numbers)
    if len(phone_digits) == 10 and not phone_digits.startswith('91'):
        phone_digits = '91' + phone_digits
    
    # Validate phone number format
    if len(phone_digits) < 10 or len(phone_digits) > 15:
        raise ValueError('Invalid phone number format')
    
    return phone_digits

def create_whatsapp_message(order: Order) -> str:
    """Create WhatsApp message with order details"""
    message = f"*Retro Restaurant*\n"
    message += f"*Order Confirmation*\n\n"
    message += f"*Customer:* {order['customer']['name']}\n"
    message += f"*Phone:* {order['customer']['phone']}\n"
    message += f"*Order ID:* {order['id']}\n"
    message += f"*Type:* {order['orderType'].replace('-', ' ').upper()}\n"
    message += f"*Payment:* {order['paymentMethod'].replace('-', ' ').upper()}\n\n"
    
    message += f"*Order Items:*\n"
    for i, item in enumerate(order['orderItems'], 1):
        # Find menu item name
        menu_item = next((m for m in MENU_ITEMS if m['id'] == item['menuItemId']), None)
        item_name = menu_item['name'] if menu_item else 'Item'
        message += f"{i}. {item['quantity']}x {item_name} - ₹{item['totalPrice']:.2f}\n"
    
    gst_rate = (order['gstAmount'] / order['subtotal'] * 100) if order['subtotal'] > 0 else 18
    message += f"\n*Bill Summary:*\n"
    message += f"Subtotal: ₹{order['subtotal']:.2f}\n"
    message += f"GST ({gst_rate:.1f}%): ₹{order['gstAmount']:.2f}\n"
    message += f"*Total: ₹{order['total']:.2f}*\n\n"
    
    message += f"*Restaurant Address:*\n"
    message += f"123 Kanyakumari Main Road, Radhapuram, Tamil Nadu 627111\n\n"
    message += f"Thank you for ordering with us!"
    
    return message

def get_whatsapp_url(phone: str, message: str) -> str:
    """Generate WhatsApp sharing URL"""
    normalized_phone = normalize_phone(phone)
    encoded_message = message.replace('\n', '%0A').replace(' ', '%20').replace('*', '%2A')
    return f"https://wa.me/{normalized_phone}?text={encoded_message}"

# Page Functions
def render_hero_section():
    """Render hero section with video background"""
    st.markdown("""
    <style>
    .hero-container {
        position: relative;
        width: 100%;
        height: 400px;
        overflow: hidden;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }
    .hero-video {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }
    .hero-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.6), transparent);
        display: flex;
        align-items: end;
        padding: 2rem;
    }
    .hero-content {
        color: white;
        text-align: left;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    </style>
    
    <div class="hero-container">
        <video class="hero-video" autoplay muted loop playsinline>
            <source src="data:video/mp4;base64," type="video/mp4">
            <!-- Fallback image if video fails -->
        </video>
        <div class="hero-overlay">
            <div class="hero-content">
                <div class="hero-title">Experience the Art of Traditional Cooking</div>
                <div class="hero-subtitle">Master chefs preparing our signature Retro Restaurant biryani</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_home_page():
    """Render the home page"""
    st.title("🍽️ RR")
    st.subheader("Legendary Biryani, Since 1957")
    
    # Hero Section
    render_hero_section()
    
    # Features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### ⏰ Fresh Daily")
        st.write("Made fresh every day with the finest ingredients")
    
    with col2:
        st.markdown("### 👨‍👩‍👧‍👦 Family Recipe")
        st.write("Traditional methods passed down through generations")
    
    with col3:
        st.markdown("### 🏆 Award Winning")
        st.write("Legendary taste recognized across Tamil Nadu")
    
    # Call to Action
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🛒 Order Now", type="primary", use_container_width=True):
            st.session_state.current_page = "Menu"
            st.rerun()
    
    # Statistics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Happy Customers Daily", "1000+")
    with col2:
        st.metric("Authentic Dishes", "24")
    with col3:
        st.metric("Locations", "3")
    with col4:
        st.metric("Customer Rating", "4.8⭐")

def render_menu_page():
    """Render the menu page"""
    st.title("🍽️ Our Menu")
    
    # Category filter
    selected_category = st.radio(
        "Select Category:",
        ["All"] + CATEGORIES,
        horizontal=True
    )
    
    # Filter menu items
    if selected_category == "All":
        filtered_items = MENU_ITEMS
    else:
        filtered_items = [item for item in MENU_ITEMS if item['category'] == selected_category]
    
    # Display menu items
    if filtered_items:
        # Create grid layout
        cols_per_row = 2
        for i in range(0, len(filtered_items), cols_per_row):
            cols = st.columns(cols_per_row)
            for j, col in enumerate(cols):
                if i + j < len(filtered_items):
                    item = filtered_items[i + j]
                    with col:
                        render_menu_item_card(item)
    else:
        st.info("No items found in this category.")

def render_menu_item_card(item: MenuItem):
    """Render a menu item card"""
    with st.container():
        st.image(item['imageUrl'], use_container_width=True)
        st.subheader(item['name'])
        st.write(item['description'])
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.write(f"**₹{item['price']:.0f}**")
        
        with col2:
            # Check if item is in cart
            item_id = item['id']
            current_qty = st.session_state.cart.get(item_id, {}).get('quantity', 0)
            
            if current_qty == 0:
                if st.button(f"Add to Cart", key=f"add_{item_id}", use_container_width=True):
                    add_to_cart(item)
                    st.success(f"Added {item['name']} to cart!")
                    st.rerun()
            else:
                # Quantity controls
                col_minus, col_qty, col_plus = st.columns([1, 2, 1])
                
                with col_minus:
                    if st.button("−", key=f"minus_{item_id}"):
                        update_cart_quantity(item_id, current_qty - 1)
                        st.rerun()
                
                with col_qty:
                    st.write(f"**{current_qty}**", key=f"qty_{item_id}")
                
                with col_plus:
                    if st.button("+", key=f"plus_{item_id}"):
                        update_cart_quantity(item_id, current_qty + 1)
                        st.rerun()
        
        st.markdown("---")

def render_cart_page():
    """Render cart and checkout page"""
    st.title("🛒 Cart & Checkout")
    
    if not st.session_state.cart:
        st.info("Your cart is empty. Add some delicious items to get started!")
        return
    
    # Display cart items
    st.subheader("Your Order")
    
    for item_id, cart_item in st.session_state.cart.items():
        menu_item = cart_item['menuItem']
        quantity = cart_item['quantity']
        
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            st.write(f"**{menu_item['name']}**")
            st.write(f"₹{menu_item['price']:.0f} each")
        
        with col2:
            new_qty = st.number_input(
                "Qty", 
                min_value=0, 
                value=quantity, 
                key=f"cart_qty_{item_id}",
                on_change=lambda: update_cart_quantity(item_id, st.session_state[f"cart_qty_{item_id}"])
            )
        
        with col3:
            st.write(f"₹{menu_item['price'] * quantity:.2f}")
        
        with col4:
            if st.button("🗑️", key=f"remove_{item_id}"):
                remove_from_cart(item_id)
                st.rerun()
    
    # Cart totals
    subtotal, gst_amount, total = get_cart_total()
    
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col2:
        st.write(f"**Subtotal:** ₹{subtotal:.2f}")
        st.write(f"**GST ({GST_RATE*100:.0f}%):** ₹{gst_amount:.2f}")
        st.write(f"**Total:** ₹{total:.2f}")
    
    # Checkout form
    st.markdown("---")
    st.subheader("Checkout Details")
    
    with st.form("checkout_form"):
        # Order type
        order_type = st.selectbox("Order Type", ORDER_TYPES, format_func=lambda x: x.replace('-', ' ').title())
        
        # Customer details
        st.write("**Customer Information**")
        col1, col2 = st.columns(2)
        
        with col1:
            customer_name = st.text_input("Name *", value=st.session_state.customer.get('name', ''))
            customer_phone = st.text_input("Phone *", value=st.session_state.customer.get('phone', ''))
        
        with col2:
            customer_email = st.text_input("Email", value=st.session_state.customer.get('email', ''))
            customer_address = st.text_area("Address", value=st.session_state.customer.get('address', ''))
        
        # Payment method
        payment_method = st.selectbox(
            "Payment Method", 
            PAYMENT_METHODS, 
            format_func=lambda x: x.replace('-', ' ').title()
        )
        
        # Submit button
        submitted = st.form_submit_button("Place Order", type="primary", use_container_width=True)
        
        if submitted:
            # Validate required fields
            if not customer_name or not customer_phone:
                st.error("Please fill in your name and phone number.")
            else:
                try:
                    # Validate phone number
                    normalized_phone = normalize_phone(customer_phone)
                    
                    # Create order
                    order_id = str(uuid.uuid4())
                    
                    # Update customer in session state
                    st.session_state.customer = {
                        'name': customer_name,
                        'phone': customer_phone,
                        'email': customer_email,
                        'address': customer_address
                    }
                    
                    order_items = []
                    for item_id, cart_item in st.session_state.cart.items():
                        menu_item = cart_item['menuItem']
                        quantity = cart_item['quantity']
                        order_items.append({
                            'menuItemId': item_id,
                            'quantity': quantity,
                            'unitPrice': menu_item['price'],
                            'totalPrice': menu_item['price'] * quantity
                        })
                    
                    order = {
                        'id': order_id,
                        'customer': st.session_state.customer,
                        'orderType': order_type,
                        'paymentMethod': payment_method,
                        'subtotal': subtotal,
                        'gstAmount': gst_amount,
                        'total': total,
                        'orderItems': order_items,
                        'createdAt': datetime.now().isoformat()
                    }
                    
                    # Save order
                    st.session_state.orders.append(order)
                    save_orders()
                    
                    # Create WhatsApp message
                    message = create_whatsapp_message(order)
                    whatsapp_url = get_whatsapp_url(customer_phone, message)
                    
                    # Clear cart
                    clear_cart()
                    
                    # Success message
                    st.success(f"✅ Order placed successfully! Order ID: {order_id}")
                    
                    # WhatsApp sharing
                    st.markdown("### 📱 Share Bill via WhatsApp")
                    st.link_button(
                        "Send Bill to WhatsApp",
                        whatsapp_url,
                        use_container_width=True
                    )
                    
                except ValueError as e:
                    st.error(f"Error: {e}")
                except Exception as e:
                    st.error("Failed to place order. Please try again.")

def render_reviews_page():
    """Render reviews page"""
    st.title("⭐ Customer Reviews")
    
    # Display average rating
    if st.session_state.reviews:
        avg_rating = sum(review['rating'] for review in st.session_state.reviews) / len(st.session_state.reviews)
        total_reviews = len(st.session_state.reviews)
        
        col1, col2 = st.columns([1, 3])
        with col1:
            st.metric("Average Rating", f"{avg_rating:.1f}⭐")
        with col2:
            st.metric("Total Reviews", total_reviews)
    
    # Add review form
    st.subheader("Write a Review")
    
    with st.form("review_form"):
        reviewer_name = st.text_input("Your Name *")
        rating = st.radio("Rating", [1, 2, 3, 4, 5], format_func=lambda x: "⭐" * x, horizontal=True)
        comment = st.text_area("Your Review *", placeholder="Share your experience with our food and service...")
        
        if st.form_submit_button("Submit Review", type="primary"):
            if not reviewer_name or not comment:
                st.error("Please fill in your name and review comment.")
            elif len(comment) < 10:
                st.error("Review comment must be at least 10 characters long.")
            else:
                # Create review
                review = {
                    'id': str(uuid.uuid4()),
                    'customerName': reviewer_name,
                    'rating': rating,
                    'comment': comment,
                    'createdAt': datetime.now().isoformat()
                }
                
                # Add to reviews
                st.session_state.reviews.insert(0, review)  # Add to beginning
                save_reviews()
                
                st.success("✅ Thank you for your review!")
                st.rerun()
    
    # Display reviews
    st.markdown("---")
    
    if st.session_state.reviews:
        st.subheader("Customer Reviews")
        
        for review in st.session_state.reviews:
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"**{review['customerName']}**")
                    st.write("⭐" * review['rating'])
                
                with col2:
                    review_date = datetime.fromisoformat(review['createdAt']).strftime("%b %d, %Y")
                    st.write(review_date)
                
                st.write(review['comment'])
                st.markdown("---")
    else:
        st.info("No reviews yet. Be the first to share your experience!")

def render_contact_page():
    """Render contact page"""
    st.title("📞 Contact Us")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Get in Touch")
        
        # Phone
        st.markdown("### 📱 Phone")
        st.markdown(f"[{RESTAURANT_PHONE}](tel:{RESTAURANT_PHONE})")
        
        # Email
        st.markdown("### 📧 Email")
        st.markdown("[contact@Retro Restaurant.com](mailto:contact@Retro Restaurant.com)")
        
        # Address
        st.markdown("### 📍 Address")
        st.write("123 Kanyankumari Main Road")
        st.write("Radhapuram, Tamil Nadu 624001")
        st.write("India")
        
    with col2:
        st.subheader("Business Hours")
        st.write("**Monday - Sunday**")
        st.write("🕐 11:00 AM - 11:00 PM")
        
        st.markdown("---")
        
        st.subheader("Follow Us")
        st.write("Stay updated with our latest offerings!")
        
        # Social media links (placeholder)
        col_fb, col_ig, col_tw = st.columns(3)
        with col_fb:
            st.markdown("📘 Facebook")
        with col_ig:
            st.markdown("📷 Instagram") 
        with col_tw:
            st.markdown("🐦 Twitter")

# Main App
def main():
    # Page configuration
    st.set_page_config(
        page_title="Retro Restaurant",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    init_session_state()
    
    # Custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    .stButton > button {
        width: 100%;
    }
    .stMetric {
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    with st.sidebar:
        st.title("🍽️ Retro Restaurant")
        
        # Cart badge
        cart_count = get_cart_count()
        if cart_count > 0:
            st.markdown(f"### 🛒 Cart ({cart_count})")
        else:
            st.markdown("### 🛒 Cart")
        
        # Navigation
        current_page = st.radio(
            "Navigate to:",
            ["Home", "Menu", "Cart & Checkout", "Reviews", "Contact"],
            key="navigation"
        )
        
        # Quick actions
        st.markdown("---")
        
        if st.button("🔄 Clear Cart", disabled=cart_count == 0):
            clear_cart()
            st.success("Cart cleared!")
            st.rerun()
        
        # Cart summary
        if cart_count > 0:
            subtotal, gst_amount, total = get_cart_total()
            st.markdown("### Cart Summary")
            st.write(f"Items: {cart_count}")
            st.write(f"Total: ₹{total:.2f}")
    
    # Main content
    if current_page == "Home":
        render_home_page()
    elif current_page == "Menu":
        render_menu_page()
    elif current_page == "Cart & Checkout":
        render_cart_page()
    elif current_page == "Reviews":
        render_reviews_page()
    elif current_page == "Contact":
        render_contact_page()
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 1rem;'>
            <p>© 2024 Retro Restaurant | Legendary Biryani Since 1957</p>
        </div>
        """, 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()