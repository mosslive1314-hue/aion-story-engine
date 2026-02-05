"""
DAO Governance - DAO治理系统
实现去中心化自治组织的治理机制
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import uuid


class ProposalType(Enum):
    """提案类型"""
    GOVERNANCE = "governance"  # 治理提案
    PARAMETER = "parameter"  # 参数调整
    SPENDING = "spending"  # 资金支出
    RULE_CHANGE = "rule_change"  # 规则变更
    WORLD_CREATION = "world_creation"  # 创建世界
    PORTAL_CREATION = "portal_creation"  # 创建传送门
    ELECTION = "election"  # 选举
    OTHER = "other"  # 其他


class ProposalStatus(Enum):
    """提案状态"""
    DRAFT = "draft"  # 草案
    ACTIVE = "active"  # 活跃（投票中）
    PASSED = "passed"  # 通过
    REJECTED = "rejected"  # 拒绝
    EXECUTED = "executed"  # 已执行
    EXPIRED = "expired"  # 过期
    CANCELLED = "cancelled"  # 取消


class VotingType(Enum):
    """投票类型"""
    TOKEN_WEIGHTED = "token_weighted"  # 代币加权
    ONE_PERSON_ONE_VOTE = "one_person_one_vote"  # 一人一票
    QUADRATIC = "quadratic"  # 二次方投票
    TIME_LOCKED = "time_locked"  # 时间锁定
    REPUTATION_BASED = "reputation_based"  # 声誉加权
    CONViction = "conviction"  # Conviction投票


class VoteChoice(Enum):
    """投票选项"""
    YES = "yes"  # 赞成
    NO = "no"  # 反对
    ABSTAIN = "abstain"  # 弃权


@dataclass
class Vote:
    """投票"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str = ""
    voter_id: str = ""
    choice: VoteChoice = VoteChoice.ABSTAIN
    weight: float = 1.0  # 投票权重
    timestamp: datetime = field(default_factory=datetime.now)
    conviction: float = 0.0  # Conviction值（用于Conviction投票）
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "voter_id": self.voter_id,
            "choice": self.choice.value,
            "weight": self.weight,
            "timestamp": self.timestamp.isoformat(),
            "conviction": self.conviction,
            "metadata": self.metadata
        }


@dataclass
class Proposal:
    """提案"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    proposal_type: ProposalType = ProposalType.OTHER
    status: ProposalStatus = ProposalStatus.DRAFT

    # 提案人
    proposer_id: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    # 投票参数
    voting_type: VotingType = VotingType.TOKEN_WEIGHTED
    quorum_required: float = 0.5  # 所需法定人数百分比
    approval_threshold: float = 0.5  # 批准阈值
    voting_starts: Optional[datetime] = None
    voting_ends: Optional[datetime] = None

    # 执行参数
    executable: bool = True  # 是否可执行
    executed_at: Optional[datetime] = None
    execution_tx: Optional[str] = None  # 执行交易哈希

    # 数据
    data: Dict[str, Any] = field(default_factory=dict)

    # 投票统计
    total_votes: int = 0
    yes_votes: int = 0
    no_votes: int = 0
    abstain_votes: int = 0
    yes_weight: float = 0.0
    no_weight: float = 0.0
    abstain_weight: float = 0.0

    def add_vote(self, vote: Vote):
        """添加投票"""
        if vote.choice == VoteChoice.YES:
            self.yes_votes += 1
            self.yes_weight += vote.weight
        elif vote.choice == VoteChoice.NO:
            self.no_votes += 1
            self.no_weight += vote.weight
        else:
            self.abstain_votes += 1
            self.abstain_weight += vote.weight

        self.total_votes += 1

    def is_passed(self) -> bool:
        """检查是否通过"""
        # 检查是否达到法定人数
        total_weight = self.yes_weight + self.no_weight + self.abstain_weight
        if total_weight == 0:
            return False

        quorum_met = self.total_votes >= 0  # 简化：只要有人投票就满足
        approval_met = self.yes_weight / total_weight >= self.approval_threshold if total_weight > 0 else False

        return quorum_met and approval_met

    def is_expired(self) -> bool:
        """检查是否过期"""
        if self.voting_ends:
            return datetime.now() > self.voting_ends
        return False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "proposal_type": self.proposal_type.value,
            "status": self.status.value,
            "proposer_id": self.proposer_id,
            "created_at": self.created_at.isoformat(),
            "voting_type": self.voting_type.value,
            "quorum_required": self.quorum_required,
            "approval_threshold": self.approval_threshold,
            "voting_starts": self.voting_starts.isoformat() if self.voting_starts else None,
            "voting_ends": self.voting_ends.isoformat() if self.voting_ends else None,
            "executable": self.executable,
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
            "execution_tx": self.execution_tx,
            "data": self.data,
            "total_votes": self.total_votes,
            "yes_votes": self.yes_votes,
            "no_votes": self.no_votes,
            "abstain_votes": self.abstain_votes,
            "yes_weight": self.yes_weight,
            "no_weight": self.no_weight,
            "abstain_weight": self.abstain_weight
        }


@dataclass
class TreasuryTransaction:
    """国库交易"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposal_id: str = ""
    from_address: str = ""
    to_address: str = ""
    amount: float = 0.0
    currency: str = "USDC"
    timestamp: datetime = field(default_factory=datetime.now)
    tx_hash: Optional[str] = None
    status: str = "pending"  # pending, confirmed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "proposal_id": self.proposal_id,
            "from_address": self.from_address,
            "to_address": self.to_address,
            "amount": self.amount,
            "currency": self.currency,
            "timestamp": self.timestamp.isoformat(),
            "tx_hash": self.tx_hash,
            "status": self.status,
            "metadata": self.metadata
        }


