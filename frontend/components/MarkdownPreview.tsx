/**
 * Markdown预览组件
 * 支持实时Markdown渲染和代码高亮
 */

'use client';

import React, { useMemo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { MarkdownOptions } from './types/rich-text';
import 'highlight.js/styles/github-dark.css';

interface MarkdownPreviewProps {
  content: string;
  theme?: 'light' | 'dark';
  options?: MarkdownOptions;
  className?: string;
  style?: React.CSSProperties;
}

const MarkdownPreview: React.FC<MarkdownPreviewProps> = ({
  content,
  theme = 'dark',
  options = {},
  className = '',
  style = {}
}) => {
  // 自定义代码块渲染
  const CodeBlock = useMemo(() => {
    return ({ children, className, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';

      if (!language) {
        return (
          <code
            className={className}
            style={{
              backgroundColor: theme === 'dark' ? '#2d2d2d' : '#f4f4f4',
              color: theme === 'dark' ? '#fff' : '#333',
              padding: '2px 6px',
              borderRadius: '4px',
              fontSize: '0.9em'
            }}
            {...props}
          >
            {children}
          </code>
        );
      }

      return (
        <SyntaxHighlighter
          style={theme === 'dark' ? vscDarkPlus : vs}
          language={language}
          PreTag="div"
          customStyle={{
            margin: '1em 0',
            borderRadius: '8px',
            fontSize: '0.9em'
          }}
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      );
    };
  }, [theme]);

  // 自定义链接渲染
  const LinkRenderer = useMemo(() => {
    return ({ href, children, ...props }: any) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          color: theme === 'dark' ? '#667eea' : '#4f46e5',
          textDecoration: 'underline',
          cursor: 'pointer'
        }}
        {...props}
      >
        {children}
      </a>
    );
  }, [theme]);

  // 自定义图片渲染
  const ImageRenderer = useMemo(() => {
    return ({ src, alt, ...props }: any) => (
      <img
        src={src}
        alt={alt}
        style={{
          maxWidth: '100%',
          height: 'auto',
          borderRadius: '8px',
          margin: '1em 0'
        }}
        loading="lazy"
        {...props}
      />
    );
  }, []);

  // 默认插件
  const defaultPlugins = useMemo(() => ({
    remarkPlugins: [remarkGfm],
    rehypePlugins: [
      rehypeHighlight,
      rehypeRaw,
    ]
  }), []);

  // 合并选项
  const mergedOptions = useMemo(() => ({
    ...defaultPlugins,
    ...options
  }), [options]);

  return (
    <div
      className={`markdown-preview ${className}`}
      style={{
        padding: '20px',
        lineHeight: '1.8',
        fontSize: '16px',
        color: theme === 'dark' ? '#e4e4e7' : '#18181b',
        backgroundColor: theme === 'dark' ? '#1f1f1f' : '#ffffff',
        borderRadius: '8px',
        overflow: 'auto',
        ...style
      }}
    >
      <ReactMarkdown
        {...mergedOptions}
        components={{
          code: CodeBlock,
          a: LinkRenderer,
          img: ImageRenderer,
        }}
      >
        {content}
      </ReactMarkdown>

      <style jsx global>{`
        .markdown-preview h1,
        .markdown-preview h2,
        .markdown-preview h3,
        .markdown-preview h4,
        .markdown-preview h5,
        .markdown-preview h6 {
          margin-top: 1.5em;
          margin-bottom: 0.5em;
          font-weight: 600;
          line-height: 1.25;
        }

        .markdown-preview h1 {
          font-size: 2em;
          border-bottom: 1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'};
          padding-bottom: 0.3em;
        }

        .markdown-preview h2 {
          font-size: 1.5em;
          border-bottom: 1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'};
          padding-bottom: 0.3em;
        }

        .markdown-preview h3 {
          font-size: 1.25em;
        }

        .markdown-preview p {
          margin: 1em 0;
        }

        .markdown-preview ul,
        .markdown-preview ol {
          padding-left: 2em;
          margin: 1em 0;
        }

        .markdown-preview li {
          margin: 0.5em 0;
        }

        .markdown-preview blockquote {
          border-left: 4px solid ${theme === 'dark' ? '#667eea' : '#4f46e5'};
          padding-left: 1em;
          margin: 1em 0;
          color: ${theme === 'dark' ? '#a1a1aa' : '#71717a'};
          font-style: italic;
        }

        .markdown-preview hr {
          border: none;
          border-top: 1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'};
          margin: 2em 0;
        }

        .markdown-preview table {
          border-collapse: collapse;
          width: 100%;
          margin: 1em 0;
        }

        .markdown-preview th,
        .markdown-preview td {
          border: 1px solid ${theme === 'dark' ? '#3f3f46' : '#e4e4e7'};
          padding: 0.5em 1em;
        }

        .markdown-preview th {
          background-color: ${theme === 'dark' ? '#2d2d2d' : '#f4f4f4'};
          font-weight: 600;
        }

        .markdown-preview code {
          font-family: 'Courier New, monospace';
        }

        .markdown-preview pre {
          background-color: ${theme === 'dark' ? '#2d2d2d' : '#f4f4f4'};
          padding: 1em;
          border-radius: 8px;
          overflow-x: auto;
        }

        .markdown-preview input[type="checkbox"] {
          margin-right: 0.5em;
        }
      `}</style>
    </div>
  );
};

export default MarkdownPreview;
