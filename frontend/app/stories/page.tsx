'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PlusCircle, BookOpen, Clock, Users, Search } from 'lucide-react';
import { api, Session } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

export default function StoriesPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const data = await api.getSessions();
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredSessions = sessions.filter(session =>
    session.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-star-white mb-2">我的故事</h1>
            <p className="text-gray-300">管理所有创作的故事世界</p>
          </div>
          <Link href="/stories/new" className="btn-primary inline-flex items-center">
            <PlusCircle className="mr-2" size={20} />
            创建新故事
          </Link>
        </div>

        {/* Search and Filters */}
        <div className="card mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="搜索故事..."
                className="input-field pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <button className="btn-secondary">全部</button>
              <button className="btn-secondary">进行中</button>
              <button className="btn-secondary">已完成</button>
            </div>
          </div>
        </div>

        {/* Stories Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-plasma-pink"></div>
            <p className="text-gray-400 mt-4">加载中...</p>
          </div>
        ) : filteredSessions.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="mx-auto text-gray-500 mb-4" size={48} />
            <p className="text-gray-400 mb-4">
              {searchQuery ? '没有找到匹配的故事' : '还没有任何故事'}
            </p>
            <Link href="/stories/new" className="btn-primary">
              创建你的第一个故事
            </Link>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredSessions.map((session) => (
              <Link
                key={session.session_id}
                href={`/stories/${session.session_id}`}
                className="card hover:scale-105 transition-transform"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-bold text-star-white">{session.name}</h3>
                  <span className={`px-3 py-1 rounded text-xs font-semibold ${
                    session.status === 'active'
                      ? 'bg-quantum-green/20 text-quantum-green'
                      : session.status === 'completed'
                      ? 'bg-plasma-pink/20 text-plasma-pink'
                      : 'bg-gray-500/20 text-gray-400'
                  }`}>
                    {session.status}
                  </span>
                </div>

                {session.collaborators && session.collaborators.length > 0 && (
                  <div className="flex items-center text-sm text-gray-400 mb-4">
                    <Users size={16} className="mr-2" />
                    <span>{session.collaborators.length} 协作者</span>
                  </div>
                )}

                {session.changes && (
                  <div className="flex items-center text-sm text-gray-400 mb-4">
                    <Clock size={16} className="mr-2" />
                    <span>{session.changes.length} 个节点</span>
                  </div>
                )}

                <div className="mt-4 pt-4 border-t border-plasma-pink/20">
                  <span className="text-sm text-plasma-pink">点击查看详情 →</span>
                </div>
              </Link>
            ))}
          </div>
        )}

        {/* Pagination placeholder */}
        {filteredSessions.length > 12 && (
          <div className="mt-8 flex justify-center">
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-nebula-purple rounded-lg text-star-white hover:bg-nebula-purple/80">
                上一页
              </button>
              <button className="px-4 py-2 bg-plasma-pink rounded-lg text-white">1</button>
              <button className="px-4 py-2 bg-nebula-purple rounded-lg text-star-white hover:bg-nebula-purple/80">
                下一页
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
