/**
 * AI 辅助创作 - 演示页面
 */

'use client';

import React, { useState } from 'react';

export default function AIAssistantPage() {
  const [selectedFeature, setSelectedFeature] = useState<string | null>(null);
  const [inputText, setInputText] = useState('');
  const [aiOutput, setAiOutput] = useState('');
  const [loading, setLoading] = useState(false);

  const features = [
    {
      id: 'complete',
      title: '✨ 智能补全',
      description: '根据上下文自动补全内容',
      icon: '✨',
      inputPlaceholder: '输入前文内容...',
      example: '夜幕降临，侦探来到了废弃的工厂...'
    },
    {
      id: 'dialogue',
      title: '💬 对话生成',
      description: '为角色生成符合性格的对话',
      icon: '💬',
      inputPlaceholder: '描述角色和场景...',
      example: '性格冷酷的女杀手，在面对求饶的反派时...'
    },
    {
      id: 'plot',
      title: '🎭 情节建议',
      description: '提供创意情节发展建议',
      icon: '🎭',
      inputPlaceholder: '描述当前情节...',
      example: '主角发现了一个隐藏的密室，里面是...'
    },
    {
      id: 'polish',
      title: '🎨 文本润色',
      description: '优化表达，提升文本质量',
      icon: '🎨',
      inputPlaceholder: '输入需要润色的文本...',
      example: '这个房间很大，里面有很多旧家具，看起来很旧了。'
    },
    {
      id: 'expand',
      title: '📝 内容扩写',
      description: '扩展细节，丰富内容',
      icon: '📝',
      inputPlaceholder: '输入需要扩写的文本...',
      example: '清晨的阳光洒在床上，她醒了过来。'
    },
    {
      id: 'character',
      title: '👤 角色创建',
      description: '创建立体鲜活的角色',
      icon: '👤',
      inputPlaceholder: '描述角色需求...',
      example: '帮我创建一个神秘的医生角色...'
    },
  ];

  const handleFeatureSelect = (featureId: string) => {
    setSelectedFeature(featureId);
    setAiOutput('');
    setInputText('');
  };

  const handleGenerate = async () => {
    if (!inputText.trim()) {
      alert('请输入内容');
      return;
    }

    setLoading(true);

    try {
      // 模拟 AI 生成（实际应调用 API）
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockOutputs: Record<string, string> = {
        complete: '门上的油漆已经剥落，露出了锈迹斑斑的铁皮。侦探推开门，生锈的铰链发出刺耳的尖叫声。工厂内部一片漆黑，只有月光透过破碎的天窗洒下斑驳的光影。空气中弥漫着机油和霉变的味道。\n\n他打开手电筒，光束在黑暗中划过。机器设备静静地伫立着，仿佛沉睡的巨兽。突然，一阵脚步声从深处传来...',
        dialogue: '女杀手冷冷地看着跪在地上的反派，嘴角勾起一抹嘲讽的弧度。\n\n"求我？"她的声音像冰一样冷，"当初你杀那些人的时候，可曾想过会有今天？"\n\n"我错了！我真的错了！"反派哭喊着，身体不住地颤抖。\n\n"晚了。"她抬起枪，眼神中没有一丝波澜，"晚安。"',
        plot: '建议1：真相揭秘\n- 情节发展：密室中发现了案件关键证人的尸体\n- 冲突点：主角意识到自己一直在被误导\n- 转折：凶手竟然是主角最信任的搭档\n\n建议2：时间陷阱\n- 情节发展：密室是时间的封印\n- 冲突点：主角被困在了过去的时间线\n- 转折：改变过去会导致现实崩塌',
        polish: '宽敞的房间内，古老的家具静静陈列，每一件都承载着岁月的痕迹。斑驳的墙壁诉说着时光的故事，空气中弥漫着怀旧的氛围，仿佛时间在这里静止。',
        expand: '清晨的第一缕阳光透过薄纱窗帘，温柔地洒在床头。她缓缓睁开双眼，睫毛轻轻颤动，从睡梦中苏醒。金色的光芒在她的发丝间跳跃，窗外传来鸟儿清脆的鸣叫声。她伸了个懒腰，感受着新一天的温暖，嘴角不由自主地扬起一抹微笑。',
        character: '姓名：林墨轩\n年龄：42岁\n外貌：身材瘦削，戴着一副金丝边眼镜，眼神深邃而神秘。总是穿着一尘不染的白大褂。\n\n性格：表面温和儒雅，实则城府极深。对医学有着近乎痴迷的执着，但在人性上存在缺陷。冷静理智到近乎冷酷。\n\n背景：曾是顶尖外科医生，因一次医疗事故被吊销执照。后在地下世界发展，成为传说中"阎王敌"的神医。\n\n语言风格：语速不快，用词精准，喜欢用医学比喻。说话时总带着三分笑意，却让人不寒而栗。\n\n其他特点：手指修长干净，从不碰酒精。有一个神秘的医疗箱，据说里面装着他"起死回生"的秘密。'
      };

      setAiOutput(mockOutputs[selectedFeature] || 'AI 生成的内容...');
    } catch (error) {
      console.error('AI generation error:', error);
      setAiOutput('生成失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  const handleUseExample = () => {
    const feature = features.find(f => f.id === selectedFeature);
    if (feature) {
      setInputText(feature.example);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px'
    }}>
      {/* 页面头部 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '20px 24px',
        marginBottom: '20px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{
          margin: 0,
          fontSize: '28px',
          fontWeight: 'bold',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text'
        }}>
          🤖 AI 辅助创作
        </h1>
        <p style={{ margin: '8px 0 0 0', color: '#666' }}>
          智能内容补全、角色对话生成、情节建议和文本优化
        </p>
      </div>

      {/* 主内容区 */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: '300px 1fr',
        gap: '20px',
        marginBottom: '20px'
      }}>
        {/* 左侧：功能列表 */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '20px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          height: 'fit-content'
        }}>
          <h2 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: 'bold', color: '#18181b' }}>
            AI 功能
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {features.map((feature) => (
              <div
                key={feature.id}
                onClick={() => handleFeatureSelect(feature.id)}
                style={{
                  padding: '16px',
                  border: `2px solid ${selectedFeature === feature.id ? '#667eea' : '#e4e4e7'}`,
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  backgroundColor: selectedFeature === feature.id ? '#f3f4f6' : 'transparent'
                }}
              >
                <div style={{ fontSize: '24px', marginBottom: '8px' }}>
                  {feature.icon}
                </div>
                <div style={{ fontWeight: '600', marginBottom: '4px', color: '#18181b' }}>
                  {feature.title}
                </div>
                <div style={{ fontSize: '12px', color: '#666' }}>
                  {feature.description}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 右侧：输入和输出 */}
        {selectedFeature && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            gap: '20px'
          }}>
            {/* 输入区 */}
            <div style={{
              background: 'white',
              borderRadius: '12px',
              padding: '20px',
              boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#18181b' }}>
                  输入
                </h3>
                <button
                  onClick={handleUseExample}
                  style={{
                    padding: '6px 12px',
                    background: '#f3f4f6',
                    border: '1px solid #e4e4e7',
                    borderRadius: '6px',
                    fontSize: '12px',
                    color: '#666',
                    cursor: 'pointer'
                  }}
                >
                  使用示例
                </button>
              </div>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder={features.find(f => f.id === selectedFeature)?.inputPlaceholder}
                style={{
                  width: '100%',
                  minHeight: '150px',
                  padding: '12px',
                  border: '1px solid #e4e4e7',
                  borderRadius: '8px',
                  fontSize: '14px',
                  fontFamily: 'inherit',
                  resize: 'vertical',
                  outline: 'none'
                }}
              />
              <button
                onClick={handleGenerate}
                disabled={loading || !inputText.trim()}
                style={{
                  marginTop: '12px',
                  width: '100%',
                  padding: '12px',
                  background: loading
                    ? '#a1a1aa'
                    : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#ffffff',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  opacity: inputText.trim() ? 1 : 0.5
                }}
              >
                {loading ? '🤖 AI 正在创作...' : '✨ 生成内容'}
              </button>
            </div>

            {/* 输出区 */}
            {aiOutput && (
              <div style={{
                background: 'white',
                borderRadius: '12px',
                padding: '20px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 'bold', color: '#18181b' }}>
                    AI 生成结果
                  </h3>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(aiOutput);
                      alert('已复制到剪贴板');
                    }}
                    style={{
                      padding: '6px 12px',
                      background: '#f3f4f6',
                      border: '1px solid #e4e4e7',
                      borderRadius: '6px',
                      fontSize: '12px',
                      color: '#666',
                      cursor: 'pointer'
                    }}
                  >
                    📋 复制
                  </button>
                </div>
                <div style={{
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  fontSize: '14px',
                  lineHeight: '1.8',
                  color: '#18181b',
                  whiteSpace: 'pre-wrap',
                  maxHeight: '400px',
                  overflow: 'auto'
                }}>
                  {aiOutput}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* 功能说明 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{ margin: '0 0 20px 0', fontSize: '20px', fontWeight: 'bold', color: '#18181b' }}>
          🌟 AI 辅助创作功能
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>✨</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              智能补全
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              根据上下文自动续写内容，保持风格一致
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>💬</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              对话生成
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              为角色生成符合性格和情境的对话
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🎭</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              情节建议
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              提供创意情节发展方向和转折建议
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🎨</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              文本润色
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              优化表达，提升文本质量和感染力
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>📝</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              内容扩写
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              扩展细节，丰富内容，增加感染力
            </p>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '32px', marginBottom: '8px' }}>👤</div>
            <div style={{ fontWeight: '600', marginBottom: '8px', color: '#18181b' }}>
              角色创建
            </div>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              创建立体、鲜活、有深度的角色
            </p>
          </div>
        </div>
      </div>

      {/* 页脚 */}
      <div style={{
        marginTop: 'auto',
        background: 'white',
        borderRadius: '8px',
        padding: '16px',
        textAlign: 'center',
        fontSize: '12px',
        color: '#999',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        AION Story Engine - Phase 6.5 AI 辅助创作 | © 2026
      </div>
    </div>
  );
}
