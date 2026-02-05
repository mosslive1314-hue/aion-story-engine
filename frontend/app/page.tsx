'use client';

import Link from 'next/link';
import { PlusCircle, BookOpen, Store, Users, Zap } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative py-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="bg-plasma-gradient bg-clip-text text-transparent">
              AION
            </span>
            <br />
            <span className="text-star-white">Story Engine</span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            想象力的基础设施 - 创建无限分支的交互式故事世界
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/stories/new" className="btn-primary inline-flex items-center justify-center">
              <PlusCircle className="mr-2" size={20} />
              创建新故事
            </Link>
            <Link href="/dashboard" className="btn-secondary inline-flex items-center justify-center">
              <BookOpen className="mr-2" size={20} />
              我的故事
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-cosmic-blue/30">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-12">
            探索无限可能性
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-plasma-gradient rounded-xl flex items-center justify-center mx-auto mb-4">
                <Zap className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-bold mb-2">AI驱动创作</h3>
              <p className="text-gray-300">
                五层世界模拟引擎，让NPC自主行动，创造真实可信的故事世界
              </p>
            </div>
            <div className="card text-center">
              <div className="w-16 h-16 bg-plasma-gradient rounded-xl flex items-center justify-center mx-auto mb-4">
                <Users className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-bold mb-2">多人协作</h3>
              <p className="text-gray-300">
                与朋友共同创作，实时同步，云端存储，让想象力自由碰撞
              </p>
            </div>
            <div className="card text-center">
              <div className="w-16 h-16 bg-plasma-gradient rounded-xl flex items-center justify-center mx-auto mb-4">
                <Store className="text-white" size={32} />
              </div>
              <h3 className="text-xl font-bold mb-2">创作者经济</h3>
              <p className="text-gray-300">
                分享你的创作资产，获得收益，构建创作者经济生态
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-plasma-pink mb-2">10K+</div>
              <div className="text-gray-300">创作者</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-quantum-green mb-2">50K+</div>
              <div className="text-gray-300">故事世界</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-plasma-pink mb-2">1M+</div>
              <div className="text-gray-300">节点数</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-quantum-green mb-2">500+</div>
              <div className="text-gray-300">协作项目</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-cosmic-blue to-nebula-purple">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            准备好创造你的宇宙了吗？
          </h2>
          <p className="text-xl text-gray-300 mb-8">
            加入我们的创作者社区，开启无限想象之旅
          </p>
          <Link href="/dashboard" className="btn-primary text-lg px-8 py-4 inline-flex items-center">
            <PlusCircle className="mr-2" size={24} />
            立即开始创作
          </Link>
        </div>
      </section>
    </div>
  );
}
