from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AssetListing:
    """Represents an asset for sale in the marketplace"""
    listing_id: str
    asset_id: str
    creator_id: str
    title: str
    description: str
    price: float
    license: str  # MIT, CC BY-NC, etc.
    downloads: int = 0
    rating: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Review:
    """User review for an asset"""
    review_id: str
    listing_id: str
    user_id: str
    rating: int  # 1-5
    comment: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class Marketplace:
    """Asset marketplace for creators"""

    def __init__(self):
        self.listings: Dict[str, AssetListing] = {}
        self.reviews: List[Review] = []
        self.transactions: List[Dict[str, Any]] = []

    def list_asset(self, asset_id: str, creator_id: str, title: str, description: str, price: float, license: str) -> AssetListing:
        """List an asset for sale"""
        listing = AssetListing(
            listing_id=f"listing-{len(self.listings)}",
            asset_id=asset_id,
            creator_id=creator_id,
            title=title,
            description=description,
            price=price,
            license=license,
        )

        self.listings[listing.listing_id] = listing
        return listing

    def get_listing(self, listing_id: str) -> Optional[AssetListing]:
        """Get a listing by ID"""
        return self.listings.get(listing_id)

    def get_all_listings(self) -> List[AssetListing]:
        """Get all listings"""
        return list(self.listings.values())

    def search_listings(self, query: str) -> List[AssetListing]:
        """Search listings by title or description"""
        query = query.lower()
        return [
            listing for listing in self.listings.values()
            if query in listing.title.lower() or query in listing.description.lower()
        ]

    def purchase_asset(self, listing_id: str, buyer_id: str) -> Dict[str, Any]:
        """Purchase an asset"""
        listing = self.get_listing(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")

        transaction = {
            "transaction_id": f"tx-{len(self.transactions)}",
            "listing_id": listing_id,
            "buyer_id": buyer_id,
            "creator_id": listing.creator_id,
            "amount": listing.price,
            "timestamp": datetime.now().isoformat(),
        }

        # Update listing
        listing.downloads += 1

        # Store transaction
        self.transactions.append(transaction)

        return transaction

    def add_review(self, listing_id: str, user_id: str, rating: int, comment: str) -> Review:
        """Add a review for an asset"""
        review = Review(
            review_id=f"review-{len(self.reviews)}",
            listing_id=listing_id,
            user_id=user_id,
            rating=rating,
            comment=comment,
        )

        self.reviews.append(review)

        # Update listing rating
        listing = self.get_listing(listing_id)
        if listing:
            reviews_for_listing = [r for r in self.reviews if r.listing_id == listing_id]
            avg_rating = sum(r.rating for r in reviews_for_listing) / len(reviews_for_listing)
            listing.rating = avg_rating

        return review

    def get_top_creators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top creators by revenue"""
        creator_revenue = {}
        for tx in self.transactions:
            creator_id = tx["creator_id"]
            creator_revenue[creator_id] = creator_revenue.get(creator_id, 0) + tx["amount"]

        sorted_creators = sorted(creator_revenue.items(), key=lambda x: x[1], reverse=True)
        return [{"creator_id": cid, "revenue": revenue} for cid, revenue in sorted_creators[:limit]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        return {
            "total_listings": len(self.listings),
            "total_transactions": len(self.transactions),
            "total_reviews": len(self.reviews),
            "total_revenue": sum(tx["amount"] for tx in self.transactions),
            "avg_rating": (
                sum(r.rating for r in self.reviews) / len(self.reviews)
                if self.reviews else 0.0
            ),
        }
