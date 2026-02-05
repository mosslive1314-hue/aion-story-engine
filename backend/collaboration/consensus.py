"""
Consensus Mechanism - 共识机制
实现分布式一致性算法，用于多用户协作的冲突解决
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import uuid
from collections import defaultdict
import hashlib


class ConsensusAlgorithm(Enum):
    """共识算法类型"""
    LAST_WRITE_WINS = "last_write_wins"  # 最后写入胜出
    FIRST_WRITE_WINS = "first_write_wins"  # 第一写入胜出
    VOTING = "voting"  # 投票机制
    QUORUM = "quorum"  # 仲裁机制
    PAXOS_LIKE = "paxos_like"  # 类Paxos算法
    MERGE = "merge"  # 自动合并


class ProposalStatus(Enum):
    """提案状态"""
    PENDING = "pending"  # 待定
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    EXPIRED = "expired"  # 已过期


@dataclass
class Proposal:
    """提案"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    change_id: str = ""
    proposer_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    status: ProposalStatus = ProposalStatus.PENDING
    votes: Dict[str, bool] = field(default_factory=dict)  # user_id -> vote
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_vote(self, user_id: str, vote: bool):
        """添加投票"""
        self.votes[user_id] = vote

    def count_votes(self) -> Tuple[int, int]:
        """统计投票"""
        approve = sum(1 for v in self.votes.values() if v)
        reject = sum(1 for v in self.votes.values() if not v)
        return approve, reject

    def is_expired(self, timeout_minutes: int = 10) -> bool:
        """检查是否过期"""
        return datetime.now() - self.timestamp > timedelta(minutes=timeout_minutes)