@dataclass
class ReputationScore:
    """声誉分数"""
    user_id: str
    score: float = 0.0
    contributions: int = 0  # 贡献次数
    proposals_created: int = 0  # 创建的提案数
    votes_cast: int = 0  # 投票次数
    successful_proposals: int = 0  # 成功的提案数
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "score": self.score,
            "contributions": self.contributions,
            "proposals_created": self.proposals_created,
            "votes_cast": self.votes_cast,
            "successful_proposals": self.successful_proposals,
            "last_updated": self.last_updated.isoformat()
        }


class DAO:
    """DAO（去中心化自治组织）"""

    def __init__(self, dao_id: str, name: str, description: str = ""):
        self.id = dao_id
        self.name = name
        self.description = description

        # 治理参数
        self.voting_period_hours: int = 168  # 投票周期（小时）
        self.quorum_percentage: float = 0.1  # 法定人数百分比
        self.approval_threshold: float = 0.5  # 批准阈值
        self.proposal_deposit: float = 100.0  # 提案押金

        # 代币信息
        self.token_name: str = "GOV"
        self.total_supply: float = 1000000.0
        self.token_holders: Dict[str, float] = {}  # user_id -> balance

        # 数据
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, Vote] = {}  # vote_id -> vote
        self.treasury_transactions: List[TreasuryTransaction] = []
        self.reputation_scores: Dict[str, ReputationScore] = {}

        # 元数据
        self.created_at: datetime = datetime.now()
        self.metadata: Dict[str, Any] = {}

    def create_proposal(
        self,
        title: str,
        description: str,
        proposal_type: ProposalType,
        proposer_id: str,
        data: Dict[str, Any] = None,
        voting_type: VotingType = VotingType.TOKEN_WEIGHTED
    ) -> Proposal:
        """创建提案"""
        proposal = Proposal(
            title=title,
            description=description,
            proposal_type=proposal_type,
            proposer_id=proposer_id,
            data=data or {},
            voting_type=voting_type
        )

        # 设置投票时间
        proposal.voting_starts = datetime.now()
        proposal.voting_ends = datetime.now() + timedelta(hours=self.voting_period_hours)

        # 添加到DAO
        self.proposals[proposal.id] = proposal

        # 更新创建者声誉
        if proposer_id not in self.reputation_scores:
            self.reputation_scores[proposer_id] = ReputationScore(user_id=proposer_id)

        self.reputation_scores[proposer_id].proposals_created += 1

        return proposal

    def vote(
        self,
        proposal_id: str,
        voter_id: str,
        choice: VoteChoice,
        weight: float = 1.0
    ) -> Optional[Vote]:
        """投票"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None

        # 检查提案状态
        if proposal.status != ProposalStatus.ACTIVE:
            return None

        # 检查是否过期
        if proposal.is_expired():
            proposal.status = ProposalStatus.EXPIRED
            return None

        # 检查是否已经投过票
        for vote in self.votes.values():
            if vote.proposal_id == proposal_id and vote.voter_id == voter_id:
                # 已经投过票，返回原投票
                return vote

        # 创建投票
        vote = Vote(
            proposal_id=proposal_id,
            voter_id=voter_id,
            choice=choice,
            weight=weight
        )

        # 添加到DAO
        self.votes[vote.id] = vote

        # 更新提案统计
        proposal.add_vote(vote)

        # 更新投票者声誉
        if voter_id not in self.reputation_scores:
            self.reputation_scores[voter_id] = ReputationScore(user_id=voter_id)

        self.reputation_scores[voter_id].votes_cast += 1

        return vote

    def execute_proposal(self, proposal_id: str) -> bool:
        """执行提案"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        # 检查是否通过
        if not proposal.is_passed():
            return False

        # 检查是否可执行
        if not proposal.executable:
            return False

        # 执行提案
        proposal.status = ProposalStatus.EXECUTED
        proposal.executed_at = datetime.now()

        # 如果是支出提案，从国库扣款
        if proposal.proposal_type == ProposalType.SPENDING:
            amount = proposal.data.get("amount", 0.0)
            to_address = proposal.data.get("to_address", "")

            tx = TreasuryTransaction(
                proposal_id=proposal_id,
                from_address="treasury",
                to_address=to_address,
                amount=amount,
                currency=self.token_name
            )

            self.treasury_transactions.append(tx)

        # 更新提案人声誉
        if proposal.proposer_id in self.reputation_scores:
            self.reputation_scores[proposal.proposer_id].successful_proposals += 1

        return True

    def finalize_proposals(self) -> List[Proposal]:
        """终结已过期但未终结的提案"""
        finalized = []

        for proposal in self.proposals.values():
            if proposal.status == ProposalStatus.ACTIVE and proposal.is_expired():
                if proposal.is_passed():
                    proposal.status = ProposalStatus.PASSED
                else:
                    proposal.status = ProposalStatus.REJECTED

                finalized.append(proposal)

        return finalized

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """获取提案"""
        return self.proposals.get(proposal_id)

    def get_active_proposals(self) -> List[Proposal]:
        """获取活跃提案"""
        return [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.ACTIVE
        ]

    def get_user_reputation(self, user_id: str) -> Optional[ReputationScore]:
        """获取用户声誉"""
        return self.reputation_scores.get(user_id)

    def calculate_vote_weight(
        self,
        user_id: str,
        voting_type: VotingType,
        token_balance: float = 0.0
    ) -> float:
        """计算投票权重"""
        if voting_type == VotingType.TOKEN_WEIGHTED:
            return token_balance

        elif voting_type == VotingType.ONE_PERSON_ONE_VOTE:
            return 1.0

        elif voting_type == VotingType.REPUTATION_BASED:
            reputation = self.get_user_reputation(user_id)
            if reputation:
                return 1.0 + reputation.score * 0.1  # 声誉加成
            return 1.0

        elif voting_type == VotingType.QUADRATIC:
            # 二次方投票：成本 = votes^2
            # 返回1表示1票
            return 1.0

        else:
            return 1.0

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "voting_period_hours": self.voting_period_hours,
            "quorum_percentage": self.quorum_percentage,
            "approval_threshold": self.approval_threshold,
            "proposal_deposit": self.proposal_deposit,
            "token_name": self.token_name,
            "total_supply": self.total_supply,
            "total_proposals": len(self.proposals),
            "active_proposals": len(self.get_active_proposals()),
            "total_votes": len(self.votes),
            "total_treasury_transactions": len(self.treasury_transactions),
            "created_at": self.created_at.isoformat()
        }


