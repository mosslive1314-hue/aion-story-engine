import pytest
from datetime import datetime, timedelta
from aion_engine.governance import (
    DAOGovernance,
    Proposal,
    Vote,
    GovernanceToken,
    ProposalType,
    ProposalStatus,
    VoteChoice,
)


@pytest.fixture
def dao():
    """创建测试用的 DAO 治理系统"""
    governance = DAOGovernance()

    # 为测试用户铸造代币
    governance.mint_tokens("alice", 5000)
    governance.mint_tokens("bob", 3000)
    governance.mint_tokens("charlie", 1000)

    return governance


def test_create_proposal(dao):
    """测试创建提案"""
    proposal = dao.create_proposal(
        title="Increase Voting Period",
        description="Extend the minimum voting period to 5 days",
        proposal_type=ProposalType.PARAMETER_CHANGE,
        proposer_id="alice",
    )

    assert proposal is not None
    assert proposal.proposal_id is not None
    assert proposal.title == "Increase Voting Period"
    assert proposal.proposer_id == "alice"
    assert proposal.status == ProposalStatus.ACTIVE


def test_create_proposal_insufficient_tokens(dao):
    """测试代币不足时创建提案"""
    # 铸造 999 代币给新用户
    dao.mint_tokens("dave", 999)

    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="dave",
    )

    assert proposal is None


def test_cast_vote(dao):
    """测试投票"""
    # 创建提案
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    assert proposal is not None

    # 投票
    success = dao.cast_vote(
        proposal_id=proposal.proposal_id,
        voter_id="bob",
        choice=VoteChoice.FOR,
    )

    assert success is True
    assert proposal.votes_for == 3000  # bob 的代币数


def test_cast_vote_multiple_times(dao):
    """测试多次投票（应该失败）"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # 第一次投票
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.FOR)
    assert proposal.votes_for == 3000

    # 第二次投票应该失败
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.AGAINST)
    assert proposal.votes_for == 3000  # 票数不变
    assert proposal.votes_against == 0


def test_vote_choice_for(dao):
    """测试 FOR 投票"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.cast_vote(proposal.proposal_id, "alice", VoteChoice.FOR)
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.FOR)

    assert proposal.votes_for == 8000  # alice + bob
    assert proposal.votes_against == 0
    assert proposal.votes_abstain == 0


def test_vote_choice_against(dao):
    """测试 AGAINST 投票"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.AGAINST)

    assert proposal.votes_against == 3000
    assert proposal.votes_for == 0
    assert proposal.votes_abstain == 0


def test_vote_choice_abstain(dao):
    """测试 ABSTAIN 投票"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.ABSTAIN)

    assert proposal.votes_abstain == 3000
    assert proposal.votes_for == 0
    assert proposal.votes_against == 0


def test_proposal_passed(dao):
    """测试提案通过"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # 投票（必须在投票期内）
    dao.cast_vote(proposal.proposal_id, "alice", VoteChoice.FOR)
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.FOR)

    # 然后修改创建时间模拟投票期结束
    proposal.created_at = datetime.now() - timedelta(days=7)

    # 检查状态
    dao._check_proposal_status(proposal.proposal_id)
    assert proposal.status == ProposalStatus.PASSED


def test_proposal_rejected(dao):
    """测试提案被拒绝"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # 模拟投票期结束
    proposal.created_at = datetime.now() - timedelta(days=7)

    # 投票反对
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.AGAINST)
    dao.cast_vote(proposal.proposal_id, "charlie", VoteChoice.AGAINST)

    # 检查状态
    dao._check_proposal_status(proposal.proposal_id)
    assert proposal.status == ProposalStatus.REJECTED