@dataclass
class ConsensusRound:
    """共识轮次"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    round_number: int = 0
    proposals: List[Proposal] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    result: Optional[str] = None

    def add_proposal(self, proposal: Proposal):
        """添加提案"""
        self.proposals.append(proposal)

    def get_winning_proposal(self) -> Optional[Proposal]:
        """获取获胜提案"""
        if not self.proposals:
            return None

        # 统计每个提案的得票
        best_proposal = None
        best_votes = -1

        for proposal in self.proposals:
            approve, _ = proposal.count_votes()
            if approve > best_votes:
                best_votes = approve
                best_proposal = proposal

        return best_proposal


@dataclass
class BlockchainBlock:
    """区块链区块（用于共识历史）"""
    index: int
    timestamp: datetime
    change_hash: str
    parent_hash: str
    consensus_result: str
    validator_votes: Dict[str, bool]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_hash(self) -> str:
        """计算区块哈希"""
        block_string = f"{self.index}{self.timestamp.isoformat()}{self.change_hash}{self.parent_hash}{self.consensus_result}"
        return hashlib.sha256(block_string.encode()).hexdigest()


class LastWriteWinsConsensus:
    """最后写入胜出共识"""

    def resolve(self, changes: List[Any]) -> Any:
        """解决冲突"""
        if not changes:
            return None

        # 返回时间戳最新的变更
        return max(changes, key=lambda c: getattr(c, 'timestamp', datetime.min))


class FirstWriteWinsConsensus:
    """第一写入胜出共识"""

    def resolve(self, changes: List[Any]) -> Any:
        """解决冲突"""
        if not changes:
            return None

        # 返回时间戳最早的变更
        return min(changes, key=lambda c: getattr(c, 'timestamp', datetime.max))


class VotingConsensus:
    """投票共识机制"""

    def __init__(self, required_quorum: float = 0.5):
        """
        Args:
            required_quorum: 通过所需的赞成票比例 (0-1)
        """
        self.required_quorum = required_quorum
        self.proposals: Dict[str, Proposal] = {}

    def create_proposal(self, change_id: str, proposer_id: str, voters: List[str]) -> Proposal:
        """创建提案"""
        proposal = Proposal(
            change_id=change_id,
            proposer_id=proposer_id
        )

        # 提议者自动投赞成票
        proposal.add_vote(proposer_id, True)

        self.proposals[proposal.id] = proposal
        return proposal

    def vote(self, proposal_id: str, user_id: str, vote: bool) -> bool:
        """投票"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        if proposal.status != ProposalStatus.PENDING:
            return False

        proposal.add_vote(user_id, vote)
        return True

    def check_consensus(self, proposal_id: str, total_voters: int) -> Optional[bool]:
        """检查是否达成共识"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return None

        approve, reject = proposal.count_votes()
        total_votes = approve + reject

        # 检查是否达到法定人数
        if total_votes < total_voters * self.required_quorum:
            return None

        # 检查是否通过
        if approve > reject:
            proposal.status = ProposalStatus.ACCEPTED
            return True
        elif reject >= approve:
            proposal.status = ProposalStatus.REJECTED
            return False

        return None


class QuorumConsensus:
    """仲裁共识机制"""

    def __init__(self, quorum_size: int = 3):
        """
        Args:
            quorum_size: 仲裁组大小
        """
        self.quorum_size = quorum_size
        self.quorum_members: List[str] = []

    def set_quorum(self, members: List[str]):
        """设置仲裁组"""
        self.quorum_members = members[:self.quorum_size]

    def resolve(self, change: Any, validators: List[str]) -> Tuple[bool, str]:
        """
        通过仲裁组解决冲突

        Returns:
            (是否通过, 理由)
        """
        approvals_needed = (self.quorum_size // 2) + 1

        # 简化实现：假设validators都投赞成票
        approvals = len(validators)

        if approvals >= approvals_needed:
            return True, f"Quorum approved: {approvals}/{self.quorum_size}"
        else:
            return False, f"Quorum rejected: {approvals}/{self.quorum_size} < {approvals_needed}"


class PaxosLikeConsensus:
    """类Paxos共识算法"""

    def __init__(self):
        self.proposals: Dict[str, Dict[str, Any]] = {}  # proposal_id -> proposal_data
        self.promises: Dict[str, List[str]] = defaultdict(list)  # proposal_id -> acceptors
        self.accepted: Dict[str, List[str]] = defaultdict(list)  # proposal_id -> acceptors

    def prepare(self, proposal_id: str, proposal_number: int, acceptors: List[str]) -> bool:
        """准备阶段（Phase 1）"""
        if proposal_id in self.proposals:
            return False

        self.proposals[proposal_id] = {
            "number": proposal_number,
            "status": "preparing"
        }

        # 模拟接受者响应承诺
        self.promises[proposal_id] = acceptors

        # 需要多数派承诺
        majority = (len(acceptors) // 2) + 1
        return len(self.promises[proposal_id]) >= majority

    def accept(self, proposal_id: str, acceptors: List[str]) -> bool:
        """接受阶段（Phase 2）"""
        if proposal_id not in self.proposals:
            return False

        if self.proposals[proposal_id]["status"] != "preparing":
            return False

        # 模拟接受者接受提案
        self.accepted[proposal_id] = acceptors

        # 需要多数派接受
        majority = (len(acceptors) // 2) + 1
        if len(self.accepted[proposal_id]) >= majority:
            self.proposals[proposal_id]["status"] = "accepted"
            return True

        return False

    def learn(self, proposal_id: str) -> bool:
        """学习阶段（Phase 3）"""
        proposal = self.proposals.get(proposal_id)
        if not proposal:
            return False

        return proposal["status"] == "accepted"


class MergeConsensus:
    """自动合并共识"""

    def merge(self, changes: List[Any]) -> Any:
        """
        尝试智能合并多个变更

        策略：
        1. 如果变更不冲突，合并所有变更
        2. 如果冲突，应用合并策略
        """
        if not changes:
            return None

        if len(changes) == 1:
            return changes[0]

        # 简化实现：应用最后写入胜出
        # 实际应用中需要更复杂的合并逻辑
        return max(changes, key=lambda c: getattr(c, 'timestamp', datetime.min))


class ConsensusEngine:
    """共识引擎主类"""

    def __init__(self, algorithm: ConsensusAlgorithm = ConsensusAlgorithm.LAST_WRITE_WINS):
        self.algorithm = algorithm
        self.rounds: List[ConsensusRound] = []
        self.current_round = 0

        # 初始化算法实例
        self.last_write_wins = LastWriteWinsConsensus()
        self.first_write_wins = FirstWriteWinsConsensus()
        self.voting = VotingConsensus()
        self.quorum = QuorumConsensus()
        self.paxos = PaxosLikeConsensus()
        self.merge = MergeConsensus()

        # 区块链（用于记录共识历史）
        self.blockchain: List[BlockchainBlock] = []
        self._init_genesis_block()

    def _init_genesis_block(self):
        """初始化创世区块"""
        genesis = BlockchainBlock(
            index=0,
            timestamp=datetime.now(),
            change_hash="0",
            parent_hash="0",
            consensus_result="genesis",
            validator_votes={}
        )
        self.blockchain.append(genesis)

    def resolve_conflict(
        self,
        changes: List[Any],
        collaborators: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> Tuple[Any, str]:
        """
        解决冲突

        Returns:
            (接受的变更, 共识结果说明)
        """
        if self.algorithm == ConsensusAlgorithm.LAST_WRITE_WINS:
            resolved = self.last_write_wins.resolve(changes)
            result = "last_write_wins"

        elif self.algorithm == ConsensusAlgorithm.FIRST_WRITE_WINS:
            resolved = self.first_write_wins.resolve(changes)
            result = "first_write_wins"

        elif self.algorithm == ConsensusAlgorithm.VOTING:
            if collaborators and len(changes) > 0:
                proposal = self.voting.create_proposal(changes[0].id, collaborators[0], collaborators)
                # 简化：自动投票
                for voter in collaborators[1:]:
                    self.voting.vote(proposal.id, voter, True)
                outcome = self.voting.check_consensus(proposal.id, len(collaborators))
                resolved = changes[0] if outcome else None
                result = f"voting:{outcome}"
            else:
                resolved = changes[0] if changes else None
                result = "voting:no_voters"

        elif self.algorithm == ConsensusAlgorithm.QUORUM:
            if collaborators:
                approved, reason = self.quorum.resolve(changes[0] if changes else None, collaborators)
                resolved = changes[0] if approved and changes else None
                result = reason
            else:
                resolved = changes[0] if changes else None
                result = "quorum:no_members"

        elif self.algorithm == ConsensusAlgorithm.MERGE:
            resolved = self.merge.merge(changes)
            result = "merged"

        else:  # PAXOS_LIKE
            if collaborators and changes:
                proposal_id = str(uuid.uuid4())
                if self.paxos.prepare(proposal_id, self.current_round, collaborators):
                    if self.paxos.accept(proposal_id, collaborators):
                        resolved = changes[0]
                        result = "paxos_accepted"
                    else:
                        resolved = None
                        result = "paxos_rejected"
                else:
                    resolved = None
                    result = "paxos_no_promises"
            else:
                resolved = changes[0] if changes else None
                result = "paxos:no_collaborators"

        # 记录到区块链
        if resolved:
            self._append_block(resolved, result, collaborators or {})

        return resolved, result

    def _append_block(self, change: Any, consensus_result: str, validators: List[str]):
        """追加区块到区块链"""
        last_block = self.blockchain[-1]

        # 计算变更哈希
        change_str = json.dumps({
            "id": getattr(change, 'id', ''),
            "timestamp": getattr(change, 'timestamp', datetime.now()).isoformat(),
            "node_id": getattr(change, 'node_id', ''),
            "change_type": getattr(change, 'change_type', ''),
            "new_value": getattr(change, 'new_value', None)
        }, sort_keys=True)
        change_hash = hashlib.sha256(change_str.encode()).hexdigest()

        # 创建新区块
        block = BlockchainBlock(
            index=len(self.blockchain),
            timestamp=datetime.now(),
            change_hash=change_hash,
            parent_hash=last_block.calculate_hash(),
            consensus_result=consensus_result,
            validator_votes={v: True for v in validators},
            metadata={}
        )

        self.blockchain.append(block)

    def start_round(self) -> ConsensusRound:
        """开始新的共识轮次"""
        self.current_round += 1
        round_obj = ConsensusRound(round_number=self.current_round)
        self.rounds.append(round_obj)
        return round_obj

    def get_consensus_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取共识历史"""
        blocks = self.blockchain[-limit:] if limit else self.blockchain

        return [
            {
                "index": block.index,
                "timestamp": block.timestamp.isoformat(),
                "change_hash": block.change_hash[:16],
                "parent_hash": block.parent_hash[:16],
                "consensus_result": block.consensus_result,
                "validators": len(block.validator_votes)
            }
            for block in reversed(blocks)
        ]

    def validate_blockchain(self) -> bool:
        """验证区块链完整性"""
        for i in range(1, len(self.blockchain)):
            current = self.blockchain[i]
            previous = self.blockchain[i - 1]

            # 验证父哈希
            if current.parent_hash != previous.calculate_hash():
                return False

            # 验证当前哈希
            if current.calculate_hash() != current.calculate_hash():
                return False

        return True

    def set_algorithm(self, algorithm: ConsensusAlgorithm):
        """设置共识算法"""
        self.algorithm = algorithm

    def get_algorithm_info(self) -> Dict[str, Any]:
        """获取当前算法信息"""
        return {
            "algorithm": self.algorithm.value,
            "current_round": self.current_round,
            "total_rounds": len(self.rounds),
            "blockchain_height": len(self.blockchain),
            "blockchain_valid": self.validate_blockchain()
        }


# 全局共识引擎实例
_consensus_engine: Optional[ConsensusEngine] = None


def get_consensus_engine(algorithm: ConsensusAlgorithm = ConsensusAlgorithm.LAST_WRITE_WINS) -> ConsensusEngine:
    """获取共识引擎单例"""
    global _consensus_engine
    if _consensus_engine is None:
        _consensus_engine = ConsensusEngine(algorithm)
    return _consensus_engine
