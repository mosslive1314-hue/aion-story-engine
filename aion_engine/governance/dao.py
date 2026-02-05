from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import uuid


class ProposalType(Enum):
    """提案类型"""
    PARAMETER_CHANGE = "parameter_change"
    TREASURY_ALLOCATION = "treasury_allocation"
    FEATURE_REQUEST = "feature_request"
    GOVERNANCE_CHANGE = "governance_change"
    EMERGENCY_ACTION = "emergency_action"


class ProposalStatus(Enum):
    """提案状态"""
    PENDING = "pending"
    ACTIVE = "active"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    EXPIRED = "expired"


class VoteChoice(Enum):
    """投票选择"""
    FOR = "for"
    AGAINST = "against"
    ABSTAIN = "abstain"


@dataclass
class Proposal:
    """治理提案"""
    proposal_id: str
    title: str
    description: str
    proposal_type: ProposalType
    proposer_id: str
    created_at: datetime
    voting_period_days: int
    status: ProposalStatus = ProposalStatus.PENDING
    votes_for: int = 0
    votes_against: int = 0
    votes_abstain: int = 0
    executed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_votes(self) -> int:
        """总票数"""
        return self.votes_for + self.votes_against + self.votes_abstain

    @property
    def voting_ends_at(self) -> datetime:
        """投票结束时间"""
        return self.created_at + timedelta(days=self.voting_period_days)

    @property
    def is_active(self) -> bool:
        """投票是否进行中"""
        now = datetime.now()
        return (
            self.status == ProposalStatus.ACTIVE
            and now < self.voting_ends_at
        )

    @property
    def has_passed(self) -> bool:
        """是否通过"""
        return self.status == ProposalStatus.PASSED

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'proposal_id': self.proposal_id,
            'title': self.title,
            'description': self.description,
            'proposal_type': self.proposal_type.value,
            'proposer_id': self.proposer_id,
            'created_at': self.created_at.isoformat(),
            'voting_period_days': self.voting_period_days,
            'status': self.status.value,
            'votes_for': self.votes_for,
            'votes_against': self.votes_against,
            'votes_abstain': self.votes_abstain,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'metadata': self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Proposal':
        """从字典创建实例"""
        data = data.copy()
        data['proposal_type'] = ProposalType(data['proposal_type'])
        data['status'] = ProposalStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data['executed_at']:
            data['executed_at'] = datetime.fromisoformat(data['executed_at'])
        return cls(**data)


@dataclass
class Vote:
    """投票记录"""
    vote_id: str
    proposal_id: str
    voter_id: str
    choice: VoteChoice
    voting_power: int
    voted_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'vote_id': self.vote_id,
            'proposal_id': self.proposal_id,
            'voter_id': self.voter_id,
            'choice': self.choice.value,
            'voting_power': self.voting_power,
            'voted_at': self.voted_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Vote':
        """从字典创建实例"""
        data = data.copy()
        data['choice'] = VoteChoice(data['choice'])
        data['voted_at'] = datetime.fromisoformat(data['voted_at'])
        return cls(**data)


