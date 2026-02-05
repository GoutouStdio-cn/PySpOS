# 旧代码存档
# 存档开始时间: 2026-02-05
# 原因: 念旧，保留旧实现

## normalizeUrl 函数的旧实现（版本1）

```javascript
function normalizeUrl(url) {
    try {
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个实现会智能处理外部链接和内部链接，确保外部链接保持原样，内部链接被规范化为相对路径。

---

## normalizeUrl 函数的旧实现（版本2 - 硬编码特定地址）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理特定地址：https://pyspos.us.ci/ota/ota/releases.html
        if (url.includes('pyspos.us.ci/ota/ota/releases.html')) {
            return '/ota/releases.html';
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本添加了硬编码处理特定地址的功能，防止404错误。（但404错误依然存在，并没有实质性解决）

---

## normalizeUrl 函数的旧实现（版本3 - 硬编码所有内部链接）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理所有内部链接，防止404错误
        const hardcodedMappings = {
            // 主页相关
            'index.html': '/index.html',
            '/index.html': '/index.html',
            
            // OTA更新页面相关
            'ota/index.html': '/ota/index.html',
            '/ota/index.html': '/ota/index.html',
            
            // 版本历史页面相关
            'ota/releases.html': '/ota/releases.html',
            '/ota/releases.html': '/ota/releases.html',
            
            // 处理可能的重复路径
            'ota/ota/index.html': '/ota/index.html',
            'ota/ota/releases.html': '/ota/releases.html',
            
            // 完整URL处理
            'pyspos.us.ci/index.html': '/index.html',
            'pyspos.us.ci/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTPS版本
            'https://pyspos.us.ci/index.html': '/index.html',
            'https://pyspos.us.ci/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'https://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTP版本
            'http://pyspos.us.ci/index.html': '/index.html',
            'http://pyspos.us.ci/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/releases.html': '/ota/releases.html',
            'http://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
        };
        
        // 检查是否匹配硬编码映射
        for (const [key, value] of Object.entries(hardcodedMappings)) {
            if (url.includes(key)) {
                return value;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本硬编码了所有内部链接，但存在一个问题：'index.html'映射有冲突，导致从OTA页面返回主页时无法正确导航。需要根据当前页面上下文来决定映射关系。

---

## normalizeUrl 函数的旧实现（版本4 - 智能硬编码，只处理重复路径）

```javascript
function normalizeUrl(url) {
    try {
        // 硬编码处理特定的问题URL，防止404错误
        const hardcodedMappings = {
            // 处理重复路径问题
            'ota/ota/index.html': '/ota/index.html',
            'ota/ota/releases.html': '/ota/releases.html',
            
            // 处理可能的多次重复
            'ota/ota/ota/index.html': '/ota/index.html',
            'ota/ota/ota/releases.html': '/ota/releases.html',
            
            // 处理完整URL中的重复路径
            'pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTPS版本
            'https://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'https://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // HTTP版本
            'http://pyspos.us.ci/ota/ota/index.html': '/ota/index.html',
            'http://pyspos.us.ci/ota/ota/releases.html': '/ota/releases.html',
            
            // 处理localhost的重复路径
            'localhost:8000/ota/ota/index.html': '/ota/index.html',
            'localhost:8000/ota/ota/releases.html': '/ota/releases.html',
            'localhost:8080/ota/ota/index.html': '/ota/index.html',
            'localhost:8080/ota/ota/releases.html': '/ota/releases.html',
        };
        
        // 检查是否匹配硬编码映射（只处理重复路径问题）
        for (const [key, value] of Object.entries(hardcodedMappings)) {
            if (url.includes(key)) {
                return value;
            }
        }
        
        // 处理完整的URL（包括http://和https://）
        if (url.startsWith('http://') || url.startsWith('https://')) {
            const parsedUrl = new URL(url);
            // 如果是外部链接（不是当前域名），直接返回原URL
            if (parsedUrl.hostname !== window.location.hostname) {
                return url;
            }
            // 如果是内部链接，返回pathname
            return parsedUrl.pathname;
        }
        
        // 处理绝对路径
        if (url.startsWith('/')) {
            return url;
        }
        
        // 处理相对路径
        const baseUrl = window.location.origin + window.location.pathname;
        const resolvedUrl = new URL(url, baseUrl);
        
        return resolvedUrl.pathname;
    } catch (error) {
        console.warn('URL规范化失败:', error, url);
        // 返回原始URL作为备选
        return url;
    }
}
```

## 说明
这个版本采用智能硬编码策略，只处理重复路径问题，不干扰正常的相对路径解析。这样既能防止404错误，又能保证SPA导航正常工作。

---

## executePageScripts 函数的旧实现（版本1 - 执行所有脚本）

```javascript
function executePageScripts(doc, url) {
    // 获取页面中的所有script标签
    const scripts = doc.querySelectorAll('script');
    
    scripts.forEach(oldScript => {
        if (oldScript.src) {
            // 外部脚本 - 创建新的script标签
            const newScript = document.createElement('script');
            newScript.src = oldScript.src;
            if (oldScript.type) newScript.type = oldScript.type;
            if (oldScript.async) newScript.async = oldScript.async;
            if (oldScript.defer) newScript.defer = oldScript.defer;
            document.head.appendChild(newScript);
        } else if (oldScript.textContent.trim()) {
            // 使用eval执行（注意安全）
            try {
                eval(oldScript.textContent);
            } catch (e) {
                console.warn('执行内联脚本时出错:', e);
            }
        }
    });
}
```

## 说明
这个实现会执行新页面中的所有脚本，包括导航相关的脚本，这会导致导航状态被重置，造成SPA导航失效。

---

## executePageScripts 函数的旧实现（版本2 - 跳过导航相关脚本）

```javascript
function executePageScripts(doc, url) {
    // 获取页面中的所有script标签
    const scripts = doc.querySelectorAll('script');
    
    scripts.forEach(oldScript => {
        // 跳过导航相关的脚本
        const scriptContent = oldScript.textContent;
        if (scriptContent && (
            scriptContent.includes('function loadPageContent') ||
            scriptContent.includes('function normalizeUrl') ||
            scriptContent.includes('function isSamePage') ||
            scriptContent.includes('function executePageScripts') ||
            scriptContent.includes('function initNavIndicator') ||
            scriptContent.includes('function updateNavIndicator') ||
            scriptContent.includes('function checkAndRedirectUrl') ||
            scriptContent.includes('function toggleMenu') ||
            scriptContent.includes('let isNavigating') ||
            scriptContent.includes('let currentFetchController') ||
            scriptContent.includes('let navigationQueue') ||
            scriptContent.includes('let isInitialized') ||
            scriptContent.includes('let resizeTimeout') ||
            scriptContent.includes('const navLinks') ||
            scriptContent.includes('const navMenu') ||
            scriptContent.includes('const navIndicator') ||
            scriptContent.includes('const navToggle') ||
            scriptContent.includes("addEventListener('click'") ||
            scriptContent.includes("addEventListener('popstate'") ||
            scriptContent.includes("addEventListener('resize'") ||
            scriptContent.includes('window.history.pushState') ||
            scriptContent.includes('window.history.replaceState')
        )) {
            return;
        }
        
        if (oldScript.src) {
            // 外部脚本 - 创建新的script标签
            const newScript = document.createElement('script');
            newScript.src = oldScript.src;
            if (oldScript.type) newScript.type = oldScript.type;
            if (oldScript.async) newScript.async = oldScript.async;
            if (oldScript.defer) newScript.defer = oldScript.defer;
            document.head.appendChild(newScript);
        } else if (oldScript.textContent.trim()) {
            // 使用eval执行（注意安全）
            try {
                eval(oldScript.textContent);
            } catch (e) {
                console.warn('执行内联脚本时出错:', e);
            }
        }
    });
}
```

## 说明
这个实现会跳过导航相关的脚本，只执行页面特定的业务逻辑脚本，确保SPA导航状态不会被重置。
