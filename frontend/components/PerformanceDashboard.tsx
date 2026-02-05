/**
 * 性能监控 Dashboard
 * 显示系统性能指标和统计信息
 */

'use client';

import React, { useState, useEffect } from 'react';

interface PerformanceStats {
  // API 性能
  apiResponseTime: number;
  apiSuccessRate: number;
  apiErrorCount: number;

  // 数据库性能
  dbQueryTime: number;
  dbConnections: number;
  dbCacheHitRate: number;

  // 缓存性能
  cacheHitRate: number;
  cacheSize: number;
  cacheMemory: number;

  // 任务队列
  pendingTasks: number;
  runningTasks: number;
  completedTasks: number;
  failedTasks: number;

  // 前端性能
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;

  // 资源使用
  memoryUsage: number;
  bundleSize: number;
}

export default function PerformanceDashboard() {
  const [stats, setStats] = useState<PerformanceStats>({
    apiResponseTime: 0,
    apiSuccessRate: 100,
    apiErrorCount: 0,
    dbQueryTime: 0,
    dbConnections: 0,
    dbCacheHitRate: 0,
    cacheHitRate: 0,
    cacheSize: 0,
    cacheMemory: 0,
    pendingTasks: 0,
    runningTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    cumulativeLayoutShift: 0,
    firstInputDelay: 0,
    memoryUsage: 0,
    bundleSize: 0,
  });

  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);

  // 模拟获取性能数据
  useEffect(() => {
    const fetchStats = async () => {
      try {
        // 这里应该调用实际的 API
        // const response = await fetch('/api/performance/stats');
        // const data = await response.json();

        // 模拟数据
        const mockStats: PerformanceStats = {
          apiResponseTime: Math.random() * 100 + 20,
          apiSuccessRate: 98 + Math.random() * 2,
          apiErrorCount: Math.floor(Math.random() * 5),
          dbQueryTime: Math.random() * 20 + 5,
          dbConnections: Math.floor(Math.random() * 10 + 5),
          dbCacheHitRate: 80 + Math.random() * 15,
          cacheHitRate: 85 + Math.random() * 10,
          cacheSize: Math.floor(Math.random() * 1000 + 500),
          cacheMemory: Math.random() * 100 + 50,
          pendingTasks: Math.floor(Math.random() * 10),
          runningTasks: Math.floor(Math.random() * 5),
          completedTasks: Math.floor(Math.random() * 100 + 50),
          failedTasks: Math.floor(Math.random() * 3),
          firstContentfulPaint: Math.random() * 1000 + 500,
          largestContentfulPaint: Math.random() * 2000 + 1000,
          cumulativeLayoutShift: Math.random() * 0.1,
          firstInputDelay: Math.random() * 100,
          memoryUsage: Math.random() * 100 + 50,
          bundleSize: 500000,
        };

        setStats(mockStats);
      } catch (error) {
        console.error('Failed to fetch performance stats:', error);
      }
    };

    fetchStats();

    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(fetchStats, refreshInterval);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval]);

  const StatCard = ({ title, value, unit, good }: { title: string; value: number; unit?: string; good?: boolean }) => (
    <div style={{
      padding: '16px',
      backgroundColor: '#2d2d2d',
      borderRadius: '8px',
      border: `1px solid ${good !== false ? '#3f3f46' : '#ef4444'}`,
    }}>
      <div style={{ fontSize: '12px', color: '#a1a1aa', marginBottom: '8px' }}>
        {title}
      </div>
      <div style={{
        fontSize: '24px',
        fontWeight: 'bold',
        color: good === false ? '#ef4444' : '#e4e4e7'
      }}>
        {value.toFixed(1)}
        {unit && <span style={{ fontSize: '14px', marginLeft: '4px' }}>{unit}</span>}
      </div>
    </div>
  );

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#1f1f1f',
      padding: '20px',
      color: '#e4e4e7'
    }}>
      {/* 头部 */}
      <div style={{
        marginBottom: '24px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
            📊 性能监控 Dashboard
          </h1>
          <p style={{ margin: '8px 0 0 0', color: '#a1a1aa' }}>
            实时系统性能指标和统计信息
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: '1px solid #3f3f46',
              backgroundColor: autoRefresh ? '#667eea' : '#2d2d2d',
              color: '#ffffff',
              cursor: 'pointer'
            }}
          >
            {autoRefresh ? '⏸ 暂停' : '▶ 刷新'}
          </button>
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            style={{
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #3f3f46',
              backgroundColor: '#2d2d2d',
              color: '#e4e4e7'
            }}
          >
            <option value={1000}>1秒</option>
            <option value={5000}>5秒</option>
            <option value={10000}>10秒</option>
            <option value={30000}>30秒</option>
          </select>
        </div>
      </div>

      {/* API 性能 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>🌐 API 性能</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard
            title="平均响应时间"
            value={stats.apiResponseTime}
            unit="ms"
            good={stats.apiResponseTime < 100}
          />
          <StatCard
            title="成功率"
            value={stats.apiSuccessRate}
            unit="%"
            good={stats.apiSuccessRate > 95}
          />
          <StatCard
            title="错误数"
            value={stats.apiErrorCount}
            good={stats.apiErrorCount === 0}
          />
        </div>
      </div>

      {/* 数据库性能 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>💾 数据库性能</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard
            title="查询时间"
            value={stats.dbQueryTime}
            unit="ms"
            good={stats.dbQueryTime < 20}
          />
          <StatCard
            title="活跃连接"
            value={stats.dbConnections}
            good={stats.dbConnections < 50}
          />
          <StatCard
            title="缓存命中率"
            value={stats.dbCacheHitRate}
            unit="%"
            good={stats.dbCacheHitRate > 80}
          />
        </div>
      </div>

      {/* 缓存性能 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>⚡ 缓存性能</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard
            title="命中率"
            value={stats.cacheHitRate}
            unit="%"
            good={stats.cacheHitRate > 80}
          />
          <StatCard
            title="缓存条目"
            value={stats.cacheSize}
          />
          <StatCard
            title="内存使用"
            value={stats.cacheMemory}
            unit="MB"
            good={stats.cacheMemory < 200}
          />
        </div>
      </div>

      {/* 任务队列 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>📋 任务队列</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard title="待处理" value={stats.pendingTasks} />
          <StatCard title="运行中" value={stats.runningTasks} />
          <StatCard title="已完成" value={stats.completedTasks} />
          <StatCard title="失败" value={stats.failedTasks} good={stats.failedTasks === 0} />
        </div>
      </div>

      {/* 前端性能 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>🖥️ 前端性能</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard
            title="FCP"
            value={stats.firstContentfulPaint}
            unit="ms"
            good={stats.firstContentfulPaint < 1800}
          />
          <StatCard
            title="LCP"
            value={stats.largestContentfulPaint}
            unit="ms"
            good={stats.largestContentfulPaint < 2500}
          />
          <StatCard
            title="CLS"
            value={stats.cumulativeLayoutShift}
            good={stats.cumulativeLayoutShift < 0.1}
          />
          <StatCard
            title="FID"
            value={stats.firstInputDelay}
            unit="ms"
            good={stats.firstInputDelay < 100}
          />
        </div>
      </div>

      {/* 资源使用 */}
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{ margin: '0 0 16px 0', fontSize: '20px' }}>💻 资源使用</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
          <StatCard
            title="内存使用"
            value={stats.memoryUsage}
            unit="MB"
            good={stats.memoryUsage < 200}
          />
          <StatCard
            title="Bundle 大小"
            value={stats.bundleSize / 1024}
            unit="KB"
            good={stats.bundleSize < 1000000}
          />
        </div>
      </div>

      {/* 性能指标说明 */}
      <div style={{
        padding: '16px',
        backgroundColor: '#2d2d2d',
        borderRadius: '8px',
        fontSize: '14px',
        color: '#a1a1aa'
      }}>
        <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', color: '#e4e4e7' }}>
          📖 性能指标说明
        </h3>
        <ul style={{ margin: 0, paddingLeft: '20px' }}>
          <li><strong>FCP</strong>: First Contentful Paint - 首次内容绘制时间（目标 < 1.8s）</li>
          <li><strong>LCP</strong>: Largest Contentful Paint - 最大内容绘制时间（目标 < 2.5s）</li>
          <li><strong>CLS</strong>: Cumulative Layout Shift - 累积布局偏移（目标 < 0.1）</li>
          <li><strong>FID</strong>: First Input Delay - 首次输入延迟（目标 < 100ms）</li>
        </ul>
      </div>
    </div>
  );
}
