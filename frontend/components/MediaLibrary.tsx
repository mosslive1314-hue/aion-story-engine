/**
 * 媒体库组件
 * 网格/列表视图，支持筛选、搜索、选择
 */

'use client';

import React, { useState, useMemo, useCallback } from 'react';
import type {
  MediaFile,
  MediaLibraryProps,
  MediaViewMode,
  MediaCategory
} from '../types/media';
import { formatFileSize, getMediaType, getFileExtension } from '../../lib/media';

const MediaLibrary: React.FC<MediaLibraryProps> = ({
  mediaFiles,
  categories = [],
  onSelect,
  onDelete,
  onUpload,
  filter = {},
  viewMode: initialViewMode = 'grid',
  theme = 'dark',
  className = '',
  style = {}
}) => {
  const [viewMode, setViewMode] = useState<MediaViewMode>(initialViewMode);
  const [selectedMedia, setSelectedMedia] = useState<Set<string>>(new Set());
  const [searchQuery, setSearchQuery] = useState(filter.searchQuery || '');
  const [selectedType, setSelectedType] = useState<string>(filter.type || 'all');
  const [selectedCategory, setSelectedCategory] = useState<string>(filter.category || 'all');

  // 筛选媒体文件
  const filteredMedia = useMemo(() => {
    return mediaFiles.filter(media => {
      // 类型筛选
      if (selectedType !== 'all' && media.type !== selectedType) {
        return false;
      }

      // 分类筛选
      if (selectedCategory !== 'all' && media.categoryId !== selectedCategory) {
        return false;
      }

      // 搜索筛选
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchName = media.metadata.fileName.toLowerCase().includes(query);
        const matchTags = media.tags?.some(tag => tag.toLowerCase().includes(query));
        const matchAlt = media.alt?.toLowerCase().includes(query);

        if (!matchName && !matchTags && !matchAlt) {
          return false;
        }
      }

      // 标签筛选
      if (filter.tags && filter.tags.length > 0) {
        const hasTag = filter.tags.some(tag => media.tags?.includes(tag));
        if (!hasTag) return false;
      }

      // 日期筛选
      if (filter.dateFrom) {
        if (media.metadata.createdAt < filter.dateFrom) return false;
      }
      if (filter.dateTo) {
        if (media.metadata.createdAt > filter.dateTo) return false;
      }

      return true;
    });
  }, [mediaFiles, selectedType, selectedCategory, searchQuery, filter]);

  // 媒体类型统计
  const typeCounts = useMemo(() => {
    const counts: Record<string, number> = {
      all: mediaFiles.length,
      image: 0,
      video: 0,
      audio: 0,
      document: 0,
      other: 0
    };

    mediaFiles.forEach(media => {
      counts[media.type] = (counts[media.type] || 0) + 1;
    });

    return counts;
  }, [mediaFiles]);

  // 处理媒体点击
  const handleMediaClick = useCallback((media: MediaFile) => {
    setSelectedMedia(prev => new Set([media.id]));
    onSelect?.(media);
  }, [onSelect]);

  // 处理删除
  const handleDelete = useCallback((mediaId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('确定要删除这个媒体文件吗？')) {
      onDelete?.(mediaId);
      setSelectedMedia(prev => {
        const next = new Set(prev);
        next.delete(mediaId);
        return next;
      });
    }
  }, [onDelete]);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    height: '100%',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
    ...style
  };

  const headerStyle: React.CSSProperties = {
    padding: '20px',
    borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    gap: '16px',
    flexWrap: 'wrap'
  };

  const searchInputStyle: React.CSSProperties = {
    flex: 1,
    minWidth: '200px',
    padding: '8px 12px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    fontSize: '14px',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    outline: 'none'
  };

  const filterButtonStyle = (active: boolean) => ({
    padding: '6px 12px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    fontSize: '12px',
    cursor: 'pointer',
    backgroundColor: active
      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      : theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
    color: active ? '#ffffff' : theme === 'dark' ? '#e4e4e7' : '#18181b',
    transition: 'all 0.2s ease'
  });

  const contentStyle: React.CSSProperties = {
    flex: 1,
    overflow: 'auto',
    padding: '20px'
  };

  // 网格视图
  const renderGridView = () => (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
      gap: '16px'
    }}>
      {filteredMedia.map(media => (
        <div
          key={media.id}
          onClick={() => handleMediaClick(media)}
          style={{
            position: 'relative',
            backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
            border: `2px solid ${selectedMedia.has(media.id) ? '#667eea' : theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
            borderRadius: '8px',
            overflow: 'hidden',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          {/* 媒体预览 */}
          <div style={{
            width: '100%',
            height: '150px',
            backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden'
          }}>
            {media.type === 'image' ? (
              <img
                src={media.metadata.thumbnail || media.url}
                alt={media.alt || media.metadata.fileName}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            ) : media.type === 'video' ? (
              <video
                src={media.url}
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover'
                }}
              />
            ) : (
              <div style={{
                fontSize: '48px',
                color: theme === 'dark' ? '#71717a' : '#a1a1aa'
              }}>
                {media.type === 'audio' ? '🎵' :
                 media.type === 'document' ? '📄' : '📁'}
              </div>
            )}
          </div>

          {/* 文件信息 */}
          <div style={{ padding: '12px' }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '500',
              color: theme === 'dark' ? '#e4e4e7' : '#18181b',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              marginBottom: '4px'
            }}>
              {media.metadata.fileName}
            </div>
            <div style={{
              fontSize: '12px',
              color: theme === 'dark' ? '#a1a1aa' : '#71717a',
              marginBottom: '4px'
            }}>
              {formatFileSize(media.metadata.fileSize)}
            </div>
            {media.tags && media.tags.length > 0 && (
              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                {media.tags.slice(0, 3).map(tag => (
                  <span
                    key={tag}
                    style={{
                      padding: '2px 6px',
                      fontSize: '10px',
                      backgroundColor: theme === 'dark' ? '#3f3f46' : '#e4e4e7',
                      borderRadius: '4px',
                      color: theme === 'dark' ? '#e4e4e7' : '#18181b'
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* 删除按钮 */}
          <button
            onClick={(e) => handleDelete(media.id, e)}
            style={{
              position: 'absolute',
              top: '8px',
              right: '8px',
              width: '24px',
              height: '24px',
              borderRadius: '50%',
              border: 'none',
              backgroundColor: 'rgba(239, 68, 68, 0.9)',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );

  // 列表视图
  const renderListView = () => (
    <div>
      {filteredMedia.map(media => (
        <div
          key={media.id}
          onClick={() => handleMediaClick(media)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            padding: '12px',
            marginBottom: '8px',
            backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
            border: `1px solid ${selectedMedia.has(media.id) ? '#667eea' : theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
            borderRadius: '6px',
            cursor: 'pointer',
            transition: 'all 0.2s ease'
          }}
        >
          {/* 缩略图 */}
          <div style={{
            width: '60px',
            height: '60px',
            backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden',
            flexShrink: 0
          }}>
            {media.type === 'image' ? (
              <img
                src={media.metadata.thumbnail || media.url}
                alt={media.alt || media.metadata.fileName}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <div style={{ fontSize: '24px' }}>
                {media.type === 'video' ? '🎬' :
                 media.type === 'audio' ? '🎵' :
                 media.type === 'document' ? '📄' : '📁'}
              </div>
            )}
          </div>

          {/* 文件信息 */}
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{
              fontSize: '14px',
              fontWeight: '500',
              color: theme === 'dark' ? '#e4e4e7' : '#18181b',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
              marginBottom: '4px'
            }}>
              {media.metadata.fileName}
            </div>
            <div style={{
              fontSize: '12px',
              color: theme === 'dark' ? '#a1a1aa' : '#71717a'
            }}>
              {formatFileSize(media.metadata.fileSize)} • {media.type}
            </div>
          </div>

          {/* 删除按钮 */}
          <button
            onClick={(e) => handleDelete(media.id, e)}
            style={{
              padding: '6px 12px',
              border: 'none',
              borderRadius: '4px',
              backgroundColor: '#ef4444',
              color: '#ffffff',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            删除
          </button>
        </div>
      ))}
    </div>
  );

  return (
    <div className={`media-library ${className}`} style={containerStyle}>
      {/* 头部 */}
      <div style={headerStyle}>
        {/* 搜索框 */}
        <input
          type="text"
          placeholder="搜索媒体文件..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          style={searchInputStyle}
        />

        {/* 类型筛选 */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {Object.entries(typeCounts).map(([type, count]) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              style={filterButtonStyle(selectedType === type)}
            >
              {type === 'all' ? '全部' :
               type === 'image' ? '图片' :
               type === 'video' ? '视频' :
               type === 'audio' ? '音频' :
               type === 'document' ? '文档' : '其他'}
              ({count})
            </button>
          ))}
        </div>

        {/* 视图切换 */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setViewMode('grid')}
            style={filterButtonStyle(viewMode === 'grid')}
          >
            网格
          </button>
          <button
            onClick={() => setViewMode('list')}
            style={filterButtonStyle(viewMode === 'list')}
          >
            列表
          </button>
        </div>
      </div>

      {/* 内容区 */}
      <div style={contentStyle}>
        {filteredMedia.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: theme === 'dark' ? '#71717a' : '#a1a1aa'
          }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <div style={{ fontSize: '16px', marginBottom: '8px' }}>没有找到媒体文件</div>
            <div style={{ fontSize: '14px' }}>
              {searchQuery || selectedType !== 'all' || selectedCategory !== 'all'
                ? '尝试调整筛选条件'
                : '点击上传按钮添加媒体文件'}
            </div>
          </div>
        ) : viewMode === 'grid' ? renderGridView() : renderListView()}
      </div>
    </div>
  );
};

export default MediaLibrary;
