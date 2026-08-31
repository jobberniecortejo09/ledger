"""Data models for Notion database records."""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from src.metatrader.models import Trade


class NotionTradeRecord(BaseModel):
    """Maps a Trade to Notion database properties."""

    notion_id: Optional[str] = Field(None, description="Notion page ID")
    symbol: str = Field(..., description="Trading instrument")
    order_type: str = Field(..., description="BUY or SELL")
    volume: float = Field(..., description="Position size in lots")
    open_price: float = Field(..., description="Entry price")
    open_time: datetime = Field(..., description="Entry time")
    close_price: Optional[float] = Field(None, description="Exit price")
    close_time: Optional[datetime] = Field(None, description="Exit time")
    profit: float = Field(..., description="P&L in account currency")
    commission: float = Field(default=0.0)
    swap: float = Field(default=0.0)
    net_profit: float = Field(..., description="Profit minus commission and swap")
    reasoning: Optional[str] = Field(None, description="Trade setup and reasoning")
    setup_notes: Optional[str] = Field(None, description="Additional setup notes")
    entry_condition: Optional[str] = Field(None, description="Entry signal")
    exit_condition: Optional[str] = Field(None, description="Exit reason")
    risk_reward_ratio: Optional[float] = Field(None)
    ict_concepts: Optional[str] = Field(None, description="ICT concepts applied")
    status: str = Field(default="Closed", description="Trade status")
    date_recorded: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_trade(cls, trade: Trade) -> "NotionTradeRecord":
        """Create a NotionTradeRecord from a Trade object.
        
        Args:
            trade: Trade object to convert
            
        Returns:
            NotionTradeRecord instance
        """
        position = trade.position
        net_profit = position.profit - position.commission + position.swap
        
        return cls(
            symbol=position.symbol,
            order_type=position.order_type,
            volume=position.volume,
            open_price=position.open_price,
            open_time=position.open_time,
            close_price=position.close_price,
            close_time=position.close_time,
            profit=position.profit,
            commission=position.commission,
            swap=position.swap,
            net_profit=net_profit,
            reasoning=trade.reasoning,
            setup_notes=trade.setup_notes,
            entry_condition=trade.entry_condition,
            exit_condition=trade.exit_condition,
            risk_reward_ratio=trade.risk_reward_ratio,
            ict_concepts=trade.ict_concepts,
            date_recorded=trade.datetime_recorded,
        )

    def to_notion_properties(self) -> Dict[str, Any]:
        """Convert to Notion database property structure.
        
        Returns:
            Dictionary compatible with Notion API
        """
        # TODO: Structure properties according to your Notion database schema
        return {
            "Symbol": {"rich_text": [{"text": {"content": self.symbol}}]},
            "Type": {"select": {"name": self.order_type}},
            "Volume": {"number": self.volume},
            "OpenPrice": {"number": self.open_price},
            "OpenTime": {"date": {"start": self.open_time.isoformat()}},
            "ClosePrice": {"number": self.close_price} if self.close_price else None,
            "CloseTime": {"date": {"start": self.close_time.isoformat()}} if self.close_time else None,
            "Profit": {"number": self.profit},
            "Commission": {"number": self.commission},
            "Swap": {"number": self.swap},
            "NetProfit": {"number": self.net_profit},
            "Reasoning": {"rich_text": [{"text": {"content": self.reasoning or ""}}]},
            "EntryCondition": {"rich_text": [{"text": {"content": self.entry_condition or ""}}]},
            "ExitCondition": {"rich_text": [{"text": {"content": self.exit_condition or ""}}]},
            "RiskReward": {"number": self.risk_reward_ratio} if self.risk_reward_ratio else None,
            "ICTConcepts": {"rich_text": [{"text": {"content": self.ict_concepts or ""}}]},
            "Status": {"select": {"name": self.status}},
            "DateRecorded": {"date": {"start": self.date_recorded.isoformat()}},
        }
