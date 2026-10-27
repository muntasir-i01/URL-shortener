from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True)
    code = Column(String(16), unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)


class Click(Base):
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True)
    link_id = Column(
        Integer, ForeignKey("links.id", ondelete="CASCADE"), nullable=False
    )
    clicked_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_clicks_link_id_clicked_at", "link_id", "clicked_at"),)
