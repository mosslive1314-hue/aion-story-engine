'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { PlusCircle, BookOpen, Clock, Users } from 'lucide-react';
import { api, Session } from '@/lib/api';
import { formatNumber } from '@/lib/utils';

export default function DashboardPage() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

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

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-star-white mb-2">创作面板</h1>
            <p className="text-gray-300">管理你的故事世界和协作项目</p>
          </div>
          <Link href="/stories/new" className="btn-primary inline-flex items-center">
            <PlusCircle className="mr-2" size={20} />
            创建新故事
          </Link>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">总故事数</p>
                <p className="text-2xl font-bold text-star-white">{formatNumber(sessions.length)}</p>
              </div>
              <BookOpen className="text-plasma-pink" size={32} />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">进行中</p>
                <p className="text-2xl font-bold text-star-white">
                  {sessions.filter(s => s.status === 'active').length}
                </p>
              </div>
              <Clock className="text-quantum-green" size={32} />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">协作项目</p>
                <p className="text-2xl font-bold text-star-white">
                  {sessions.filter(s => s.collaborators && s.collaborators.length > 0).length}
                </p>
              </div>
              <Users className="text-plasma-pink" size={32} />
            </div>
          </div>
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm">本月创作</p>
                <p className="text-2xl font-bold text-star-white">12</p>
              </div>
              <PlusCircle className="text-quantum-green" size={32} />
            </div>
          </div>
        </div>

        {/* Recent Sessions */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-star-white">最近的故事</h2>
            <Link href="/stories" className="text-plasma-pink hover:text-plasma-pink/80">
              查看全部 →
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-plasma-pink"></div>
              <p className="text-gray-400 mt-4">加载中...</p>
            </div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-12">
              <BookOpen className="mx-auto text-gray-500 mb-4" size={48} />
              <p className="text-gray-400 mb-4">还没有任何故事</p>
              <Link href="/stories/new" className="btn-primary">
                创建你的第一个故事
              </Link>
            </div>
          ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sessions.slice(0, 6).map((session) => (
                <Link
                  key={session.session_id}
                  href={`/stories/${session.session_id}`}
                  className="p-4 bg-cosmic-blue/50 rounded-lg border border-plasma-pink/20 hover:border-plasma-pink/40 transition-colors"
                >
                  <h3 className="font-bold text-star-white mb-2">{session.name}</h3>
                  <div className="flex items-center justify-between text-sm">
                    <span className={`px-2 py-1 rounded ${
                      session.status === 'active' ? 'bg-quantum-green/20 text-quantum-green' : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {session.status}
                    </span>
                    {session.collaborators && (
                      <span className="text-gray-400">
                        {session.collaborators.length} 协作者
                      </span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
