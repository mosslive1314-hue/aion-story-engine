/**
 * 媒体预览组件
 * 全屏预览媒体，支持导航
 */

'use client';

import React, { useState, useCallback, useEffect } from 'react';
import type { MediaPreviewProps, MediaFile } from '../types/media';

const MediaPreview: React.FC<MediaPreviewProps> = ({
  media,
  onClose,
  onNext,
  onPrevious,
  theme = 'dark',
  className = '',
  style = {}
}) => {
  const [loading, setLoading] = useState(true);

  // 处理加载完成
  const handleLoad = useCallback(() => {
    setLoading(false);
  }, []);

  // 处理加载错误
  const handleError = useCallback(() => {
    setLoading(false);
  }, []);

  // 键盘导航
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose?.();
      } else if (e.key === 'ArrowRight') {
        onNext?.();
      } else if (e.key === 'ArrowLeft') {
        onPrevious?.();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose, onNext, onPrevious]);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.95)',
    zIndex: 1000,
    display: 'flex',
    flexDirection: 'column',
    ...style
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff'
  };

  const contentStyle: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    overflow: 'auto',
    padding: '20px'
  };

  const navButtonStyle: React.CSSProperties = {
    position: 'absolute',
    top: '50%',
    transform: 'translateY(-50%)',
    width: '50px',
    height: '50px',
    borderRadius: '50%',
    border: 'none',
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    color: '#ffffff',
    fontSize: '24px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s ease'
  };

  const infoStyle: React.CSSProperties = {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    padding: '20px',
    backgroundColor: theme === 'dark' ? 'rgba(31, 31, 31, 0.95)' : 'rgba(255, 255, 255, 0.95)',
    backdropFilter: 'blur(10px)'
  };

  return (
    <div className={`media-preview ${className}`} style={containerStyle}>
      {/* 头部 */}
      <div style={headerStyle}>
        <div style={{
          flex: 1,
          overflow: 'hidden'
        }}>
          <div style={{
            fontSize: '16px',
            fontWeight: '600',
            color: theme === 'dark' ? '#e4e4e7' : '#18181b',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap'
          }}>
            {media.metadata.fileName}
          </div>
          <div style={{
            fontSize: '12px',
            color: theme === 'dark' ? '#a1a1aa' : '#71717a',
            marginTop: '4px'
          }}>
            {media.type.toUpperCase()} • {Math.round(media.metadata.fileSize / 1024)} KB
            {media.metadata.width && media.metadata.height && (
              <> • {media.metadata.width} × {media.metadata.height}</>
            )}
          </div>
        </div>

        <button
          onClick={onClose}
          style={{
            padding: '8px 16px',
            border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
            borderRadius: '6px',
            backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
            color: theme === 'dark' ? '#e4e4e7' : '#18181b',
            cursor: 'pointer',
            fontSize: '14px'
          }}
        >
          关闭 (ESC)
        </button>
      </div>

      {/* 媒体内容 */}
      <div style={contentStyle}>
        {/* 上一个按钮 */}
        {onPrevious && (
          <button
            onClick={onPrevious}
            style={{
              ...navButtonStyle,
              left: '20px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            ‹
          </button>
        )}

        {/* 媒体 */}
        <div style={{
          maxWidth: '100%',
          maxHeight: '100%',
          position: 'relative'
        }}>
          {loading && (
            <div style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
              fontSize: '24px',
              color: '#ffffff'
            }}>
              加载中...
            </div>
          )}

          {media.type === 'image' && (
            <img
              src={media.url}
              alt={media.alt || media.metadata.fileName}
              onLoad={handleLoad}
              onError={handleError}
              style={{
                maxWidth: '100%',
                maxHeight: 'calc(100vh - 200px)',
                objectFit: 'contain',
                display: loading ? 'none' : 'block'
              }}
            />
          )}

          {media.type === 'video' && (
            <video
              src={media.url}
              controls
              autoPlay
              onLoadedData={handleLoad}
              onError={handleError}
              style={{
                maxWidth: '100%',
                maxHeight: 'calc(100vh - 200px)',
                display: loading ? 'none' : 'block'
              }}
            />
          )}

          {media.type === 'audio' && (
            <div style={{
              width: '100%',
              maxWidth: '600px',
              padding: '40px',
              backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '20px' }}>🎵</div>
              <audio
                src={media.url}
                controls
                autoPlay
                onLoadedData={handleLoad}
                onError={handleError}
                style={{ width: '100%' }}
              />
            </div>
          )}

          {media.type === 'document' && (
            <div style={{
              padding: '40px',
              backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '20px' }}>📄</div>
              <div style={{
                fontSize: '18px',
                color: theme === 'dark' ? '#e4e4e7' : '#18181b',
                marginBottom: '12px'
              }}>
                {media.metadata.fileName}
              </div>
              <a
                href={media.url}
                download={media.metadata.fileName}
                style={{
                  display: 'inline-block',
                  padding: '10px 20px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#ffffff',
                  textDecoration: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                下载文件
              </a>
            </div>
          )}

          {media.type === 'other' && (
            <div style={{
              padding: '40px',
              backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
              borderRadius: '12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '64px', marginBottom: '20px' }}>📁</div>
              <div style={{
                fontSize: '18px',
                color: theme === 'dark' ? '#e4e4e7' : '#18181b',
                marginBottom: '12px'
              }}>
                {media.metadata.fileName}
              </div>
              <div style={{
                fontSize: '14px',
                color: theme === 'dark' ? '#a1a1aa' : '#71717a',
                marginBottom: '20px'
              }}>
                无法预览此文件类型
              </div>
              <a
                href={media.url}
                download={media.metadata.fileName}
                style={{
                  display: 'inline-block',
                  padding: '10px 20px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: '#ffffff',
                  textDecoration: 'none',
                  borderRadius: '6px',
                  fontSize: '14px',
                  fontWeight: '600'
                }}
              >
                下载文件
              </a>
            </div>
          )}
        </div>

        {/* 下一个按钮 */}
        {onNext && (
          <button
            onClick={onNext}
            style={{
              ...navButtonStyle,
              right: '20px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.1)';
            }}
          >
            ›
          </button>
        )}
      </div>

      {/* 底部信息 */}
      {(media.alt || media.caption || (media.tags && media.tags.length > 0)) && (
        <div style={infoStyle}>
          {media.alt && (
            <div style={{
              fontSize: '14px',
              color: theme === 'dark' ? '#e4e4e7' : '#18181b',
              marginBottom: '8px'
            }}>
              <strong>描述:</strong> {media.alt}
            </div>
          )}
          {media.caption && (
            <div style={{
              fontSize: '14px',
              color: theme === 'dark' ? '#e4e4e7' : '#18181b',
              marginBottom: '8px'
            }}>
              <strong>说明:</strong> {media.caption}
            </div>
          )}
          {media.tags && media.tags.length > 0 && (
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
              {media.tags.map(tag => (
                <span
                  key={tag}
                  style={{
                    padding: '4px 8px',
                    fontSize: '12px',
                    backgroundColor: theme === 'dark' ? '#3f3f46' : '#e4e4e7',
                    borderRadius: '4px',
                    color: theme === 'dark' ? '#e4e4e7' : '#18181b'
                  }}
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MediaPreview;
