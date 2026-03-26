from sqlalchemy.orm import Session
from model.news import News
from util.helper import calculate_distance
import datetime

def create_news(db: Session, latitude: str, longitude: str, content: str, datetime: datetime.datetime = None) -> News:
    news = News(latitude=latitude, longitude=longitude, content=content, datetime=datetime)
    db.add(news)
    db.commit()
    db.refresh(news)
    return news


def get_all_news(db: Session) -> list[News]:
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=10)
    return db.query(News).filter(News.datetime > cutoff_time).all()


def get_news_by_id(db: Session, news_id: int) -> News | None:
    return db.query(News).filter(News.id == news_id).first()


def get_news_by_location(db: Session, latitude: str = None, longitude: str = None, radius_km: float = 50.0) -> list[News]:
    """
    Get news by location with radius search.
    Finds all news within a certain radius from the given coordinates.
    For duplicate coordinates, only returns the most recent one based on updated_at.
    
    Args:
        db: Database session
        latitude: User's latitude
        longitude: User's longitude
        radius_km: Search radius in kilometers (default: 50 km)
    
    Returns:
        List of news within the radius, sorted by distance
    """
    if not latitude or not longitude:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=10)
        return db.query(News).filter(News.datetime > cutoff_time).all()
    
    try:
        user_lat = float(latitude)
        user_lon = float(longitude)
    except (ValueError, TypeError):
        return []
    
    # Filter for news within last 24 hours
    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=10)
    
    # Get all news with coordinates, ordered by updated_at descending (newest first)
    all_news = db.query(News).filter(
        News.latitude.isnot(None), 
        News.longitude.isnot(None),
        News.datetime > cutoff_time
    ).order_by(News.updated_at.desc()).all()
    
    # Dictionary to store unique locations with their most recent news
    unique_locations = {}
    
    # Filter by distance and keep only the most recent for each location
    for news in all_news:
        try:
            news_lat = float(news.latitude)
            news_lon = float(news.longitude)
            
            # Calculate distance
            distance = calculate_distance(user_lat, user_lon, news_lat, news_lon)
            
            # Include if within radius
            if distance <= radius_km:
                # Create a key from coordinates to identify unique locations
                location_key = f"{news.latitude},{news.longitude}"
                
                # Only keep the first occurrence (most recent due to ordering)
                if location_key not in unique_locations:
                    # Add distance as a transient attribute for sorting
                    news.distance = distance
                    unique_locations[location_key] = news
        except (ValueError, TypeError):
            # Skip news with invalid coordinates
            continue
    
    # Convert dictionary values to list and sort by distance (closest first)
    nearby_news = list(unique_locations.values())
    nearby_news.sort(key=lambda x: x.distance)
    
    return nearby_news


def delete_news(db: Session, news_id: int) -> bool:
    news = db.query(News).filter(News.id == news_id).first()
    if news:
        db.delete(news)
        db.commit()
        return True
    return False

def delete_old_news(db: Session, days_old: int = 3) -> int:
    """
    Delete news that are older than a certain number of days.
    
    Args:
        db: Database session
        days_old: Number of days to determine old news (default: 30 days)
    
    Returns:
        Number of news deleted
    """
    cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_old)
    old_news = db.query(News).filter(News.updated_at < cutoff_date).all()
    
    deleted_count = 0
    for news in old_news:
        db.delete(news)
        deleted_count += 1
    
    db.commit()
    return deleted_count