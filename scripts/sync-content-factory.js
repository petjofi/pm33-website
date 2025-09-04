#!/usr/bin/env node

/**
 * PM33 Content Factory Sync Script
 * 
 * Syncs content from local content factory to web application
 * Usage: node scripts/sync-content-factory.js [command]
 * Commands: sync, deploy, update-blog, help
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  // Content factory paths
  CONTENT_FACTORY_ROOT: '/Users/ssaper/Desktop/my-projects/PM33',
  FINAL_DRAFTS_DIR: 'final drafts',
  KEYWORDS_FILE: 'keywords.md',
  
  // Web app paths  
  WEB_APP_ROOT: path.join(__dirname, '..'),
  MARKETING_PAGES_DIR: path.join(__dirname, '../app/(marketing)'),
  BLOG_PAGE_PATH: path.join(__dirname, '../app/(marketing)/blog/page.tsx'),
  PUBLIC_DIR: path.join(__dirname, '../public'),
  SITEMAP_PATH: path.join(__dirname, '../public/sitemap.xml'),
  ROBOTS_PATH: path.join(__dirname, '../public/robots.txt'),
  
  // Sync settings
  AUTO_DEPLOY_PAGES: true,  // Enhanced: Auto-create SEO-optimized pages
  UPDATE_BLOG_ONLY: false,  // Enhanced: Create individual pages with full SEO
  GENERATE_SITEMAP: true,   // Enhanced: Auto-generate sitemap.xml
  UPDATE_ROBOTS: true,      // Enhanced: Update robots.txt
  
  // SEO Configuration
  BASE_URL: 'https://pm33-website.vercel.app',
  DEFAULT_AUTHOR: 'PM33 Team',
  DEFAULT_IMAGE: '/pm33-logo.png',
  TWITTER_HANDLE: '@PM33AI'
};

class ContentFactorySync {
  constructor() {
    this.articles = [];
  }

  /**
   * Main sync command - syncs content factory to web app
   */
  async sync() {
    console.log('🏭 PM33 Content Factory Sync Starting...');
    console.log(`📂 Source: ${CONFIG.CONTENT_FACTORY_ROOT}`);
    console.log(`🌐 Target: ${CONFIG.WEB_APP_ROOT}`);
    console.log('─'.repeat(50));

    try {
      // Step 1: Scan content factory
      await this.scanContentFactory();
      
      // Step 2: Update blog page with discovered content
      await this.updateBlogPage();
      
      // Step 3: Deploy individual pages with SEO optimization
      if (CONFIG.AUTO_DEPLOY_PAGES) {
        await this.deployPages();
      }

      // Step 4: Generate SEO assets
      if (CONFIG.GENERATE_SITEMAP) {
        await this.generateSitemap();
      }
      
      if (CONFIG.UPDATE_ROBOTS) {
        await this.updateRobotsTxt();
      }

      console.log('─'.repeat(50));
      console.log(`✅ Sync complete! ${this.articles.length} articles processed`);
      console.log('🎯 SEO Features Generated:');
      console.log(`   • ${this.articles.length} SEO-optimized pages with meta tags`);
      console.log('   • Updated sitemap.xml with new URLs');
      console.log('   • Enhanced robots.txt for better crawling');
      console.log('   • Schema markup for rich snippets');
      console.log('🚀 Next steps:');
      console.log('   • Run "npm run dev" to see updated content');
      console.log('   • Deploy to production for SEO benefits');

    } catch (error) {
      console.error('❌ Sync failed:', error.message);
      process.exit(1);
    }
  }

  /**
   * Scan content factory directories for articles
   */
  async scanContentFactory() {
    console.log('🔍 Scanning content factory...');
    
    if (!fs.existsSync(CONFIG.CONTENT_FACTORY_ROOT)) {
      throw new Error(`Content factory not found at: ${CONFIG.CONTENT_FACTORY_ROOT}`);
    }

    const finalDraftsPath = path.join(CONFIG.CONTENT_FACTORY_ROOT, CONFIG.FINAL_DRAFTS_DIR);
    
    if (!fs.existsSync(finalDraftsPath)) {
      console.log('⚠️  Final drafts directory not found, using existing content');
      return;
    }

    // Scan product-sites directory
    const productSitesPath = path.join(finalDraftsPath, 'product-sites');
    if (fs.existsSync(productSitesPath)) {
      const productFiles = fs.readdirSync(productSitesPath).filter(f => f.endsWith('.md'));
      console.log(`📄 Found ${productFiles.length} product landing pages`);
      
      for (const file of productFiles) {
        const article = this.processMarkdownFile(path.join(productSitesPath, file), true);
        if (article) this.articles.push(article);
      }
    }

    // Scan blogs directory
    const blogsPath = path.join(finalDraftsPath, 'blogs');
    if (fs.existsSync(blogsPath)) {
      const blogFiles = fs.readdirSync(blogsPath).filter(f => f.endsWith('.md'));
      console.log(`📝 Found ${blogFiles.length} blog posts`);
      
      for (const file of blogFiles) {
        const article = this.processMarkdownFile(path.join(blogsPath, file), false);
        if (article) this.articles.push(article);
      }
    }

    console.log(`✅ Processed ${this.articles.length} total articles`);
  }

  /**
   * Process individual markdown file
   */
  processMarkdownFile(filePath, featured = false) {
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      const filename = path.basename(filePath, '.md');
      
      // Extract title from first heading
      const titleMatch = content.match(/^#\s+(.+)$/m);
      const title = titleMatch ? titleMatch[1].trim() : this.formatTitle(filename);
      
      // Extract description from content
      const descriptionMatch = content.match(/^\*\*(.+?)\*\*$/m) || 
                              content.match(/^>?\s*(.+?)$/m);
      let description = descriptionMatch ? descriptionMatch[1] : '';
      
      // Fallback description extraction
      if (!description) {
        const paragraphMatch = content.match(/^[^#\*\-\n]+$/m);
        description = paragraphMatch ? paragraphMatch[0].trim() : '';
      }
      
      // Ensure description is properly formatted
      description = description
        .replace(/\*\*(.+?)\*\*/g, '$1') // Remove bold formatting
        .replace(/^\*+\s*/, '')          // Remove leading asterisks
        .trim();
      
      if (description.length > 150) {
        description = description.substring(0, 150) + '...';
      }
      
      if (!description) {
        description = `Comprehensive guide for ${this.extractKeywordFromFilename(filename)}`;
      }

      // Calculate read time
      const wordCount = content.split(/\s+/).length;
      const readTime = Math.ceil(wordCount / 200) + ' min read';

      // Generate URL
      const url = '/' + filename.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');

      // Determine category
      const keyword = this.extractKeywordFromFilename(filename);
      const category = this.determineCategory(keyword, filename);

      // Enhanced SEO metadata extraction
      const seoMetadata = this.extractSEOMetadata(content, title, description, keyword, url);
      
      return {
        id: filename,
        title,
        description,
        category,
        readTime,
        featured,
        url,
        keyword,
        filePath,
        content, // Store full content for page generation
        seo: seoMetadata,
        lastModified: new Date().toISOString()
      };

    } catch (error) {
      console.error(`❌ Error processing ${filePath}:`, error.message);
      return null;
    }
  }

  /**
   * Extract keyword from filename
   */
  extractKeywordFromFilename(filename) {
    return filename
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Format filename to title
   */
  formatTitle(filename) {
    return filename
      .replace(/-/g, ' ')
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  /**
   * Determine category
   */
  determineCategory(keyword, filename) {
    if (keyword.includes('AI') || keyword.includes('Automation')) return 'AI Tools';
    if (keyword.includes('Strategic') || keyword.includes('Strategy')) return 'Strategic Intelligence';
    if (keyword.includes('Resource') || keyword.includes('Planning')) return 'Resource Management';
    if (keyword.includes('Demo') || filename.includes('demo')) return 'Platform Demo';
    if (filename.includes('blog')) return 'Strategic Insights';
    return 'Product Management';
  }

  /**
   * Update blog page with discovered articles
   */
  async updateBlogPage() {
    console.log('📝 Updating blog page with content factory articles...');
    
    if (!fs.existsSync(CONFIG.BLOG_PAGE_PATH)) {
      throw new Error(`Blog page not found at: ${CONFIG.BLOG_PAGE_PATH}`);
    }

    // Read current blog page
    let blogContent = fs.readFileSync(CONFIG.BLOG_PAGE_PATH, 'utf8');
    
    // Generate articles array code
    const articlesCode = this.articles.map(article => `  {
    id: '${article.id}',
    title: '${article.title.replace(/'/g, "\\'")}',
    description: '${article.description.replace(/'/g, "\\'")}',
    category: '${article.category}',
    readTime: '${article.readTime}',
    featured: ${article.featured},
    url: '${article.url}'
  }`).join(',\n');

    const newArticlesArray = `// Auto-generated from PM33 Content Factory - ${new Date().toISOString()}
const resourceArticles = [
${articlesCode}
];`;

    // Replace existing resourceArticles array
    const arrayRegex = /\/\/[^\n]*resourceArticles[\s\S]*?const resourceArticles = \[[^\]]*\];/;
    
    if (arrayRegex.test(blogContent)) {
      blogContent = blogContent.replace(arrayRegex, newArticlesArray);
    } else {
      // If not found, replace the old simple array
      const simpleArrayRegex = /const resourceArticles = \[[^\]]*\];/s;
      if (simpleArrayRegex.test(blogContent)) {
        blogContent = blogContent.replace(simpleArrayRegex, newArticlesArray);
      } else {
        console.log('⚠️  Could not find resourceArticles array to replace');
        return;
      }
    }

    // Write updated blog page
    fs.writeFileSync(CONFIG.BLOG_PAGE_PATH, blogContent);
    console.log(`✅ Updated blog page with ${this.articles.length} articles`);
  }

  /**
   * Deploy individual pages for articles
   */
  async deployPages() {
    console.log('🚀 Deploying individual pages...');
    
    let deployedCount = 0;
    
    for (const article of this.articles) {
      try {
        const urlPath = article.url.substring(1); // Remove leading slash
        const pageDir = path.join(CONFIG.MARKETING_PAGES_DIR, urlPath);
        const pagePath = path.join(pageDir, 'page.tsx');
        
        // Create directory if it doesn't exist
        if (!fs.existsSync(pageDir)) {
          fs.mkdirSync(pageDir, { recursive: true });
        }
        
        // Generate page component
        const pageComponent = this.generatePageComponent(article);
        
        // Write page file
        fs.writeFileSync(pagePath, pageComponent);
        
        console.log(`✅ Created: ${urlPath}/page.tsx`);
        deployedCount++;
        
      } catch (error) {
        console.error(`❌ Failed to deploy ${article.url}:`, error.message);
      }
    }
    
    console.log(`✅ Deployed ${deployedCount} pages`);
  }

  /**
   * Generate Next.js page component
   */
  generatePageComponent(article) {
    const componentName = article.keyword.replace(/[^a-zA-Z0-9]/g, '');
    const seo = article.seo || {};
    
    return `/**
 * Generated by PM33 Content Factory Sync - SEO Optimized
 * Source: ${article.filePath || 'Content Factory'}
 * Target keyword: ${article.keyword}
 * Generated: ${new Date().toISOString()}
 * SEO: Full meta tags, structured data, Open Graph, Twitter Cards
 */

import { Metadata } from 'next';
import { Container, Title, Text, Button, Card, Stack, Group } from '@mantine/core';
import Link from 'next/link';

// SEO Metadata
export const metadata: Metadata = {
  title: '${seo.title || article.title}',
  description: '${seo.description || article.description}',
  keywords: '${seo.keywords || article.keyword}',
  authors: [{ name: '${seo.author || 'PM33 Team'}' }],
  robots: '${seo.robots || 'index, follow'}',
  canonical: '${seo.canonical || ''}',
  openGraph: {
    title: '${seo.ogTitle || article.title}',
    description: '${seo.ogDescription || article.description}',
    url: '${seo.ogUrl || ''}',
    siteName: 'PM33',
    images: [
      {
        url: '${seo.ogImage || '/pm33-logo.png'}',
        width: 1200,
        height: 630,
        alt: '${article.title}'
      }
    ],
    type: 'article',
  },
  twitter: {
    card: '${seo.twitterCard || 'summary_large_image'}',
    title: '${seo.twitterTitle || article.title}',
    description: '${seo.twitterDescription || article.description}',
    images: ['${seo.twitterImage || '/pm33-logo.png'}'],
    creator: '${CONFIG.TWITTER_HANDLE}',
  },
  alternates: {
    canonical: '${seo.canonical || ''}'
  }
};

export default function ${componentName}Page() {
  return (
    <>
      {/* Schema.org Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(${JSON.stringify(seo.schemaMarkup || {})})
        }}
      />
      
      <div className="marketing-context">
        <Container size={1200} px={24} py={80}>
        {/* Hero Section */}
        <Card shadow="md" padding={32} radius={16} mb={48}>
          <Stack align="center" gap={24}>
            <Title order={1} size="48px" fw={700} ta="center">
              ${article.title}
            </Title>
            
            <Text size="xl" c="var(--marketing-text-secondary)" ta="center" maw={800}>
              ${article.description}
            </Text>
            
            <Group>
              <Button 
                component={Link}
                href="/trial"
                size="lg"
                style={{ 
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  fontWeight: 600
                }}
              >
                Start Free 14-Day Trial
              </Button>
              
              <Button 
                component={Link}
                href="/strategic-intelligence"
                size="lg"
                variant="outline"
                style={{ borderColor: 'var(--marketing-primary)' }}
              >
                See Live Demo
              </Button>
            </Group>
          </Stack>
        </Card>

        {/* Processed Content */}
        <Card shadow="sm" padding={32} radius={16} mb={48}>
          <div 
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ 
              __html: \`${this.markdownToHtml(article.content || '').replace(/`/g, '\\`').replace(/\${/g, '\\${')}\` 
            }} 
          />
        </Card>

        {/* CTA Section */}
        <Card 
          shadow="xl" 
          padding="xl" 
          radius="lg" 
          mt={60} 
          ta="center"
          style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white'
          }}
        >
          <Title order={2} c="white" mb="lg">Ready to Transform Your PM Workflow?</Title>
          <Text size="lg" mb="lg" opacity={0.9}>
            Join 2,500+ product managers using PM33's AI-powered strategic intelligence platform
          </Text>
          <Group justify="center">
            <Button 
              size="lg"
              variant="white"
              color="dark"
              component={Link}
              href="/trial"
            >
              Start Free Trial
            </Button>
            <Button 
              size="lg"
              variant="outline"
              style={{ borderColor: 'white', color: 'white' }}
              component={Link}
              href="/strategic-intelligence"
            >
              See Live Demo
            </Button>
          </Group>
        </Card>
      </Container>
      </div>
    </>
  );
}`;
  }

  /**
   * Convert markdown to HTML (enhanced version)
   */
  markdownToHtml(markdown) {
    if (!markdown) return '';
    
    return markdown
      // Headers
      .replace(/^### (.+)$/gm, '<h3>$1</h3>')
      .replace(/^## (.+)$/gm, '<h2>$1</h2>')
      .replace(/^# (.+)$/gm, '<h1>$1</h1>')
      // Bold and italic
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      // Links
      .replace(/\[(.+?)\]\((.+?)\)/g, '<a href="$2" class="text-blue-600 hover:underline">$1</a>')
      // Lists
      .replace(/^\- (.+)$/gm, '<li>$1</li>')
      .replace(/(<li>.*<\/li>)/s, '<ul class="list-disc pl-6 mb-4">$1</ul>')
      // Tables (basic support)
      .replace(/\|(.+)\|/g, (match, content) => {
        const cells = content.split('|').map(cell => `<td class="border px-4 py-2">${cell.trim()}</td>`).join('');
        return `<tr>${cells}</tr>`;
      })
      // Paragraphs
      .replace(/\n\n/g, '</p><p class="mb-4">')
      .replace(/^(.+)$/gm, '<p class="mb-4">$1</p>')
      // Clean up
      .replace(/<p class="mb-4"><h/g, '<h')
      .replace(/<\/h([1-6])><\/p>/g, '</h$1>')
      .replace(/<p class="mb-4"><ul/g, '<ul')
      .replace(/<\/ul><\/p>/g, '</ul>')
      .replace(/<p class="mb-4"><tr>/g, '<tr>')
      .replace(/<\/tr><\/p>/g, '</tr>')
      // Wrap tables
      .replace(/(<tr>.*<\/tr>)/s, '<table class="table-auto border-collapse border mb-6">$1</table>');
  }

  /**
   * Show help information
   */
  /**
   * Extract comprehensive SEO metadata from content
   */
  extractSEOMetadata(content, title, description, keyword, url) {
    // Extract keywords from content
    const keywords = this.extractKeywords(content, keyword);
    
    // Create schema markup
    const schemaMarkup = this.generateSchemaMarkup(title, description, url);
    
    return {
      title: title,
      description: description,
      keywords: keywords.join(', '),
      canonical: CONFIG.BASE_URL + url,
      ogTitle: title,
      ogDescription: description,
      ogImage: CONFIG.BASE_URL + CONFIG.DEFAULT_IMAGE,
      ogUrl: CONFIG.BASE_URL + url,
      twitterTitle: title,
      twitterDescription: description,
      twitterImage: CONFIG.BASE_URL + CONFIG.DEFAULT_IMAGE,
      twitterCard: 'summary_large_image',
      author: CONFIG.DEFAULT_AUTHOR,
      schemaMarkup: schemaMarkup,
      lastModified: new Date().toISOString(),
      robots: 'index, follow'
    };
  }

  /**
   * Extract relevant keywords from content
   */
  extractKeywords(content, primaryKeyword) {
    const keywords = [primaryKeyword];
    
    // Common PM33-related terms
    const pmTerms = ['product management', 'AI tools', 'strategic intelligence', 'PM33', 'roadmap', 'prioritization'];
    const contentLower = content.toLowerCase();
    
    pmTerms.forEach(term => {
      if (contentLower.includes(term.toLowerCase()) && !keywords.includes(term)) {
        keywords.push(term);
      }
    });
    
    return keywords.slice(0, 10); // Limit to 10 keywords
  }

  /**
   * Generate Schema.org structured data
   */
  generateSchemaMarkup(title, description, url) {
    return {
      "@context": "https://schema.org",
      "@type": "Article",
      "headline": title,
      "description": description,
      "url": CONFIG.BASE_URL + url,
      "datePublished": new Date().toISOString(),
      "dateModified": new Date().toISOString(),
      "author": {
        "@type": "Organization",
        "name": CONFIG.DEFAULT_AUTHOR,
        "url": CONFIG.BASE_URL
      },
      "publisher": {
        "@type": "Organization",
        "name": "PM33",
        "logo": {
          "@type": "ImageObject",
          "url": CONFIG.BASE_URL + CONFIG.DEFAULT_IMAGE
        }
      },
      "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": CONFIG.BASE_URL + url
      }
    };
  }

  /**
   * Generate sitemap.xml for all articles
   */
  async generateSitemap() {
    console.log('🗺️  Generating sitemap.xml...');
    
    let sitemapXml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Homepage -->
  <url>
    <loc>${CONFIG.BASE_URL}</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- Main pages -->
  <url>
    <loc>${CONFIG.BASE_URL}/pricing</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.9</priority>
  </url>
  
  <url>
    <loc>${CONFIG.BASE_URL}/about</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
  
  <url>
    <loc>${CONFIG.BASE_URL}/blog</loc>
    <lastmod>${new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
`;

    // Add all articles to sitemap
    for (const article of this.articles) {
      sitemapXml += `  
  <url>
    <loc>${CONFIG.BASE_URL}${article.url}</loc>
    <lastmod>${article.lastModified ? article.lastModified.split('T')[0] : new Date().toISOString().split('T')[0]}</lastmod>
    <changefreq>${article.featured ? 'weekly' : 'monthly'}</changefreq>
    <priority>${article.featured ? '0.9' : '0.7'}</priority>
  </url>`;
    }

    sitemapXml += `
</urlset>`;

    // Write sitemap
    fs.writeFileSync(CONFIG.SITEMAP_PATH, sitemapXml);
    console.log(`✅ Generated sitemap.xml with ${this.articles.length + 4} URLs`);
  }

  /**
   * Update robots.txt for better crawling
   */
  async updateRobotsTxt() {
    console.log('🤖 Updating robots.txt...');
    
    const robotsTxt = `User-agent: *
Allow: /

# Sitemaps
Sitemap: ${CONFIG.BASE_URL}/sitemap.xml

# Block admin and private areas
Disallow: /admin/
Disallow: /_next/
Disallow: /api/

# Allow important pages
Allow: /
Allow: /pricing
Allow: /about
Allow: /blog
${this.articles.map(article => `Allow: ${article.url}`).join('\n')}

# Crawl delay
Crawl-delay: 1
`;

    fs.writeFileSync(CONFIG.ROBOTS_PATH, robotsTxt);
    console.log('✅ Updated robots.txt with article URLs');
  }

  showHelp() {
    console.log(`
🏭 PM33 Content Factory Sync Tool - Enhanced SEO Edition

Commands:
  sync     - Sync content factory with full SEO optimization
  deploy   - Deploy individual pages with SEO metadata
  help     - Show this help information

Usage:
  node scripts/sync-content-factory.js [command]

Examples:
  node scripts/sync-content-factory.js sync
  node scripts/sync-content-factory.js deploy

SEO Features:
  ✅ Auto-generated meta tags and Open Graph data
  ✅ Schema.org structured data for rich snippets
  ✅ Dynamic sitemap.xml generation
  ✅ Enhanced robots.txt with article URLs
  ✅ Keyword extraction and optimization
  ✅ Canonical URLs and social media tags

Configuration:
  Content Factory: ${CONFIG.CONTENT_FACTORY_ROOT}
  Web App: ${CONFIG.WEB_APP_ROOT}
  Base URL: ${CONFIG.BASE_URL}
  Auto Deploy: ${CONFIG.AUTO_DEPLOY_PAGES}
  SEO Features: ${CONFIG.GENERATE_SITEMAP ? 'Enabled' : 'Disabled'}
    `);
  }
}

// Command line interface
async function main() {
  const command = process.argv[2] || 'sync';
  const sync = new ContentFactorySync();

  switch (command) {
    case 'sync':
      await sync.sync();
      break;
      
    case 'deploy':
      await sync.scanContentFactory();
      await sync.deployPages();
      break;
      
    case 'help':
      sync.showHelp();
      break;
      
    default:
      console.log(`Unknown command: ${command}`);
      sync.showHelp();
      process.exit(1);
  }
}

if (require.main === module) {
  main().catch(console.error);
}

module.exports = ContentFactorySync;