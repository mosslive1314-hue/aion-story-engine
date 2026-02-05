"""
Advanced Economy - 高级经济系统
实现代币、质押、NFT和高级经济功能
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid


class TokenType(Enum):
    """代币类型"""
    GOVERNANCE = "governance"  # 治理代币
    UTILITY = "utility"  # 实用代币
    CREATOR = "creator"  # 创作者代币
    WORLD = "world"  # 世界代币
    STABLECOIN = "stablecoin"  # 稳定币


class TransactionStatus(Enum):
    """交易状态"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TokenBalance:
    """代币余额"""
    user_id: str
    token_type: TokenType
    balance: float = 0.0
    locked: float = 0.0  # 锁定余额（质押中）
    staked: float = 0.0  # 质押余额
    last_updated: datetime = field(default_factory=datetime.now)

    def available_balance(self) -> float:
        """可用余额"""
        return self.balance - self.locked - self.staked

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "token_type": self.token_type.value,
            "balance": self.balance,
            "locked": self.locked,
            "staked": self.staked,
            "available": self.available_balance(),
            "last_updated": self.last_updated.isoformat()
        }


@dataclass
class StakePosition:
    """质押位置"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    token_type: TokenType = TokenType.GOVERNANCE
    amount: float = 0.0
    apy: float = 0.0  # 年化收益率
    started_at: datetime = field(default_factory=datetime.now)
    lock_period_days: int = 0  # 锁定期（天）
    rewards_earned: float = 0.0
    auto_compound: bool = False

    def is_locked(self) -> bool:
        """检查是否锁定"""
        if self.lock_period_days == 0:
            return False

        unlock_date = self.started_at + timedelta(days=self.lock_period_days)
        return datetime.now() < unlock_date

    def days_until_unlock(self) -> int:
        """距离解锁的天数"""
        if self.lock_period_days == 0:
            return 0

        unlock_date = self.started_at + timedelta(days=self.lock_period_days)
        delta = unlock_date - datetime.now()
        return max(0, delta.days)

    def calculate_rewards(self) -> float:
        """计算奖励"""
        days_staked = (datetime.now() - self.started_at).days
        daily_rate = self.apy / 365
        rewards = self.amount * daily_rate * days_staked
        return rewards

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "token_type": self.token_type.value,
            "amount": self.amount,
            "apy": self.apy,
            "started_at": self.started_at.isoformat(),
            "lock_period_days": self.lock_period_days,
            "rewards_earned": self.rewards_earned,
            "auto_compound": self.auto_compound,
            "is_locked": self.is_locked(),
            "days_until_unlock": self.days_until_unlock(),
            "pending_rewards": self.calculate_rewards()
        }


@dataclass
class NFTMetadata:
    """NFT元数据"""
    name: str
    description: str
    image: Optional[str] = None  # IPFS哈希或URL
    attributes: List[Dict[str, Any]] = field(default_factory=list)
    collection: Optional[str] = None
    creator: Optional[str] = None


@dataclass
class NFT:
    """NFT（非同质化代币）"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    token_id: str = ""
    contract_address: str = ""
    owner_id: str = ""
    metadata: NFTMetadata = field(default_factory=NFTMetadata)
    created_at: datetime = field(default_factory=datetime.now)
    last_transferred: Optional[datetime] = None
    transfer_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "token_id": self.token_id,
            "contract_address": self.contract_address,
            "owner_id": self.owner_id,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
                "image": self.metadata.image,
                "attributes": self.metadata.attributes,
                "collection": self.metadata.collection,
                "creator": self.metadata.creator
            },
            "created_at": self.created_at.isoformat(),
            "last_transferred": self.last_transferred.isoformat() if self.last_transferred else None,
            "transfer_count": self.transfer_count
        }