@dataclass
class GovernanceToken:
    """治理代币"""
    token_id: str
    owner_id: str
    balance: int
    total_supply: int = 0
    last_claim_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'token_id': self.token_id,
            'owner_id': self.owner_id,
            'balance': self.balance,
            'total_supply': self.total_supply,
            'last_claim_at': self.last_claim_at.isoformat() if self.last_claim_at else None,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GovernanceToken':
        """从字典创建实例"""
        data = data.copy()
        if data['last_claim_at']:
            data['last_claim_at'] = datetime.fromisoformat(data['last_claim_at'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class DAOGovernance:
    """DAO 治理系统"""

    def __init__(self):
        self.proposals: Dict[str, Proposal] = {}
        self.votes: Dict[str, Vote] = {}
        self.tokens: Dict[str, GovernanceToken] = {}
        self.governance_config = {
            'min_voting_period_days': 3,
            'max_voting_period_days': 14,
            'quorum_percentage': 0.10,  # 10% of total supply
            'pass_threshold': 0.50,  # 50% of votes must be FOR
            'emergency_voting_period_days': 1,
            'token_claim_period_days': 30,
            'max_proposals_per_user': 5,
        }

    def create_proposal(
        self,
        title: str,
        description: str,
        proposal_type: ProposalType,
        proposer_id: str,
        voting_period_days: Optional[int] = None,
    ) -> Optional[Proposal]:
        """创建提案"""
        # 检查用户是否有足够代币
        if proposer_id not in self.tokens:
            return None

        # 检查用户是否有创建提案的权限（至少持有 1000 代币）
        if self.tokens[proposer_id].balance < 1000:
            return None

        # 检查用户是否已达到最大提案数
        user_proposals = [
            p for p in self.proposals.values()
            if p.proposer_id == proposer_id
            and p.status in [ProposalStatus.PENDING, ProposalStatus.ACTIVE]
        ]
        if len(user_proposals) >= self.governance_config['max_proposals_per_user']:
            return None

        # 验证投票周期
        if voting_period_days is None:
            if proposal_type == ProposalType.EMERGENCY_ACTION:
                voting_period_days = self.governance_config['emergency_voting_period_days']
            else:
                voting_period_days = self.governance_config['min_voting_period_days']

        # 对于紧急提案，允许使用更短的投票周期
        if proposal_type == ProposalType.EMERGENCY_ACTION:
            if not (
                self.governance_config['emergency_voting_period_days']
                <= voting_period_days
                <= self.governance_config['max_voting_period_days']
            ):
                return None
        else:
            if not (
                self.governance_config['min_voting_period_days']
                <= voting_period_days
                <= self.governance_config['max_voting_period_days']
            ):
                return None

        proposal_id = str(uuid.uuid4())
        proposal = Proposal(
            proposal_id=proposal_id,
            title=title,
            description=description,
            proposal_type=proposal_type,
            proposer_id=proposer_id,
            created_at=datetime.now(),
            voting_period_days=voting_period_days,
            status=ProposalStatus.ACTIVE,
        )

        self.proposals[proposal_id] = proposal
        return proposal

    def cast_vote(
        self,
        proposal_id: str,
        voter_id: str,
        choice: VoteChoice,
        voting_power: Optional[int] = None,
    ) -> bool:
        """投票"""
        # 检查提案是否存在且处于活跃状态
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]
        if not proposal.is_active:
            return False

        # 检查投票者是否已有投票记录
        existing_votes = [
            v for v in self.votes.values()
            if v.proposal_id == proposal_id and v.voter_id == voter_id
        ]
        if existing_votes:
            return False

        # 获取投票权（代币余额）
        if voting_power is None:
            if voter_id not in self.tokens:
                return False
            voting_power = self.tokens[voter_id].balance

        # 创建投票记录
        vote_id = str(uuid.uuid4())
        vote = Vote(
            vote_id=vote_id,
            proposal_id=proposal_id,
            voter_id=voter_id,
            choice=choice,
            voting_power=voting_power,
        )

        self.votes[vote_id] = vote

        # 更新提案票数
        if choice == VoteChoice.FOR:
            proposal.votes_for += voting_power
        elif choice == VoteChoice.AGAINST:
            proposal.votes_against += voting_power
        else:
            proposal.votes_abstain += voting_power

        # 检查是否应该结束投票
        self._check_proposal_status(proposal_id)

        return True

    def _check_proposal_status(self, proposal_id: str):
        """检查并更新提案状态"""
        if proposal_id not in self.proposals:
            return

        proposal = self.proposals[proposal_id]

        # 如果投票期已结束，更新状态
        if not proposal.is_active:
            now = datetime.now()
            if proposal.status == ProposalStatus.ACTIVE:
                # 检查是否达到法定人数
                total_supply = self.get_total_token_supply()
                quorum_required = int(total_supply * self.governance_config['quorum_percentage'])

                if proposal.total_votes >= quorum_required:
                    # 检查是否通过
                    if proposal.votes_for > proposal.votes_against:
                        proposal.status = ProposalStatus.PASSED
                    else:
                        proposal.status = ProposalStatus.REJECTED
                else:
                    proposal.status = ProposalStatus.REJECTED
            # 如果投票期已过期
            elif now >= proposal.voting_ends_at:
                proposal.status = ProposalStatus.EXPIRED

    def execute_proposal(self, proposal_id: str) -> bool:
        """执行已通过的提案"""
        if proposal_id not in self.proposals:
            return False

        proposal = self.proposals[proposal_id]

        if proposal.status != ProposalStatus.PASSED:
            return False

        # 执行提案（这里只是模拟，实际会调用具体的执行逻辑）
        proposal.status = ProposalStatus.EXECUTED
        proposal.executed_at = datetime.now()

        return True

    def mint_tokens(self, owner_id: str, amount: int) -> bool:
        """铸造代币"""
        if owner_id not in self.tokens:
            self.tokens[owner_id] = GovernanceToken(
                token_id=str(uuid.uuid4()),
                owner_id=owner_id,
                balance=0,
                total_supply=0,
            )

        self.tokens[owner_id].balance += amount
        self.tokens[owner_id].total_supply += amount

        # 更新总供应量
        for token in self.tokens.values():
            token.total_supply = sum(t.balance for t in self.tokens.values())

        return True

    def claim_tokens(self, user_id: str) -> bool:
        """认领代币奖励"""
        if user_id not in self.tokens:
            return False

        token = self.tokens[user_id]

        # 检查是否可认领
        now = datetime.now()
        if token.last_claim_at:
            days_since_claim = (now - token.last_claim_at).days
            if days_since_claim < self.governance_config['token_claim_period_days']:
                return False

        # 发放奖励（基于持有量和活跃度）
        reward = max(1, token.balance // 1000)  # 每 1000 持有量获得 1 奖励
        token.balance += reward
        token.last_claim_at = now

        # 更新总供应量
        for t in self.tokens.values():
            t.total_supply = sum(x.balance for x in self.tokens.values())

        return True

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """获取提案"""
        return self.proposals.get(proposal_id)

    def get_user_votes(self, proposal_id: str, voter_id: str) -> List[Vote]:
        """获取用户的投票"""
        return [
            v for v in self.votes.values()
            if v.proposal_id == proposal_id and v.voter_id == voter_id
        ]

    def get_active_proposals(self) -> List[Proposal]:
        """获取活跃提案"""
        return [
            p for p in self.proposals.values()
            if p.status == ProposalStatus.ACTIVE
        ]

    def get_user_proposals(self, user_id: str) -> List[Proposal]:
        """获取用户的提案"""
        return [
            p for p in self.proposals.values()
            if p.proposer_id == user_id
        ]

    def get_user_token_balance(self, user_id: str) -> int:
        """获取用户代币余额"""
        if user_id not in self.tokens:
            return 0
        return self.tokens[user_id].balance

    def get_total_token_supply(self) -> int:
        """获取总代币供应量"""
        return sum(token.balance for token in self.tokens.values())

    def update_governance_config(self, new_config: Dict[str, Any]) -> bool:
        """更新治理参数"""
        # 只有通过治理提案才能修改，这里只是简单验证
        required_fields = [
            'min_voting_period_days',
            'max_voting_period_days',
            'quorum_percentage',
            'pass_threshold',
        ]

        for field in required_fields:
            if field not in new_config:
                return False

        self.governance_config.update(new_config)
        return True

    def get_governance_statistics(self) -> Dict[str, Any]:
        """获取治理统计"""
        total_proposals = len(self.proposals)
        active_proposals = len(self.get_active_proposals())
        passed_proposals = len([
            p for p in self.proposals.values()
            if p.status == ProposalStatus.PASSED
        ])
        total_votes = sum(p.total_votes for p in self.proposals.values())
        total_tokens = self.get_total_token_supply()
        unique_voters = len(set(v.voter_id for v in self.votes.values()))

        return {
            'total_proposals': total_proposals,
            'active_proposals': active_proposals,
            'passed_proposals': passed_proposals,
            'rejected_proposals': len([
                p for p in self.proposals.values()
                if p.status == ProposalStatus.REJECTED
            ]),
            'total_votes': total_votes,
            'total_tokens': total_tokens,
            'unique_voters': unique_voters,
            'participation_rate': (unique_voters / len(self.tokens) * 100) if self.tokens else 0,
            'governance_config': self.governance_config,
        }
