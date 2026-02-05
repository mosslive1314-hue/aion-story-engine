from aion_engine.nodes import Node, NodeTree


def test_create_node():
    tree = NodeTree()
    node = tree.create_node("点燃酒精", {"fire": True})

    assert node.node_id is not None
    assert node.user_action == "点燃酒精"
    assert node.world_state["fire"] == True


def test_branch_creation():
    tree = NodeTree()
    parent = tree.create_node("起始", {})
    child = tree.create_node("点燃", {}, parent.node_id)

    assert child.parent_id == parent.node_id
    assert child in tree.get_children(parent.node_id)