class DAOManager:
    """DAO管理器"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or "data/dao.json"
        self.daos: Dict[str, DAO] = {}

        # 加载数据
        self._load_data()

    def create_dao(self, dao_id: str, name: str, description: str = "") -> DAO:
        """创建DAO"""
        dao = DAO(dao_id=dao_id, name=name, description=description)
        self.daos[dao_id] = dao
        self._save_data()
        return dao

    def get_dao(self, dao_id: str) -> Optional[DAO]:
        """获取DAO"""
        return self.daos.get(dao_id)

    def get_all_daos(self) -> List[DAO]:
        """获取所有DAO"""
        return list(self.daos.values())

    def _load_data(self):
        """加载数据"""
        if not os.path.exists(self.storage_path):
            return

        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for dao_data in data.get("daos", []):
                dao = DAO(
                    dao_id=dao_data["id"],
                    name=dao_data["name"],
                    description=dao_data.get("description", "")
                )

                dao.voting_period_hours = dao_data.get("voting_period_hours", 168)
                dao.quorum_percentage = dao_data.get("quorum_percentage", 0.1)
                dao.approval_threshold = dao_data.get("approval_threshold", 0.5)
                dao.proposal_deposit = dao_data.get("proposal_deposit", 100.0)
                dao.token_name = dao_data.get("token_name", "GOV")
                dao.total_supply = dao_data.get("total_supply", 1000000.0)
                dao.token_holders = dao_data.get("token_holders", {})
                dao.created_at = datetime.fromisoformat(dao_data["created_at"])
                dao.metadata = dao_data.get("metadata", {})

                self.daos[dao.id] = dao

        except Exception as e:
            print(f"Error loading DAO data: {e}")

    def _save_data(self):
        """保存数据"""
        try:
            data = {
                "daos": [dao.to_dict() for dao in self.daos.values()],
                "last_updated": datetime.now().isoformat()
            }

            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"Error saving DAO data: {e}")


# 全局DAO管理器实例
_dao_manager: Optional[DAOManager] = None


def get_dao_manager(storage_path: Optional[str] = None) -> DAOManager:
    """获取DAO管理器单例"""
    global _dao_manager
    if _dao_manager is None:
        _dao_manager = DAOManager(storage_path)
    return _dao_manager