def test_execute_proposal(dao):
    """测试执行提案"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # 投票（必须在投票期内）
    dao.cast_vote(proposal.proposal_id, "alice", VoteChoice.FOR)
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.FOR)

    # 模拟投票期结束并通过
    proposal.created_at = datetime.now() - timedelta(days=7)
    dao._check_proposal_status(proposal.proposal_id)

    assert proposal.status == ProposalStatus.PASSED

    # 执行提案
    success = dao.execute_proposal(proposal.proposal_id)
    assert success is True
    assert proposal.status == ProposalStatus.EXECUTED
    assert proposal.executed_at is not None


def test_mint_tokens(dao):
    """测试铸造代币"""
    initial_balance = dao.get_user_token_balance("alice")
    assert initial_balance == 5000

    success = dao.mint_tokens("alice", 1000)
    assert success is True

    new_balance = dao.get_user_token_balance("alice")
    assert new_balance == 6000


def test_claim_tokens(dao):
    """测试认领代币"""
    # 第一次认领应该成功
    success = dao.claim_tokens("alice")
    assert success is True

    # 立即再次认领应该失败（需要等待 period_days）
    success = dao.claim_tokens("alice")
    assert success is False


def test_get_active_proposals(dao):
    """测试获取活跃提案"""
    # 创建多个提案
    dao.create_proposal(
        title="Proposal 1",
        description="First proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.create_proposal(
        title="Proposal 2",
        description="Second proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    active = dao.get_active_proposals()
    assert len(active) == 2


def test_get_user_proposals(dao):
    """测试获取用户提案"""
    # alice 创建提案
    dao.create_proposal(
        title="Alice's Proposal",
        description="A proposal by alice",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # bob 创建提案
    dao.create_proposal(
        title="Bob's Proposal",
        description="A proposal by bob",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="bob",
    )

    alice_proposals = dao.get_user_proposals("alice")
    bob_proposals = dao.get_user_proposals("bob")

    assert len(alice_proposals) == 1
    assert len(bob_proposals) == 1
    assert alice_proposals[0].title == "Alice's Proposal"
    assert bob_proposals[0].title == "Bob's Proposal"


def test_total_token_supply(dao):
    """测试总代币供应量"""
    total = dao.get_total_token_supply()
    assert total == 9000  # 5000 + 3000 + 1000

    # 铸造更多代币
    dao.mint_tokens("alice", 1000)
    new_total = dao.get_total_token_supply()
    assert new_total == 10000


def test_get_governance_statistics(dao):
    """测试获取治理统计"""
    # 创建提案
    dao.create_proposal(
        title="Proposal 1",
        description="First proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.create_proposal(
        title="Proposal 2",
        description="Second proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="bob",
    )

    # 投票
    proposal = dao.create_proposal(
        title="Proposal 3",
        description="Third proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.cast_vote(proposal.proposal_id, "alice", VoteChoice.FOR)
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.FOR)

    stats = dao.get_governance_statistics()

    assert stats['total_proposals'] == 3
    assert stats['active_proposals'] == 3  # 所有提案都是活跃的（没有修改时间）
    assert stats['total_tokens'] == 9000
    assert stats['unique_voters'] == 2  # alice 和 bob 都投票了


def test_update_governance_config(dao):
    """测试更新治理参数"""
    new_config = {
        'min_voting_period_days': 5,
        'max_voting_period_days': 21,
        'quorum_percentage': 0.15,
        'pass_threshold': 0.60,
    }

    success = dao.update_governance_config(new_config)
    assert success is True
    assert dao.governance_config['min_voting_period_days'] == 5
    assert dao.governance_config['max_voting_period_days'] == 21
    assert dao.governance_config['quorum_percentage'] == 0.15
    assert dao.governance_config['pass_threshold'] == 0.60


def test_emergency_proposal(dao):
    """测试紧急提案"""
    proposal = dao.create_proposal(
        title="Emergency Fix",
        description="Fix critical bug",
        proposal_type=ProposalType.EMERGENCY_ACTION,
        proposer_id="alice",
    )

    assert proposal is not None
    assert proposal.proposal_type == ProposalType.EMERGENCY_ACTION
    assert proposal.voting_period_days == 1  # 默认的紧急投票期


def test_voting_power(dao):
    """测试投票权"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    # 使用自定义投票权
    dao.cast_vote(
        proposal_id=proposal.proposal_id,
        voter_id="bob",
        choice=VoteChoice.FOR,
        voting_power=1000,
    )

    assert proposal.votes_for == 1000  # 自定义投票权


def test_proposal_total_votes(dao):
    """测试提案总票数"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
    )

    dao.cast_vote(proposal.proposal_id, "alice", VoteChoice.FOR)
    dao.cast_vote(proposal.proposal_id, "bob", VoteChoice.AGAINST)
    dao.cast_vote(proposal.proposal_id, "charlie", VoteChoice.ABSTAIN)

    assert proposal.total_votes == 9000  # 5000 + 3000 + 1000


def test_proposal_voting_ends_at(dao):
    """测试投票结束时间"""
    proposal = dao.create_proposal(
        title="Test Proposal",
        description="A test proposal",
        proposal_type=ProposalType.FEATURE_REQUEST,
        proposer_id="alice",
        voting_period_days=7,
    )

    expected_end = proposal.created_at + timedelta(days=7)
    assert proposal.voting_ends_at == expected_end