@dataclass
class Transaction:
    """交易"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_user_id: str = ""
    to_user_id: str = ""
    token_type: TokenType = TokenType.GOVERNANCE
    amount: float = 0.0
    status: TransactionStatus = TransactionStatus.PENDING
    tx_hash: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    gas_fee: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "from_user_id": self.from_user_id,
            "to_user_id": self.to_user_id,
            "token_type": self.token_type.value,
            "amount": self.amount,
            "status": self.status.value,
            "tx_hash": self.tx_hash,
            "timestamp": self.timestamp.isoformat(),
            "gas_fee": self.gas_fee,
            "metadata": self.metadata
        }


@dataclass
class CreatorToken:
    """创作者代币"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    creator_id: str = ""
    symbol: str = ""
    name: str = ""
    total_supply: float = 1000000.0
    circulating_supply: float = 0.0
    price: float = 1.0  # 单价（USD）
    market_cap: float = 0.0
    holders: Dict[str, float] = field(default_factory=dict)  # user_id -> balance
    created_at: datetime = field(default_factory=datetime.now)

    def calculate_market_cap(self) -> float:
        """计算市值"""
        return self.circulating_supply * self.price

    def get_holders_count(self) -> int:
        """获取持有人数"""
        return len([h for h, b in self.holders.items() if b > 0])

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "creator_id": self.creator_id,
            "symbol": self.symbol,
            "name": self.name,
            "total_supply": self.total_supply,
            "circulating_supply": self.circulating_supply,
            "price": self.price,
            "market_cap": self.calculate_market_cap(),
            "holders_count": self.get_holders_count(),
            "created_at": self.created_at.isoformat()
        }


