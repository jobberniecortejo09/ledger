"""Notion integration module.

Handles syncing trade data with a Notion database.
"""

from .client import NotionClient
from .models import NotionTradeRecord

__all__ = ["NotionClient", "NotionTradeRecord"]
