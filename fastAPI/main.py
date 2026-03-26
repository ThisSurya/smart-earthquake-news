from fastapi import FastAPI, Query, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.fetch_news import fetch_cnn, fetch_kumparan, fetch_bmkg, search_items
from util.helper import prepare_summary_text, filter_results
from util.db import storeEvent, storeSemantic, search_events, cluster
from services.get_recomendation import get_summary_api
from util.database import get_db, init_db
from repository.news_repository import create_news, delete_old_news, get_all_news, get_news_by_id, delete_news, get_news_by_location
from fastapi.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:5173",
    "http://localhost:8080",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()

@app.get("/news")
def get_news(search: str = Query(default=None)):
    try:
        # Fetch data from all sources
        events = fetch_bmkg("gempadirasakan")
        cnn = search_items(fetch_cnn(), "gempa")
        kumparan = search_items(fetch_kumparan(), "gempa")
        print(f"show cnn data: {cnn}")  # Debug print
        print(f"show kumparan data: {kumparan}")  # Debug print

        # Store events (gempa) to event collection
        for event in events:
            try:
                storeEvent(event)
                storeSemantic(event)
            except Exception as e:
                print(f"Error storing event {event.get('id')}: {str(e)}")

        # Store news articles to semantic collection
        for article in cnn:
            try:
                storeEvent(article)
                storeSemantic(article)
            except Exception as e:
                print(f"Error storing CNN article {article.get('id')}: {str(e)}")

        for article in kumparan:
            try:
                storeEvent(article)
                storeSemantic(article)
            except Exception as e:
                print(f"Error storing Kumparan article {article.get('id')}: {str(e)}")

        result = search_events("Gempa")
        clustered = cluster(result)
        print(f"Total clusters by location: {len(clustered)}")

        # For each location cluster, prepare combined text and get recommendation
        cluster_results = []
        for cluster_items in clustered:
            text_ready = [prepare_summary_text(item) for item in cluster_items]
            combined_text = "\n".join(text_ready)

            # Get lat/lon from the first BMKG item in this cluster
            lat = "none"
            lon = "none"
            location_label = ""
            for item in cluster_items:
                meta = item.get("metadata", {})
                if meta.get("latitude", "none") not in ("none", None, "") and \
                   meta.get("longitude", "none") not in ("none", None, ""):
                    lat = meta["latitude"]
                    lon = meta["longitude"]
                    location_label = meta.get("location", "")
                    break
            
            recomendation = get_summary_api(combined_text) if combined_text else "Tidak ada data gempa."

            cluster_results.append({
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "label": location_label
                },
                "item_count": len(cluster_items),
                "items": cluster_items,
                "recomendation": recomendation
            })

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Data fetched and stored successfully",
                "total_clusters": len(cluster_results),
                "clusters": cluster_results
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to fetch and process news",
                "error": str(e)
            }
        )


@app.get("/news/recommendation")
def get_news_recommendation(
    latitude: str = Query(default=None),
    longitude: str = Query(default=None),
    lokasi: str = Query(default=None),
    radius_km: float = Query(default=50.0, description="Search radius in kilometers"),
    db: Session = Depends(get_db)
):
    """
    GET route for user: retrieve saved recommendations from DB,
    filtered by location (latitude/longitude or lokasi) within a specified radius.

    Args:
        latitude: User's latitude
        longitude: User's longitude
        lokasi: Location text filter (optional)
        radius_km: Search radius in kilometers (default: 50 km)
    """
    try:
        if latitude and longitude:
            news_list = get_news_by_location(db, latitude=latitude, longitude=longitude, radius_km=radius_km)
        else:
            news_list = get_all_news(db)

        # Filter by lokasi text if provided
        if lokasi:
            news_list = [n for n in news_list if lokasi.lower() in (n.content or "").lower()]

        data = [
            {
                "id": n.id,
                "latitude": n.latitude,
                "longitude": n.longitude,
                "content": n.content,
                "datetime": n.datetime.isoformat() if n.datetime else None,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
            }
            for n in news_list
        ]

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Recommendations retrieved successfully",
                "data": data
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to retrieve recommendations",
                "error": str(e)
            }
        )


