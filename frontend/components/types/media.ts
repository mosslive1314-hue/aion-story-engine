/**
 * 多媒体支持 - 类型定义
 */

// 媒体类型
export type MediaType = 'image' | 'video' | 'audio' | 'document' | 'other';

// 媒体状态
export type MediaStatus = 'uploading' | 'processing' | 'completed' | 'error';

// 媒体视图模式
export type MediaViewMode = 'grid' | 'list';

// 上传进度状态
export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

// 媒体文件元数据
export interface MediaMetadata {
  fileName: string;
  fileSize: number;
  fileType: string;
  width?: number;
  height?: number;
  duration?: number;
  thumbnail?: string;
  createdAt: Date;
  updatedAt: Date;
}

// 媒体文件
export interface MediaFile {
  id: string;
  url: string;
  type: MediaType;
  status: MediaStatus;
  metadata: MediaMetadata;
  alt?: string;
  caption?: string;
  tags?: string[];
  categoryId?: string;
}

// 上传任务
export interface UploadTask {
  id: string;
  file: File;
  progress: UploadProgress;
  status: MediaStatus;
  error?: string;
  mediaFile?: MediaFile;
}

// 媒体分类
export interface MediaCategory {
  id: string;
  name: string;
  icon?: string;
  count: number;
}

// 媒体库筛选条件
export interface MediaFilter {
  type?: MediaType;
  category?: string;
  tags?: string[];
  searchQuery?: string;
  dateFrom?: Date;
  dateTo?: Date;
}

// 媒体嵌入选项
export interface MediaEmbedOptions {
  width?: number;
  height?: number;
  autoplay?: boolean;
  controls?: boolean;
  loop?: boolean;
  muted?: boolean;
}

// 媒体嵌入代码
export interface MediaEmbedCode {
  markdown: string;
  html: string;
  url: string;
}

// 图片压缩选项
export interface ImageCompressionOptions {
  maxSizeMB?: number;
  maxWidthOrHeight?: number;
  useWebWorker?: boolean;
  quality?: number;
}

// 视频压缩选项
export interface VideoCompressionOptions {
  quality?: 'low' | 'medium' | 'high';
  resolution?: '720p' | '1080p' | '4k';
  format?: 'mp4' | 'webm';
}

// 媒体上传器属性
export interface MediaUploaderProps {
  onUpload?: (files: MediaFile[]) => void;
  onProgress?: (tasks: UploadTask[]) => void;
  onError?: (error: string) => void;
  accept?: string;
  multiple?: boolean;
  maxSize?: number; // MB
  maxFiles?: number;
  compressionOptions?: ImageCompressionOptions;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

// 媒体库属性
export interface MediaLibraryProps {
  mediaFiles: MediaFile[];
  categories?: MediaCategory[];
  onSelect?: (media: MediaFile) => void;
  onDelete?: (mediaId: string) => void;
  onUpload?: (files: File[]) => void;
  filter?: MediaFilter;
  viewMode?: MediaViewMode;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

// 媒体预览属性
export interface MediaPreviewProps {
  media: MediaFile;
  onClose?: () => void;
  onNext?: () => void;
  onPrevious?: () => void;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

// 媒体嵌入组件属性
export interface MediaEmbedProps {
  media: MediaFile;
  options?: MediaEmbedOptions;
  onCopy?: (code: MediaEmbedCode) => void;
  theme?: 'light' | 'dark';
  className?: string;
  style?: React.CSSProperties;
}

// 文件验证结果
export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

// 媒体统计数据
export interface MediaStats {
  totalFiles: number;
  totalSize: number;
  byType: Record<MediaType, number>;
  recentlyAdded: number;
}
