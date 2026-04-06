from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .database import Base


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (UniqueConstraint("platform", "username", name="uq_platform_username"),)

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(20), nullable=False)       # 'threads' or 'instagram'
    username = Column(String(100), nullable=False)
    full_name = Column(String(200), nullable=True)
    bio = Column(Text, nullable=True)
    followers_count = Column(BigInteger, default=0)
    following_count = Column(BigInteger, default=0)
    posts_count = Column(Integer, default=0)
    is_verified = Column(Boolean, default=False)
    profile_pic_local = Column(String(500), nullable=True)  # /static/avatars/xxx.jpg
    website = Column(String(500), nullable=True)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    posts = relationship("Post", back_populates="profile", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.id", ondelete="CASCADE"), nullable=False)
    external_id = Column(String(100), nullable=True)
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=True)
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    repost_count = Column(Integer, default=0)
    post_url = Column(String(500), nullable=True)
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    profile = relationship("Profile", back_populates="posts")
