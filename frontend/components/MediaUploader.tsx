/**
 * 媒体上传器组件
 * 支持拖拽、点击上传、多文件上传、进度显示
 */

'use client';

import React, { useState, useCallback, useRef } from 'react';
import type {
  MediaFile,
  UploadTask,
  MediaUploaderProps,
  FileValidationResult
} from '../types/media';
import {
  validateFile,
  generateMediaId,
  readFileMetadata,
  generateImageThumbnail,
  generateVideoThumbnail,
  compressImage,
  getMediaType,
  createObjectURL
} from '../../lib/media';

const MediaUploader: React.FC<MediaUploaderProps> = ({
  onUpload,
  onProgress,
  onError,
  accept = 'image/*,video/*,audio/*,.pdf,.doc,.docx',
  multiple = true,
  maxSize = 10,
  maxFiles = 10,
  compressionOptions = { maxSizeMB: 2, maxWidthOrHeight: 1920, quality: 0.8 },
  theme = 'dark',
  className = '',
  style = {}
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadTasks, setUploadTasks] = useState<UploadTask[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 处理文件选择
  const handleFiles = useCallback(async (files: FileList | File[]) => {
    const fileArray = Array.from(files).slice(0, maxFiles);
    const tasks: UploadTask[] = [];

    // 验证文件
    const validFiles: File[] = [];
    for (const file of fileArray) {
      const validation: FileValidationResult = validateFile(file, maxSize);

      if (validation.valid) {
        validFiles.push(file);
      } else {
        onError?.(validation.error || `文件 ${file.name} 验证失败`);
      }
    }

    if (validFiles.length === 0) {
      return;
    }

    // 创建上传任务
    for (const file of validFiles) {
      const taskId = generateMediaId();

      tasks.push({
        id: taskId,
        file,
        progress: { loaded: 0, total: file.size, percentage: 0 },
        status: 'uploading'
      });
    }

    setUploadTasks(prev => [...prev, ...tasks]);

    // 处理每个文件
    const mediaFiles: MediaFile[] = [];

    for (let i = 0; i < validFiles.length; i++) {
      const file = validFiles[i];
      const task = tasks[i];

      try {
        // 读取元数据
        const metadata = await readFileMetadata(file);

        // 生成缩略图
        let thumbnail: string | undefined;
        const mediaType = getMediaType(file.type);

        if (mediaType === 'image') {
          thumbnail = await generateImageThumbnail(file);
        } else if (mediaType === 'video') {
          thumbnail = await generateVideoThumbnail(file);
        }

        // 压缩图片
        let processedFile = file;
        if (mediaType === 'image' && file.size > compressionOptions.maxSizeMB! * 1024 * 1024) {
          processedFile = await compressImage(file, compressionOptions);
        }

        // 模拟上传进度
        await simulateUpload(task.id, processedFile.size);

        // 创建媒体文件对象
        const mediaFile: MediaFile = {
          id: taskId,
          url: createObjectURL(processedFile),
          type: mediaType,
          status: 'completed',
          metadata: {
            ...metadata,
            thumbnail
          },
          tags: [],
          createdAt: new Date(),
          updatedAt: new Date()
        };

        mediaFiles.push(mediaFile);

        // 更新任务状态
        setUploadTasks(prev =>
          prev.map(t =>
            t.id === task.id
              ? { ...t, status: 'completed', mediaFile }
              : t
          )
        );
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : '上传失败';

        setUploadTasks(prev =>
          prev.map(t =>
            t.id === task.id
              ? { ...t, status: 'error', error: errorMessage }
              : t
          )
        );

        onError?.(`${file.name}: ${errorMessage}`);
      }
    }

    // 完成上传
    onUpload?.(mediaFiles);
  }, [maxFiles, maxSize, compressionOptions, onUpload, onProgress, onError]);

  // 模拟上传进度
  const simulateUpload = useCallback(async (taskId: string, fileSize: number) => {
    return new Promise<void>((resolve) => {
      let loaded = 0;
      const chunkSize = fileSize / 20; // 分20次更新

      const interval = setInterval(() => {
        loaded += chunkSize;
        const percentage = Math.min(Math.round((loaded / fileSize) * 100), 100);

        setUploadTasks(prev =>
          prev.map(t =>
            t.id === taskId
              ? {
                  ...t,
                  progress: {
                    loaded: Math.min(loaded, fileSize),
                    total: fileSize,
                    percentage
                  }
                }
              : t
          )
        );

        onProgress?.(uploadTasks);

        if (loaded >= fileSize) {
          clearInterval(interval);
          resolve();
        }
      }, 50);
    });
  }, [uploadTasks, onProgress]);

  // 处理拖拽事件
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFiles(files);
    }
  }, [handleFiles]);

  // 处理点击上传
  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // 处理文件选择变化
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFiles(files);
    }
    // 重置input，允许重复选择同一文件
    e.target.value = '';
  }, [handleFiles]);

  // 容器样式
  const containerStyle: React.CSSProperties = {
    border: `2px dashed ${isDragging ? '#667eea' : theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`,
    borderRadius: '12px',
    padding: '40px 20px',
    textAlign: 'center',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    backgroundColor: isDragging
      ? 'rgba(102, 126, 234, 0.1)'
      : theme === 'dark' ? '#1f1f1f' : '#ffffff',
    ...style
  };

  const iconStyle: React.CSSProperties = {
    fontSize: '48px',
    marginBottom: '16px',
    color: isDragging ? '#667eea' : theme === 'dark' ? '#a1a1aa' : '#71717a'
  };

  const textStyle: React.CSSProperties = {
    fontSize: '16px',
    fontWeight: '600',
    color: theme === 'dark' ? '#e4e4e7' : '#18181b',
    marginBottom: '8px'
  };

  const hintStyle: React.CSSProperties = {
    fontSize: '14px',
    color: theme === 'dark' ? '#a1a1aa' : '#71717a'
  };

  return (
    <div className={`media-uploader ${className}`}>
      {/* 上传区域 */}
      <div
        style={containerStyle}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
      >
        <div style={iconStyle}>
          {isDragging ? '📥' : '☁️'}
        </div>
        <div style={textStyle}>
          {isDragging ? '释放文件以上传' : '拖拽文件到此处'}
        </div>
        <div style={hintStyle}>
          或点击选择文件 • 最大 {maxSize}MB • 最多 {maxFiles} 个文件
        </div>
        <div style={{ marginTop: '12px', fontSize: '12px', color: theme === 'dark' ? '#71717a' : '#a1a1aa' }}>
          支持图片、视频、音频、PDF、Word、Excel
        </div>
      </div>

      {/* 隐藏的文件输入 */}
      <input
        ref={fileInputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />

      {/* 上传任务列表 */}
      {uploadTasks.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          {uploadTasks.map(task => (
            <div
              key={task.id}
              style={{
                padding: '12px',
                marginBottom: '8px',
                backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
                borderRadius: '8px',
                border: `1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'}`
              }}
            >
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '8px'
              }}>
                <div style={{
                  fontSize: '14px',
                  fontWeight: '500',
                  color: theme === 'dark' ? '#e4e4e7' : '#18181b',
                  flex: 1,
                  overflow: 'hidden',
                  textOverflow: 'ellipsis',
                  whiteSpace: 'nowrap'
                }}>
                  {task.file.name}
                </div>
                <div style={{
                  fontSize: '12px',
                  color: task.status === 'completed' ? '#22c55e' :
                          task.status === 'error' ? '#ef4444' :
                          theme === 'dark' ? '#a1a1aa' : '#71717a',
                  marginLeft: '12px'
                }}>
                  {task.status === 'uploading' ? `${task.progress.percentage}%` :
                   task.status === 'completed' ? '✅ 完成' :
                   task.status === 'error' ? '❌ 失败' : '处理中'}
                </div>
              </div>

              {/* 进度条 */}
              {task.status === 'uploading' && (
                <div style={{
                  width: '100%',
                  height: '4px',
                  backgroundColor: theme === 'dark' ? '#3f3f46' : '#e4e4e7',
                  borderRadius: '2px',
                  overflow: 'hidden'
                }}>
                  <div style={{
                    width: `${task.progress.percentage}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
              )}

              {/* 错误信息 */}
              {task.status === 'error' && task.error && (
                <div style={{
                  marginTop: '8px',
                  fontSize: '12px',
                  color: '#ef4444'
                }}>
                  {task.error}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MediaUploader;