class AdvancedEconomy:
    """高级经济系统"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/advanced_economy.json"

        # 代币余额
        self.token_balances: Dict[str, TokenBalance] = {}  # (user_id, token_type) -> balance

        # 质押
        self.stake_positions: Dict[str, StakePosition] = {}

        # NFT
        self.nfts: Dict[str, NFT] = {}

        # 创作者代币
        self.creator_tokens: Dict[str, CreatorToken] = {}

        # 交易历史
        self.transactions: List[Transaction] = []

        # 质押APY配置
        self.staking_apy: Dict[TokenType, float] = {
            TokenType.GOVERNANCE: 0.05,  # 5%
            TokenType.CREATOR: 0.08,  # 8%
            TokenType.WORLD: 0.06,  # 6%
        }

        # 加载数据
        self._load_data()

    def get_balance(self, user_id: str, token_type: TokenType) -> float:
        """获取余额"""
        key = f"{user_id}_{token_type.value}"
        balance = self.token_balances.get(key)
        return balance.balance if balance else 0.0

    def deposit(self, user_id: str, token_type: TokenType, amount: float) -> bool:
        """存款"""
        if amount <= 0:
            return False

        key = f"{user_id}_{token_type.value}"

        if key not in self.token_balances:
            self.token_balances[key] = TokenBalance(
                user_id=user_id,
                token_type=token_type
            )

        self.token_balances[key].balance += amount
        self.token_balances[key].last_updated = datetime.now()

        self._save_data()
        return True

    def withdraw(self, user_id: str, token_type: TokenType, amount: float) -> bool:
        """取款"""
        if amount <= 0:
            return False

        key = f"{user_id}_{token_type.value}"
        balance = self.token_balances.get(key)

        if not balance or balance.available_balance() < amount:
            return False

        balance.balance -= amount
        balance.last_updated = datetime.now()

        self._save_data()
        return True

    def transfer(
        self,
        from_user_id: str,
        to_user_id: str,
        token_type: TokenType,
        amount: float
    ) -> Optional[Transaction]:
        """转账"""
        if amount <= 0:
            return None

        # 扣款
        if not self.withdraw(from_user_id, token_type, amount):
            return None

        # 存款
        if not self.deposit(to_user_id, token_type, amount):
            # 回滚
            self.deposit(from_user_id, token_type, amount)
            return None

        # 记录交易
        transaction = Transaction(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            token_type=token_type,
            amount=amount,
            status=TransactionStatus.CONFIRMED
        )

        self.transactions.append(transaction)
        self._save_data()

        return transaction

    def stake(
        self,
        user_id: str,
        token_type: TokenType,
        amount: float,
        lock_period_days: int = 0,
        auto_compound: bool = False
    ) -> Optional[StakePosition]:
        """质押"""
        key = f"{user_id}_{token_type.value}"
        balance = self.token_balances.get(key)

        if not balance or balance.available_balance() < amount:
            return None

        # 锁定余额
        balance.balance -= amount
        balance.staked += amount

        # 创建质押位置
        apy = self.staking_apy.get(token_type, 0.0)
        position = StakePosition(
            user_id=user_id,
            token_type=token_type,
            amount=amount,
            apy=apy,
            lock_period_days=lock_period_days,
            auto_compound=auto_compound
        )

        self.stake_positions[position.id] = position
        self._save_data()

        return position

    def unstake(self, position_id: str, user_id: str) -> Tuple[bool, str]:
        """取消质押"""
        position = self.stake_positions.get(position_id)
        if not position:
            return False, "Position not found"

        if position.user_id != user_id:
            return False, "Not owner of position"

        if position.is_locked():
            days_left = position.days_until_unlock()
            return False, f"Position locked for {days_left} more days"

        # 计算奖励
        rewards = position.calculate_rewards()

        # 解锁质押的代币
        key = f"{user_id}_{position.token_type.value}"
        balance = self.token_balances.get(key)
        if balance:
            balance.staked -= position.amount
            balance.balance += position.amount + rewards

        # 删除质押位置
        del self.stake_positions[position_id]

        self._save_data()
        return True, f"Unstaked {position.amount} + {rewards:.2f} rewards"

    def get_staking_positions(self, user_id: str) -> List[StakePosition]:
        """获取用户的质押位置"""
        return [
            pos for pos in self.stake_positions.values()
            if pos.user_id == user_id
        ]

    def create_creator_token(
        self,
        creator_id: str,
        symbol: str,
        name: str,
        initial_supply: float = 1000000.0
    ) -> CreatorToken:
        """创建创作者代币"""
        token = CreatorToken(
            creator_id=creator_id,
            symbol=symbol,
            name=name,
            total_supply=initial_supply
        )

        # 创作者持有初始供应的100%
        token.holders[creator_id] = initial_supply
        token.circulating_supply = 0.0

        self.creator_tokens[token.id] = token
        self._save_data()

        return token

    def buy_creator_token(
        self,
        token_id: str,
        user_id: str,
        amount: float,
        usd_amount: float
    ) -> bool:
        """购买创作者代币"""
        token = self.creator_tokens.get(token_id)
        if not token:
            return False

        # 检查是否有足够供应
        if token.circulating_supply + amount > token.total_supply:
            return False

        # 购买
        token.holders[user_id] = token.holders.get(user_id, 0.0) + amount
        token.circulating_supply += amount

        self._save_data()
        return True

    def sell_creator_token(
        self,
        token_id: str,
        user_id: str,
        amount: float
    ) -> Tuple[bool, str]:
        """出售创作者代币"""
        token = self.creator_tokens.get(token_id)
        if not token:
            return False, "Token not found"

        user_balance = token.holders.get(user_id, 0.0)
        if user_balance < amount:
            return False, "Insufficient balance"

        # 出售
        token.holders[user_id] = user_balance - amount
        token.circulating_supply -= amount

        usd_amount = amount * token.price

        self._save_data()
        return True, f"Sold {amount} {token.symbol} for ${usd_amount:.2f}"

    def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """获取用户投资组合"""
        # 代币余额
        balances = {}
        for token_type in TokenType:
            balance = self.get_balance(user_id, token_type)
            if balance > 0:
                balances[token_type.value] = balance

        # 质押位置
        positions = self.get_staking_positions(user_id)
        total_staked = sum(pos.amount for pos in positions)
        pending_rewards = sum(pos.calculate_rewards() for pos in positions)

        # 创作者代币
        creator_tokens = []
        for token in self.creator_tokens.values():
            if user_id in token.holders and token.holders[user_id] > 0:
                creator_tokens.append({
                    "symbol": token.symbol,
                    "name": token.name,
                    "balance": token.holders[user_id],
                    "value_usd": token.holders[user_id] * token.price
                })

        return {
            "user_id": user_id,
            "token_balances": balances,
            "staked_amount": total_staked,
            "pending_rewards": pending_rewards,
            "stake_positions": len(positions),
            "creator_tokens": creator_tokens
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        total_balances = sum(
            b.balance for b in self.token_balances.values()
        )

        total_staked = sum(
            pos.amount for pos in self.stake_positions.values()
        )

        total_nfts = len(self.nfts)

        total_creator_tokens = len(self.creator_tokens)
        total_creator_token_market_cap = sum(
            token.calculate_market_cap()
            for token in self.creator_tokens.values()
        )

        return {
            "total_balances": total_balances,
            "total_staked": total_staked,
            "active_stake_positions": len(self.stake_positions),
            "total_nfts": total_nfts,
            "total_creator_tokens": total_creator_tokens,
            "total_creator_token_market_cap": total_creator_token_market_cap,
            "total_transactions": len(self.transactions)
        }

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 加载代币余额
            for balance_data in data.get("token_balances", []):
                balance = TokenBalance(
                    user_id=balance_data["user_id"],
                    token_type=TokenType(balance_data["token_type"]),
                    balance=balance_data["balance"],
                    locked=balance_data.get("locked", 0.0),
                    staked=balance_data.get("staked", 0.0)
                )
                balance.last_updated = datetime.fromisoformat(balance_data["last_updated"])
                key = f"{balance.user_id}_{balance.token_type.value}"
                self.token_balances[key] = balance

            # 加载质押位置
            for position_data in data.get("stake_positions", []):
                position = StakePosition(
                    user_id=position_data["user_id"],
                    token_type=TokenType(position_data["token_type"]),
                    amount=position_data["amount"],
                    apy=position_data["apy"],
                    lock_period_days=position_data.get("lock_period_days", 0),
                    auto_compound=position_data.get("auto_compound", False)
                )
                position.id = position_data["id"]
                position.started_at = datetime.fromisoformat(position_data["started_at"])
                position.rewards_earned = position_data.get("rewards_earned", 0.0)
                self.stake_positions[position.id] = position

            # 加载创作者代币
            for token_data in data.get("creator_tokens", []):
                token = CreatorToken(
                    creator_id=token_data["creator_id"],
                    symbol=token_data["symbol"],
                    name=token_data["name"],
                    total_supply=token_data["total_supply"]
                )
                token.id = token_data["id"]
                token.circulating_supply = token_data.get("circulating_supply", 0.0)
                token.price = token_data.get("price", 1.0)
                token.holders = token_data.get("holders", {})
                token.created_at = datetime.fromisoformat(token_data["created_at"])
                self.creator_tokens[token.id] = token

            # 加载交易
            for tx_data in data.get("transactions", []):
                tx = Transaction(
                    from_user_id=tx_data["from_user_id"],
                    to_user_id=tx_data["to_user_id"],
                    token_type=TokenType(tx_data["token_type"]),
                    amount=tx_data["amount"],
                    status=TransactionStatus(tx_data["status"])
                )
                tx.id = tx_data["id"]
                tx.timestamp = datetime.fromisoformat(tx_data["timestamp"])
                tx.tx_hash = tx_data.get("tx_hash")
                tx.gas_fee = tx_data.get("gas_fee", 0.0)
                tx.metadata = tx_data.get("metadata", {})
                self.transactions.append(tx)

        except Exception as e:
            print(f"Error loading advanced economy data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "token_balances": [b.to_dict() for b in self.token_balances.values()],
                "stake_positions": [pos.to_dict() for pos in self.stake_positions.values()],
                "creator_tokens": [token.to_dict() for token in self.creator_tokens.values()],
                "transactions": [tx.to_dict() for tx in self.transactions[-1000:]],  # 只保留最近1000条
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving advanced economy data: {e}")


# 全局高级经济系统实例
_advanced_economy: Optional[AdvancedEconomy] = None


def get_advanced_economy(storage_path: Optional[str] = None) -> AdvancedEconomy:
    """获取高级经济系统单例"""
    global _advanced_economy
    if _advanced_economy is None:
        _advanced_economy = AdvancedEconomy(storage_path)
    return _advanced_economy
