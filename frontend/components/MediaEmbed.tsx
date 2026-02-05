/**
 * 媒体嵌入组件
 * 生成Markdown和HTML嵌入代码
 */

'use client';

import React, { useState, useCallback, useMemo } from 'react';
import type { MediaEmbedProps, MediaEmbedCode, MediaEmbedOptions } from '../types/media';
import { copyToClipboard } from '../../lib/media';

const MediaEmbed: React.FC<MediaEmbedProps> = ({
  media,
  options = {},
  onCopy,
  theme = 'dark',
  className = '',
  style = {}
}) => {
  const [embedOptions, setEmbedOptions] = useState<MediaEmbedOptions>({
    width: options.width || 800,
    height: options.height || 600,
    autoplay: options.autoplay || false,
    controls: options.controls !== false,
    loop: options.loop || false,
    muted: options.muted || false
  });
  const [copied, setCopied] = useState<string | null>(null);

  // 生成嵌入代码
  const embedCode: MediaEmbedCode = useMemo(() => {
    const { width, height, autoplay, controls, loop, muted } = embedOptions;

    let markdown = '';
    let html = '';

    if (media.type === 'image') {
      // 图片嵌入
      const altText = media.alt || media.metadata.fileName;
      markdown = `![${altText}](${media.url})`;

      html = `<img src="${media.url}" alt="${altText}" style="max-width: ${width}px; height: auto;" />`;
    } else if (media.type === 'video') {
      // 视频嵌入
      const videoAttrs = [
        `width="${width}"`,
        `height="${height}"`,
        controls ? 'controls' : '',
        autoplay ? 'autoplay' : '',
        loop ? 'loop' : '',
        muted ? 'muted' : ''
      ].filter(Boolean).join(' ');

      markdown = `[${media.metadata.fileName}](${media.url})`;
      html = `<video ${videoAttrs}><source src="${media.url}" type="${media.metadata.fileType}" /></video>`;
    } else if (media.type === 'audio') {
      // 音频嵌入
      const audioAttrs = [
        controls ? 'controls' : '',
        autoplay ? 'autoplay' : '',
        loop ? 'loop' : ''
      ].filter(Boolean).join(' ');

      markdown = `[🎵 ${media.metadata.fileName}](${media.url})`;
      html = `<audio ${audioAttrs}><source src="${media.url}" type="${media.metadata.fileType}" /></audio>`;
    } else {
      // 其他文件
      markdown = `[${media.metadata.fileName}](${media.url})`;
      html = `<a href="${media.url}" download="${media.metadata.fileName}">📄 ${media.metadata.fileName}</a>`;
    }

    return { markdown, html, url: media.url };
  }, [media, embedOptions]);

  // 复制到剪贴板
  const handleCopy = useCallback(async (codeType: 'markdown' | 'html' | 'url') => {
    const text = embedCode[codeType];
    const success = await copyToClipboard(text);

    if (success) {
      setCopied(codeType);
      onCopy?.(embedCode);

      setTimeout(() => {
        setCopied(null);
      }, 2000);
    }
  }, [embedCode, onCopy]);

  // 更新选项
  const handleOptionChange = useCallback((key: keyof MediaEmbedOptions, value: any) => {
    setEmbedOptions(prev => ({ ...prev, [key]: value }));
  }, []);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    padding: '20px',
    backgroundColor: theme === 'dark' ? '#2d2d2d' : '#ffffff',
    borderRadius: '8px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    ...style
  };

  const sectionStyle: React.CSSProperties = {
    marginBottom: '20px'
  };

  const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '8px',
    fontSize: '14px',
    fontWeight: '600',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b'
  };

  const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '10px 12px',
    border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '6px',
    fontSize: '13px',
    fontFamily: 'monospace',
    backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    outline: 'none',
    resize: 'none'
  };

  const buttonStyle: React.CSSProperties = {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '6px',
    fontSize: '14px',
    fontWeight: '600',
    cursor: 'pointer',
    transition: 'all 0.2s ease'
  };

  return (
    <div className={`media-embed ${className}`} style={containerStyle}>
      {/* 头部 */}
      <div style={{
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
      }}>
        <div style={{
          fontSize: '18px',
          fontWeight: 'bold',
          color: theme === 'dark' ? '#e4e4e7' : '#18181b',
          marginBottom: '4px'
        }}>
          媒体嵌入代码
        </div>
        <div style={{
          fontSize: '12px',
          color: theme === 'dark' ? '#a1a1aa' : '#71717a'
        }}>
          复制以下代码到您的编辑器中
        </div>
      </div>

      {/* 选项设置 */}
      {(media.type === 'video' || media.type === 'audio') && (
        <div style={sectionStyle}>
          <div style={labelStyle}>嵌入选项</div>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
            gap: '12px'
          }}>
            {media.type === 'video' && (
              <>
                <div>
                  <label style={{ ...labelStyle, fontSize: '12px' }}>宽度</label>
                  <input
                    type="number"
                    value={embedOptions.width}
                    onChange={(e) => handleOptionChange('width', parseInt(e.target.value))}
                    style={inputStyle}
                  />
                </div>
                <div>
                  <label style={{ ...labelStyle, fontSize: '12px' }}>高度</label>
                  <input
                    type="number"
                    value={embedOptions.height}
                    onChange={(e) => handleOptionChange('height', parseInt(e.target.value))}
                    style={inputStyle}
                  />
                </div>
              </>
            )}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 0' }}>
              <input
                type="checkbox"
                id="autoplay"
                checked={embedOptions.autoplay}
                onChange={(e) => handleOptionChange('autoplay', e.target.checked)}
              />
              <label htmlFor="autoplay" style={{ fontSize: '14px', cursor: 'pointer' }}>
                自动播放
              </label>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 0' }}>
              <input
                type="checkbox"
                id="controls"
                checked={embedOptions.controls}
                onChange={(e) => handleOptionChange('controls', e.target.checked)}
              />
              <label htmlFor="controls" style={{ fontSize: '14px', cursor: 'pointer' }}>
                显示控制
              </label>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 0' }}>
              <input
                type="checkbox"
                id="loop"
                checked={embedOptions.loop}
                onChange={(e) => handleOptionChange('loop', e.target.checked)}
              />
              <label htmlFor="loop" style={{ fontSize: '14px', cursor: 'pointer' }}>
                循环播放
              </label>
            </div>
            {media.type === 'video' && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 0' }}>
                <input
                  type="checkbox"
                  id="muted"
                  checked={embedOptions.muted}
                  onChange={(e) => handleOptionChange('muted', e.target.checked)}
                />
                <label htmlFor="muted" style={{ fontSize: '14px', cursor: 'pointer' }}>
                  静音
                </label>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Markdown 代码 */}
      <div style={sectionStyle}>
        <div style={labelStyle}>Markdown</div>
        <div style={{ position: 'relative' }}>
          <textarea
            readOnly
            value={embedCode.markdown}
            rows={3}
            style={{
              ...inputStyle,
              paddingRight: '80px'
            }}
          />
          <button
            onClick={() => handleCopy('markdown')}
            style={{
              ...buttonStyle,
              position: 'absolute',
              top: '6px',
              right: '6px',
              background: copied === 'markdown' ? '#22c55e' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#ffffff'
            }}
          >
            {copied === 'markdown' ? '✓ 已复制' : '复制'}
          </button>
        </div>
      </div>

      {/* HTML 代码 */}
      <div style={sectionStyle}>
        <div style={labelStyle}>HTML</div>
        <div style={{ position: 'relative' }}>
          <textarea
            readOnly
            value={embedCode.html}
            rows={4}
            style={{
              ...inputStyle,
              paddingRight: '80px'
            }}
          />
          <button
            onClick={() => handleCopy('html')}
            style={{
              ...buttonStyle,
              position: 'absolute',
              top: '6px',
              right: '6px',
              background: copied === 'html' ? '#22c55e' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#ffffff'
            }}
          >
            {copied === 'html' ? '✓ 已复制' : '复制'}
          </button>
        </div>
      </div>

      {/* URL 链接 */}
      <div style={sectionStyle}>
        <div style={labelStyle}>文件 URL</div>
        <div style={{ position: 'relative' }}>
          <input
            type="text"
            readOnly
            value={embedCode.url}
            style={{
              ...inputStyle,
              paddingRight: '80px'
            }}
          />
          <button
            onClick={() => handleCopy('url')}
            style={{
              ...buttonStyle,
              position: 'absolute',
              top: '4px',
              right: '4px',
              background: copied === 'url' ? '#22c55e' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: '#ffffff'
            }}
          >
            {copied === 'url' ? '✓ 已复制' : '复制'}
          </button>
        </div>
      </div>

      {/* 预览 */}
      <div style={sectionStyle}>
        <div style={labelStyle}>预览</div>
        <div style={{
          padding: '16px',
          backgroundColor: theme === 'dark' ? '#1f1f1f' : '#f4f4f4',
          borderRadius: '6px',
          border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
        }}>
          {media.type === 'image' && (
            <img
              src={media.url}
              alt={media.alt || media.metadata.fileName}
              style={{
                maxWidth: embedOptions.width ? `${embedOptions.width}px` : '100%',
                height: 'auto',
                display: 'block'
              }}
            />
          )}
          {media.type === 'video' && (
            <video
              src={media.url}
              width={embedOptions.width}
              height={embedOptions.height}
              controls={embedOptions.controls}
              autoPlay={embedOptions.autoplay}
              loop={embedOptions.loop}
              muted={embedOptions.muted}
              style={{ maxWidth: '100%' }}
            />
          )}
          {media.type === 'audio' && (
            <audio
              src={media.url}
              controls={embedOptions.controls}
              autoPlay={embedOptions.autoplay}
              loop={embedOptions.loop}
              style={{ width: '100%' }}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default MediaEmbed;
