'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { ArrowLeft, Plus, GitBranch, MessageSquare, Users } from 'lucide-react';
import Link from 'next/link';
import { api, Session } from '@/lib/api';

export default function StoryEditorPage() {
  const params = useParams();
  const sessionId = params.id as string;
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const data = await api.getSession(sessionId);
      setSession(data);
    } catch (error) {
      console.error('Failed to load session:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-plasma-pink"></div>
      </div>
    );
  }

  if (!session) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-star-white mb-4">故事未找到</h1>
          <Link href="/stories" className="btn-primary">
            返回故事列表
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <div className="bg-cosmic-blue/50 backdrop-blur-sm border-b border-plasma-pink/20 px-4 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/stories" className="text-gray-400 hover:text-star-white">
              <ArrowLeft size={24} />
            </Link>
            <div>
              <h1 className="text-2xl font-bold text-star-white">{session.name}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-400">
                <span className="flex items-center">
                  <GitBranch size={16} className="mr-1" />
                  {session.status}
                </span>
                {session.collaborators && (
                  <span className="flex items-center">
                    <Users size={16} className="mr-1" />
                    {session.collaborators.length} 协作者
                  </span>
                )}
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button className="btn-secondary">
              <MessageSquare size={18} className="mr-2" />
              讨论
            </button>
            <button className="btn-primary">
              <Plus size={18} className="mr-2" />
              添加节点
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-80px)]">
        {/* Node Tree Sidebar */}
        <div className="w-80 bg-cosmic-blue/30 border-r border-plasma-pink/20 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-bold text-star-white mb-4">节点树</h2>
            <div className="space-y-2">
              <div className="p-3 bg-plasma-pink/20 rounded-lg border border-plasma-pink/40 cursor-pointer">
                <div className="font-semibold text-star-white">开始</div>
                <div className="text-sm text-gray-400">故事起点</div>
              </div>
              <div className="p-3 bg-nebula-purple/50 rounded-lg border border-plasma-pink/20 hover:border-plasma-pink/40 cursor-pointer">
                <div className="font-semibold text-star-white">进入实验室</div>
                <div className="text-sm text-gray-400">场景设定</div>
              </div>
              <div className="pl-6 space-y-2">
                <div className="p-3 bg-cosmic-blue/50 rounded-lg border border-plasma-pink/20 hover:border-plasma-pink/40 cursor-pointer">
                  <div className="font-semibold text-star-white">触发火灾</div>
                  <div className="text-sm text-gray-400">关键转折</div>
                </div>
                <div className="pl-4 space-y-2">
                  <div className="p-3 bg-cosmic-blue/30 rounded-lg border border-gray-600 cursor-pointer">
                    <div className="font-semibold text-gray-300">选择灭火</div>
                    <div className="text-sm text-gray-500">行动分支</div>
                  </div>
                  <div className="p-3 bg-cosmic-blue/30 rounded-lg border border-gray-600 cursor-pointer">
                    <div className="font-semibold text-gray-300">选择逃跑</div>
                    <div className="text-sm text-gray-500">逃避分支</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Editor */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto p-8">
            <div className="card">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-star-white">节点详情</h2>
                <button className="btn-secondary text-sm">编辑</button>
              </div>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">内容</label>
                  <div className="p-4 bg-cosmic-blue/50 rounded-lg border border-plasma-pink/20 min-h-[200px]">
                    <p className="text-star-white">
                      艾萨克在实验室中工作，专注于他的研究。突然，他不小心打翻了酒精瓶，火焰迅速蔓延。
                      他需要立即做出决定...
                    </p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">NPC 状态</label>
                    <div className="space-y-2">
                      <div className="p-3 bg-cosmic-blue/50 rounded-lg">
                        <div className="font-semibold text-star-white">Isaac</div>
                        <div className="text-sm text-quantum-green">状态: panic</div>
                        <div className="text-sm text-gray-400">优先级: 保护研究资料</div>
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">世界状态</label>
                    <div className="space-y-2">
                      <div className="p-3 bg-cosmic-blue/50 rounded-lg">
                        <div className="text-sm">
                          <div className="flex justify-between text-gray-300">
                            <span>火势强度:</span>
                            <span className="text-plasma-pink">0.7</span>
                          </div>
                          <div className="flex justify-between text-gray-300">
                            <span>温度:</span>
                            <span className="text-plasma-pink">350°C</span>
                          </div>
                          <div className="flex justify-between text-gray-300">
                            <span>氧气:</span>
                            <span className="text-quantum-green">充足</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">可执行操作</label>
                  <div className="flex flex-wrap gap-2">
                    <button className="px-4 py-2 bg-quantum-green/20 text-quantum-green rounded-lg border border-quantum-green/40 hover:bg-quantum-green/30">
                      使用灭火器
                    </button>
                    <button className="px-4 py-2 bg-nebula-purple/50 text-star-white rounded-lg border border-plasma-pink/40 hover:bg-nebula-purple/70">
                      保护重要文件
                    </button>
                    <button className="px-4 py-2 bg-plasma-pink/20 text-plasma-pink rounded-lg border border-plasma-pink/40 hover:bg-plasma-pink/30">
                      呼叫帮助
                    </button>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">AI 建议</label>
                  <div className="p-4 bg-gradient-to-r from-plasma-pink/10 to-quantum-green/10 rounded-lg border border-plasma-pink/20">
                    <div className="flex items-start space-x-3">
                      <div className="w-8 h-8 bg-plasma-gradient rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-sm">AI</span>
                      </div>
                      <div>
                        <p className="text-star-white mb-2">💡 基于当前情况，建议：</p>
                        <ul className="space-y-1 text-sm text-gray-300">
                          <li>• 优先保护研究数据，符合 Isaac 的性格特征</li>
                          <li>• 火势正在蔓延，需要立即行动</li>
                          <li>• 温度升高可能触发更多物理反应</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Sidebar - Properties */}
        <div className="w-80 bg-cosmic-blue/30 border-l border-plasma-pink/20 overflow-y-auto">
          <div className="p-4">
            <h2 className="text-lg font-bold text-star-white mb-4">属性面板</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">节点ID</label>
                <div className="p-2 bg-cosmic-blue/50 rounded border border-plasma-pink/20 text-sm text-gray-400">
                  node-001
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">创建时间</label>
                <div className="p-2 bg-cosmic-blue/50 rounded border border-plasma-pink/20 text-sm text-gray-400">
                  2025-02-05 18:00
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">修改者</label>
                <div className="p-2 bg-cosmic-blue/50 rounded border border-plasma-pink/20 text-sm text-gray-400">
                  alice
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">标签</label>
                <div className="flex flex-wrap gap-2">
                  <span className="px-2 py-1 bg-plasma-pink/20 text-plasma-pink rounded text-xs">火灾</span>
                  <span className="px-2 py-1 bg-quantum-green/20 text-quantum-green rounded text-xs">实验室</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
