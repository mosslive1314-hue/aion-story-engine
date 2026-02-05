/**
 * 多媒体支持 - 演示页面
 */

'use client';

import React, { useState, useCallback } from 'react';
import MediaUploader from '../../components/MediaUploader';
import MediaLibrary from '../../components/MediaLibrary';
import MediaPreview from '../../components/MediaPreview';
import MediaEmbed from '../../components/MediaEmbed';
import type { MediaFile } from '../../components/types/media';

export default function MultimediaPage() {
  const [mediaFiles, setMediaFiles] = useState<MediaFile[]>([
    // 示例媒体文件
    {
      id: 'media-1',
      url: 'https://picsum.photos/800/600?random=1',
      type: 'image',
      status: 'completed',
      metadata: {
        fileName: 'example-image.jpg',
        fileSize: 125000,
        fileType: 'image/jpeg',
        width: 800,
        height: 600,
        thumbnail: 'https://picsum.photos/200/150?random=1',
        createdAt: new Date('2026-01-01'),
        updatedAt: new Date('2026-01-01')
      },
      alt: '示例图片',
      caption: '这是一个示例图片',
      tags: ['示例', '图片']
    },
    {
      id: 'media-2',
      url: 'https://picsum.photos/1920/1080?random=2',
      type: 'image',
      status: 'completed',
      metadata: {
        fileName: 'landscape-photo.jpg',
        fileSize: 350000,
        fileType: 'image/jpeg',
        width: 1920,
        height: 1080,
        thumbnail: 'https://picsum.photos/200/150?random=2',
        createdAt: new Date('2026-01-02'),
        updatedAt: new Date('2026-01-02')
      },
      alt: '风景照片',
      tags: ['风景', '摄影']
    },
    {
      id: 'media-3',
      url: 'https://picsum.photos/640/480?random=3',
      type: 'image',
      status: 'completed',
      metadata: {
        fileName: 'portrait.jpg',
        fileSize: 180000,
        fileType: 'image/jpeg',
        width: 640,
        height: 480,
        thumbnail: 'https://picsum.photos/200/150?random=3',
        createdAt: new Date('2026-01-03'),
        updatedAt: new Date('2026-01-03')
      },
      tags: ['人像', '艺术']
    }
  ]);

  const [selectedMedia, setSelectedMedia] = useState<MediaFile | null>(null);
  const [previewMedia, setPreviewMedia] = useState<MediaFile | null>(null);
  const [showEmbed, setShowEmbed] = useState(false);
  const [currentPreviewIndex, setCurrentPreviewIndex] = useState(0);

  // 处理上传
  const handleUpload = useCallback((files: MediaFile[]) => {
    setMediaFiles(prev => [...files, ...prev]);
    console.log('Uploaded files:', files);
  }, []);

  // 处理选择
  const handleSelect = useCallback((media: MediaFile) => {
    setSelectedMedia(media);
    setShowEmbed(true);
  }, []);

  // 处理删除
  const handleDelete = useCallback((mediaId: string) => {
    setMediaFiles(prev => prev.filter(m => m.id !== mediaId));
    if (selectedMedia?.id === mediaId) {
      setSelectedMedia(null);
      setShowEmbed(false);
    }
  }, [selectedMedia]);

  // 打开预览
  const openPreview = useCallback((media: MediaFile) => {
    setPreviewMedia(media);
    const index = mediaFiles.findIndex(m => m.id === media.id);
    setCurrentPreviewIndex(index);
  }, [mediaFiles]);

  // 预览导航
  const handleNextPreview = useCallback(() => {
    const nextIndex = (currentPreviewIndex + 1) % mediaFiles.length;
    setPreviewMedia(mediaFiles[nextIndex]);
    setCurrentPreviewIndex(nextIndex);
  }, [currentPreviewIndex, mediaFiles]);

  const handlePreviousPreview = useCallback(() => {
    const prevIndex = (currentPreviewIndex - 1 + mediaFiles.length) % mediaFiles.length;
    setPreviewMedia(mediaFiles[prevIndex]);
    setCurrentPreviewIndex(prevIndex);
  }, [currentPreviewIndex, mediaFiles]);

  // 处理错误
  const handleError = useCallback((error: string) => {
    console.error('Upload error:', error);
    alert(error);
  }, []);

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
          🎨 多媒体支持演示
        </h1>
        <p style={{ margin: '8px 0 0 0', color: '#666' }}>
          图片上传、视频嵌入、媒体库管理和文件压缩
        </p>
      </div>

      {/* 主内容区 */}
      <div style={{
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '20px',
        marginBottom: '20px'
      }}>
        {/* 左侧：上传器 */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          overflow: 'hidden'
        }}>
          <h2 style={{
            margin: '0 0 20px 0',
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#18181b'
          }}>
            📤 上传媒体
          </h2>
          <MediaUploader
            onUpload={handleUpload}
            onError={handleError}
            maxSize={10}
            maxFiles={5}
            compressionOptions={{
              maxSizeMB: 2,
              maxWidthOrHeight: 1920,
              quality: 0.8
            }}
            theme="dark"
          />
          <div style={{
            marginTop: '20px',
            padding: '16px',
            backgroundColor: '#f4f4f4',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#666'
          }}>
            <div style={{ fontWeight: '600', marginBottom: '8px' }}>✨ 功能特性:</div>
            <ul style={{ margin: 0, paddingLeft: '20px' }}>
              <li>拖拽或点击上传文件</li>
              <li>支持图片、视频、音频、文档</li>
              <li>自动图片压缩和缩略图生成</li>
              <li>实时上传进度显示</li>
              <li>文件类型和大小验证</li>
            </ul>
          </div>
        </div>

        {/* 右侧：媒体库 */}
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          height: '600px'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '20px'
          }}>
            <h2 style={{
              margin: 0,
              fontSize: '20px',
              fontWeight: 'bold',
              color: '#18181b'
            }}>
              📚 媒体库
            </h2>
            <div style={{
              fontSize: '14px',
              color: '#666'
            }}>
              共 {mediaFiles.length} 个文件
            </div>
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <MediaLibrary
              mediaFiles={mediaFiles}
              onSelect={handleSelect}
              onDelete={handleDelete}
              theme="dark"
              style={{ height: '100%' }}
            />
          </div>
        </div>
      </div>

      {/* 嵌入代码面板 */}
      {showEmbed && selectedMedia && (
        <div style={{
          background: 'white',
          borderRadius: '12px',
          padding: '24px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
          marginBottom: '20px'
        }}>
          <h2 style={{
            margin: '0 0 20px 0',
            fontSize: '20px',
            fontWeight: 'bold',
            color: '#18181b'
          }}>
            🔗 嵌入代码
          </h2>
          <MediaEmbed
            media={selectedMedia}
            theme="dark"
          />
        </div>
      )}

      {/* 使用说明 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
        marginBottom: '20px'
      }}>
        <h2 style={{
          margin: '0 0 20px 0',
          fontSize: '20px',
          fontWeight: 'bold',
          color: '#18181b'
        }}>
          📖 使用说明
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
          gap: '20px'
        }}>
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600' }}>
              📤 上传文件
            </h3>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              拖拽文件到上传区域，或点击选择文件。支持批量上传，自动压缩大图片。
            </p>
          </div>
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600' }}>
              🔍 浏览媒体
            </h3>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              切换网格/列表视图，使用搜索和筛选功能快速找到需要的媒体文件。
            </p>
          </div>
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600' }}>
              🔗 嵌入代码
            </h3>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              点击媒体文件查看嵌入选项，复制 Markdown 或 HTML 代码到编辑器。
            </p>
          </div>
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: '600' }}>
              🖼️ 预览媒体
            </h3>
            <p style={{ margin: 0, fontSize: '14px', color: '#666' }}>
              双击图片打开全屏预览，使用方向键或按钮浏览其他媒体文件。
            </p>
          </div>
        </div>
      </div>

      {/* 支持的文件格式 */}
      <div style={{
        background: 'white',
        borderRadius: '12px',
        padding: '24px',
        boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{
          margin: '0 0 20px 0',
          fontSize: '20px',
          fontWeight: 'bold',
          color: '#18181b'
        }}>
          ✅ 支持的文件格式
        </h2>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          <div style={{ padding: '12px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🖼️</div>
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>图片</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              JPG, PNG, GIF, WebP, SVG
            </div>
          </div>
          <div style={{ padding: '12px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎬</div>
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>视频</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              MP4, WebM, OGG, MOV
            </div>
          </div>
          <div style={{ padding: '12px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>🎵</div>
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>音频</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              MP3, WAV, OGG, WebM
            </div>
          </div>
          <div style={{ padding: '12px', backgroundColor: '#f4f4f4', borderRadius: '8px' }}>
            <div style={{ fontSize: '24px', marginBottom: '8px' }}>📄</div>
            <div style={{ fontWeight: '600', marginBottom: '4px' }}>文档</div>
            <div style={{ fontSize: '12px', color: '#666' }}>
              PDF, DOC, DOCX, XLS, XLSX
            </div>
          </div>
        </div>
      </div>

      {/* 媒体预览模态框 */}
      {previewMedia && (
        <MediaPreview
          media={previewMedia}
          onClose={() => setPreviewMedia(null)}
          onNext={mediaFiles.length > 1 ? handleNextPreview : undefined}
          onPrevious={mediaFiles.length > 1 ? handlePreviousPreview : undefined}
          theme="dark"
        />
      )}

      {/* 页脚 */}
      <div style={{
        marginTop: '20px',
        background: 'white',
        borderRadius: '8px',
        padding: '16px',
        textAlign: 'center',
        fontSize: '12px',
        color: '#999',
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
      }}>
        AION Story Engine - Phase 6.3 多媒体支持 | © 2026
      </div>
    </div>
  );
}