@app.post("/news/cron")
def cron_fetch_and_store(db: Session = Depends(get_db)):
    """
    Cron job route: fetch news from all sources, process recommendations per location cluster,
    and save each cluster's result to PostgreSQL.
    """
    try:
        # Fetch data from all sources
        events = fetch_bmkg("gempadirasakan")
        cnn = search_items(fetch_cnn(), "gempa")
        kumparan = search_items(fetch_kumparan(), "gempa")

        # Store all data to ChromaDB
        for item in events + cnn + kumparan:
            try:
                storeEvent(item)
                storeSemantic(item)
            except Exception as e:
                print(f"Error storing item {item.get('id')}: {str(e)}")

        result = search_events("Gempa")
        clustered = cluster(result)
        print(f"Total location clusters: {len(clustered)}")
        print(f"Clustered items example: {clustered[0][:1]}")  # Debug print first 2 items of first cluster

        # Process and save each location cluster separately
        saved_results = []
        for cluster_items in clustered:
            text_ready = [prepare_summary_text(item) for item in cluster_items]
            combined_text = "\n".join(text_ready)
            print(f"Cluster text ({len(cluster_items)} items): {combined_text[:100]}...")  # Debug

            # Get lat/lon from the first BMKG item in this cluster
            latitude = "none"
            longitude = "none"
            location_label = ""
            datetime = None
            for item in cluster_items:
                meta = item.get("metadata", {})
                datetime = meta.get("datetime", None)
                if meta.get("latitude", "none") not in ("none", None, "") and \
                   meta.get("longitude", "none") not in ("none", None, ""):
                    latitude = meta["latitude"]
                    longitude = meta["longitude"]
                    location_label = meta.get("location", "")
                    break
            
            try:
                
                recomendation = get_summary_api(combined_text) if combined_text else "Tidak ada data gempa."

                # Save this cluster's recommendation to PostgreSQL
                saved_news = create_news(
                    db=db,
                    latitude=latitude,
                    longitude=longitude,
                    content=recomendation,
                    datetime=datetime
                )

                saved_results.append({
                    "saved_id": saved_news.id,
                    "location": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "label": location_label
                    },
                    "item_count": len(cluster_items),
                    "recomendation": recomendation
                })
            except Exception as e:
                print(f"Error processing cluster with location {location_label}: {str(e)}")
                continue

        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": f"Cron job completed. {len(saved_results)} location cluster(s) processed and saved.",
                "total_clusters": len(saved_results),
                "results": saved_results
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Cron job failed",
                "error": str(e)
            }
        )


@app.get("/news/saved")
def get_saved_news(db: Session = Depends(get_db)):
    """Get all saved news recommendations from PostgreSQL."""
    try:
        news_list = get_all_news(db)
        data = [
            {
                "id": n.id,
                "latitude": n.latitude,
                "longitude": n.longitude,
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None,
                "updated_at": n.updated_at.isoformat() if n.updated_at else None,
            }
            for n in news_list
        ]
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Saved news retrieved successfully",
                "data": data
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to retrieve saved news",
                "error": str(e)
            }
        )


@app.get("/news/saved/{news_id}")
def get_saved_news_by_id(news_id: int, db: Session = Depends(get_db)):
    """Get a specific saved news recommendation by ID."""
    try:
        news = get_news_by_id(db, news_id)
        if not news:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"News with id {news_id} not found"
                }
            )
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "News retrieved successfully",
                "data": {
                    "id": news.id,
                    "latitude": news.latitude,
                    "created_at": news.created_at.isoformat() if news.created_at else None,
                    "updated_at": news.updated_at.isoformat() if news.updated_at else None,
                    "longitude": news.longitude,
                    "content": news.content
                }
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to retrieve news",
                "error": str(e)
            }
        )


@app.delete("/news/saved/{news_id}")
def delete_saved_news(news_id: int, db: Session = Depends(get_db)):
    """Delete a saved news recommendation by ID."""
    try:
        success = delete_news(db, news_id)
        if not success:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "message": f"News with id {news_id} not found"
                }
            )
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "News deleted successfully"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Failed to delete news",
                "error": str(e)
            }
        )
    
@app.delete("/news/cron/delete-old")
def cron_delete_old_news(db: Session = Depends(get_db), days_old: int = 3):
    try:
        deleted_count = delete_old_news(db, days_old=days_old)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": f"Cron job completed. {deleted_count} old news item(s) deleted."
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Cron job failed to delete old news",
                "error": str(e)
            }
        )