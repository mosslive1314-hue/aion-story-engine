'use client';

import { useState, useEffect } from 'react';
import { Search, Star, Download, Filter } from 'lucide-react';
import { api, Asset } from '@/lib/api';
import { formatNumber, formatCurrency } from '@/lib/utils';

export default function MarketplacePage() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState('all');

  useEffect(() => {
    loadAssets();
  }, []);

  const loadAssets = async () => {
    try {
      const data = await api.getMarketplaceAssets();
      setAssets(data);
    } catch (error) {
      console.error('Failed to load assets:', error);
      // Use mock data for demo
      setAssets([
        {
          id: 'asset-1',
          name: '硬核热力学规则',
          type: 'world_rule',
          price: 0,
          creator: 'alice',
          rating: 5.0,
          downloads: 1247,
        },
        {
          id: 'asset-2',
          name: '中世纪魔法体系',
          type: 'asset_pack',
          price: 9.99,
          creator: 'FantasyWizard',
          rating: 4.8,
          downloads: 892,
        },
        {
          id: 'asset-3',
          name: '赛博朋克NPC模板',
          type: 'npc_template',
          price: 5.0,
          creator: 'CyberCreator',
          rating: 4.6,
          downloads: 567,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter = filterType === 'all' || asset.type === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-star-white mb-2">创作者市场</h1>
          <p className="text-gray-300">发现和使用来自全球创作者的优质资产</p>
        </div>

        {/* Search and Filters */}
        <div className="card mb-8">
          <div className="flex flex-col lg:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="搜索资产..."
                className="input-field pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex gap-2">
              <button
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === 'all'
                    ? 'bg-plasma-pink text-white'
                    : 'bg-nebula-purple text-gray-300 hover:bg-nebula-purple/80'
                }`}
                onClick={() => setFilterType('all')}
              >
                全部
              </button>
              <button
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === 'world_rule'
                    ? 'bg-plasma-pink text-white'
                    : 'bg-nebula-purple text-gray-300 hover:bg-nebula-purple/80'
                }`}
                onClick={() => setFilterType('world_rule')}
              >
                世界规则
              </button>
              <button
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === 'npc_template'
                    ? 'bg-plasma-pink text-white'
                    : 'bg-nebula-purple text-gray-300 hover:bg-nebula-purple/80'
                }`}
                onClick={() => setFilterType('npc_template')}
              >
                NPC模板
              </button>
              <button
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === 'asset_pack'
                    ? 'bg-plasma-pink text-white'
                    : 'bg-nebula-purple text-gray-300 hover:bg-nebula-purple/80'
                }`}
                onClick={() => setFilterType('asset_pack')}
              >
                资产包
              </button>
            </div>
          </div>
        </div>

        {/* Assets Grid */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-plasma-pink"></div>
            <p className="text-gray-400 mt-4">加载中...</p>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAssets.map((asset) => (
              <div key={asset.id} className="card hover:scale-105 transition-transform cursor-pointer">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-star-white mb-1">{asset.name}</h3>
                    <p className="text-sm text-gray-400">by {asset.creator}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-star-white">
                      {asset.price === 0 ? 'Free' : formatCurrency(asset.price)}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center">
                    <Star className="text-yellow-400 mr-1" size={16} fill="currentColor" />
                    <span className="text-sm text-gray-300">{asset.rating || 4.5}</span>
                  </div>
                  <div className="flex items-center">
                    <Download className="text-gray-400 mr-1" size={16} />
                    <span className="text-sm text-gray-300">{formatNumber(asset.downloads || 0)}</span>
                  </div>
                  <span className="px-2 py-1 bg-nebula-purple/50 rounded text-xs text-gray-300">
                    {asset.type}
                  </span>
                </div>

                <div className="flex gap-2">
                  <button className="flex-1 btn-primary text-sm py-2">
                    {asset.price === 0 ? '获取' : '购买'}
                  </button>
                  <button className="btn-secondary text-sm py-2 px-4">
                    预览
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Load More */}
        {!loading && filteredAssets.length > 0 && (
          <div className="mt-8 text-center">
            <button className="btn-secondary px-8 py-3">
              加载更多
            </button>
          </div>
        )}

        {/* Featured Section */}
        {!loading && (
          <div className="mt-16">
            <h2 className="text-2xl font-bold text-star-white mb-6">热门创作者</h2>
            <div className="grid md:grid-cols-4 gap-4">
              {['alice', 'FantasyWizard', 'CyberCreator', 'MysteryMaker'].map((creator) => (
                <div key={creator} className="card text-center">
                  <div className="w-16 h-16 bg-plasma-gradient rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-white font-bold text-xl">
                      {creator[0].toUpperCase()}
                    </span>
                  </div>
                  <h3 className="font-bold text-star-white mb-1">{creator}</h3>
                  <p className="text-sm text-gray-400">15 资产</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
