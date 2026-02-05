from aion_engine.intent.engine import IntentEngine


def test_vague_input_interpretation():
    """Test interpreting vague user inputs"""
    engine = IntentEngine()

    # Test vague input
    vague = "来个那种...你懂的"
    intent = engine.infer_intent(vague)

    assert intent is not None
    assert "intent" in intent
    assert "confidence" in intent


def test_intent_classification():
    """Test intent classification by keywords"""
    engine = IntentEngine()

    # Test fire-related intent
    intent = engine.infer_intent("实验室起火了")
    assert intent["intent"] == "fire_scenario"
    assert intent["confidence"] > 0.8

    # Test NPC-related intent
    intent = engine.infer_intent("NPC 表现很奇怪")
    assert intent["intent"] == "npc_issue"
    assert intent["confidence"] > 0.7

    # Test story structure intent
    intent = engine.infer_intent("想要分叉情节")
    assert intent["intent"] == "story_branching"
    assert intent["confidence"] > 0.7


def test_confidence_scoring():
    """Test confidence scoring for intents"""
    engine = IntentEngine()

    # Clear intent should have high confidence
    intent = engine.infer_intent("点燃烧烧")
    assert intent["confidence"] > 0.9

    # Vague intent should have lower confidence
    intent = engine.infer_intent("就是那个...你懂的")
    assert intent["confidence"] < 0.9


def test_pattern_matching():
    """Test pattern matching from memory"""
    engine = IntentEngine()

    # Add patterns to memory
    engine.add_pattern("实验室", "fire_scenario", 0.9)
    engine.add_pattern("火", "fire_scenario", 0.8)

    # Match against input
    intent = engine.infer_intent("实验室有火")

    assert intent["intent"] == "fire_scenario"
    assert intent["confidence"] > 0.85


def test_learning_from_corrections():
    """Test learning from user corrections"""
    engine = IntentEngine()

    # Infer wrong intent
    vague_input = "搞点那个"
    inferred = engine.infer_intent(vague_input)
    original_intent = inferred["intent"]

    # User corrects it
    engine.correct_intent(vague_input, "fire_scenario")

    # Re-infer
    corrected = engine.infer_intent(vague_input)

    assert corrected["intent"] == "fire_scenario"
    assert corrected["confidence"] > inferred["confidence"]
